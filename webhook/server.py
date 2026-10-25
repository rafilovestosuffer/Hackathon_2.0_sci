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
from collections import defaultdict, deque
from typing import Any

# Load .env BEFORE importing whatsapp clients (they read env eagerly)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from fastapi import FastAPI, File, Form, Header, HTTPException, Request, Response, UploadFile
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


@app.on_event("startup")
def _warm_model() -> None:
    """Start loading BD-SkinNet in the background so the first bot photo isn't slow."""
    if os.environ.get("SKINAI_NO_WARMUP"):
        return
    from model import service as model_service
    model_service.warm_up_async()


# --- Outbound dispatch helpers ---

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


# --- Health ---

@app.get("/health")
def health() -> JSONResponse:
    return JSONResponse({
        "status": "ok",
        "uptime_sec": int(time.time() - _BOOT_TS),
        "active_sessions": store.active_count(),
        "meta_configured": bool(os.environ.get("META_ACCESS_TOKEN")),
        "telegram_configured": bool(os.environ.get("TELEGRAM_BOT_TOKEN")),
        "gemini_configured": bool(os.environ.get("GEMINI_API_KEY")),
        "model_loaded": _model_loaded(),
    })


def _model_loaded() -> bool:
    from model import service as model_service
    return model_service._model is not None


@app.get("/debug/telegram-getme")
def debug_telegram_getme() -> JSONResponse:
    """Confirm container can reach api.telegram.org with the configured token."""
    import httpx
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    if not token:
        return JSONResponse({"ok": False, "error": "no token"}, status_code=500)
    host = os.environ.get("TELEGRAM_API_BASE", "https://api.telegram.org").rstrip("/")
    try:
        with httpx.Client(timeout=15.0) as c:
            r = c.get(f"{host}/bot{token}/getMe")
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


# --- WhatsApp (Meta) ---

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


# --- Telegram ---

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


# --- Case API (offline /lite page: store-and-forward sync) ---

MAX_IMAGE_BYTES = 2 * 1024 * 1024
_API_RATE_MAX = 20          # requests per window per client IP
_API_RATE_WINDOW_SEC = 60
_api_hits: dict[str, deque] = defaultdict(lambda: deque(maxlen=_API_RATE_MAX))

# /lite checklist ids → the Bengali words severity.engine.ESCALATION_KEYWORDS matches
RED_FLAG_KEYWORDS = {
    "fever":     "জ্বর",
    "spreading": "ছড়িয়ে",
    "pain":      "ব্যথা",
    "bleeding":  "রক্ত",
}


def _api_rate_ok(client_ip: str) -> bool:
    now = time.time()
    hits = _api_hits[client_ip]
    while hits and now - hits[0] > _API_RATE_WINDOW_SEC:
        hits.popleft()
    if len(hits) >= _API_RATE_MAX:
        return False
    hits.append(now)
    return True


def _client_ip(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for", "")
    return fwd.split(",")[0].strip() if fwd else (request.client.host if request.client else "?")


@app.post("/api/cases")
async def create_case(
    request: Request,
    image: UploadFile = File(...),
    red_flags: list[str] = Form(default=[]),
    district: str = Form(default=""),
    consent: str = Form(default="false"),
    client_ts: str = Form(default=""),
) -> JSONResponse:
    """Triage one synced /lite case. Stores it for doctor review only with consent."""
    if not _api_rate_ok(_client_ip(request)):
        return JSONResponse({"error": "rate_limited"}, status_code=429)

    img_bytes = await image.read(MAX_IMAGE_BYTES + 1)
    if not img_bytes:
        return JSONResponse({"error": "empty_image"}, status_code=400)
    if len(img_bytes) > MAX_IMAGE_BYTES:
        return JSONResponse({"error": "image_too_large", "max_bytes": MAX_IMAGE_BYTES},
                            status_code=413)

    unknown = [f for f in red_flags if f not in RED_FLAG_KEYWORDS]
    if unknown:
        return JSONResponse({"error": "unknown_red_flag", "values": unknown}, status_code=400)

    blur = router._laplacian_variance(img_bytes)
    if blur < 0:
        return JSONResponse({"error": "unreadable_image"}, status_code=400)
    if blur < 50.0:
        return JSONResponse({"error": "blurry_image", "blur": round(blur, 1)}, status_code=422)

    from model import service as model_service
    pred = model_service.run_inference(img_bytes)
    if not pred.get("available"):
        return JSONResponse({"error": "model_unavailable",
                             "message_en": model_service.UNAVAILABLE_EN,
                             "message_bn": model_service.UNAVAILABLE_BN}, status_code=503)

    from severity.engine import compute_tier, explain_tier
    from model.disease_labels import get_bengali
    transcript = " ".join(RED_FLAG_KEYWORDS[f] for f in red_flags)
    tier_result = compute_tier(pred["disease"], pred["confidence"], transcript)
    reasons = explain_tier(pred["disease"], pred["confidence"], transcript)

    case_id = None
    if consent.strip().lower() in ("true", "1", "yes", "on"):
        from cases.store import add_case
        case_id = add_case(
            consent=True, source="lite", image=img_bytes,
            ai_disease=pred["disease"], ai_conf=pred["confidence"],
            ai_tier=tier_result["tier"], reasons=reasons,
            red_flags=list(red_flags), district=district,
        )

    try:
        from analytics.db import log_event
        conf = pred["confidence"]
        log_event("triage_lite", disease_class=pred["disease"], tier=tier_result["tier"],
                  conf_bucket="high" if conf >= 0.60 else ("medium" if conf >= 0.40 else "low"))
    except Exception:
        pass

    return JSONResponse({
        "case_id": case_id,
        "disease": pred["disease"],
        "disease_bn": get_bengali(pred["disease"]),
        "confidence": round(pred["confidence"], 4),
        "tier": tier_result["tier"],
        "urgency_label": tier_result["urgency_label"],
        "action_en": tier_result["action"],
        "action_bn": tier_result["bengali_text"],
        "facility": tier_result["facility"],
        "reasons": reasons,
        "bytes_received": len(img_bytes),
    })


@app.get("/api/cases/{case_id}")
def get_case_status(case_id: str) -> JSONResponse:
    """Status + doctor decision for a synced case (no photo, no notes about others)."""
    from cases.store import get_case
    from severity.engine import TIER_ACTIONS
    case = get_case(case_id)
    if case is None:
        return JSONResponse({"error": "not_found"}, status_code=404)
    out = {"case_id": case_id, "status": case["status"], "ai_tier": case["ai_tier"]}
    if case["status"] != "pending":
        act = TIER_ACTIONS[int(case["dr_tier"])]
        out.update({
            "dr_disease": case["dr_disease"],
            "dr_tier": case["dr_tier"],
            "dr_note": case["dr_note"] or "",
            "dr_action_en": act["action"],
            "dr_action_bn": act["bengali_text"],
        })
    return JSONResponse(out)
