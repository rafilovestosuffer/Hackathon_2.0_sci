import pytest
from severity.engine import compute_tier, TIER_ACTIONS, CONF_TIER2, CONF_TIER3, COVERAGE_THRESHOLD


def _result(disease, conf, cov, transcript=""):
    return compute_tier(disease, conf, cov, transcript)


# ── Signal 1 base tiers ───────────────────────────────────────────────────────

class TestSignal1BaseTier:
    def test_tinea_high_conf_low_cov_no_kw(self):
        r = _result("Tinea", 0.90, 10.0)
        assert r["tier"] == 1

    def test_scabies_high_conf_low_cov_no_kw(self):
        r = _result("Scabies", 0.90, 10.0)
        assert r["tier"] == 2

    def test_atopic_dermatitis_base_tier(self):
        r = _result("Atopic_Dermatitis", 0.85, 5.0)
        assert r["tier"] == 2

    def test_contact_dermatitis_base_tier(self):
        r = _result("Contact_Dermatitis", 0.85, 5.0)
        assert r["tier"] == 1

    def test_vitiligo_base_tier(self):
        r = _result("Vitiligo", 0.85, 5.0)
        assert r["tier"] == 2

    def test_unknown_class_defaults_to_tier2(self):
        r = _result("UnknownDisease", 0.85, 5.0)
        assert r["tier"] == 2


# ── Signal 2 confidence modifier ─────────────────────────────────────────────

class TestSignal2Confidence:
    def test_below_040_forces_tier3(self):
        r = _result("Tinea", 0.35, 5.0)
        assert r["tier"] == 3

    def test_exactly_040_not_tier3(self):
        # boundary: < 0.40 triggers tier 3; 0.40 does not
        r = _result("Tinea", 0.40, 5.0)
        assert r["tier"] != 3

    def test_below_060_raises_to_tier2(self):
        # Tinea base = 1; conf 0.50 → max(1,2) = 2
        r = _result("Tinea", 0.50, 5.0)
        assert r["tier"] == 2

    def test_below_060_does_not_lower_tier2(self):
        # Scabies base = 2; conf 0.50 → max(2,2) = 2
        r = _result("Scabies", 0.50, 5.0)
        assert r["tier"] == 2

    def test_high_conf_no_escalation(self):
        r = _result("Tinea", 0.95, 5.0)
        assert r["tier"] == 1


# ── Signal 3 GradCAM coverage modifier ───────────────────────────────────────

class TestSignal3Coverage:
    def test_coverage_above_40_escalates_tier1_to_tier2(self):
        r = _result("Tinea", 0.90, 45.0)
        assert r["tier"] == 2

    def test_coverage_above_40_escalates_tier2_to_tier3(self):
        r = _result("Scabies", 0.90, 45.0)
        assert r["tier"] == 3

    def test_coverage_exactly_40_no_escalation(self):
        # > 40.0 required; exactly 40.0 does NOT trigger
        r = _result("Tinea", 0.90, 40.0)
        assert r["tier"] == 1

    def test_coverage_cap_at_3(self):
        # tier 3 + high coverage → stays 3
        r = _result("Scabies", 0.35, 45.0)
        assert r["tier"] == 3


# ── Signal 4 Bengali keyword modifier ────────────────────────────────────────

class TestSignal4Keywords:
    def test_fever_keyword_escalates(self):
        r = _result("Scabies", 0.90, 5.0, transcript="রোগীর জ্বর আছে")
        assert r["tier"] == 3

    def test_spreading_keyword_escalates(self):
        r = _result("Scabies", 0.90, 5.0, transcript="র‍্যাশ ছড়িয়ে পড়ছে")
        assert r["tier"] == 3

    def test_pain_keyword_escalates(self):
        r = _result("Scabies", 0.90, 5.0, transcript="অনেক ব্যথা হচ্ছে")
        assert r["tier"] == 3

    def test_blood_keyword_escalates(self):
        r = _result("Scabies", 0.90, 5.0, transcript="রক্ত বের হচ্ছে")
        assert r["tier"] == 3

    def test_keyword_escalates_tier1_to_tier2(self):
        r = _result("Tinea", 0.90, 5.0, transcript="একটু জ্বর আছে")
        assert r["tier"] == 2

    def test_no_keyword_no_escalation(self):
        r = _result("Scabies", 0.90, 5.0, transcript="সাধারণ লক্ষণ")
        assert r["tier"] == 2

    def test_keyword_cap_at_3(self):
        # already tier 3 via Signal 2; keyword should not push beyond 3
        r = _result("Tinea", 0.35, 5.0, transcript="জ্বর আছে")
        assert r["tier"] == 3


