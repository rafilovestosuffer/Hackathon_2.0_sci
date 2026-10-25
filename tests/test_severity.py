import pytest
from severity.engine import compute_tier, TIER_ACTIONS, CONF_TIER2, CONF_TIER3


def _result(disease, conf, transcript=""):
    return compute_tier(disease, conf, transcript)


# --- Signal 1 base tiers ---

class TestSignal1BaseTier:
    def test_tinea_high_conf_no_kw(self):
        r = _result("Tinea", 0.90)
        assert r["tier"] == 1

    def test_scabies_high_conf_no_kw(self):
        r = _result("Scabies", 0.90)
        assert r["tier"] == 2

    def test_atopic_dermatitis_base_tier(self):
        r = _result("Atopic_Dermatitis", 0.85)
        assert r["tier"] == 2

    def test_contact_dermatitis_base_tier(self):
        r = _result("Contact_Dermatitis", 0.85)
        assert r["tier"] == 1

    def test_vitiligo_base_tier(self):
        r = _result("Vitiligo", 0.85)
        assert r["tier"] == 2

    def test_unknown_class_defaults_to_tier2(self):
        r = _result("UnknownDisease", 0.85)
        assert r["tier"] == 2


# --- Signal 2 confidence modifier ---

class TestSignal2Confidence:
    def test_below_040_forces_tier3(self):
        r = _result("Tinea", 0.35)
        assert r["tier"] == 3

    def test_exactly_040_not_tier3(self):
        r = _result("Tinea", 0.40)
        assert r["tier"] != 3

    def test_below_060_raises_to_tier2(self):
        r = _result("Tinea", 0.50)
        assert r["tier"] == 2

    def test_below_060_does_not_lower_tier2(self):
        r = _result("Scabies", 0.50)
        assert r["tier"] == 2

    def test_high_conf_no_escalation(self):
        r = _result("Tinea", 0.95)
        assert r["tier"] == 1


# --- Signal 3 Bengali keyword modifier ---

class TestSignal3Keywords:
    def test_fever_keyword_escalates(self):
        r = _result("Scabies", 0.90, transcript="রোগীর জ্বর আছে")
        assert r["tier"] == 3

    def test_spreading_keyword_escalates(self):
        r = _result("Scabies", 0.90, transcript="র‍্যাশ ছড়িয়ে পড়ছে")
        assert r["tier"] == 3

    def test_pain_keyword_escalates(self):
        r = _result("Scabies", 0.90, transcript="অনেক ব্যথা হচ্ছে")
        assert r["tier"] == 3

    def test_blood_keyword_escalates(self):
        r = _result("Scabies", 0.90, transcript="রক্ত বের হচ্ছে")
        assert r["tier"] == 3

    def test_keyword_escalates_tier1_to_tier2(self):
        r = _result("Tinea", 0.90, transcript="একটু জ্বর আছে")
        assert r["tier"] == 2

    def test_no_keyword_no_escalation(self):
        r = _result("Scabies", 0.90, transcript="সাধারণ লক্ষণ")
        assert r["tier"] == 2

    def test_keyword_cap_at_3(self):
        r = _result("Tinea", 0.35, transcript="জ্বর আছে")
        assert r["tier"] == 3


# --- Combined escalation ---

class TestCombinedEscalation:
    def test_tier_never_exceeds_3(self):
        r = _result("Scabies", 0.30, transcript="জ্বর ছড়িয়ে ব্যথা রক্ত")
        assert r["tier"] == 3


# --- Return dict structure ---

class TestReturnStructure:
    def test_required_keys_present(self):
        r = _result("Tinea", 0.90)
        for key in ("tier", "urgency_label", "action", "facility", "bengali_text"):
            assert key in r, f"missing key: {key}"

    def test_tier1_labels(self):
        r = _result("Tinea", 0.90)
        assert r["urgency_label"] == "NON-URGENT"
        assert r["facility"] == "Local Pharmacy"

    def test_tier2_labels(self):
        r = _result("Scabies", 0.90)
        assert r["urgency_label"] == "ROUTINE"
        assert r["facility"] == "Upazila Health Complex"

    def test_tier3_labels(self):
        r = _result("Tinea", 0.35)
        assert r["urgency_label"] == "URGENT"
        assert r["facility"] == "District Hospital"

    def test_bengali_text_nonempty(self):
        for conf in [0.90, 0.50, 0.35]:
            r = _result("Tinea", conf)
            assert r["bengali_text"], "Bengali text must not be empty"


