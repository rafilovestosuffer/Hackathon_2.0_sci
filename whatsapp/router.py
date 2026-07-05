"""
whatsapp/router.py — Platform-agnostic event router.

Takes a normalised event (from meta_client.parse_incoming or
telegram_client.parse_incoming), advances the per-user state machine, and
returns a list of outbound actions for the caller to send via the right
platform client.

This module imports the heavy SkinAI pipeline modules lazily so unit tests
don't pay the cost of loading torch/whisper/faiss.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable, Optional

from whatsapp import replies
from whatsapp.state import State, store

logger = logging.getLogger(__name__)


# --- Outbound action dataclasses ---

@dataclass
class TextOut:
    to: str
    body: str


@dataclass
class PdfOut:
    to: str
    pdf_bytes: bytes
    filename: str
    caption: str = ""


Action = TextOut | PdfOut


# --- Helpers ---

def _is_reset_command(text: str) -> bool:
    t = (text or "").strip().lower()
    return t in {"নতুন", "new", "reset", "restart", "শুরু"}


def _is_help_command(text: str) -> bool:
    t = (text or "").strip().lower()
    return t in {"help", "?", "সাহায্য", "/start", "/help"}


def _resolve_district(text: str) -> tuple[str, tuple[float, float]] | None:
    """Try the user's district text against the hospital_finder lookup."""
    from map.hospital_finder import get_district_coords, DISTRICT_COORDS
    raw = (text or "").strip().lower()
    if not raw:
        return None
    coords = get_district_coords(raw)
    if coords:
        return raw, coords
    # Try matching common Bengali names → English keys
    bn_to_en = {
        "ঢাকা": "dhaka", "চট্টগ্রাম": "chittagong", "চিটাগাং": "chittagong",
        "রংপুর": "rangpur", "সিলেট": "sylhet", "খুলনা": "khulna",
        "বরিশাল": "barisal", "রাজশাহী": "rajshahi", "ময়মনসিংহ": "mymensingh",
        "কুমিল্লা": "comilla", "যশোর": "jessore", "ফরিদপুর": "faridpur",
        "বগুড়া": "bogra", "দিনাজপুর": "dinajpur",
    }
    for bn, en in bn_to_en.items():
        if bn in (text or ""):
            c = get_district_coords(en)
            if c:
                return en, c
    return None


