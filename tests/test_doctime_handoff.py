"""Unit tests for the DocTime telemedicine handoff layer."""

from __future__ import annotations

import urllib.parse as up

import pytest

from telemedicine import get_provider, payload_from_session
from telemedicine.providers import HandoffPayload, REGISTRY


@pytest.fixture
def payload() -> HandoffPayload:
    return HandoffPayload(
        patient_name="Rahim Mia",
        patient_age="34",
        chief_complaint="Itchy spreading rash on forearm for 5 days",
        ai_disease_en="Tinea",
        ai_disease_bn="দাদ",
        confidence=0.87,
        tier=2,
        tier_label_en="ROUTINE",
        tier_label_bn="নিয়মিত",
        facility_type="Upazila Health Complex",
        referral_pdf_bytes=b"%PDF-1.4 fake",
    )


def test_doctime_registered():
    dt = get_provider("DocTime")
    assert dt.available is True
    assert dt.name == "DocTime"
    assert dt.hotline.startswith("+880")


def test_deep_link_is_doctime_web(payload):
    dt = get_provider("DocTime")
    url = dt.deep_link(payload)
    assert url.startswith("https://doctime.com.bd/")
    assert "utm_source=skinai_bangladesh" in url
    assert "ref_tier=2" in url


def test_whatsapp_url_format_and_bengali(payload):
    dt = get_provider("DocTime")
    url = dt.whatsapp_url(payload)
    assert url.startswith("https://wa.me/8809610990077?text=")
    decoded = up.unquote(url.split("text=", 1)[1])
    assert "Rahim Mia" in decoded
    # Bengali AI disease name preserved
    assert "দাদ" in decoded
    # Tier reference present
    assert "Tier 2" in decoded


def test_qr_payload_nonempty_and_matches_deep_link(payload):
    dt = get_provider("DocTime")
    assert dt.qr_payload(payload) == dt.deep_link(payload)


def test_prefilled_message_bilingual(payload):
    dt = get_provider("DocTime")
    bn = dt.prefilled_message(payload, "bn")
    en = dt.prefilled_message(payload, "en")
    assert "AI" in bn and "DocTime" in bn
    assert "Patient: Rahim Mia" in en
    assert bn != en


def test_phase3_stubs_registered_but_not_available():
    for key in ("praava health", "medical", "maya"):
        p = REGISTRY[key]
        assert p.available is False
        with pytest.raises(NotImplementedError):
            p.deep_link(None)


def test_payload_from_session_returns_none_when_no_diagnosis():
    state = {"prediction": None, "tier_result": None}
    assert payload_from_session(state) is None


def test_payload_from_session_builds_from_state():
    state = {
        "prediction": {"disease": "Tinea", "confidence": 0.91, "top2": []},
        "tier_result": {
            "tier": 3,
            "urgency_label": "URGENT",
            "facility": "District Hospital",
        },
        "history": {
            "patient_name": "Test Patient",
            "patient_age": "40",
            "chief_complaint": "Spreading lesion",
        },
        "pdf_bytes": b"%PDF-1.4 stub",
    }
    p = payload_from_session(state)
    assert p is not None
    assert p.patient_name == "Test Patient"
    assert p.tier == 3
    assert p.ai_disease_en == "Tinea"
    assert p.referral_pdf_bytes == b"%PDF-1.4 stub"


def test_no_fake_doctime_api_calls_in_module():
    """Honesty guarantee: we never call api.doctime.com.bd."""
    import telemedicine.doctime as mod
    src = open(mod.__file__, encoding="utf-8").read()
    assert "api.doctime" not in src
    assert "requests.get" not in src and "requests.post" not in src
