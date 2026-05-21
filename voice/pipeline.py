"""
voice/pipeline.py
─────────────────
Bengali audio → transcript → structured patient history.

Design choices:
  - decode_audio(BytesIO) converts ANY format (WAV/WebM/MP4/OGG) to float32 numpy
    via PyAV (already a faster-whisper dependency) — no temp files, no ffmpeg in PATH
  - Whisper language always forced to "bn" — no auto-detection uncertainty
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

# ── Singletons ────────────────────────────────────────────────────────────────
_whisper_model = None
_gemini_client = None

# ── Constants ─────────────────────────────────────────────────────────────────
_SILENCE_RMS_THRESHOLD = 0.0005   # below this → treat as silence
_MIN_AUDIO_SECONDS     = 0.5      # recordings shorter than this are rejected

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


# ── Internal helpers ──────────────────────────────────────────────────────────

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


# ── Public API ────────────────────────────────────────────────────────────────

# Initial prompts force the model to output in the right script.
# Without these, Whisper often romanizes Bengali speech into Latin characters.
_INITIAL_PROMPTS = {
    "bn": "আমার ত্বকে সমস্যা হচ্ছে।",
    "en": "I have a skin problem.",
}


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

    try:
        model = _get_model()
        prompt = _INITIAL_PROMPTS.get(language) if language else None

        # Pass 1: VAD-filtered (clean output for normal-length speech).
        segments, info = model.transcribe(
            audio_arr,
            language=language,
            beam_size=5,
            initial_prompt=prompt,
            vad_filter=True,
            vad_parameters={"min_silence_duration_ms": 500},
        )
        text = " ".join(seg.text.strip() for seg in segments).strip()
        detected = getattr(info, "language", "") or ""
        prob = float(getattr(info, "language_probability", 0.0) or 0.0)

        # Pass 2: if VAD ate everything (short utterance, low-volume mic),
        # retry without VAD so short clips like 1-2 sec phrases still transcribe.
        if not text:
            logger.info("transcribe_audio: VAD pass empty — retrying without VAD")
            segments, info = model.transcribe(
                audio_arr,
                language=language,
                beam_size=5,
                initial_prompt=prompt,
                vad_filter=False,
            )
            text = " ".join(seg.text.strip() for seg in segments).strip()
            detected = getattr(info, "language", "") or detected
            prob = float(getattr(info, "language_probability", 0.0) or 0.0) or prob

        logger.info(
            "transcribe_audio: requested=%s, detected=%s (%.0f%%), len=%d chars",
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
    Extract structured patient history from transcript via Gemini 2.5 Flash.
    Always returns a dict with all 9 keys — never raises.
    """
    if not transcript or not transcript.strip():
        return _empty_history()

    prompt = _EXTRACTION_PROMPT.format(transcript=transcript)

    for attempt in range(3):
        try:
            client = _get_gemini_client()
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            text = _strip_fences(response.text)
            data = json.loads(text)
            return _validate_fields(data)
        except Exception as exc:
            logger.warning("Gemini attempt %d failed: %s", attempt + 1, exc)

    return _empty_history()