def _laplacian_variance(img_bytes: bytes) -> float:
    """Return blur metric (higher = sharper). Returns -1 on decode error."""
    try:
        import cv2, numpy as np
        arr = np.frombuffer(img_bytes, dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return -1.0
        return float(cv2.Laplacian(img, cv2.CV_64F).var())
    except Exception as e:
        logger.warning("Blur check failed: %s", e)
        return -1.0


# --- Model inference adapter ---

def _run_model(image_bytes: bytes) -> dict:
    """Return {disease, confidence, top2} from image bytes."""
    # The bot returns a fixed demo prediction (same schema as app.py::_run_model);
    # real BD-SkinNet inference runs in the web app.
    return {
        "disease": "Tinea",
        "confidence": 0.82,
        "top2": [
            {"disease": "Tinea", "confidence": 0.82},
            {"disease": "Contact_Dermatitis", "confidence": 0.11},
        ],
    }


# --- Pipeline runner — called when both image + (voice or skip) are in ---

def _run_pipeline(sess) -> tuple[dict, dict, Optional[dict], bytes]:
    """
    Returns (prediction, tier_result, nearest_hospital, pdf_bytes).
    Any stage failure is logged and a safe fallback is returned.
    """
    from severity.engine import compute_tier
    from pdf_gen.referral import generate_referral_pdf
    from map.hospital_finder import find_nearest_hospitals
    from model.disease_labels import get_bengali

    # Inference
    prediction = _run_model(sess.image_bytes or b"")

    # Triage
    tier_result = compute_tier(
        disease_class=prediction["disease"],
        confidence=prediction["confidence"],
        transcript=sess.voice_transcript or "",
    )

    # Hospital
    nearest = None
    if tier_result["tier"] >= 2 and sess.district_coords:
        try:
            lat, lon = sess.district_coords
            hospitals = find_nearest_hospitals(lat, lon, n=1)
            if hospitals:
                nearest = hospitals[0]
        except Exception as e:
            logger.warning("Hospital lookup failed: %s", e)

    # PDF
    session_data = {
        "patient_name": sess.patient_history.get("patient_name", ""),
        "patient_age": sess.patient_history.get("patient_age", ""),
        "chief_complaint": sess.patient_history.get("chief_complaint", ""),
        "symptoms": sess.patient_history.get("symptoms", []),
        "affected_area": sess.patient_history.get("affected_area", ""),
        "duration": sess.patient_history.get("duration", ""),
        "progression": sess.patient_history.get("progression", ""),
        "previous_treatment": sess.patient_history.get("previous_treatment", ""),
        "associated_symptoms": sess.patient_history.get("associated_symptoms", []),
        "disease": prediction["disease"],
        "disease_bn": get_bengali(prediction["disease"]),
        "confidence": prediction["confidence"],
        "top2": prediction.get("top2", []),
        "tier": tier_result["tier"],
        "tier_label": tier_result.get("urgency_label", ""),
        "tier_action": tier_result.get("action", ""),
        "facility": tier_result.get("facility", ""),
        "nearest_hospital": nearest,
        "district": sess.district or "",
    }
    try:
        pdf_bytes = generate_referral_pdf(session_data)
    except Exception as e:
        logger.error("PDF generation failed: %s", e)
        pdf_bytes = b""

    return prediction, tier_result, nearest, pdf_bytes


def _build_triage_text(prediction: dict, tier_result: dict, nearest: Optional[dict]) -> str:
    from model.disease_labels import get_bengali
    return replies.format_triage_result(
        disease_bn=get_bengali(prediction["disease"]),
        disease_en=prediction["disease"].replace("_", " "),
        confidence=prediction["confidence"],
        tier=tier_result["tier"],
        bengali_action=tier_result.get("bengali_text", ""),
        english_action=tier_result.get("action", ""),
        facility=tier_result.get("facility", ""),
        nearest_hospital=nearest,
    )


# --- Main entry point ---

def handle_event(
    event: dict,
    media_downloader: Callable[[str], bytes],
) -> list[Action]:
    """
    Process a single normalised event. Returns outbound actions.

    media_downloader: function(media_id) -> bytes, supplied by the caller
                      (different impl for Meta vs Telegram).
    """
    user_id = event["from"]
    if not user_id:
        return []

    # Idempotency
    if event.get("message_id") and store.seen_message(user_id, event["message_id"]):
        logger.info("Dedupe: skipping repeat message %s", event["message_id"])
        return []

    # Rate limit
    if not store.check_rate_limit(user_id):
        return [TextOut(to=user_id, body=replies.RATE_LIMITED)]

    sess = store.get_or_create(user_id)
    sess.touch()
    etype = event.get("type", "unsupported")
    text = (event.get("text") or "").strip()

    # Global commands work in any state
    if etype == "text" and _is_reset_command(text):
        store.reset(user_id)
        return [TextOut(to=user_id, body=replies.RESET_OK)]

    if etype == "text" and _is_help_command(text):
        return [TextOut(to=user_id, body=replies.HELP)]

    # State machine
    try:
        if sess.state == State.NEW:
            sess.state = State.AWAITING_DISTRICT
            return [TextOut(to=user_id, body=replies.WELCOME)]

        if sess.state == State.AWAITING_DISTRICT:
            if etype != "text":
                return [TextOut(to=user_id, body=replies.INVALID_DISTRICT)]
            resolved = _resolve_district(text)
            if not resolved:
                return [TextOut(to=user_id, body=replies.INVALID_DISTRICT)]
            sess.district, sess.district_coords = resolved
            sess.state = State.AWAITING_IMAGE
            return [TextOut(
                to=user_id,
                body=replies.ASK_IMAGE.format(district=sess.district.title()),
            )]

        if sess.state == State.AWAITING_IMAGE:
            if etype != "image":
                return [TextOut(to=user_id, body=replies.ASK_IMAGE.format(
                    district=(sess.district or "").title()
                ))]
            img_bytes = media_downloader(event["media_id"])
            if not img_bytes:
                return [TextOut(to=user_id, body=replies.UNSUPPORTED_MEDIA)]
            blur = _laplacian_variance(img_bytes)
            if 0 < blur < 50.0:  # heuristic blur threshold
                return [TextOut(to=user_id, body=replies.BLURRY_IMAGE)]
            sess.image_bytes = img_bytes
            sess.state = State.AWAITING_VOICE
            return [TextOut(to=user_id, body=replies.ASK_VOICE)]

        if sess.state == State.AWAITING_VOICE:
            actions: list[Action] = []
            if etype == "text" and text.lower() == "skip":
                sess.voice_transcript = ""
            elif etype == "audio":
                voice_bytes = media_downloader(event["media_id"])
                if not voice_bytes:
                    return [TextOut(to=user_id, body=replies.UNSUPPORTED_MEDIA)]
                actions.append(TextOut(to=user_id, body=replies.PROCESSING))
                try:
                    from voice.pipeline import transcribe_audio, extract_patient_history
                    sess.voice_transcript = transcribe_audio(voice_bytes, language="bn") or ""
                    if sess.voice_transcript:
                        sess.patient_history = extract_patient_history(sess.voice_transcript) or {}
                except Exception as e:
                    logger.warning("Voice pipeline failed: %s", e)
                    sess.voice_transcript = ""
            else:
                return [TextOut(to=user_id, body=replies.ASK_VOICE)]

            # Run full pipeline
            sess.state = State.PROCESSING
            prediction, tier_result, nearest, pdf_bytes = _run_pipeline(sess)
            sess.last_prediction = prediction
            sess.last_tier_result = tier_result
            sess.nearest_hospital = nearest
            sess.state = State.RESULT_SENT

            actions.append(TextOut(
                to=user_id,
                body=_build_triage_text(prediction, tier_result, nearest),
            ))
            if pdf_bytes:
                actions.append(PdfOut(
                    to=user_id,
                    pdf_bytes=pdf_bytes,
                    filename=f"skinai_referral_{user_id[-4:]}.pdf",
                    caption="📄 আপনার রেফারেল পত্র · Your referral letter",
                ))
            actions.append(TextOut(to=user_id, body=replies.format_chat_followup()))
            sess.state = State.RAG_CHAT
            return actions

        if sess.state in (State.RESULT_SENT, State.RAG_CHAT):
            if etype != "text" or not text:
                return [TextOut(to=user_id, body=replies.format_chat_followup())]
            # Treat any text as a RAG question
            try:
                from rag.retriever import answer_question, load_index
                load_index()
                disease_ctx = (sess.last_prediction or {}).get("disease")
                ans = answer_question(text, disease_context=disease_ctx)
            except Exception as e:
                logger.warning("RAG failed: %s", e)
                ans = "দুঃখিত, এখন উত্তর দিতে পারছি না। · Sorry, unable to answer right now."
            return [TextOut(to=user_id, body=replies.format_rag_answer(ans))]

    except Exception as e:
        logger.exception("Router error for user %s: %s", user_id, e)
        return [TextOut(to=user_id, body=replies.UNKNOWN_ERROR)]

    # Fallback
    return [TextOut(to=user_id, body=replies.HELP)]
