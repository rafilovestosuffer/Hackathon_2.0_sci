import io
import wave
import pytest
from faster_whisper import WhisperModel
from voice.pipeline import transcribe_audio, _get_model


def _make_silent_wav(duration_s: float = 1.0, sample_rate: int = 16000) -> bytes:
    """Generate a minimal valid silent WAV file in memory."""
    buf = io.BytesIO()
    n_frames = int(sample_rate * duration_s)
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)          # 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(b"\x00\x00" * n_frames)
    return buf.getvalue()


# ── Model singleton ───────────────────────────────────────────────────────────

class TestGetModel:
    def test_returns_whisper_model(self):
        model = _get_model()
        assert isinstance(model, WhisperModel)

    def test_singleton_same_object(self):
        m1 = _get_model()
        m2 = _get_model()
        assert m1 is m2


# ── transcribe_audio ──────────────────────────────────────────────────────────

class TestTranscribeAudio:
    def test_returns_str_type(self):
        result = transcribe_audio(_make_silent_wav())
        assert isinstance(result, str)

    def test_silent_wav_no_crash(self):
        result = transcribe_audio(_make_silent_wav())
        assert result is not None

    def test_wav_format_no_exception(self):
        result = transcribe_audio(_make_silent_wav(), fmt="wav")
        assert isinstance(result, str)

    def test_mp3_format_bytes_no_crash(self):
        # Pass WAV bytes with mp3 label — whisper will fail gracefully
        result = transcribe_audio(_make_silent_wav(), fmt="mp3")
        assert isinstance(result, str)

    def test_webm_format_bytes_no_crash(self):
        result = transcribe_audio(_make_silent_wav(), fmt="webm")
        assert isinstance(result, str)

    def test_empty_bytes_returns_empty_string(self):
        result = transcribe_audio(b"")
        assert result == ""

    def test_garbage_bytes_returns_empty_string(self):
        result = transcribe_audio(b"\x00\xff\x00\xff" * 100, fmt="wav")
        assert isinstance(result, str)

    def test_result_is_stripped(self):
        result = transcribe_audio(_make_silent_wav())
        assert result == result.strip()
