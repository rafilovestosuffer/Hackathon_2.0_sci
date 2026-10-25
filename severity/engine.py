from model.disease_labels import get_tier

ESCALATION_KEYWORDS = ["জ্বর", "ছড়িয়ে", "ব্যথা", "রক্ত"]

# Single source of truth for confidence thresholds — imported by ui/components.py too
CONF_TIER3: float = 0.40
CONF_TIER2: float = 0.60

COST_ESTIMATE = {
    0: {
        "range":   "৳0",
        "note":    "No treatment needed — healthy skin",
        "note_bn": "কোনো চিকিৎসার প্রয়োজন নেই — ত্বক সুস্থ",
    },
    1: {
        "range":   "৳50–200",
        "note":    "OTC cream / antihistamine at local pharmacy",
        "note_bn": "স্থানীয় ফার্মেসি থেকে সাশ্রয়ী ওষুধ কিনুন",
    },
    2: {
        "range":   "৳0–100",
        "note":    "Free or subsidised at Upazila Health Complex (government)",
        "note_bn": "উপজেলা স্বাস্থ্য কমপ্লেক্সে বিনামূল্যে বা ভর্তুকিমূলক",
    },
    3: {
        "range":   "৳0–500",
        "note":    "Subsidised emergency care at District Hospital",
        "note_bn": "জেলা হাসপাতালে ভর্তুকিমূলক জরুরি চিকিৎসা",
    },
}

TIER_ACTIONS = {
    0: {
        "urgency_label": "HEALTHY",
        "action": "No treatment needed. Your skin appears normal and healthy.",
        "facility": "None",
        "bengali_text": "আপনার ত্বক স্বাভাবিক দেখাচ্ছে। কোনো চিকিৎসার প্রয়োজন নেই।",
    },
    1: {
        "urgency_label": "NON-URGENT",
        "action": "Consult local pharmacist within 3-5 days",
        "facility": "Local Pharmacy",
        "bengali_text": "৩-৫ দিনের মধ্যে নিকটস্থ ফার্মাসিস্টের সাথে পরামর্শ করুন",
    },
    2: {
        "urgency_label": "ROUTINE",
        "action": "Visit Upazila Health Complex within 48 hours",
        "facility": "Upazila Health Complex",
        "bengali_text": "৪৮ ঘণ্টার মধ্যে উপজেলা স্বাস্থ্য কমপ্লেক্সে যান",
    },
    3: {
        "urgency_label": "URGENT",
        "action": "Seek emergency care TODAY at District Hospital",
        "facility": "District Hospital",
        "bengali_text": "আজই জেলা হাসপাতালে জরুরি চিকিৎসা নিন — জরুরি চিকিৎসা প্রয়োজন",
    },
}


def compute_tier(
    disease_class: str,
    confidence: float,
    transcript: str,
) -> dict:
    # Early return: confident Normal detection → tier 0 (healthy), no escalation
    if disease_class == "Normal" and confidence >= CONF_TIER2:
        return {"tier": 0, **TIER_ACTIONS[0]}

    # Signal 1: base tier from disease class
    # Low-confidence Normal falls through as tier 1 (non-urgent) for patient safety
    tier = get_tier(disease_class)
    if disease_class == "Normal":
        tier = 1

    # Signal 2: confidence modifier
    if confidence < CONF_TIER3:
        tier = 3
    elif confidence < CONF_TIER2:
        tier = max(tier, 2)

    # Signal 3: Bengali voice keyword modifier
    if any(kw in transcript for kw in ESCALATION_KEYWORDS):
        tier = min(tier + 1, 3)

    result = {"tier": tier}
    result.update(TIER_ACTIONS[tier])
    return result


_TIER_NAME_EN = {0: "healthy", 1: "non-urgent", 2: "routine", 3: "urgent"}
_TIER_NAME_BN = {0: "সুস্থ", 1: "জরুরি নয়", 2: "নিয়মিত", 3: "জরুরি"}

_KEYWORD_EN = {"জ্বর": "fever", "ছড়িয়ে": "spreading", "ব্যথা": "pain", "রক্ত": "bleeding"}


def explain_tier(
    disease_class: str,
    confidence: float,
    transcript: str,
) -> list[dict]:
    """
    Plain-language reasons for the tier compute_tier() returns, one entry per
    signal that shaped it. Mirrors compute_tier step by step; it never
    changes the tier. Each entry: {"signal", "en", "bn"}.
    """
    pct = f"{confidence:.0%}"
    name = disease_class.replace("_", " ")

    if disease_class == "Normal" and confidence >= CONF_TIER2:
        return [{
            "signal": "healthy",
            "en": f"Model sees normal skin with {pct} confidence (≥ {CONF_TIER2:.0%}) → healthy, no referral.",
            "bn": f"মডেল {pct} নিশ্চয়তায় স্বাভাবিক ত্বক দেখছে → সুস্থ, রেফারেলের প্রয়োজন নেই।",
        }]

    reasons: list[dict] = []
    tier = get_tier(disease_class)
    if disease_class == "Normal":
        tier = 1
        reasons.append({
            "signal": "class",
            "en": f"Model leans to normal skin but only at {pct} → kept at non-urgent for safety.",
            "bn": f"মডেল স্বাভাবিক ত্বক বলছে কিন্তু নিশ্চয়তা মাত্র {pct} → নিরাপত্তার জন্য 'জরুরি নয়' স্তরে রাখা হলো।",
        })
    else:
        reasons.append({
            "signal": "class",
            "en": f"{name} usually needs {_TIER_NAME_EN[tier]} care (tier {tier}).",
            "bn": f"{name} সাধারণত {_TIER_NAME_BN[tier]} স্তরের চিকিৎসা চায় (স্তর {tier})।",
        })

    if confidence < CONF_TIER3:
        tier = 3
        reasons.append({
            "signal": "confidence",
            "en": f"Model confidence {pct} is below {CONF_TIER3:.0%} → too uncertain, escalated to urgent.",
            "bn": f"মডেলের নিশ্চয়তা {pct}, যা {CONF_TIER3:.0%}-এর কম → অনিশ্চিত, তাই জরুরি স্তরে পাঠানো হলো।",
        })
    elif confidence < CONF_TIER2:
        if tier < 2:
            reasons.append({
                "signal": "confidence",
                "en": f"Model confidence {pct} is below {CONF_TIER2:.0%} → raised to at least routine.",
                "bn": f"মডেলের নিশ্চয়তা {pct}, যা {CONF_TIER2:.0%}-এর কম → অন্তত 'নিয়মিত' স্তরে তোলা হলো।",
            })
        tier = max(tier, 2)

    hits = [kw for kw in ESCALATION_KEYWORDS if kw in transcript]
    if hits:
        new_tier = min(tier + 1, 3)
        words_en = ", ".join(_KEYWORD_EN.get(k, k) for k in hits)
        words_bn = ", ".join(hits)
        if new_tier > tier:
            en = f"Patient reported warning signs ({words_en}) → escalated one level."
            bn = f"রোগী সতর্কসংকেত জানিয়েছেন ({words_bn}) → এক স্তর বাড়ানো হলো।"
        else:
            en = f"Patient reported warning signs ({words_en}); already at the highest level."
            bn = f"রোগী সতর্কসংকেত জানিয়েছেন ({words_bn}); ইতিমধ্যে সর্বোচ্চ স্তরে আছে।"
        reasons.append({"signal": "keywords", "en": en, "bn": bn})

    return reasons