# --- Boundary regression tests ---

class TestBoundaryConstants:
    def test_conf_tier3_constant_value(self):
        assert CONF_TIER3 == 0.40

    def test_conf_tier2_constant_value(self):
        assert CONF_TIER2 == 0.60

    def test_exactly_conf_tier2_is_not_escalated(self):
        r = _result("Tinea", CONF_TIER2)
        assert r["tier"] == 1

    def test_just_below_conf_tier2_escalates_tinea_to_tier2(self):
        r = _result("Tinea", CONF_TIER2 - 0.001)
        assert r["tier"] == 2

    def test_exactly_conf_tier3_is_not_tier3(self):
        r = _result("Tinea", CONF_TIER3)
        assert r["tier"] != 3

    def test_just_below_conf_tier3_forces_tier3(self):
        r = _result("Tinea", CONF_TIER3 - 0.001)
        assert r["tier"] == 3


# --- explain_tier: reasons mirror compute_tier ---

from severity.engine import explain_tier

_CASES = [
    ("Normal", 0.91, ""), ("Normal", 0.50, ""), ("Normal", 0.30, ""),
    ("Tinea", 0.90, ""), ("Tinea", 0.50, ""), ("Tinea", 0.30, ""),
    ("Scabies", 0.90, "জ্বর আছে"), ("Scabies", 0.38, "জ্বর, ব্যথা"),
    ("Eczema", 0.72, ""), ("Vitiligo", 0.55, "রক্ত"), ("Contact_Dermatitis", 0.95, "ছড়িয়ে পড়ছে"),
]


class TestExplainTier:
    @pytest.mark.parametrize("disease,conf,transcript", _CASES)
    def test_every_reason_is_bilingual(self, disease, conf, transcript):
        reasons = explain_tier(disease, conf, transcript)
        assert reasons
        for r in reasons:
            assert r["signal"] in {"healthy", "class", "confidence", "keywords"}
            assert r["en"] and r["bn"]

    @pytest.mark.parametrize("disease,conf,transcript", _CASES)
    def test_does_not_change_tier(self, disease, conf, transcript):
        before = compute_tier(disease, conf, transcript)
        explain_tier(disease, conf, transcript)
        assert compute_tier(disease, conf, transcript) == before

    def test_healthy_short_circuit(self):
        assert [r["signal"] for r in explain_tier("Normal", 0.91, "জ্বর")] == ["healthy"]

    def test_low_confidence_reason_present_iff_tier3_by_confidence(self):
        assert any(r["signal"] == "confidence" for r in explain_tier("Tinea", 0.30, ""))
        assert compute_tier("Tinea", 0.30, "")["tier"] == 3
        assert not any(r["signal"] == "confidence" for r in explain_tier("Tinea", 0.90, ""))

    def test_midband_reason_only_when_it_raises(self):
        assert any(r["signal"] == "confidence" for r in explain_tier("Tinea", 0.50, ""))
        assert not any(r["signal"] == "confidence" for r in explain_tier("Scabies", 0.50, ""))

    def test_keyword_reason_names_the_symptom(self):
        r = [x for x in explain_tier("Scabies", 0.90, "জ্বর আছে") if x["signal"] == "keywords"]
        assert len(r) == 1 and "fever" in r[0]["en"] and "জ্বর" in r[0]["bn"]

    def test_keyword_at_max_tier_says_already_highest(self):
        r = [x for x in explain_tier("Scabies", 0.30, "ব্যথা") if x["signal"] == "keywords"]
        assert "highest" in r[0]["en"]
