"""Tests for whatsapp/meta_client.py and whatsapp/telegram_client.py."""

import hashlib
import hmac
import json
import os
from unittest.mock import patch, MagicMock

import pytest


# --- Meta client tests ---

class TestMetaSignatureVerification:
    def setup_method(self):
        os.environ["META_APP_SECRET"] = "test_secret"

    def teardown_method(self):
        os.environ.pop("META_APP_SECRET", None)

    def test_valid_signature_accepted(self):
        from whatsapp.meta_client import verify_webhook_signature
        body = b'{"foo":"bar"}'
        sig = "sha256=" + hmac.new(b"test_secret", body, hashlib.sha256).hexdigest()
        assert verify_webhook_signature(body, sig) is True

    def test_invalid_signature_rejected(self):
        from whatsapp.meta_client import verify_webhook_signature
        assert verify_webhook_signature(b'{}', "sha256=deadbeef") is False

    def test_missing_header_rejected(self):
        from whatsapp.meta_client import verify_webhook_signature
        assert verify_webhook_signature(b'{}', "") is False

    def test_no_sha256_prefix_rejected(self):
        from whatsapp.meta_client import verify_webhook_signature
        assert verify_webhook_signature(b'{}', "deadbeef") is False


class TestMetaSubscribeChallenge:
    def setup_method(self):
        os.environ["META_VERIFY_TOKEN"] = "my_token"

    def teardown_method(self):
        os.environ.pop("META_VERIFY_TOKEN", None)

    def test_correct_token_returns_challenge(self):
        from whatsapp.meta_client import verify_subscribe_challenge
        assert verify_subscribe_challenge("subscribe", "my_token", "abc123") == "abc123"

    def test_wrong_token_returns_none(self):
        from whatsapp.meta_client import verify_subscribe_challenge
        assert verify_subscribe_challenge("subscribe", "wrong", "abc") is None

    def test_wrong_mode_returns_none(self):
        from whatsapp.meta_client import verify_subscribe_challenge
        assert verify_subscribe_challenge("unsubscribe", "my_token", "abc") is None


class TestMetaParseIncoming:
    def test_parse_text_message(self):
        from whatsapp.meta_client import parse_incoming
        payload = {
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{
                            "from": "8801711111111",
                            "id": "wamid.ABC",
                            "type": "text",
                            "text": {"body": "hello"},
                        }]
                    }
                }]
            }]
        }
        events = parse_incoming(payload)
        assert len(events) == 1
        assert events[0]["from"] == "8801711111111"
        assert events[0]["type"] == "text"
        assert events[0]["text"] == "hello"
        assert events[0]["message_id"] == "wamid.ABC"

    def test_parse_image_message(self):
        from whatsapp.meta_client import parse_incoming
        payload = {
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{
                            "from": "8801711111111",
                            "id": "wamid.IMG",
                            "type": "image",
                            "image": {"id": "media123", "mime_type": "image/jpeg"},
                        }]
                    }
                }]
            }]
        }
        events = parse_incoming(payload)
        assert events[0]["type"] == "image"
        assert events[0]["media_id"] == "media123"
        assert events[0]["mime_type"] == "image/jpeg"

    def test_parse_voice_message(self):
        from whatsapp.meta_client import parse_incoming
        payload = {
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{
                            "from": "880", "id": "v1", "type": "audio",
                            "audio": {"id": "amid", "mime_type": "audio/ogg"},
                        }]
                    }
                }]
            }]
        }
        events = parse_incoming(payload)
        assert events[0]["type"] == "audio"
        assert events[0]["media_id"] == "amid"

    def test_parse_empty_payload(self):
        from whatsapp.meta_client import parse_incoming
        assert parse_incoming({}) == []
        assert parse_incoming({"entry": []}) == []


