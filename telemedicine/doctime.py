"""DocTime concrete provider (Phase 1 launch partner).

DocTime has no public developer API. Their B2B offering is a corporate
subscription, not a programmatic integration. The honest, demo-able
pattern is a co-branded handoff:

  • deep-link → opens DocTime app (Android intent) or web fallback
  • QR code  → patient scans on their own phone
  • WhatsApp → prefilled Bengali message to DocTime's hotline,
              with the AI referral PDF attached manually by the patient.

We do NOT fabricate a DocTime booking ID. We do NOT call any DocTime
endpoint. Everything below is local URL synthesis.
"""

from __future__ import annotations

import urllib.parse as _u

from telemedicine.providers import HandoffPayload, register


_HOTLINE_DIGITS = "8809610990077"  # +880 9610 990077 — DocTime call center
_WEB = "https://doctime.com.bd/"
_PKG = "com.media365ltd.doctime"
_PLAY = f"https://play.google.com/store/details?id={_PKG}"
_IOS = "https://apps.apple.com/app/doctime/id1525316696"


def _msg_bn(p: HandoffPayload) -> str:
    tier_word = {0: "সাধারণ", 1: "জরুরি নয়", 2: "নিয়মিত", 3: "জরুরি"}.get(p.tier, "")
    return (
        f"আসসালামু আলাইকুম, DocTime দল।\n\n"
        f"রোগী: {p.patient_name} ({p.patient_age})\n"
        f"অভিযোগ: {p.chief_complaint}\n"
        f"AI বিশ্লেষণ (SkinAI Bangladesh): {p.ai_disease_bn} "
        f"({p.ai_disease_en}) — আস্থা {int(p.confidence * 100)}%\n"
        f"ত্রিভাজন স্তর: Tier {p.tier} — {tier_word}\n\n"
        f"AI-উৎপাদিত রেফারেল পত্র (PDF) সংযুক্ত করছি। অনুগ্রহ করে আজই একজন "
        f"BMDC-নিবন্ধিত চর্ম বিশেষজ্ঞের সাথে অ্যাপয়েন্টমেন্ট দিন।"
    )


def _msg_en(p: HandoffPayload) -> str:
    return (
        f"Hello DocTime team,\n\n"
        f"Patient: {p.patient_name} ({p.patient_age})\n"
        f"Complaint: {p.chief_complaint}\n"
        f"SkinAI AI assessment: {p.ai_disease_en} "
        f"({int(p.confidence * 100)}% confidence) — Tier {p.tier} "
        f"{p.tier_label_en}\n\n"
        f"Attaching the AI-generated referral PDF. Please schedule a "
        f"BMDC-registered dermatologist consultation today."
    )


class DocTime:
    name = "DocTime"
    bn_name = "ডকটাইম"
    logo_path = "telemedicine/assets/doctime_logo.png"
    tagline_en = "Bangladesh's #1 telemedicine — BMDC doctors, 24/7 video"
    tagline_bn = "বাংলাদেশের শীর্ষস্থানীয় টেলিমেডিসিন — ২৪/৭ ভিডিও পরামর্শ"
    hotline = "+8809610990077"
    web_url = _WEB
    android_package = _PKG
    ios_url = _IOS
    fee_range_bdt = "৳ 100 – 500"
    available = True

    def deep_link(self, p: HandoffPayload) -> str:
        # Use the public web URL as the universal entry point. The DocTime
        # Android app intercepts doctime.com.bd via app-link, so this opens
        # the native app when installed and the website otherwise.
        params = {
            "utm_source": "skinai_bangladesh",
            "utm_medium": "ai_referral",
            "utm_campaign": "phase1_handoff",
            "ref_tier": str(p.tier),
            "ref_disease": p.ai_disease_en,
        }
        return f"{_WEB}?{_u.urlencode(params)}"

    def play_store_url(self) -> str:
        return _PLAY

    def whatsapp_url(self, p: HandoffPayload) -> str:
        return f"https://wa.me/{_HOTLINE_DIGITS}?text={_u.quote(_msg_bn(p))}"

    def qr_payload(self, p: HandoffPayload) -> str:
        # Patient scans this with their phone — opens DocTime via deep link.
        return self.deep_link(p)

    def prefilled_message(self, p: HandoffPayload, lang: str = "bn") -> str:
        return _msg_bn(p) if lang == "bn" else _msg_en(p)


register(DocTime())
