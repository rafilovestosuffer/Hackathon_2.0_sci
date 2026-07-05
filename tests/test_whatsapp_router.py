"""End-to-end conversation flow tests for whatsapp/router.py.

Heavy modules (voice/severity/pdf/hospital/rag) are mocked so these tests
run in <1s without loading torch or whisper.
"""

import sys
import types
from unittest.mock import MagicMock, patch

import pytest

from whatsapp import router
from whatsapp.router import handle_event, TextOut, PdfOut
from whatsapp.state import State, store


# --- Fixtures ---

USER = "u_test"


@pytest.fixture(autouse=True)
def fresh_store():
    """Reset the global session store between tests."""
    store._sessions.clear()
    yield
    store._sessions.clear()


@pytest.fixture
def mock_media_dl():
    return MagicMock(return_value=b"\x89PNG\r\n\x1a\n" + b"X" * 1024)


@pytest.fixture(autouse=True)
def mock_pipeline_modules():
    """Mock the heavy modules used by router so tests stay fast."""
    # severity.engine
    severity_mod = types.ModuleType("severity")
    engine_mod = types.ModuleType("severity.engine")
    engine_mod.compute_tier = MagicMock(return_value={
        "tier": 2,
        "urgency_label": "ROUTINE",
        "action": "Visit Upazila Health Complex within 48 hours",
        "facility": "Upazila Health Complex",
        "bengali_text": "৪৮ ঘণ্টার মধ্যে যান",
    })
    severity_mod.engine = engine_mod

    # pdf_gen.referral
    pdf_pkg = types.ModuleType("pdf_gen")
    pdf_mod = types.ModuleType("pdf_gen.referral")
    pdf_mod.generate_referral_pdf = MagicMock(return_value=b"%PDF-1.4 fake")
    pdf_pkg.referral = pdf_mod

    # map.hospital_finder — keep real get_district_coords, mock find_nearest_hospitals
    from map import hospital_finder as real_hf
    hf_mock = MagicMock()
    hf_mock.get_district_coords = real_hf.get_district_coords
    hf_mock.DISTRICT_COORDS = real_hf.DISTRICT_COORDS
    hf_mock.find_nearest_hospitals = MagicMock(return_value=[
        {"name": "Rangpur Medical College Hospital", "address": "Medical Rd",
         "lat": 25.7, "lon": 89.2, "dist_km": 4.2, "phone": ""},
    ])

    # voice.pipeline
    voice_pkg = types.ModuleType("voice")
    voice_mod = types.ModuleType("voice.pipeline")
    voice_mod.transcribe_audio = MagicMock(return_value="রোগী বলছেন তিন সপ্তাহ ধরে চুলকানি")
    voice_mod.extract_patient_history = MagicMock(return_value={
        "patient_name": "Test User",
        "chief_complaint": "rash",
        "symptoms": ["itching"],
        "duration": "3 weeks",
    })
    voice_pkg.pipeline = voice_mod

    # rag.retriever
    rag_pkg = types.ModuleType("rag")
    rag_mod = types.ModuleType("rag.retriever")
    rag_mod.load_index = MagicMock(return_value=True)
    rag_mod.answer_question = MagicMock(return_value="Keep the area dry and clean.")
    rag_pkg.retriever = rag_mod

    # model.disease_labels — keep real
    from model import disease_labels as real_dl

    overrides = {
        "severity": severity_mod, "severity.engine": engine_mod,
        "pdf_gen": pdf_pkg, "pdf_gen.referral": pdf_mod,
        "voice": voice_pkg, "voice.pipeline": voice_mod,
        "rag": rag_pkg, "rag.retriever": rag_mod,
    }
    # patch map.hospital_finder.find_nearest_hospitals directly (don't replace module)
    with patch("map.hospital_finder.find_nearest_hospitals",
               hf_mock.find_nearest_hospitals):
        with patch.dict(sys.modules, overrides):
            yield {
                "compute_tier": engine_mod.compute_tier,
                "generate_pdf": pdf_mod.generate_referral_pdf,
                "find_hospitals": hf_mock.find_nearest_hospitals,
                "transcribe": voice_mod.transcribe_audio,
                "extract_history": voice_mod.extract_patient_history,
                "rag_answer": rag_mod.answer_question,
            }


