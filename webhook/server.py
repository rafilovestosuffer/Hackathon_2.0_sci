"""
webhook/server.py — FastAPI app for WhatsApp + Telegram webhooks.

Run locally:
  uvicorn webhook.server:app --host 0.0.0.0 --port 7860

Endpoints:
  GET  /health                 → liveness + diagnostics JSON
  GET  /webhook/whatsapp       → Meta subscribe handshake
  POST /webhook/whatsapp       → Meta inbound messages
  POST /webhook/telegram       → Telegram inbound updates
"""

from __future__ import annotations

import logging
import os
import time
from typing import Any

# Load .env BEFORE importing whatsapp clients (they read env eagerly)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from fastapi import FastAPI, Header, HTTPException, Request, Response
from fastapi.responses import JSONResponse, PlainTextResponse

from whatsapp import meta_client, telegram_client, router
from whatsapp.state import store

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("webhook")

app = FastAPI(title="SkinAI Bangladesh — WhatsApp + Telegram Webhook")
_BOOT_TS = time.time()


# ── Outbound dispatch helpers ────────────────────────────────────────────────

def _send_actions_meta(actions: list[router.Action]) -> None:
    for act in actions:
        try:
            if isinstance(act, router.TextOut):
                meta_client.send_text(act.to, act.body)
            elif isinstance(act, router.PdfOut):
                meta_client.send_document(act.to, act.pdf_bytes, act.filename, act.caption)
        except Exception as e:
            logger.error("Meta send failed: %s", e)


def _send_actions_telegram(actions: list[router.Action]) -> None:
    for act in actions:
        try:
            if isinstance(act, router.TextOut):
                telegram_client.send_text(act.to, act.body)
            elif isinstance(act, router.PdfOut):
                telegram_client.send_document(act.to, act.pdf_bytes, act.filename, act.caption)
        except Exception as e:
            logger.error("Telegram send failed: %s", e)


# ── Health ───────────────────────────────────────────────────────────────────

@app.get("/health")
def health() -> JSONResponse:
    return JSONResponse({
        "status": "ok",
        "uptime_sec": int(time.time() - _BOOT_TS),
        "active_sessions": store.active_count(),
        "meta_configured": bool(os.environ.get("META_ACCESS_TOKEN")),
        "telegram_configured": bool(os.environ.get("TELEGRAM_BOT_TOKEN")),
        "gemini_configured": bool(os.environ.get("GEMINI_API_KEY")),
    })


@app.get("/debug/telegram-getme")
def debug_telegram_getme() -> JSONResponse:
    """Confirm container can reach api.telegram.org with the configured token."""
    import httpx
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    if not token:
        return JSONResponse({"ok": False, "error": "no token"}, status_code=500)
    try:
        with httpx.Client(timeout=10.0) as c:
            r = c.get(f"https://api.telegram.org/bot{token}/getMe")
        return JSONResponse({"status": r.status_code, "body": r.json()})
    except Exception as e:
        return JSONResponse({"ok": False, "error": repr(e), "type": type(e).__name__},
                            status_code=500)


@app.get("/debug/connectivity")
def debug_connectivity() -> JSONResponse:
    """Probe outbound to several hosts to localise the network restriction."""
    import httpx, socket
    targets = [
        ("api.telegram.org", "https://api.telegram.org/"),
        ("google", "https://www.google.com/"),
        ("httpbin", "https://httpbin.org/get"),
        ("public-dns", "https://1.1.1.1/"),
    ]
    out = {}
    for label, url in targets:
        try:
            host = url.split("/")[2]
            ip = socket.gethostbyname(host)
            with httpx.Client(timeout=httpx.Timeout(connect=20.0, read=20.0, write=20.0, pool=5.0)) as c:
                r = c.get(url)
            out[label] = {"ip": ip, "status": r.status_code}
        except Exception as e:
            out[label] = {"error": repr(e)[:200], "type": type(e).__name__}
    return JSONResponse(out)


@app.get("/debug/send")
def debug_send(chat_id: str = "", body: str = "hello from skinai") -> JSONResponse:
    """Try a direct send_text. Returns the actual exception if it fails."""
    if not chat_id:
        return JSONResponse({"error": "pass ?chat_id=..."}, status_code=400)
    try:
        from whatsapp import telegram_client
        result = telegram_client.send_text(chat_id, body)
        return JSONResponse({"ok": True, "result": result})
    except Exception as e:
        return JSONResponse({"ok": False, "error": repr(e),
                             "type": type(e).__name__}, status_code=500)


@app.get("/")
def root() -> JSONResponse:
    return JSONResponse({
        "service": "SkinAI Bangladesh WhatsApp + Telegram bot",
        "health": "/health",
        "endpoints": [
            "GET  /webhook/whatsapp",
            "POST /webhook/whatsapp",
            "POST /webhook/telegram",
        ],
    })


# ── WhatsApp (Meta) ──────────────────────────────────────────────────────────

@app.get("/webhook/whatsapp")
def whatsapp_verify(
    hub_mode: str = "",
    hub_verify_token: str = "",
    hub_challenge: str = "",
    request: Request = None,
):
    """Meta subscription handshake.
    Meta sends ?hub.mode=subscribe&hub.verify_token=...&hub.challenge=...
    FastAPI converts dots to underscores when using Query but to be safe
    we read from request.query_params directly.
    """
    if request is not None:
        qp = request.query_params
        hub_mode = qp.get("hub.mode", hub_mode)
        hub_verify_token = qp.get("hub.verify_token", hub_verify_token)
        hub_challenge = qp.get("hub.challenge", hub_challenge)

    challenge = meta_client.verify_subscribe_challenge(
        hub_mode, hub_verify_token, hub_challenge
    )
    if challenge is None:
        raise HTTPException(status_code=403, detail="verify_token mismatch")
    return PlainTextResponse(challenge)


@app.post("/webhook/whatsapp")
async def whatsapp_receive(
    request: Request,
    x_hub_signature_256: str = Header(default=""),
):
    raw = await request.body()
    if not meta_client.verify_webhook_signature(raw, x_hub_signature_256):
        raise HTTPException(status_code=403, detail="bad signature")

    payload = await request.json()
    events = meta_client.parse_incoming(payload)
    for ev in events:
        try:
            actions = router.handle_event(ev, media_downloader=meta_client.download_media)
            _send_actions_meta(actions)
        except Exception as e:
            logger.exception("Meta event handling failed: %s", e)
    return Response(status_code=200)


# ── Telegram ─────────────────────────────────────────────────────────────────

@app.post("/webhook/telegram")
async def telegram_receive(request: Request):
    payload = await request.json()
    events = telegram_client.parse_incoming(payload)
    for ev in events:
        try:
            actions = router.handle_event(ev, media_downloader=telegram_client.download_file)
            _send_actions_telegram(actions)
        except Exception as e:
            logger.exception("Telegram event handling failed: %s", e)
    return Response(status_code=200)
