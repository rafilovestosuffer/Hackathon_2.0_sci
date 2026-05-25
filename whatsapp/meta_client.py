"""
whatsapp/meta_client.py — Meta WhatsApp Cloud API HTTP wrapper.

Env vars required:
  META_PHONE_NUMBER_ID  — from Meta dashboard (e.g. 123456789012345)
  META_ACCESS_TOKEN     — permanent system user token
  META_APP_SECRET       — for X-Hub-Signature-256 webhook verification
  META_VERIFY_TOKEN     — chosen by us, registered with Meta during webhook setup

API docs: https://developers.facebook.com/docs/whatsapp/cloud-api
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import os
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

GRAPH_API_BASE = "https://graph.facebook.com/v21.0"
TIMEOUT_SEC = 30.0


def _env(name: str) -> str:
    val = os.environ.get(name, "")
    if not val:
        raise RuntimeError(f"Missing env var: {name}")
    return val


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {_env('META_ACCESS_TOKEN')}",
        "Content-Type": "application/json",
    }


def verify_webhook_signature(raw_body: bytes, signature_header: str) -> bool:
    """
    Verify Meta's X-Hub-Signature-256 header.
    Header format: 'sha256=<hex>'
    """
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    expected = signature_header[len("sha256="):]
    app_secret = os.environ.get("META_APP_SECRET", "")
    if not app_secret:
        logger.warning("META_APP_SECRET not set — signature check skipped (DEV ONLY).")
        return True
    mac = hmac.new(app_secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(mac, expected)


def verify_subscribe_challenge(
    mode: str, token: str, challenge: str
) -> Optional[str]:
    """
    Handle Meta's GET subscribe handshake. Returns challenge if valid.
    """
    expected = os.environ.get("META_VERIFY_TOKEN", "")
    if mode == "subscribe" and token and token == expected:
        return challenge
    return None


# ── Outbound API ──────────────────────────────────────────────────────────────

def send_text(to: str, body: str) -> dict:
    """Send a plain text message. `to` = E.164 phone number without +."""
    url = f"{GRAPH_API_BASE}/{_env('META_PHONE_NUMBER_ID')}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {"body": body[:4096]},  # WhatsApp text cap
    }
    with httpx.Client(timeout=TIMEOUT_SEC) as client:
        r = client.post(url, headers=_headers(), json=payload)
    r.raise_for_status()
    return r.json()


def send_document(to: str, pdf_bytes: bytes, filename: str, caption: str = "") -> dict:
    """Upload PDF via Meta media API, then send as document message."""
    media_id = _upload_media(pdf_bytes, mime_type="application/pdf", filename=filename)
    url = f"{GRAPH_API_BASE}/{_env('META_PHONE_NUMBER_ID')}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "document",
        "document": {
            "id": media_id,
            "filename": filename,
        },
    }
    if caption:
        payload["document"]["caption"] = caption[:1024]
    with httpx.Client(timeout=TIMEOUT_SEC) as client:
        r = client.post(url, headers=_headers(), json=payload)
    r.raise_for_status()
    return r.json()


def _upload_media(data: bytes, mime_type: str, filename: str) -> str:
    """Upload a file to Meta and return media_id."""
    url = f"{GRAPH_API_BASE}/{_env('META_PHONE_NUMBER_ID')}/media"
    files = {
        "file": (filename, data, mime_type),
        "messaging_product": (None, "whatsapp"),
        "type": (None, mime_type),
    }
    headers = {"Authorization": f"Bearer {_env('META_ACCESS_TOKEN')}"}
    with httpx.Client(timeout=TIMEOUT_SEC) as client:
        r = client.post(url, headers=headers, files=files)
    r.raise_for_status()
    return r.json()["id"]


def download_media(media_id: str) -> bytes:
    """Two-step: GET media URL → GET file bytes."""
    url = f"{GRAPH_API_BASE}/{media_id}"
    with httpx.Client(timeout=TIMEOUT_SEC) as client:
        r = client.get(url, headers=_headers())
        r.raise_for_status()
        media_url = r.json()["url"]
        # Bearer token required here too
        r2 = client.get(media_url, headers={"Authorization": f"Bearer {_env('META_ACCESS_TOKEN')}"})
        r2.raise_for_status()
        return r2.content


# ── Webhook payload parsing ───────────────────────────────────────────────────

def parse_incoming(payload: dict) -> list[dict]:
    """
    Flatten Meta's nested webhook payload into a list of normalised events.

    Each event: {
      from: str,           # sender phone (E.164 no +)
      message_id: str,
      type: 'text'|'image'|'audio'|'document'|'unsupported',
      text: str | None,
      media_id: str | None,
      mime_type: str | None,
    }
    """
    events: list[dict] = []
    for entry in payload.get("entry", []) or []:
        for change in entry.get("changes", []) or []:
            value = change.get("value", {}) or {}
            for msg in value.get("messages", []) or []:
                ev = {
                    "from": msg.get("from", ""),
                    "message_id": msg.get("id", ""),
                    "type": msg.get("type", "unsupported"),
                    "text": None,
                    "media_id": None,
                    "mime_type": None,
                }
                t = ev["type"]
                if t == "text":
                    ev["text"] = (msg.get("text") or {}).get("body", "")
                elif t in ("image", "audio", "voice", "document"):
                    media = msg.get(t) or {}
                    ev["media_id"] = media.get("id")
                    ev["mime_type"] = media.get("mime_type")
                events.append(ev)
    return events