# --- Helper: build canonical events ---

def text_event(body: str, mid: str = "m_auto") -> dict:
    return {"from": USER, "message_id": mid, "type": "text", "text": body,
            "media_id": None, "mime_type": None}

def image_event(mid: str = "m_img") -> dict:
    return {"from": USER, "message_id": mid, "type": "image",
            "text": None, "media_id": "media_abc", "mime_type": "image/jpeg"}

def audio_event(mid: str = "m_aud") -> dict:
    return {"from": USER, "message_id": mid, "type": "audio",
            "text": None, "media_id": "media_xyz", "mime_type": "audio/ogg"}


# --- State transition tests ---

class TestNewUserFlow:
    def test_first_message_sends_welcome(self, mock_media_dl):
        out = handle_event(text_event("hi", "m1"), mock_media_dl)
        assert len(out) == 1
        assert isinstance(out[0], TextOut)
        assert "স্বাগতম" in out[0].body
        assert store.get_or_create(USER).state == State.AWAITING_DISTRICT

    def test_invalid_district_keeps_state(self, mock_media_dl):
        handle_event(text_event("hi", "m1"), mock_media_dl)
        out = handle_event(text_event("xyzland", "m2"), mock_media_dl)
        assert "চিনতে পারিনি" in out[0].body or "not recognised" in out[0].body
        assert store.get_or_create(USER).state == State.AWAITING_DISTRICT

    def test_valid_english_district_advances(self, mock_media_dl):
        handle_event(text_event("hi", "m1"), mock_media_dl)
        out = handle_event(text_event("rangpur", "m2"), mock_media_dl)
        assert "ছবি" in out[0].body
        sess = store.get_or_create(USER)
        assert sess.state == State.AWAITING_IMAGE
        assert sess.district == "rangpur"
        assert sess.district_coords is not None

    def test_valid_bengali_district_advances(self, mock_media_dl):
        handle_event(text_event("hi", "m1"), mock_media_dl)
        out = handle_event(text_event("রংপুর", "m2"), mock_media_dl)
        assert store.get_or_create(USER).state == State.AWAITING_IMAGE


class TestImageStage:
    def _to_image_stage(self, dl):
        handle_event(text_event("hi", "m1"), dl)
        handle_event(text_event("rangpur", "m2"), dl)

    def test_image_advances_to_voice(self, mock_media_dl):
        self._to_image_stage(mock_media_dl)
        out = handle_event(image_event("m3"), mock_media_dl)
        assert "ভয়েস" in out[0].body
        assert store.get_or_create(USER).state == State.AWAITING_VOICE
        assert store.get_or_create(USER).image_bytes is not None

    def test_text_at_image_stage_reasks(self, mock_media_dl):
        self._to_image_stage(mock_media_dl)
        out = handle_event(text_event("hello", "m3"), mock_media_dl)
        assert "ছবি" in out[0].body
        assert store.get_or_create(USER).state == State.AWAITING_IMAGE


