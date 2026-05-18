# 7 classes from BD-SkinNet training — Faridpur MCH + Rangpur MCH + SkinDisNet
# Class index order matches CLASS_TO_IDX from notebook (alphabetical)

CLASS_NAMES = [
    "Atopic_Dermatitis",       # 0
    "Contact_Dermatitis",      # 1
    "Eczema",                  # 2
    "Scabies",                 # 3
    "Seborrheic_Dermatitis",   # 4
    "Tinea",                   # 5
    "Vitiligo",                # 6
]

NUM_CLASSES = len(CLASS_NAMES)

# English display name → Bengali name
DISEASE_BENGALI = {
    "Atopic_Dermatitis":     "অ্যাটোপিক ডার্মাটাইটিস",
    "Contact_Dermatitis":    "কন্টাক্ট ডার্মাটাইটিস",
    "Eczema":                "একজিমা",
    "Scabies":               "খোস-পাঁচড়া",
    "Seborrheic_Dermatitis": "সেবোরিক ডার্মাটাইটিস",
    "Tinea":                 "দাদ (টিনিয়া)",
    "Vitiligo":              "শ্বেতী রোগ",
}

# Severity tier per class — used by severity/engine.py
# Tier 1: Pharmacist | Tier 2: Upazila Health Complex | Tier 3: District Hospital
DISEASE_TIER = {
    "Atopic_Dermatitis":     2,
    "Contact_Dermatitis":    1,
    "Eczema":                2,
    "Scabies":               2,
    "Seborrheic_Dermatitis": 1,
    "Tinea":                 1,
    "Vitiligo":              2,
}


def get_bengali(class_name: str) -> str:
    return DISEASE_BENGALI.get(class_name, class_name)


def get_tier(class_name: str) -> int:
    return DISEASE_TIER.get(class_name, 2)
