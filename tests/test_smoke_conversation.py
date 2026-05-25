"""
End-to-end smoke test: live uvicorn server + simulated Telegram conversation
walks NEW → AWAITING_DISTRICT → AWAITING_IMAGE → AWAITING_VOICE → RESULT_SENT.

Voice transcription + PDF generation are mocked so the test stays fast.
This proves the HTTP layer + state machine + outbound dispatch all integrate.
"""

import os
import threading
import time
from unittest.mock import patch, MagicMock

import httpx
import pytest


# ── Env setup BEFORE any whatsapp imports ─────────────────────────────────────
os.environ["META_VERIFY_TOKEN"] = "vt"
os.environ["META_APP_SECRET"] = "sec"
os.environ["META_ACCESS_TOKEN"] = "tok"
os.environ["META_PHONE_NUMBER_ID"] = "1"
os.environ["TELEGRAM_BOT_TOKEN"] = "bt"

PORT = 18799


@pytest.fixture(scope="module")
def live_server():
    import uvicorn
    from webhook.server import app
    config = uvicorn.Config(app, host="127.0.0.1", port=PORT, log_level="warning")
    server = uvicorn.Server(config)
    t = threading.Thread(target=server.run, daemon=True)
    t.start()
    for _ in range(50):
        try:
            httpx.get(f"http://127.0.0.1:{PORT}/health", timeout=1)
            break
        except Exception:
            time.sleep(0.1)
    yield f"http://127.0.0.1:{PORT}"
    server.should_exit = True
    time.sleep(0.5)


def _send(base: str, body: dict) -> int:
    r = httpx.post(f"{base}/webhook/telegram", json=body, timeout=10)
    return r.status_code


def _tg(text=None, photo=False, voice=False, message_id=1, chat_id=12345):
    msg = {"message_id": message_id, "chat": {"id": chat_id}}
    if text is not None:
        msg["text"] = text
    elif photo:
        msg["photo"] = [{"file_id": "p1", "file_size": 50000}]
    elif voice:
        msg["voice"] = {"file_id": "v1", "mime_type": "audio/ogg"}
    return {"update_id": message_id, "message": msg}


def test_full_telegram_conversation(live_server):
    """Walk a complete user journey through the live server."""
    from whatsapp.state import store
    store._sessions.clear()

    sent_messages = []
    sent_documents = []

    def fake_send_text(chat_id, body):
        sent_messages.append((chat_id, body))
        return {"ok": True}

    def fake_send_document(chat_id, pdf_bytes, filename, caption=""):
        sent_documents.append((chat_id, filename, len(pdf_bytes), caption))
        return {"ok": True}

    def fake_download(file_id):
        if file_id == "p1":
            # tiny but non-blurry-enough PNG: just bytes; blur check uses cv2
            # if cv2 can't decode → returns -1.0 → router treats as OK
            return b"\x89PNG\r\n\x1a\n" + b"\x00" * 2048
        return b"OggS" + b"\x00" * 1024  # voice

    # Mock pipeline-heavy modules
    with patch("whatsapp.telegram_client.send_text", side_effect=fake_send_text), \
         patch("whatsapp.telegram_client.send_document", side_effect=fake_send_document), \
         patch("whatsapp.telegram_client.download_file", side_effect=fake_download), \
         patch("voice.pipeline.transcribe_audio",
               return_value="তিন সপ্তাহ ধরে চুলকানি"), \
         patch("voice.pipeline.extract_patient_history",
               return_value={"chief_complaint": "rash", "symptoms": ["itching"]}), \
         patch("severity.engine.compute_tier",
               return_value={"tier": 2, "urgency_label": "ROUTINE",
                             "action": "See doctor in 48h",
                             "facility": "UHC", "bengali_text": "৪৮ ঘণ্টায় যান"}), \
         patch("map.hospital_finder.find_nearest_hospitals",
               return_value=[{"name": "RMCH", "address": "Medical Rd",
                              "lat": 25.7, "lon": 89.2, "dist_km": 4.2, "phone": ""}]), \
         patch("pdf_gen.referral.generate_referral_pdf",
               return_value=b"%PDF-1.4 fake_pdf_bytes_here"):

        # Step 1: hello → expect welcome
        assert _send(live_server, _tg(text="hi", message_id=1)) == 200
        assert len(sent_messages) == 1
        assert "স্বাগতম" in sent_messages[-1][1]

        # Step 2: district → expect ask-image
        assert _send(live_server, _tg(text="rangpur", message_id=2)) == 200
        assert "ছবি" in sent_messages[-1][1]

        # Step 3: image → expect ask-voice
        assert _send(live_server, _tg(photo=True, message_id=3)) == 200
        assert "ভয়েস" in sent_messages[-1][1]

        # Step 4: voice → expect PROCESSING + triage + PDF + followup
        before_count = len(sent_messages)
        assert _send(live_server, _tg(voice=True, message_id=4)) == 200
        new_msgs = sent_messages[before_count:]
        assert any("পেয়েছি" in m[1] or "অপেক্ষা" in m[1] for m in new_msgs)
        assert any("ফলাফল" in m[1] for m in new_msgs)
        assert len(sent_documents) == 1
        assert sent_documents[0][2] > 0  # PDF has bytes

        # Step 5: RAG chat
        with patch("rag.retriever.load_index", return_value=True), \
             patch("rag.retriever.answer_question", return_value="Keep area dry"):
            assert _send(live_server, _tg(text="how long to heal", message_id=5)) == 200
            assert "Keep area dry" in sent_messages[-1][1]

        # Step 6: reset
        assert _send(live_server, _tg(text="নতুন", message_id=6)) == 200
        assert "শুরু থেকে" in sent_messages[-1][1]


def test_health_endpoint_responds(live_server):
    r = httpx.get(f"{live_server}/health", timeout=5)
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert "uptime_sec" in body