class TestMetaSendText:
    def setup_method(self):
        os.environ["META_PHONE_NUMBER_ID"] = "123"
        os.environ["META_ACCESS_TOKEN"] = "tok"

    def teardown_method(self):
        os.environ.pop("META_PHONE_NUMBER_ID", None)
        os.environ.pop("META_ACCESS_TOKEN", None)

    def test_send_text_posts_correct_payload(self):
        from whatsapp import meta_client
        mock_response = MagicMock()
        mock_response.json.return_value = {"messages": [{"id": "abc"}]}
        mock_response.raise_for_status = MagicMock()

        with patch("whatsapp.meta_client.httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.__enter__.return_value = mock_client
            mock_client.post.return_value = mock_response
            mock_client_cls.return_value = mock_client

            result = meta_client.send_text("8801711111111", "hello")

            assert result == {"messages": [{"id": "abc"}]}
            call = mock_client.post.call_args
            payload = call.kwargs["json"]
            assert payload["to"] == "8801711111111"
            assert payload["text"]["body"] == "hello"
            assert payload["messaging_product"] == "whatsapp"

    def test_send_text_truncates_long_messages(self):
        from whatsapp import meta_client
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status = MagicMock()

        with patch("whatsapp.meta_client.httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.__enter__.return_value = mock_client
            mock_client.post.return_value = mock_response
            mock_client_cls.return_value = mock_client

            meta_client.send_text("123", "x" * 5000)
            payload = mock_client.post.call_args.kwargs["json"]
            assert len(payload["text"]["body"]) == 4096


# --- Telegram client tests ---

class TestTelegramParseIncoming:
    def test_parse_text(self):
        from whatsapp.telegram_client import parse_incoming
        payload = {
            "message": {
                "message_id": 42,
                "chat": {"id": 999},
                "text": "hi",
            }
        }
        events = parse_incoming(payload)
        assert len(events) == 1
        assert events[0]["from"] == "999"
        assert events[0]["type"] == "text"
        assert events[0]["text"] == "hi"
        assert events[0]["message_id"] == "42"

    def test_parse_photo_picks_largest(self):
        from whatsapp.telegram_client import parse_incoming
        payload = {
            "message": {
                "message_id": 1,
                "chat": {"id": 1},
                "photo": [
                    {"file_id": "small", "file_size": 1000},
                    {"file_id": "big",   "file_size": 50000},
                    {"file_id": "med",   "file_size": 10000},
                ],
            }
        }
        events = parse_incoming(payload)
        assert events[0]["type"] == "image"
        assert events[0]["media_id"] == "big"
        assert events[0]["mime_type"] == "image/jpeg"

    def test_parse_voice(self):
        from whatsapp.telegram_client import parse_incoming
        payload = {
            "message": {
                "message_id": 1, "chat": {"id": 1},
                "voice": {"file_id": "v1", "mime_type": "audio/ogg"},
            }
        }
        events = parse_incoming(payload)
        assert events[0]["type"] == "audio"
        assert events[0]["media_id"] == "v1"

    def test_parse_audio(self):
        from whatsapp.telegram_client import parse_incoming
        payload = {
            "message": {
                "message_id": 1, "chat": {"id": 1},
                "audio": {"file_id": "a1", "mime_type": "audio/mpeg"},
            }
        }
        events = parse_incoming(payload)
        assert events[0]["type"] == "audio"

    def test_parse_image_document(self):
        from whatsapp.telegram_client import parse_incoming
        payload = {
            "message": {
                "message_id": 1, "chat": {"id": 1},
                "document": {"file_id": "d1", "mime_type": "image/png"},
            }
        }
        events = parse_incoming(payload)
        assert events[0]["type"] == "image"

    def test_parse_empty(self):
        from whatsapp.telegram_client import parse_incoming
        assert parse_incoming({}) == []

    def test_parse_unsupported(self):
        from whatsapp.telegram_client import parse_incoming
        payload = {
            "message": {
                "message_id": 1, "chat": {"id": 1},
                "sticker": {"file_id": "s1"},
            }
        }
        events = parse_incoming(payload)
        assert events[0]["type"] == "unsupported"


class TestTelegramSendText:
    def setup_method(self):
        os.environ["TELEGRAM_BOT_TOKEN"] = "test_token"

    def teardown_method(self):
        os.environ.pop("TELEGRAM_BOT_TOKEN", None)

    def test_send_text(self):
        from whatsapp import telegram_client
        mock_response = MagicMock()
        mock_response.json.return_value = {"ok": True}
        mock_response.raise_for_status = MagicMock()

        with patch("whatsapp.telegram_client.httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.__enter__.return_value = mock_client
            mock_client.post.return_value = mock_response
            mock_client_cls.return_value = mock_client

            telegram_client.send_text(999, "hi")
            call = mock_client.post.call_args
            assert "sendMessage" in call.args[0]
            assert call.kwargs["json"]["chat_id"] == 999
            assert call.kwargs["json"]["text"] == "hi"