class TestVoiceAndPipeline:
    def _to_voice_stage(self, dl):
        handle_event(text_event("hi", "m1"), dl)
        handle_event(text_event("rangpur", "m2"), dl)
        handle_event(image_event("m3"), dl)

    def test_skip_triggers_pipeline(self, mock_media_dl, mock_pipeline_modules):
        self._to_voice_stage(mock_media_dl)
        out = handle_event(text_event("skip", "m4"), mock_media_dl)
        # Expect: triage text + PDF + chat-followup prompt
        types_seen = [type(a).__name__ for a in out]
        assert "TextOut" in types_seen
        assert "PdfOut" in types_seen
        assert store.get_or_create(USER).state == State.RAG_CHAT
        mock_pipeline_modules["compute_tier"].assert_called_once()
        mock_pipeline_modules["generate_pdf"].assert_called_once()

    def test_voice_triggers_transcribe_then_pipeline(self, mock_media_dl, mock_pipeline_modules):
        self._to_voice_stage(mock_media_dl)
        out = handle_event(audio_event("m4"), mock_media_dl)
        types_seen = [type(a).__name__ for a in out]
        # PROCESSING + triage + PDF + followup
        assert types_seen.count("TextOut") >= 2
        assert "PdfOut" in types_seen
        mock_pipeline_modules["transcribe"].assert_called_once()
        mock_pipeline_modules["extract_history"].assert_called_once()
        mock_pipeline_modules["compute_tier"].assert_called_once()

    def test_pdf_failure_still_sends_triage_text(self, mock_media_dl, mock_pipeline_modules):
        self._to_voice_stage(mock_media_dl)
        mock_pipeline_modules["generate_pdf"].return_value = b""  # PDF fails
        out = handle_event(text_event("skip", "m4"), mock_media_dl)
        # No PdfOut emitted, but triage text + followup still go out
        assert all(not isinstance(a, PdfOut) for a in out)
        assert any(isinstance(a, TextOut) and "ফলাফল" in a.body for a in out)


class TestRagChatStage:
    def _to_rag(self, dl, mods):
        handle_event(text_event("hi", "m1"), dl)
        handle_event(text_event("rangpur", "m2"), dl)
        handle_event(image_event("m3"), dl)
        handle_event(text_event("skip", "m4"), dl)

    def test_text_after_result_goes_to_rag(self, mock_media_dl, mock_pipeline_modules):
        self._to_rag(mock_media_dl, mock_pipeline_modules)
        out = handle_event(text_event("How long to heal?", "m5"), mock_media_dl)
        assert isinstance(out[0], TextOut)
        assert "Keep the area dry" in out[0].body
        mock_pipeline_modules["rag_answer"].assert_called_once()


# --- Global commands ---

class TestGlobalCommands:
    def test_reset_command_restarts(self, mock_media_dl):
        handle_event(text_event("hi", "m1"), mock_media_dl)
        handle_event(text_event("rangpur", "m2"), mock_media_dl)
        out = handle_event(text_event("নতুন", "m3"), mock_media_dl)
        assert "শুরু থেকে" in out[0].body
        assert store.get_or_create(USER).state == State.NEW

    def test_help_command_returns_help(self, mock_media_dl):
        handle_event(text_event("hi", "m1"), mock_media_dl)
        out = handle_event(text_event("help", "m2"), mock_media_dl)
        assert "সাহায্য" in out[0].body

    def test_help_command_does_not_advance_state(self, mock_media_dl):
        handle_event(text_event("hi", "m1"), mock_media_dl)
        s_before = store.get_or_create(USER).state
        handle_event(text_event("?", "m2"), mock_media_dl)
        assert store.get_or_create(USER).state == s_before


# --- Idempotency + rate limit ---

class TestIdempotency:
    def test_duplicate_message_id_dropped(self, mock_media_dl):
        out1 = handle_event(text_event("hi", "dup"), mock_media_dl)
        out2 = handle_event(text_event("hi", "dup"), mock_media_dl)
        assert len(out1) == 1
        assert len(out2) == 0  # deduped


class TestRateLimit:
    def test_blocks_when_exceeded(self, mock_media_dl):
        from whatsapp.state import RATE_LIMIT_MAX_MSGS
        for i in range(RATE_LIMIT_MAX_MSGS):
            handle_event(text_event(f"hi{i}", f"m{i}"), mock_media_dl)
        out = handle_event(text_event("again", "m_over"), mock_media_dl)
        assert "অপেক্ষা করুন" in out[0].body or "wait" in out[0].body.lower()
