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

_EXTRACTION_PROMPT = """You are a medical assistant. Extract patient history from this transcript (Bengali or English).
Return ONLY valid JSON with exactly these keys:
{{
  "chief_complaint": "",
  "symptoms": [],
  "affected_area": "",
  "duration": "",
  "progression": "",
  "previous_treatment": "",
  "associated_symptoms": [],
  "patient_name": "",
  "patient_age": ""
}}
Fill each field from the transcript. Use empty string "" or empty list [] if information is not mentioned.
Do not add any text outside the JSON.

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
        _whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
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

def transcribe_audio(
    audio_bytes: bytes,
    fmt: str = "wav",              # kept for API compatibility, not used for format detection
    language: str = "bn",
) -> str:
    """
    Transcribe audio bytes → Bengali transcript string.

    - Accepts ANY audio format (WAV/WebM/MP4/OGG/MP3) — format detected from
      magic bytes by PyAV, not the `fmt` hint.
    - language="bn" forces Bengali; pass language=None for auto-detect.
    - Returns "" on silence, very short audio, or any error.
    """
    if not audio_bytes or len(audio_bytes) < 500:
        logger.warning("transcribe_audio: audio_bytes too short (%d)", len(audio_bytes))
        return ""

    # 1. Decode to float32 numpy array
    audio_arr = _bytes_to_audio_array(audio_bytes)
    if audio_arr is None:
        logger.error("transcribe_audio: could not decode audio bytes")
        return ""

    # 2. Quality gate
    is_ok, rms, reason = _check_audio_quality(audio_arr)
    if not is_ok:
        logger.warning("transcribe_audio: audio rejected — %s (RMS=%.6f)", reason, rms)
        return ""

    # 3. Transcribe
    try:
        model = _get_model()
        segments, info = model.transcribe(
            audio_arr,
            language=language,
            beam_size=5,
            vad_filter=True,        # skip non-speech segments
            vad_parameters={"min_silence_duration_ms": 500},
        )
        text = " ".join(seg.text.strip() for seg in segments).strip()
        logger.info(
            "transcribe_audio: lang=%s (%.0f%%), len=%d chars",
            info.language, info.language_probability * 100, len(text),
        )
        return text
    except Exception as exc:
        logger.error("transcribe_audio: transcription failed: %s", exc)
        return ""


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
