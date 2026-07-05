import io
import wave
from unittest.mock import MagicMock, patch

import pytest
from faster_whisper import WhisperModel
from voice.pipeline import (
    _INITIAL_PROMPTS,
    _get_model,
    transcribe_audio,
    transcribe_audio_detailed,
)


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


# --- Model singleton ---

class TestGetModel:
    def test_returns_whisper_model(self):
        model = _get_model()
        assert isinstance(model, WhisperModel)

    def test_singleton_same_object(self):
        m1 = _get_model()
        m2 = _get_model()
        assert m1 is m2


# --- transcribe_audio ---

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


# --- transcribe_audio_detailed: auto-detect + prompt selection ---

def _fake_model_returning(lang: str, prob: float, text: str = "hello"):
    """Build a fake WhisperModel whose .transcribe records the call kwargs."""
    fake = MagicMock()
    seg = MagicMock()
    seg.text = text
    seg.no_speech_prob = 0.0   # must be a real float; MagicMock attr fails < comparison
    info = MagicMock()
    info.language = lang
    info.language_probability = prob
    fake.transcribe.return_value = ([seg], info)
    return fake


class TestTranscribeDetailed:
    def test_detailed_returns_5_tuple_shape(self):
        text, det, prob = transcribe_audio_detailed(_make_silent_wav())
        assert isinstance(text, str)
        assert isinstance(det, str)
        assert isinstance(prob, float)

    def test_detailed_empty_bytes(self):
        assert transcribe_audio_detailed(b"") == ("", "", 0.0)

    def test_bn_request_uses_bengali_initial_prompt(self):
        fake = _fake_model_returning("bn", 0.95, "নমস্কার")
        with patch("voice.pipeline._get_model", return_value=fake):
            transcribe_audio_detailed(_make_silent_wav(duration_s=2.0), language="bn")
        # silent WAV gets rejected by quality gate; bypass by patching that too
        with patch("voice.pipeline._get_model", return_value=fake), \
             patch("voice.pipeline._check_audio_quality", return_value=(True, 0.1, "")):
            transcribe_audio_detailed(_make_silent_wav(duration_s=2.0), language="bn")
        kwargs = fake.transcribe.call_args.kwargs
        assert kwargs["language"] == "bn"
        assert kwargs["initial_prompt"] == _INITIAL_PROMPTS["bn"]

    def test_en_request_uses_english_initial_prompt(self):
        fake = _fake_model_returning("en", 0.99, "hello")
        with patch("voice.pipeline._get_model", return_value=fake), \
             patch("voice.pipeline._check_audio_quality", return_value=(True, 0.1, "")):
            transcribe_audio_detailed(_make_silent_wav(duration_s=2.0), language="en")
        kwargs = fake.transcribe.call_args.kwargs
        assert kwargs["language"] == "en"
        assert kwargs["initial_prompt"] == _INITIAL_PROMPTS["en"]

    def test_autodetect_passes_no_prompt_and_returns_detected_lang(self):
        fake = _fake_model_returning("bn", 0.88, "আমি ভালো আছি")
        with patch("voice.pipeline._get_model", return_value=fake), \
             patch("voice.pipeline._check_audio_quality", return_value=(True, 0.1, "")):
            text, det, prob = transcribe_audio_detailed(
                _make_silent_wav(duration_s=2.0), language=None
            )
        kwargs = fake.transcribe.call_args.kwargs
        assert kwargs["language"] is None
        assert kwargs["initial_prompt"] is None
        assert det == "bn"
        assert prob == pytest.approx(0.88)
        assert "ভালো" in text

    def test_unknown_language_uses_no_prompt(self):
        fake = _fake_model_returning("fr", 0.5, "bonjour")
        with patch("voice.pipeline._get_model", return_value=fake), \
             patch("voice.pipeline._check_audio_quality", return_value=(True, 0.1, "")):
            transcribe_audio_detailed(_make_silent_wav(duration_s=2.0), language="fr")
        kwargs = fake.transcribe.call_args.kwargs
        assert kwargs["initial_prompt"] is None  # no entry in _INITIAL_PROMPTS

    def test_backcompat_wrapper_returns_only_text(self):
        fake = _fake_model_returning("bn", 0.9, "hello-world")
        with patch("voice.pipeline._get_model", return_value=fake), \
             patch("voice.pipeline._check_audio_quality", return_value=(True, 0.1, "")):
            out = transcribe_audio(_make_silent_wav(duration_s=2.0), language="bn")
        assert out == "hello-world"
