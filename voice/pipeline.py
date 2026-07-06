"""
voice/pipeline.py
─────────────────
Bengali audio → transcript → structured patient history.

Design choices:
  - decode_audio(BytesIO) converts ANY format (WAV/WebM/MP4/OGG) to float32 numpy
    via PyAV (already a faster-whisper dependency) — no temp files, no ffmpeg in PATH
  - language defaults to "bn" but "en"/None (auto-detect) are supported; a 3-pass
    transcription (VAD filter → no-VAD retry → Bengali-script correction) handles the
    `small` model's tendency to leak Devanagari on short Bengali clinical speech
  - RMS energy check prevents empty-transcript errors on silent recordings
  - Gemini extraction retries 3× with full validation
"""

import io
import json
import logging
import os
import tempfile

import numpy as np
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# --- Singletons ---
_whisper_model = None
_gemini_client = None

# --- Constants ---
_SILENCE_RMS_THRESHOLD  = 0.0005   # below this → treat as silence
_MIN_AUDIO_SECONDS      = 0.5      # recordings shorter than this are rejected
_NO_SPEECH_PROB_MAX     = 0.55     # segments above this threshold are hallucination
_MIN_GOOD_SEGMENT_RATIO = 0.4      # if fewer than 40% of segs pass, reject whole result
_PASS2_MIN_SECONDS      = 2.0      # only do no-VAD retry for audio longer than this

_HISTORY_KEYS = {
    "chief_complaint":    "",
    "symptoms":           [],
    "affected_area":      "",
    "duration":           "",
    "progression":        "",
    "previous_treatment": "",
    "associated_symptoms": [],
    "patient_name":       "",
    "patient_age":        "",
}

_EXTRACTION_PROMPT = """You are a medical assistant helping rural Bangladeshi patients. \
Extract patient history from the transcript below. The transcript may be in Bengali (বাংলা), \
English, or a mix. It may also contain romanized Bengali (e.g. "amar gaye khuj hocche" means \
"I have itching on my body"). Interpret the meaning carefully regardless of script.

Return ONLY valid JSON with exactly these keys — no extra text, no markdown:
{{
  "chief_complaint": "primary skin complaint in English (e.g. Itching, Rash, Redness)",
  "symptoms": ["list", "of", "symptoms", "in", "English"],
  "affected_area": "body part in English (e.g. arm, face, back) or empty string",
  "duration": "how long (e.g. 3 days, 2 weeks) or empty string",
  "progression": "getting better / getting worse / stable / spreading or empty string",
  "previous_treatment": "any treatment tried or empty string",
  "associated_symptoms": ["fever", "pain", "etc. or empty list"],
  "patient_name": "name if mentioned or empty string",
  "patient_age": "age if mentioned or empty string"
}}

Rules:
- Only extract what is CLEARLY stated. Do NOT guess or hallucinate.
- If the transcript is unclear noise or random words with no medical meaning, return all empty strings/lists.
- chief_complaint and symptoms must relate to a SKIN or BODY condition.

Transcript: {transcript}"""


# --- Internal helpers ---

def _empty_history() -> dict:
    return {k: ([] if isinstance(v, list) else "") for k, v in _HISTORY_KEYS.items()}


def _validate_fields(data: dict) -> dict:
    result = _empty_history()
    for key, default in _HISTORY_KEYS.items():
        val = data.get(key, default)
        if isinstance(default, list) and not isinstance(val, list):
            val = [val] if val else []
        if isinstance(default, str) and not isinstance(val, str):
            val = str(val) if val else ""
        result[key] = val
    return result


def _strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        parts = text.split("```")
        text = parts[1] if len(parts) > 1 else text
        if text.startswith("json"):
            text = text[4:]
    return text.strip()


def _get_model():
    """Singleton faster-whisper model (tests patch this name)."""
    global _whisper_model
    if _whisper_model is None:
        from faster_whisper import WhisperModel
        _whisper_model = WhisperModel("small", device="cpu", compute_type="int8")
    return _whisper_model

# Alias used internally
_get_whisper = _get_model


def _get_gemini_client():
    """Singleton Gemini client (tests patch this name)."""
    global _gemini_client
    if _gemini_client is None:
        from google import genai
        _gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY", ""))
    return _gemini_client

# Alias used internally
_get_gemini = _get_gemini_client


def _bytes_to_audio_array(audio_bytes: bytes) -> np.ndarray | None:
    """
    Convert raw audio bytes (ANY format) → float32 mono numpy array @ 16kHz.

    Uses faster_whisper.audio.decode_audio which calls PyAV internally.
    PyAV reads format from file magic bytes, not extension — works for
    WAV, WebM, MP4, OGG, MP3, M4A, etc.

    Returns None on failure.
    """
    try:
        from faster_whisper.audio import decode_audio
        audio_arr = decode_audio(io.BytesIO(audio_bytes))   # float32, 16kHz, mono
        return audio_arr
    except Exception as exc:
        logger.error("decode_audio failed: %s", exc)
        return None


