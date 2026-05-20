from model.disease_labels import get_tier

ESCALATION_KEYWORDS = ["জ্বর", "ছড়িয়ে", "ব্যথা", "রক্ত"]

TIER_ACTIONS = {
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
    coverage_pct: float,
    transcript: str,
) -> dict:
    # Signal 1: base tier from disease class
    tier = get_tier(disease_class)

    # Signal 2: confidence modifier
    if confidence < 0.40:
        tier = 3
    elif confidence < 0.60:
        tier = max(tier, 2)

    # Signal 3: GradCAM coverage modifier
    if coverage_pct > 40.0:
        tier = min(tier + 1, 3)

    # Signal 4: Bengali voice keyword modifier
    if any(kw in transcript for kw in ESCALATION_KEYWORDS):
        tier = min(tier + 1, 3)

    result = {"tier": tier}
    result.update(TIER_ACTIONS[tier])
    return result
