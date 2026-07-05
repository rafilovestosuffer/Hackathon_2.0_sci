import json
from unittest.mock import MagicMock, patch

import pytest

from voice.pipeline import (
    _empty_history,
    _validate_fields,
    extract_patient_history,
)

_FULL_RESPONSE = {
    "chief_complaint": "চুলকানি এবং লাল দাগ",
    "symptoms": ["চুলকানি", "লালভাব", "খোসা"],
    "affected_area": "বাহু",
    "duration": "দুই সপ্তাহ",
    "progression": "ধীরে ছড়িয়ে পড়ছে",
    "previous_treatment": "কোনোটি নয়",
    "associated_symptoms": ["জ্বর নেই"],
    "patient_name": "রহিম উদ্দিন",
    "patient_age": "৩৫",
}


def _make_client_mock(json_text: str):
    mock_resp = MagicMock()
    mock_resp.text = json_text
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_resp
    return mock_client


# --- _empty_history & _validate_fields ---

class TestHelpers:
    def test_empty_history_has_all_keys(self):
        h = _empty_history()
        for key in ("chief_complaint", "symptoms", "affected_area", "duration",
                    "progression", "previous_treatment", "associated_symptoms",
                    "patient_name", "patient_age"):
            assert key in h

    def test_empty_history_lists_are_lists(self):
        h = _empty_history()
        assert isinstance(h["symptoms"], list)
        assert isinstance(h["associated_symptoms"], list)

    def test_validate_fills_missing_keys(self):
        result = _validate_fields({"chief_complaint": "rash"})
        assert result["symptoms"] == []
        assert result["patient_name"] == ""

    def test_validate_coerces_list_field(self):
        result = _validate_fields({"symptoms": "itching"})
        assert isinstance(result["symptoms"], list)

    def test_validate_coerces_str_field(self):
        result = _validate_fields({"patient_age": 35})
        assert isinstance(result["patient_age"], str)


# --- extract_patient_history ---

class TestExtractPatientHistory:
    def test_returns_dict(self):
        with patch("voice.pipeline._get_gemini_client",
                   return_value=_make_client_mock(json.dumps(_FULL_RESPONSE))):
            result = extract_patient_history("আমার হাতে চুলকানি")
        assert isinstance(result, dict)

    def test_all_nine_keys_present(self):
        with patch("voice.pipeline._get_gemini_client",
                   return_value=_make_client_mock(json.dumps(_FULL_RESPONSE))):
            result = extract_patient_history("আমার হাতে চুলকানি")
        for key in ("chief_complaint", "symptoms", "affected_area", "duration",
                    "progression", "previous_treatment", "associated_symptoms",
                    "patient_name", "patient_age"):
            assert key in result, f"missing key: {key}"

    def test_symptoms_is_list(self):
        with patch("voice.pipeline._get_gemini_client",
                   return_value=_make_client_mock(json.dumps(_FULL_RESPONSE))):
            result = extract_patient_history("test")
        assert isinstance(result["symptoms"], list)
        assert isinstance(result["associated_symptoms"], list)

    def test_valid_json_parsed_correctly(self):
        with patch("voice.pipeline._get_gemini_client",
                   return_value=_make_client_mock(json.dumps(_FULL_RESPONSE))):
            result = extract_patient_history("রহিমের হাতে চুলকানি")
        assert result["patient_name"] == "রহিম উদ্দিন"
        assert result["duration"] == "দুই সপ্তাহ"

    def test_json_in_fences_handled(self):
        fenced = f"```json\n{json.dumps(_FULL_RESPONSE)}\n```"
        with patch("voice.pipeline._get_gemini_client",
                   return_value=_make_client_mock(fenced)):
            result = extract_patient_history("test transcript")
        assert result["chief_complaint"] == "চুলকানি এবং লাল দাগ"

    def test_invalid_json_returns_empty_history(self):
        with patch("voice.pipeline._get_gemini_client",
                   return_value=_make_client_mock("this is not json")):
            result = extract_patient_history("test")
        assert result == _empty_history()

    def test_api_exception_retries_and_returns_empty(self):
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = Exception("API error")
        with patch("voice.pipeline._get_gemini_client", return_value=mock_client):
            result = extract_patient_history("test")
        assert result == _empty_history()
        assert mock_client.models.generate_content.call_count == 3

    def test_missing_keys_filled_with_defaults(self):
        partial = {"chief_complaint": "rash", "symptoms": ["itching"]}
        with patch("voice.pipeline._get_gemini_client",
                   return_value=_make_client_mock(json.dumps(partial))):
            result = extract_patient_history("test")
        assert result["patient_name"] == ""
        assert result["duration"] == ""
        assert result["associated_symptoms"] == []

    def test_empty_transcript_returns_empty_history(self):
        result = extract_patient_history("")
        assert result == _empty_history()

    def test_patient_name_and_age_are_strings(self):
        with patch("voice.pipeline._get_gemini_client",
                   return_value=_make_client_mock(json.dumps(_FULL_RESPONSE))):
            result = extract_patient_history("test")
        assert isinstance(result["patient_name"], str)
        assert isinstance(result["patient_age"], str)