def _check_audio_quality(audio_arr: np.ndarray) -> tuple[bool, float, str]:
    """
    Returns (is_ok, rms_energy, reason_if_not_ok).
    """
    if audio_arr is None or len(audio_arr) == 0:
        return False, 0.0, "empty"

    duration_sec = len(audio_arr) / 16000.0
    rms = float(np.sqrt(np.mean(audio_arr.astype(np.float64) ** 2)))

    logger.info("Audio quality: duration=%.2fs, RMS=%.6f", duration_sec, rms)

    if duration_sec < _MIN_AUDIO_SECONDS:
        return False, rms, f"too_short ({duration_sec:.2f}s)"
    if rms < _SILENCE_RMS_THRESHOLD:
        return False, rms, "silence"
    return True, rms, ""


# --- Public API ---

# Initial prompts force the model to output in the right script.
# Without these, Whisper often romanizes Bengali into Latin OR — worse —
# transcribes Bengali speech into Devanagari (Hindi) characters because the
# `small` model is biased toward higher-resource Indic scripts.
_INITIAL_PROMPTS = {
    "bn": "আমার ত্বকে সমস্যা হচ্ছে।",
    "en": "I have a skin problem.",
}

# Unicode ranges used to detect script leaks (e.g. Bengali speech transcribed
# as Devanagari) so we can do a corrective second pass.
_SCRIPT_RANGES = {
    "bn": ("ঀ", "৿"),   # Bengali block
    "en": (" ", "~"),   # Basic Latin
}


def _script_matches(text: str, language: str, min_chars: int = 3) -> bool:
    """Does `text` contain enough characters from the expected script for `language`?"""
    bounds = _SCRIPT_RANGES.get(language)
    if not bounds or not text:
        return True   # nothing to check
    lo, hi = bounds
    return sum(1 for c in text if lo <= c <= hi) >= min_chars


def _is_hallucinated(text: str) -> bool:
    """
    Detect Whisper hallucination signatures:
    - Box/diamond replacement chars (□ ◆ ◇ ▪ ▫ ■ etc.)  U+2500–U+27FF
    - Unicode replacement char U+FFFD
    - Excessive repetition of the same token
    """
    if not text:
        return False
    # Geometric/box chars that appear when Whisper maps noise to invalid tokens.
    # These NEVER appear in legitimate Bengali medical speech output.
    garbage = sum(1 for c in text if '─' <= c <= '⟿' or c == '�')
    if garbage >= 1:
        return True
    # Repetition: any word repeated 4+ times in a row
    words = text.split()
    for i in range(len(words) - 3):
        if words[i] == words[i+1] == words[i+2] == words[i+3]:
            return True
    return False


def _filter_segments(segments) -> tuple[list, int]:
    """
    Materialise segment generator, drop high-no_speech_prob segments.
    Returns (good_segments, total_count).
    """
    all_segs = list(segments)
    total = len(all_segs)
    good = [s for s in all_segs if getattr(s, "no_speech_prob", 0.0) < _NO_SPEECH_PROB_MAX]
    return good, total


def _segs_to_text(segments: list) -> str:
    return " ".join(s.text.strip() for s in segments).strip()


