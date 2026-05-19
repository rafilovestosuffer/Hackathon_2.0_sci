import numpy as np
import pytest
from pdf_gen.referral import generate_referral_pdf


def _base_session(**overrides):
    data = {
        "patient_name": "Rahim Uddin",
        "patient_age": "35",
        "chief_complaint": "Spreading rash on forearm",
        "symptoms": ["itching", "redness", "scaling"],
        "associated_symptoms": ["fever", "pain"],
        "affected_area": "Forearm",
        "duration": "2 weeks",
        "progression": "Slowly spreading",
        "previous_treatment": "None",
        "heatmap": np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8),
        "coverage_pct": 22.5,
        "disease_class": "Tinea",
        "disease_bengali": "দাদ (টিনিয়া)",
        "confidence": 0.87,
        "top2": [
            {"class": "Tinea", "confidence": 0.87},
            {"class": "Eczema", "confidence": 0.10},
        ],
        "tier": 1,
        "urgency_label": "NON-URGENT",
        "action": "Consult local pharmacist within 3-5 days",
        "facility": "Local Pharmacy",
        "bengali_text": "৩-৫ দিনের মধ্যে নিকটস্থ ফার্মাসিস্টের সাথে পরামর্শ করুন",
        "hospital_name": None,
        "hospital_address": None,
    }
    data.update(overrides)
    return data


class TestPdfGeneration:
    def test_returns_bytes(self):
        result = generate_referral_pdf(_base_session())
        assert isinstance(result, bytes)

    def test_size_greater_than_zero(self):
        result = generate_referral_pdf(_base_session())
        assert len(result) > 0

    def test_is_valid_pdf_header(self):
        result = generate_referral_pdf(_base_session())
        assert result[:4] == b"%PDF"

    def test_tier1_non_urgent(self):
        data = _base_session(tier=1, urgency_label="NON-URGENT",
                             action="Consult local pharmacist within 3-5 days",
                             facility="Local Pharmacy")
        result = generate_referral_pdf(data)
        assert isinstance(result, bytes) and len(result) > 0

    def test_tier2_routine(self):
        data = _base_session(
            tier=2,
            urgency_label="ROUTINE",
            action="Visit Upazila Health Complex within 48 hours",
            facility="Upazila Health Complex",
            bengali_text="৪৮ ঘণ্টার মধ্যে উপজেলা স্বাস্থ্য কমপ্লেক্সে যান",
        )
        result = generate_referral_pdf(data)
        assert isinstance(result, bytes) and len(result) > 0

    def test_tier3_with_hospital(self):
        data = _base_session(
            tier=3,
            urgency_label="URGENT",
            action="Seek emergency care TODAY at District Hospital",
            facility="District Hospital",
            bengali_text="আজই জেলা হাসপাতালে জরুরি চিকিৎসা নিন",
            hospital_name="Rangpur Medical College Hospital",
            hospital_address="Rangpur Sadar, Rangpur",
        )
        result = generate_referral_pdf(data)
        assert isinstance(result, bytes) and len(result) > 0

    def test_heatmap_none_no_crash(self):
        data = _base_session(heatmap=None)
        result = generate_referral_pdf(data)
        assert isinstance(result, bytes) and len(result) > 0

    def test_differential_above_threshold(self):
        data = _base_session(top2=[
            {"class": "Tinea", "confidence": 0.75},
            {"class": "Eczema", "confidence": 0.20},
        ])
        result = generate_referral_pdf(data)
        assert isinstance(result, bytes) and len(result) > 0

    def test_differential_below_threshold(self):
        data = _base_session(top2=[
            {"class": "Tinea", "confidence": 0.87},
            {"class": "Eczema", "confidence": 0.10},
        ])
        result = generate_referral_pdf(data)
        assert isinstance(result, bytes) and len(result) > 0

    def test_empty_symptoms_list(self):
        data = _base_session(symptoms=[])
        result = generate_referral_pdf(data)
        assert isinstance(result, bytes) and len(result) > 0

    def test_associated_symptoms_included(self):
        data = _base_session(associated_symptoms=["জ্বর", "ব্যথা"])
        result = generate_referral_pdf(data)
        assert isinstance(result, bytes) and len(result) > 0

    def test_top2_disease_key_works(self):
        """top2 dicts with 'disease' key (from checkpoint integration) render correctly."""
        data = _base_session(top2=[
            {"disease": "Tinea", "confidence": 0.80},
            {"disease": "Eczema", "confidence": 0.18},
        ])
        result = generate_referral_pdf(data)
        assert isinstance(result, bytes) and len(result) > 0

    def test_missing_optional_fields_no_crash(self):
        minimal = {
            "patient_name": "Test",
            "patient_age": "25",
            "tier": 1,
            "urgency_label": "NON-URGENT",
            "action": "See pharmacist",
            "facility": "Pharmacy",
            "bengali_text": "ফার্মাসিস্ট দেখুন",
        }
        result = generate_referral_pdf(minimal)
        assert isinstance(result, bytes) and len(result) > 0
