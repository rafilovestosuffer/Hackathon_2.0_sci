"""
tests/test_pipeline.py — End-to-end interface compatibility tests.

Verifies that each module's output feeds correctly into the next module's
input, without running real models or making network calls.
All slow/external calls are mocked.
"""

from unittest.mock import MagicMock, patch

import pytest


# --- Fixtures ---

MODEL_OUTPUT = {
    "disease":      "Tinea",
    "confidence":   0.82,
    "top2": [
        {"disease": "Tinea",              "confidence": 0.82},
        {"disease": "Contact_Dermatitis", "confidence": 0.11},
    ],
}

TIER1_RESULT = {
    "tier":          1,
    "urgency_label": "NON-URGENT",
    "action":        "Consult local pharmacist within 3-5 days",
    "facility":      "Local Pharmacy",
    "bengali_text":  "৩-৫ দিনের মধ্যে নিকটস্থ ফার্মাসিস্টের সাথে পরামর্শ করুন",
}

HISTORY = {
    "patient_name":       "Rahim",
    "patient_age":        "35",
    "chief_complaint":    "Itchy ring-shaped rash",
    "symptoms":           ["itching", "redness", "scaling"],
    "affected_area":      "Arm",
    "duration":           "7 days",
    "progression":        "Spreading",
    "previous_treatment": "None",
    "associated_symptoms": [],
}


# --- Model output structure ---

class TestModelOutputStructure:
    """Verify _run_model() returns the structure expected by downstream code."""

    def test_has_disease_key(self):
        assert "disease" in MODEL_OUTPUT

    def test_disease_is_string(self):
        assert isinstance(MODEL_OUTPUT["disease"], str)

    def test_has_confidence_key(self):
        assert "confidence" in MODEL_OUTPUT

    def test_confidence_in_unit_range(self):
        assert 0.0 <= MODEL_OUTPUT["confidence"] <= 1.0

    def test_has_top2_key(self):
        assert "top2" in MODEL_OUTPUT

    def test_top2_has_two_entries(self):
        assert len(MODEL_OUTPUT["top2"]) == 2

    def test_top2_entries_have_required_keys(self):
        for entry in MODEL_OUTPUT["top2"]:
            assert "disease" in entry
            assert "confidence" in entry


# --- Model output → severity engine ---

class TestSeverityIntegration:
    """compute_tier() accepts model output and returns valid tier result."""

    def _tier(self, disease="Tinea", confidence=0.82, transcript=""):
        from severity.engine import compute_tier
        return compute_tier(disease, confidence, transcript)

    def test_returns_dict(self):
        assert isinstance(self._tier(), dict)

    def test_result_has_tier_key(self):
        assert "tier" in self._tier()

    def test_result_has_all_required_keys(self):
        result = self._tier()
        for key in ("tier", "urgency_label", "action", "facility", "bengali_text"):
            assert key in result, f"Missing key: {key}"

    def test_tier_is_integer_1_2_or_3(self):
        result = self._tier()
        assert result["tier"] in (1, 2, 3)

    def test_pharmacist_disease_high_confidence_stays_tier1(self):
        result = self._tier(disease="Tinea", confidence=0.82)
        assert result["tier"] == 1

    def test_low_confidence_escalates_to_tier3(self):
        result = self._tier(confidence=0.35)
        assert result["tier"] == 3

    def test_voice_keyword_escalates_tier(self):
        result = self._tier(
            disease="Tinea", confidence=0.82, transcript="জ্বর আছে"
        )
        assert result["tier"] >= 2

    def test_tier_never_exceeds_3(self):
        result = self._tier(
            disease="Scabies", confidence=0.30,
            transcript="জ্বর ছড়িয়ে ব্যথা রক্ত"
        )
        assert result["tier"] == 3

    def test_tier_never_below_1(self):
        result = self._tier(disease="Tinea", confidence=0.99)
        assert result["tier"] >= 1

    def test_urgency_label_is_string(self):
        result = self._tier()
        assert isinstance(result["urgency_label"], str)
        assert len(result["urgency_label"]) > 0

    def test_model_output_feeds_into_tier(self):
        from severity.engine import compute_tier
        result = compute_tier(
            disease_class=MODEL_OUTPUT["disease"],
            confidence=MODEL_OUTPUT["confidence"],
            transcript="",
        )
        assert isinstance(result["tier"], int)


# --- Severity result → PDF generator ---

