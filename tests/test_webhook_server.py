"""HTTP-level tests for webhook/server.py via FastAPI TestClient."""

import hashlib
import hmac
import json
import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

# Set Meta env BEFORE importing server (modules read env eagerly via _env())
os.environ.setdefault("META_VERIFY_TOKEN", "test_verify")
os.environ.setdefault("META_APP_SECRET", "test_app_secret")
os.environ.setdefault("META_ACCESS_TOKEN", "test_access")
os.environ.setdefault("META_PHONE_NUMBER_ID", "999")
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "test_bot")

from webhook.server import app  # noqa: E402
from whatsapp.state import store  # noqa: E402

client = TestClient(app)


@pytest.fixture(autouse=True)
def fresh_store(monkeypatch):
    # Re-assert env vars before every test (other test files pop them on teardown)
    monkeypatch.setenv("META_VERIFY_TOKEN", "test_verify")
    monkeypatch.setenv("META_APP_SECRET", "test_app_secret")
    monkeypatch.setenv("META_ACCESS_TOKEN", "test_access")
    monkeypatch.setenv("META_PHONE_NUMBER_ID", "999")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_bot")
    store._sessions.clear()
    yield
    store._sessions.clear()


def _sign(body: bytes) -> str:
    mac = hmac.new(b"test_app_secret", body, hashlib.sha256).hexdigest()
    return f"sha256={mac}"


# --- Health ---

def test_health_returns_200_with_diagnostics():
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "uptime_sec" in data
    assert "active_sessions" in data
    assert data["meta_configured"] is True
    assert data["telegram_configured"] is True


def test_root_lists_endpoints():
    r = client.get("/")
    assert r.status_code == 200
    assert "/webhook/whatsapp" in str(r.json())


# --- Meta subscribe handshake ---

class TestMetaSubscribe:
    def test_correct_token_echoes_challenge(self):
        r = client.get(
            "/webhook/whatsapp",
            params={
                "hub.mode": "subscribe",
                "hub.verify_token": "test_verify",
                "hub.challenge": "ABC123",
            },
        )
        assert r.status_code == 200
        assert r.text == "ABC123"

    def test_wrong_token_403(self):
        r = client.get(
            "/webhook/whatsapp",
            params={
                "hub.mode": "subscribe",
                "hub.verify_token": "WRONG",
                "hub.challenge": "X",
            },
        )
        assert r.status_code == 403


# --- Meta inbound ---

class TestMetaInbound:
    def test_bad_signature_403(self):
        body = json.dumps({"entry": []}).encode()
        r = client.post(
            "/webhook/whatsapp",
            content=body,
            headers={"X-Hub-Signature-256": "sha256=deadbeef",
                     "Content-Type": "application/json"},
        )
        assert r.status_code == 403

    def test_valid_text_triggers_send_text(self):
        body_obj = {
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{
                            "from": "8801711111111", "id": "wamid.M1",
                            "type": "text", "text": {"body": "hi"},
                        }]
                    }
                }]
            }]
        }
        body = json.dumps(body_obj).encode()
        with patch("webhook.server.meta_client.send_text") as mock_send:
            r = client.post(
                "/webhook/whatsapp",
                content=body,
                headers={"X-Hub-Signature-256": _sign(body),
                         "Content-Type": "application/json"},
            )
            assert r.status_code == 200
            mock_send.assert_called_once()
            args, _ = mock_send.call_args
            assert args[0] == "8801711111111"
            assert "স্বাগতম" in args[1]


# --- Telegram inbound ---

class TestTelegramInbound:
    def test_text_triggers_send(self):
        body = {
            "update_id": 1,
            "message": {
                "message_id": 100,
                "chat": {"id": 12345},
                "text": "hello",
            },
        }
        with patch("webhook.server.telegram_client.send_text") as mock_send:
            r = client.post("/webhook/telegram", json=body)
            assert r.status_code == 200
            mock_send.assert_called_once()
            args, _ = mock_send.call_args
            assert args[0] == "12345"

    def test_empty_payload_returns_200(self):
        r = client.post("/webhook/telegram", json={})
        assert r.status_code == 200

    def test_unsupported_sticker_still_200(self):
        body = {
            "update_id": 2,
            "message": {
                "message_id": 1, "chat": {"id": 1},
                "sticker": {"file_id": "s1"},
            },
        }
        with patch("webhook.server.telegram_client.send_text") as mock_send:
            r = client.post("/webhook/telegram", json=body)
            assert r.status_code == 200
            # Sticker → unsupported → router returns HELP fallback
            mock_send.assert_called_once()
