"""
tests/test_consultation_summary.py — Post-Consultation Summary PDF Tests

4 tests covering: full transcript, empty transcript fallback, null medicines,
and missing session_state fields. Gemini calls are mocked throughout.
"""
import json
from unittest.mock import MagicMock, patch

import pytest

from pdf_gen.consultation_summary import generate_consultation_summary_pdf

# ── Mock helpers ──────────────────────────────────────────────────────────────

_FULL_DATA = {
    "diagnosis_confirmed": "Tinea Corporis",
    "prescribed_medicines": [
        {
            "name": "Clotrimazole cream",
            "name_bn": "ক্লোট্রিমাজল ক্রিম",
            "dose": "Apply thin layer",
            "frequency": "Twice daily",
            "duration": "14 days",
            "instructions": "Apply after washing and drying the area",
        }
    ],
    "dos": [
        "Keep the affected area clean and dry",
        "Wash clothes and bedsheets in hot water",
    ],
    "donts": [
        "Do not share towels or clothing",
        "Avoid tight clothing on the affected area",
    ],
    "diet_instructions": ["Reduce sugar intake"],
    "activity_restrictions": ["Avoid swimming pools for 2 weeks"],
    "follow_up_date": "2026-06-06",
    "follow_up_condition": "If rash spreads or does not improve in 7 days",
    "warning_signs": ["Rapidly spreading redness", "Fever above 102F"],
    "warning_signs_bn": ["দ্রুত ছড়িয়ে পড়া লালভাব", "জ্বর ১০২°F এর উপরে"],
    "doctor_notes": "Avoid DermNet self-diagnosis. Return if no improvement.",
    "consultation_date": "2026-05-23",
    "consultation_duration": "30 minutes",
}

_FULL_SESSION = {
    "prediction": {
        "disease": "Tinea",
        "confidence": 0.82,
        "top2": [
            {"disease": "Tinea", "confidence": 0.82},
            {"disease": "Contact_Dermatitis", "confidence": 0.11},
        ],
        "heatmap": None,
        "coverage_pct": 22.5,
    },
    "history": {
        "chief_complaint": "Itching and ring-shaped rash",
        "symptoms": ["itching", "redness", "ring-shaped rash"],
        "affected_area": "arm",
        "duration": "2 weeks",
        "progression": "spreading",
        "previous_treatment": "none",
        "associated_symptoms": [],
        "patient_name": "Rahim Uddin",
        "patient_age": "35",
    },
    "tier_result": {"tier": 1, "urgency_label": "NON-URGENT"},
}


def _make_gemini_mock(data: dict):
    """Return a mock Gemini client that responds with the given dict as JSON."""
    mock_resp = MagicMock()
    mock_resp.text = json.dumps(data)
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_resp
    return mock_client


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestFullTranscript:
    def test_full_transcript_generates_pdf(self):
        """Full Bengali transcript with valid Gemini response produces a valid PDF."""
        transcript = (
            "ডাক্তার: আপনার সমস্যা কী? রোগী: আমার হাতে চুলকানি। "
            "ডাক্তার: এটি দাদ রোগ। ক্লোট্রিমাজল ক্রিম দিনে দুইবার লাগান ১৪ দিন।"
        )
        with patch(
            "pdf_gen.consultation_summary._get_gemini_client",
            return_value=_make_gemini_mock(_FULL_DATA),
        ):
            result = generate_consultation_summary_pdf(
                consultation_transcript=transcript,
                session_state=_FULL_SESSION,
                consultation_duration_minutes=30,
            )

        assert isinstance(result, bytes), "Output should be bytes"
        assert len(result) > 1000, "PDF too small — likely empty"
        assert result[:4] == b"%PDF", "Output is not a valid PDF"


class TestEmptyTranscriptFallback:
    def test_empty_transcript_returns_fallback_pdf(self):
        """Empty transcript skips Gemini and returns a safe fallback PDF."""
        result = generate_consultation_summary_pdf(
            consultation_transcript="",
            session_state=_FULL_SESSION,
            consultation_duration_minutes=30,
        )
        assert isinstance(result, bytes)
        assert result[:4] == b"%PDF", "Fallback output is not a valid PDF"
        assert len(result) > 500

    def test_gemini_all_retries_fail_returns_fallback(self):
        """When Gemini fails 3 times, a fallback PDF is returned without raising."""
        failing_client = MagicMock()
        failing_client.models.generate_content.side_effect = RuntimeError("API error")

        with patch(
            "pdf_gen.consultation_summary._get_gemini_client",
            return_value=failing_client,
        ):
            result = generate_consultation_summary_pdf(
                consultation_transcript="Doctor said something",
                session_state=_FULL_SESSION,
                consultation_duration_minutes=60,
            )

        assert isinstance(result, bytes)
        assert result[:4] == b"%PDF"


class TestNullMedicinesHandled:
    def test_null_medicines_does_not_crash(self):
        """Gemini response with null/empty prescribed_medicines generates PDF without KeyError."""
        data_no_meds = dict(_FULL_DATA)
        data_no_meds["prescribed_medicines"] = []

        with patch(
            "pdf_gen.consultation_summary._get_gemini_client",
            return_value=_make_gemini_mock(data_no_meds),
        ):
            result = generate_consultation_summary_pdf(
                consultation_transcript="Doctor said: rest and drink water.",
                session_state=_FULL_SESSION,
                consultation_duration_minutes=30,
            )

        assert isinstance(result, bytes)
        assert result[:4] == b"%PDF"

    def test_none_medicines_field_does_not_crash(self):
        """Gemini response with prescribed_medicines: null generates PDF without KeyError."""
        data_null_meds = dict(_FULL_DATA)
        data_null_meds["prescribed_medicines"] = None

        with patch(
            "pdf_gen.consultation_summary._get_gemini_client",
            return_value=_make_gemini_mock(data_null_meds),
        ):
            result = generate_consultation_summary_pdf(
                consultation_transcript="No medicines prescribed.",
                session_state=_FULL_SESSION,
                consultation_duration_minutes=30,
            )

        assert isinstance(result, bytes)
        assert result[:4] == b"%PDF"


class TestMissingSessionStateFields:
    def test_minimal_session_state_does_not_crash(self):
        """session_state with only disease set — all other fields use safe fallbacks."""
        minimal_state = {
            "prediction": {"disease": "Tinea", "confidence": 0.8},
        }
        with patch(
            "pdf_gen.consultation_summary._get_gemini_client",
            return_value=_make_gemini_mock(_FULL_DATA),
        ):
            result = generate_consultation_summary_pdf(
                consultation_transcript="Doctor: apply cream twice daily.",
                session_state=minimal_state,
                consultation_duration_minutes=30,
            )

        assert isinstance(result, bytes)
        assert result[:4] == b"%PDF"

    def test_completely_empty_session_state_does_not_crash(self):
        """Completely empty session_state — every field uses fallback without crashing."""
        with patch(
            "pdf_gen.consultation_summary._get_gemini_client",
            return_value=_make_gemini_mock(_FULL_DATA),
        ):
            result = generate_consultation_summary_pdf(
                consultation_transcript="Doctor: take rest.",
                session_state={},
                consultation_duration_minutes=30,
            )

        assert isinstance(result, bytes)
        assert result[:4] == b"%PDF"
