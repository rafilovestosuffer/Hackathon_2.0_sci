"""
whatsapp/telegram_client.py — Telegram Bot API HTTP wrapper.

Free, no verification, no limits. Used as primary dev channel and
production demo backup.

Env var required:
  TELEGRAM_BOT_TOKEN — from @BotFather

API docs: https://core.telegram.org/bots/api
"""

from __future__ import annotations

import logging
import os
from io import BytesIO
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

TIMEOUT_SEC = 60.0


def _make_client() -> "httpx.Client":
    """httpx client tuned for HF Spaces outbound (slow TLS, prefer IPv4)."""
    import socket as _sk
    # Force IPv4 (HF outbound sometimes fails on IPv6 dual-stack)
    transport = httpx.HTTPTransport(retries=2, local_address="0.0.0.0")
    return httpx.Client(
        timeout=httpx.Timeout(connect=30.0, read=60.0, write=30.0, pool=10.0),
        transport=transport,
        http2=False,
    )


def _token() -> str:
    t = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    if not t:
        raise RuntimeError("Missing env var: TELEGRAM_BOT_TOKEN")
    return t


def _base() -> str:
    return f"https://api.telegram.org/bot{_token()}"


def _file_base() -> str:
    return f"https://api.telegram.org/file/bot{_token()}"


# ── Outbound API ──────────────────────────────────────────────────────────────

def send_text(chat_id: int | str, body: str) -> dict:
    url = f"{_base()}/sendMessage"
    payload = {"chat_id": chat_id, "text": body[:4096]}
    with _make_client() as client:
        r = client.post(url, json=payload)
    r.raise_for_status()
    return r.json()


def send_document(
    chat_id: int | str, pdf_bytes: bytes, filename: str, caption: str = ""
) -> dict:
    url = f"{_base()}/sendDocument"
    files = {"document": (filename, BytesIO(pdf_bytes), "application/pdf")}
    data = {"chat_id": chat_id}
    if caption:
        data["caption"] = caption[:1024]
    with _make_client() as client:
        r = client.post(url, data=data, files=files)
    r.raise_for_status()
    return r.json()


def download_file(file_id: str) -> bytes:
    """Two-step: getFile → download from file path."""
    with _make_client() as client:
        r = client.get(f"{_base()}/getFile", params={"file_id": file_id})
        r.raise_for_status()
        file_path = r.json()["result"]["file_path"]
        r2 = client.get(f"{_file_base()}/{file_path}")
        r2.raise_for_status()
        return r2.content


# ── Webhook payload parsing ───────────────────────────────────────────────────

def parse_incoming(payload: dict) -> list[dict]:
    """
    Normalise Telegram update → same event shape as meta_client.parse_incoming.

    Each event: {
      from: str,           # str(chat_id) — Telegram uses ints, we stringify
      message_id: str,
      type: 'text'|'image'|'audio'|'unsupported',
      text: str | None,
      media_id: str | None,  # Telegram file_id
      mime_type: str | None,
    }
    """
    msg = payload.get("message") or payload.get("edited_message") or {}
    if not msg:
        return []

    chat_id = str((msg.get("chat") or {}).get("id", ""))
    message_id = str(msg.get("message_id", ""))
    ev: dict = {
        "from": chat_id,
        "message_id": message_id,
        "type": "unsupported",
        "text": None,
        "media_id": None,
        "mime_type": None,
    }

    if "text" in msg:
        ev["type"] = "text"
        ev["text"] = msg["text"]
    elif "photo" in msg:
        # photo is an array of sizes — pick the largest
        photos = msg["photo"]
        largest = max(photos, key=lambda p: p.get("file_size") or 0)
        ev["type"] = "image"
        ev["media_id"] = largest["file_id"]
        ev["mime_type"] = "image/jpeg"
    elif "voice" in msg:
        ev["type"] = "audio"
        ev["media_id"] = msg["voice"]["file_id"]
        ev["mime_type"] = msg["voice"].get("mime_type", "audio/ogg")
    elif "audio" in msg:
        ev["type"] = "audio"
        ev["media_id"] = msg["audio"]["file_id"]
        ev["mime_type"] = msg["audio"].get("mime_type", "audio/mpeg")
    elif "document" in msg:
        doc = msg["document"]
        mt = doc.get("mime_type", "")
        if mt.startswith("image/"):
            ev["type"] = "image"
        elif mt.startswith("audio/"):
            ev["type"] = "audio"
        ev["media_id"] = doc["file_id"]
        ev["mime_type"] = mt

    return [ev]
