import logging
import os
import tempfile

from faster_whisper import WhisperModel

logger = logging.getLogger(__name__)

_model: WhisperModel | None = None


def _get_model() -> WhisperModel:
    global _model
    if _model is None:
        _model = WhisperModel("base", device="cpu", compute_type="int8")
    return _model


def transcribe_audio(audio_bytes: bytes, fmt: str = "wav") -> str:
    """
    Transcribe Bengali audio bytes → Bengali transcript string.

    Args:
        audio_bytes: Raw audio content from mic recorder or file upload.
        fmt: File format hint — "wav", "mp3", or "webm".

    Returns:
        Bengali transcript string, or "" on failure / silence.
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
        segments, _ = model.transcribe(tmp_path, language="bn", beam_size=5)
        transcript = " ".join(seg.text.strip() for seg in segments).strip()
        return transcript

    except Exception as exc:
        logger.error("transcribe_audio failed: %s", exc)
        return ""

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
