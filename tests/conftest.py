"""Shared test fixtures.

model.service.run_inference is replaced with a fixed stub so tests never
download or run the 89 MB checkpoint. Tests that exercise the service itself
opt out with @pytest.mark.real_model_service.
"""

from unittest.mock import patch

import pytest

STUB_PREDICTION = {
    "available":  True,
    "disease":    "Tinea",
    "confidence": 0.82,
    "top2": [
        {"disease": "Tinea",              "confidence": 0.82},
        {"disease": "Contact_Dermatitis", "confidence": 0.11},
    ],
}


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "real_model_service: do not stub model.service.run_inference")


@pytest.fixture(autouse=True)
def stub_model_inference(request):
    if request.node.get_closest_marker("real_model_service"):
        yield None
        return
    with patch("model.service.run_inference",
               side_effect=lambda image: dict(STUB_PREDICTION)) as m:
        yield m