def transcribe_audio_detailed(
    audio_bytes: bytes,
    fmt: str = "wav",              # kept for API compatibility, not used for format detection
    language: str | None = "bn",
) -> tuple[str, str, float]:
    """
    Transcribe audio bytes → (transcript, detected_language, language_probability).

    - Accepts ANY audio format (WAV/WebM/MP4/OGG/MP3) — format detected from
      magic bytes by PyAV, not the `fmt` hint.
    - language="bn" forces Bengali, "en" forces English, None auto-detects.
    - initial_prompt is chosen to match the *requested* language so Whisper
      outputs in the correct script. Auto-detect uses no prompt to avoid bias.
    - Returns ("", "", 0.0) on silence, very short audio, or any error.
    """
    if not audio_bytes or len(audio_bytes) < 500:
        logger.warning("transcribe_audio: audio_bytes too short (%d)", len(audio_bytes))
        return "", "", 0.0

    audio_arr = _bytes_to_audio_array(audio_bytes)
    if audio_arr is None:
        logger.error("transcribe_audio: could not decode audio bytes")
        return "", "", 0.0

    is_ok, rms, reason = _check_audio_quality(audio_arr)
    if not is_ok:
        logger.warning("transcribe_audio: audio rejected — %s (RMS=%.6f)", reason, rms)
        return "", "", 0.0

    duration_sec = len(audio_arr) / 16000.0

    try:
        model = _get_model()
        prompt = _INITIAL_PROMPTS.get(language) if language else None

        # Pass 1: VAD-filtered + no_speech_prob segment filtering.
        raw_segs, info = model.transcribe(
            audio_arr,
            language=language,
            beam_size=1,
            initial_prompt=prompt,
            vad_filter=True,
            vad_parameters={"min_silence_duration_ms": 500},
        )
        good_segs, total_segs = _filter_segments(raw_segs)
        detected = getattr(info, "language", "") or ""
        prob = float(getattr(info, "language_probability", 0.0) or 0.0)

        # Reject if too few segments passed the no_speech filter
        if total_segs > 0 and len(good_segs) / total_segs < _MIN_GOOD_SEGMENT_RATIO:
            logger.warning(
                "transcribe_audio: %d/%d segs passed no_speech filter — likely noise",
                len(good_segs), total_segs,
            )
            return "", detected, prob

        text = _segs_to_text(good_segs)

        # Pass 2: only retry without VAD for longer audio where VAD may have been
        # too aggressive. Skip for short clips where VAD silence = real silence.
        if not text and duration_sec >= _PASS2_MIN_SECONDS:
            logger.info("transcribe_audio: VAD pass empty on %.1fs audio — retrying without VAD", duration_sec)
            raw_segs2, info2 = model.transcribe(
                audio_arr,
                language=language,
                beam_size=1,
                initial_prompt=prompt,
                vad_filter=False,
            )
            good_segs2, total_segs2 = _filter_segments(raw_segs2)
            text2 = _segs_to_text(good_segs2)
            if text2 and not _is_hallucinated(text2):
                text = text2
                detected = getattr(info2, "language", "") or detected
                prob = float(getattr(info2, "language_probability", 0.0) or 0.0) or prob

        # Reject hallucinated output (box chars, looping tokens, mixed garbage)
        if text and _is_hallucinated(text):
            logger.warning("transcribe_audio: hallucination detected — discarding: %s", text[:80])
            return "", detected, prob

        # Pass 3: BD-centric correction. In auto-detect mode the `small` model
        # is noisy on short Bengali clinical speech — common failures are:
        #   - detects "bn" but outputs Devanagari (Hindi) because no prompt
        #   - mis-detects Bengali as Urdu / Hindi / Marathi at low confidence
        if language is None and text:
            needs_correction = False
            if detected not in _INITIAL_PROMPTS:
                needs_correction = True
                fallback_lang = "bn"
            elif not _script_matches(text, detected):
                needs_correction = True
                fallback_lang = detected
            else:
                fallback_lang = None

            if needs_correction and fallback_lang:
                logger.info(
                    "transcribe_audio: correcting (detected=%s prob=%.2f) → re-running as %s",
                    detected, prob, fallback_lang,
                )
                raw_segs3, info3 = model.transcribe(
                    audio_arr,
                    language=fallback_lang,
                    beam_size=1,
                    initial_prompt=_INITIAL_PROMPTS[fallback_lang],
                    vad_filter=True,
                    vad_parameters={"min_silence_duration_ms": 500},
                )
                good_segs3, _ = _filter_segments(raw_segs3)
                corrected = _segs_to_text(good_segs3)
                if corrected and _script_matches(corrected, fallback_lang) and not _is_hallucinated(corrected):
                    text = corrected
                    detected = fallback_lang
                    prob = max(prob, 0.85)

        logger.info(
            "transcribe_audio: requested=%s detected=%s (%.0f%%) len=%d chars",
            language, detected, prob * 100, len(text),
        )
        return text, detected, prob
    except Exception as exc:
        logger.error("transcribe_audio: transcription failed: %s", exc)
        return "", "", 0.0


def transcribe_audio(
    audio_bytes: bytes,
    fmt: str = "wav",
    language: str | None = "bn",
) -> str:
    """Backward-compatible thin wrapper around transcribe_audio_detailed()."""
    text, _, _ = transcribe_audio_detailed(audio_bytes, fmt=fmt, language=language)
    return text


def extract_patient_history(transcript: str) -> dict:
    """
    Extract structured patient history from transcript via Gemini 2.5 Flash-Lite.
    Always returns a dict with all 9 keys — never raises.
    """
    if not transcript or not transcript.strip():
        return _empty_history()

    prompt = _EXTRACTION_PROMPT.format(transcript=transcript)

    for attempt in range(3):
        try:
            client = _get_gemini_client()
            response = client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=prompt,
            )
            text = _strip_fences(response.text)
            data = json.loads(text)
            return _validate_fields(data)
        except Exception as exc:
            logger.warning("Gemini attempt %d failed: %s", attempt + 1, exc)

    return _empty_history()
