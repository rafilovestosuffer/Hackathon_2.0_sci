"""model/service.py — the shared inference entry point never invents a result."""

import io
from unittest.mock import patch

import pytest
from PIL import Image

from model import service

pytestmark = pytest.mark.real_model_service


def _png_bytes() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (32, 32), (180, 120, 100)).save(buf, format="PNG")
    return buf.getvalue()


def test_unavailable_when_model_cannot_load():
    with patch.object(service, "get_model", return_value=None):
        out = service.run_inference(_png_bytes())
    assert out["available"] is False
    assert out["disease"] is None
    assert out["confidence"] is None
    assert out["top2"] == []


def test_unavailable_when_inference_raises():
    with patch.object(service, "get_model", return_value=object()), \
         patch("model.bd_skinnet.predict", side_effect=RuntimeError("boom")):
        out = service.run_inference(_png_bytes())
    assert out["available"] is False
    assert out["disease"] is None


def test_maps_predict_output_to_app_schema():
    fake = {
        "disease_class": "Scabies",
        "confidence": 0.55,
        "top2": [{"class": "Scabies", "confidence": 0.55},
                 {"class": "Eczema", "confidence": 0.30}],
    }
    with patch.object(service, "get_model", return_value=object()), \
         patch("model.bd_skinnet.predict", return_value=fake):
        out = service.run_inference(_png_bytes())
    assert out == {
        "available": True,
        "disease": "Scabies",
        "confidence": 0.55,
        "top2": [{"disease": "Scabies", "confidence": 0.55},
                 {"disease": "Eczema", "confidence": 0.30}],
    }


def test_accepts_pil_image():
    fake = {"disease_class": "Normal", "confidence": 0.9,
            "top2": [{"class": "Normal", "confidence": 0.9},
                     {"class": "Tinea", "confidence": 0.05}]}
    with patch.object(service, "get_model", return_value=object()), \
         patch("model.bd_skinnet.predict", return_value=fake) as p:
        out = service.run_inference(Image.new("RGB", (16, 16)))
    assert out["available"] is True
    assert p.call_args[0][1].shape == (16, 16, 3)


# --- model/bd_skinnet.load_model: labels come from the checkpoint ---

import torch


def test_load_model_uses_checkpoint_class_order(tmp_path):
    from model.bd_skinnet import BDSkinNet, load_model
    net = BDSkinNet(num_classes=3)
    ckpt = {"model_state": net.state_dict(), "num_classes": 3, "quantized": False,
            "class_to_idx": {"Tinea": 2, "Eczema": 0, "Scabies": 1}, "val_f1": 0.5}
    path = tmp_path / "ck.pth"
    torch.save(ckpt, path)
    model = load_model(str(path))
    assert model.class_names == ["Eczema", "Scabies", "Tinea"]
    assert model.checkpoint_meta == {"val_f1": 0.5}


def test_load_model_rejects_inconsistent_checkpoint(tmp_path):
    from model.bd_skinnet import BDSkinNet, load_model
    net = BDSkinNet(num_classes=3)
    ckpt = {"model_state": net.state_dict(), "num_classes": 3,
            "class_to_idx": {"A": 0, "B": 1}}
    path = tmp_path / "bad.pth"
    torch.save(ckpt, path)
    with pytest.raises(ValueError):
        load_model(str(path))
