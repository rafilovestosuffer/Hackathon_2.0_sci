"""
model/service.py — the single BD-SkinNet inference entry point.

Used by the Streamlit app, the WhatsApp/Telegram router and the /api case
endpoint, so every channel runs the same checkpoint. If the model cannot be
loaded or inference fails, the result carries available=False and NO
prediction — callers must show a "model unavailable" message, never a
made-up class.
"""

from __future__ import annotations

import io
import logging
import os
import threading
from typing import Optional

import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

HF_REPO     = os.environ.get("BD_SKINNET_REPO", "rafilovestosuffer/bd-skinnet")
HF_FILENAME = os.environ.get("BD_SKINNET_FILE", "bd_skinnet_int8.pth")

UNAVAILABLE_EN = "The AI model is not available right now. Please try again in a minute."
UNAVAILABLE_BN = "এআই মডেল এই মুহূর্তে চালু নেই। এক মিনিট পরে আবার চেষ্টা করুন।"

_lock = threading.Lock()
_model = None
_load_error: Optional[str] = None


def get_model():
    """Load the INT8 checkpoint once per process (thread-safe). Returns None on failure."""
    global _model, _load_error
    if _model is not None:
        return _model
    with _lock:
        if _model is not None:
            return _model
        try:
            from huggingface_hub import hf_hub_download
            from model.bd_skinnet import load_model
            ckpt_path = hf_hub_download(repo_id=HF_REPO, filename=HF_FILENAME)
            _model = load_model(ckpt_path)
            _load_error = None
            logger.info("BD-SkinNet loaded from %s/%s", HF_REPO, HF_FILENAME)
        except Exception as exc:
            _load_error = repr(exc)
            logger.warning("BD-SkinNet load failed: %s", exc)
            return None
    return _model


def load_error() -> Optional[str]:
    return _load_error


def warm_up_async() -> None:
    """Start loading the model in a background thread (used at server startup)."""
    threading.Thread(target=get_model, daemon=True).start()


def _to_rgb_array(image) -> np.ndarray:
    if isinstance(image, (bytes, bytearray)):
        image = Image.open(io.BytesIO(image))
    if isinstance(image, Image.Image):
        return np.array(image.convert("RGB"))
    if isinstance(image, np.ndarray):
        return image
    raise TypeError(f"unsupported image type: {type(image).__name__}")


def unavailable() -> dict:
    return {"available": False, "disease": None, "confidence": None, "top2": []}


def run_inference(image) -> dict:
    """
    Args:
        image: PIL.Image, raw image bytes, or an RGB np.ndarray.
    Returns:
        {"available": True,  "disease", "confidence", "top2": [{disease, confidence}]}
        or {"available": False, ...} when the model can't run.
    """
    model = get_model()
    if model is None:
        return unavailable()
    try:
        from model.bd_skinnet import predict
        arr = _to_rgb_array(image)
        result = predict(model, arr)
    except Exception as exc:
        logger.warning("BD-SkinNet inference failed: %s", exc)
        return unavailable()
    return {
        "available":  True,
        "disease":    result["disease_class"],
        "confidence": result["confidence"],
        "top2": [
            {"disease": t["class"], "confidence": t["confidence"]}
            for t in result["top2"]
        ],
    }
