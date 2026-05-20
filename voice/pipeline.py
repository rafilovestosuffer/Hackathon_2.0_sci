import json
import logging
import os
import tempfile

from dotenv import load_dotenv
from faster_whisper import WhisperModel
from google import genai

load_dotenv()

logger = logging.getLogger(__name__)

_model: WhisperModel | None = None
_gemini_client: genai.Client | None = None

_HISTORY_KEYS = {
    "chief_complaint": "",
    "symptoms": [],
    "affected_area": "",
    "duration": "",
    "progression": "",
    "previous_treatment": "",
    "associated_symptoms": [],
    "patient_name": "",
    "patient_age": "",
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


# ── Helpers ───────────────────────────────────────────────────────────────────

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


def _get_gemini_client() -> genai.Client:
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY", ""))
    return _gemini_client


# ── Whisper model singleton ───────────────────────────────────────────────────

def _get_model() -> WhisperModel:
    global _model
    if _model is None:
        _model = WhisperModel("base", device="cpu", compute_type="int8")
    return _model


# ── Public API ────────────────────────────────────────────────────────────────

def transcribe_audio(audio_bytes: bytes, fmt: str = "wav", language: str | None = None) -> str:
    """Transcribe audio bytes → transcript string.

    language: ISO-639-1 code ("bn", "en") or None for auto-detect.
    """
    if not audio_bytes:
        return ""

    suffix = f".{fmt.lstrip('.')}"
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        model = _get_model()
        segments, _ = model.transcribe(tmp_path, language=language, beam_size=5)
        return " ".join(seg.text.strip() for seg in segments).strip()

    except Exception as exc:
        logger.error("transcribe_audio failed: %s", exc)
        return ""

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)


def extract_patient_history(transcript: str) -> dict:
    """
    Extract structured patient history from a Bengali transcript via Gemini.
    Always returns a dict with all 9 keys — never raises.
    """
    if not transcript or not transcript.strip():
        return _empty_history()

    prompt = _EXTRACTION_PROMPT.format(transcript=transcript)
    client = _get_gemini_client()

    for attempt in range(3):
        try:
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
