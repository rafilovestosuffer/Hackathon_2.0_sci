"""
cases/notify.py — tell the patient about the doctor's decision.

Telegram cases carry a chat id until the decision is sent; it is cleared
right after. Web and /lite cases have no chat id — those patients see the
decision by polling GET /api/cases/{id}.
"""
from __future__ import annotations

import logging

from cases import store

logger = logging.getLogger(__name__)


def build_message(case: dict) -> str:
    from model.disease_labels import get_bengali
    from severity.engine import TIER_ACTIONS
    from whatsapp.replies import format_doctor_decision
    tier = int(case["dr_tier"])
    act = TIER_ACTIONS[tier]
    return format_doctor_decision(
        status=case["status"],
        disease_bn=get_bengali(case["dr_disease"]),
        disease_en=case["dr_disease"].replace("_", " "),
        tier=tier,
        bengali_action=act["bengali_text"],
        english_action=act["action"],
        note=case.get("dr_note") or "",
    )


def notify_patient(case: dict) -> bool:
    """Send the decision to a Telegram patient. Returns True if a message was sent."""
    chat_id = case.get("notify_chat_id")
    if not chat_id or case.get("status") == "pending":
        return False
    try:
        from whatsapp import telegram_client
        telegram_client.send_text(chat_id, build_message(case))
    except Exception as exc:
        logger.warning("Doctor-decision notify failed for case %s: %s", case.get("id"), exc)
        return False
    store.clear_notify_chat_id(case["id"])
    return True
