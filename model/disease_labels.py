# Every label the app knows (UI, knowledge graph, doctor override, demos).
# The live model's own output order comes from its checkpoint (class_to_idx),
# see model/bd_skinnet.load_model — never index logits with this list.

CLASS_NAMES = [
    "Atopic_Dermatitis",       # 0
    "Contact_Dermatitis",      # 1
    "Eczema",                  # 2
    "Normal",                  # 3
    "Scabies",                 # 4
    "Seborrheic_Dermatitis",   # 5
    "Tinea",                   # 6
    "Vitiligo",                # 7
]

NUM_CLASSES = len(CLASS_NAMES)

# English display name → Bengali name
DISEASE_BENGALI = {
    "Atopic_Dermatitis":     "অ্যাটোপিক ডার্মাটাইটিস",
    "Contact_Dermatitis":    "কন্টাক্ট ডার্মাটাইটিস",
    "Eczema":                "একজিমা",
    "Normal":                "স্বাভাবিক ত্বক",
    "Scabies":               "খোস-পাঁচড়া",
    "Seborrheic_Dermatitis": "সেবোরিক ডার্মাটাইটিস",
    "Tinea":                 "দাদ (টিনিয়া)",
    "Vitiligo":              "শ্বেতী রোগ",
}

# Severity tier per class — used by severity/engine.py
# Tier 0: Healthy (no disease) | Tier 1: Pharmacist | Tier 2: Upazila Health Complex | Tier 3: District Hospital
DISEASE_TIER = {
    "Atopic_Dermatitis":     2,
    "Contact_Dermatitis":    1,
    "Eczema":                2,
    "Normal":                0,
    "Scabies":               2,
    "Seborrheic_Dermatitis": 1,
    "Tinea":                 1,
    "Vitiligo":              2,
}


def get_bengali(class_name: str) -> str:
    return DISEASE_BENGALI.get(class_name, class_name)


def get_tier(class_name: str) -> int:
    return DISEASE_TIER.get(class_name, 2)