# ── Combined escalation ───────────────────────────────────────────────────────

class TestCombinedEscalation:
    def test_coverage_and_keyword_on_tier2_caps_at_3(self):
        # Signal 3: Scabies(2) + cov 45% → 3; Signal 4: keyword → min(4,3)=3
        r = _result("Scabies", 0.90, 45.0, transcript="জ্বর আছে")
        assert r["tier"] == 3

    def test_tier_never_exceeds_3(self):
        r = _result("Scabies", 0.30, 60.0, transcript="জ্বর ছড়িয়ে ব্যথা রক্ত")
        assert r["tier"] == 3


# ── Return dict structure ─────────────────────────────────────────────────────

class TestReturnStructure:
    def test_required_keys_present(self):
        r = _result("Tinea", 0.90, 5.0)
        for key in ("tier", "urgency_label", "action", "facility", "bengali_text"):
            assert key in r, f"missing key: {key}"

    def test_tier1_labels(self):
        r = _result("Tinea", 0.90, 5.0)
        assert r["urgency_label"] == "NON-URGENT"
        assert r["facility"] == "Local Pharmacy"

    def test_tier2_labels(self):
        r = _result("Scabies", 0.90, 5.0)
        assert r["urgency_label"] == "ROUTINE"
        assert r["facility"] == "Upazila Health Complex"

    def test_tier3_labels(self):
        r = _result("Tinea", 0.35, 5.0)
        assert r["urgency_label"] == "URGENT"
        assert r["facility"] == "District Hospital"

    def test_bengali_text_nonempty(self):
        for tier_conf in [(0.90, 5.0), (0.50, 5.0), (0.35, 5.0)]:
            r = _result("Tinea", *tier_conf)
            assert r["bengali_text"], "Bengali text must not be empty"


# ── Boundary regression tests (guard against threshold drift) ─────────────────

class TestBoundaryConstants:
    """Pinned tests that break immediately if CONF_TIER2/CONF_TIER3 are accidentally changed."""

    def test_conf_tier3_constant_value(self):
        assert CONF_TIER3 == 0.40, "CONF_TIER3 must be exactly 0.40 per CLAUDE.md spec"

    def test_conf_tier2_constant_value(self):
        assert CONF_TIER2 == 0.60, "CONF_TIER2 must be exactly 0.60 per CLAUDE.md spec"

    def test_coverage_threshold_constant_value(self):
        assert COVERAGE_THRESHOLD == 40.0, "COVERAGE_THRESHOLD must be exactly 40.0 per CLAUDE.md spec"

    def test_exactly_conf_tier2_is_not_escalated(self):
        r = _result("Tinea", CONF_TIER2, 5.0)
        assert r["tier"] == 1, "At exactly CONF_TIER2 (0.60), Tinea must stay Tier 1"

    def test_just_below_conf_tier2_escalates_tinea_to_tier2(self):
        r = _result("Tinea", CONF_TIER2 - 0.001, 5.0)
        assert r["tier"] == 2

    def test_exactly_conf_tier3_is_not_tier3(self):
        r = _result("Tinea", CONF_TIER3, 5.0)
        assert r["tier"] != 3, "At exactly CONF_TIER3 (0.40), should not be Tier 3"

    def test_just_below_conf_tier3_forces_tier3(self):
        r = _result("Tinea", CONF_TIER3 - 0.001, 5.0)
        assert r["tier"] == 3

    def test_exactly_coverage_threshold_no_escalation(self):
        r = _result("Tinea", 0.90, COVERAGE_THRESHOLD)
        assert r["tier"] == 1, "At exactly 40.0% coverage, must NOT escalate"

    def test_just_above_coverage_threshold_escalates(self):
        r = _result("Tinea", 0.90, COVERAGE_THRESHOLD + 0.001)
        assert r["tier"] == 2