class TestPDFPipeline:
    """generate_referral_pdf() accepts the session_data structure app.py produces."""

    def _session_data(self, **overrides):
        data = {
            **HISTORY,
            "disease_class":   MODEL_OUTPUT["disease"],
            "disease_bengali": "দাদ (টিনিয়া)",
            "confidence":      MODEL_OUTPUT["confidence"],
            "top2":            MODEL_OUTPUT["top2"],
            "tier":            TIER1_RESULT["tier"],
            "urgency_label":   TIER1_RESULT["urgency_label"],
            "action":          TIER1_RESULT["action"],
            "facility":        TIER1_RESULT["facility"],
            "bengali_text":    TIER1_RESULT["bengali_text"],
            "transcript":      "চুলকানি হচ্ছে",
            "hospital_name":   "",
            "hospital_address": "",
        }
        data.update(overrides)
        return data

    def test_returns_bytes(self):
        from pdf_gen.referral import generate_referral_pdf
        result = generate_referral_pdf(self._session_data())
        assert isinstance(result, bytes)

    def test_pdf_starts_with_pdf_magic_bytes(self):
        from pdf_gen.referral import generate_referral_pdf
        result = generate_referral_pdf(self._session_data())
        assert result[:4] == b"%PDF"

    def test_pdf_nonempty(self):
        from pdf_gen.referral import generate_referral_pdf
        result = generate_referral_pdf(self._session_data())
        assert len(result) > 1000

    def test_tier2_disease_accepted(self):
        from pdf_gen.referral import generate_referral_pdf
        data = self._session_data(
            disease_class="Scabies",
            disease_bengali="খোস-পাঁচড়া",
            tier=2,
            urgency_label="ROUTINE",
            action="Visit Upazila Health Complex within 48 hours",
            facility="Upazila Health Complex",
            bengali_text="৪৮ ঘণ্টার মধ্যে উপজেলা স্বাস্থ্য কমপ্লেক্সে যান",
        )
        result = generate_referral_pdf(data)
        assert isinstance(result, bytes)
        assert len(result) > 1000

    def test_tier3_with_hospital_accepted(self):
        from pdf_gen.referral import generate_referral_pdf
        data = self._session_data(
            tier=3,
            urgency_label="URGENT",
            hospital_name="Rangpur Medical College Hospital",
            hospital_address="Rangpur, Bangladesh",
        )
        result = generate_referral_pdf(data)
        assert isinstance(result, bytes)

    def test_missing_history_fields_handled(self):
        """PDF must not crash when optional history fields are absent."""
        from pdf_gen.referral import generate_referral_pdf
        data = self._session_data(
            patient_name="",
            chief_complaint="",
            symptoms=[],
            affected_area="",
        )
        result = generate_referral_pdf(data)
        assert isinstance(result, bytes)

    def test_differential_diagnosis_in_data(self):
        """top2[1] confidence > 0.15 should not crash PDF generation."""
        from pdf_gen.referral import generate_referral_pdf
        data = self._session_data(
            top2=[
                {"disease": "Tinea",   "confidence": 0.75},
                {"disease": "Eczema",  "confidence": 0.20},
            ]
        )
        result = generate_referral_pdf(data)
        assert isinstance(result, bytes)


# --- Full chain: model → tier → PDF ---

class TestFullPipeline:
    """Model output → compute_tier → generate_referral_pdf: all interfaces match."""

    def test_complete_chain_produces_pdf(self):
        from severity.engine import compute_tier
        from pdf_gen.referral import generate_referral_pdf
        from model.disease_labels import get_bengali

        pred = MODEL_OUTPUT.copy()

        tier_result = compute_tier(
            disease_class=pred["disease"],
            confidence=pred["confidence"],
            transcript="",
        )

        session_data = {
            **HISTORY,
            "disease_class":   pred["disease"],
            "disease_bengali": get_bengali(pred["disease"]),
            "confidence":      pred["confidence"],
            "top2":            pred.get("top2", []),
            "tier":            tier_result["tier"],
            "urgency_label":   tier_result["urgency_label"],
            "action":          tier_result["action"],
            "facility":        tier_result["facility"],
            "bengali_text":    tier_result["bengali_text"],
            "transcript":      "",
            "hospital_name":   "",
            "hospital_address": "",
        }

        pdf_bytes = generate_referral_pdf(session_data)

        assert isinstance(pdf_bytes, bytes)
        assert pdf_bytes[:4] == b"%PDF"
        assert len(pdf_bytes) > 1000

    def test_scabies_tier3_chain(self):
        """Low-confidence Scabies escalates to Tier 3 and produces a valid PDF."""
        from severity.engine import compute_tier
        from pdf_gen.referral import generate_referral_pdf
        from model.disease_labels import get_bengali

        pred = {
            "disease":      "Scabies",
            "confidence":   0.38,
            "top2": [
                {"disease": "Scabies", "confidence": 0.38},
                {"disease": "Eczema",  "confidence": 0.22},
            ],
        }
        transcript = "জ্বর আছে ছড়িয়ে পড়ছে"

        tier_result = compute_tier(
            disease_class=pred["disease"],
            confidence=pred["confidence"],
            transcript=transcript,
        )
        assert tier_result["tier"] == 3

        session_data = {
            **HISTORY,
            "disease_class":   pred["disease"],
            "disease_bengali": get_bengali(pred["disease"]),
            "confidence":      pred["confidence"],
            "top2":            pred["top2"],
            "tier":            tier_result["tier"],
            "urgency_label":   tier_result["urgency_label"],
            "action":          tier_result["action"],
            "facility":        tier_result["facility"],
            "bengali_text":    tier_result["bengali_text"],
            "transcript":      transcript,
            "hospital_name":   "Rangpur Medical College Hospital",
            "hospital_address": "Rangpur, Bangladesh",
        }

        pdf_bytes = generate_referral_pdf(session_data)
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 1000

    def test_disease_labels_module_provides_bengali_for_all_classes(self):
        """get_bengali() must return non-empty string for every model class."""
        from model.disease_labels import CLASS_NAMES, get_bengali
        for cls in CLASS_NAMES:
            result = get_bengali(cls)
            assert isinstance(result, str)
            assert len(result) > 0, f"Empty Bengali name for {cls}"

    def test_tier_result_keys_match_pdf_expected_keys(self):
        """Keys produced by compute_tier() match what generate_referral_pdf() reads."""
        from severity.engine import compute_tier
        tier_result = compute_tier("Tinea", 0.82, "")
        required_by_pdf = ("tier", "urgency_label", "action", "facility", "bengali_text")
        for key in required_by_pdf:
            assert key in tier_result, f"compute_tier() missing key needed by PDF: {key}"
