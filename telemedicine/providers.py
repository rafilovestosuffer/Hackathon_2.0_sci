"""Telemedicine provider abstraction.

Defines the data carried across the handoff boundary (`HandoffPayload`) and
the provider interface every integration must satisfy. Concrete providers
register themselves into `REGISTRY` by importing this module.

This is what makes the pitch "telemedicine integration layer" real code,
not a slide: adding Praava or MediCal in Phase 3 is one new file.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Protocol, runtime_checkable


@dataclass(frozen=True)
class HandoffPayload:
    """Patient context handed off to the telemedicine provider.

    The referral PDF is the canonical payload — the doctor on the other
    end opens it and sees the full AI analysis. Structured fields are for
    UI prefill and message templating, not for the doctor's diagnosis.
    """
    patient_name: str
    patient_age: str
    chief_complaint: str
    ai_disease_en: str
    ai_disease_bn: str
    confidence: float
    tier: int
    tier_label_en: str
    tier_label_bn: str
    facility_type: str
    referral_pdf_bytes: Optional[bytes] = field(default=None, repr=False)


@runtime_checkable
class TelemedicineProvider(Protocol):
    name: str
    bn_name: str
    logo_path: str
    tagline_en: str
    tagline_bn: str
    hotline: str
    web_url: str
    android_package: str
    ios_url: str
    fee_range_bdt: str
    available: bool  # False for Phase-3 stubs

    def deep_link(self, p: HandoffPayload) -> str: ...
    def whatsapp_url(self, p: HandoffPayload) -> str: ...
    def qr_payload(self, p: HandoffPayload) -> str: ...
    def prefilled_message(self, p: HandoffPayload, lang: str = "bn") -> str: ...


REGISTRY: dict[str, TelemedicineProvider] = {}


def register(provider: TelemedicineProvider) -> None:
    REGISTRY[provider.name.lower()] = provider


def get_provider(name: str) -> TelemedicineProvider:
    return REGISTRY[name.lower()]


# ── Session → payload helper ─────────────────────────────────────────────────

def payload_from_session(session_state) -> Optional[HandoffPayload]:
    """Build a HandoffPayload from Streamlit session_state. Returns None if
    diagnosis hasn't run yet."""
    pred = session_state.get("prediction")
    tier = session_state.get("tier_result")
    if not pred or not tier:
        return None

    history = session_state.get("history") or {}

    try:
        from model.disease_labels import get_bengali
        disease_bn = get_bengali(pred.get("disease", ""))
    except Exception:
        disease_bn = pred.get("disease", "")

    tier_int = int(tier.get("tier", 0) or 0)
    _BN = {
        0: "সুস্থ", 1: "জরুরি নয়", 2: "নিয়মিত", 3: "জরুরি",
    }

    return HandoffPayload(
        patient_name=history.get("patient_name") or "Patient",
        patient_age=str(history.get("patient_age") or ""),
        chief_complaint=history.get("chief_complaint") or "Skin condition assessment",
        ai_disease_en=pred.get("disease", "Unknown"),
        ai_disease_bn=disease_bn,
        confidence=float(pred.get("confidence", 0.0)),
        tier=tier_int,
        tier_label_en=tier.get("urgency_label", ""),
        tier_label_bn=_BN.get(tier_int, ""),
        facility_type=tier.get("facility", ""),
        referral_pdf_bytes=session_state.get("pdf_bytes"),
    )


# ── Phase-3 stubs ────────────────────────────────────────────────────────────
# These exist so the Impact roadmap and provider grid are backed by real code.
# They deliberately raise on handoff — calling them is a bug.

class _StubProvider:
    available = False
    fee_range_bdt = "—"
    logo_path = ""
    android_package = ""
    ios_url = ""

    def deep_link(self, p):       raise NotImplementedError(f"{self.name} is a Phase-3 stub")
    def whatsapp_url(self, p):    raise NotImplementedError(f"{self.name} is a Phase-3 stub")
    def qr_payload(self, p):      raise NotImplementedError(f"{self.name} is a Phase-3 stub")
    def prefilled_message(self, p, lang="bn"):
        raise NotImplementedError(f"{self.name} is a Phase-3 stub")


class _Praava(_StubProvider):
    name = "Praava Health"
    bn_name = "প্রাভা হেলথ"
    tagline_en = "Family-care telehealth — full GP + diagnostic stack"
    tagline_bn = "পারিবারিক টেলিহেলথ"
    hotline = "+8801332220033"
    web_url = "https://praavahealth.com/"


class _MediCal(_StubProvider):
    name = "MediCal"
    bn_name = "মেডিক্যাল"
    tagline_en = "Doctor-on-demand video consults"
    tagline_bn = "চাহিদামতো ভিডিও পরামর্শ"
    hotline = ""
    web_url = "https://medical.com.bd/"


class _Maya(_StubProvider):
    name = "Maya"
    bn_name = "মায়া"
    tagline_en = "Anonymous Bengali health Q&A — women & adolescents"
    tagline_bn = "নারীদের স্বাস্থ্য পরামর্শ"
    hotline = ""
    web_url = "https://maya.com.bd/"


register(_Praava())
register(_MediCal())
register(_Maya())
