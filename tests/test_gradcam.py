"""
Tests for model/gradcam.py

Run with:  pytest tests/test_gradcam.py -v

No checkpoint required — all tests use randomly initialised BDSkinNet weights.
"""

import numpy as np
import torch
import pytest

from model.bd_skinnet import BDSkinNet, IMAGE_SIZE
from model.gradcam import compute_gradcam, compute_coverage_pct


@pytest.fixture(scope="module")
def model():
    m = BDSkinNet()
    m.eval()
    return m


@pytest.fixture(scope="module")
def dummy_tensor():
    torch.manual_seed(0)
    return torch.rand(1, 3, IMAGE_SIZE, IMAGE_SIZE)


# ── compute_gradcam tests ─────────────────────────────────────────────────────

class TestComputeGradcam:

    def test_heatmap_shape(self, model, dummy_tensor):
        result = compute_gradcam(model, dummy_tensor)
        assert result["heatmap"].shape == (IMAGE_SIZE, IMAGE_SIZE), (
            f"Expected heatmap shape ({IMAGE_SIZE}, {IMAGE_SIZE}), "
            f"got {result['heatmap'].shape}"
        )

    def test_heatmap_value_range(self, model, dummy_tensor):
        result = compute_gradcam(model, dummy_tensor)
        heatmap = result["heatmap"]
        assert heatmap.min() >= 0.0, f"Heatmap min {heatmap.min():.4f} < 0"
        assert heatmap.max() <= 1.0, f"Heatmap max {heatmap.max():.4f} > 1"

    def test_coverage_pct_range(self, model, dummy_tensor):
        result = compute_gradcam(model, dummy_tensor)
        cov = result["coverage_pct"]
        assert 0.0 <= cov <= 100.0, (
            f"coverage_pct {cov:.2f} outside valid range [0, 100]"
        )

    def test_overlay_shape(self, model, dummy_tensor):
        result = compute_gradcam(model, dummy_tensor)
        assert result["overlay"].shape == (IMAGE_SIZE, IMAGE_SIZE, 3), (
            f"Expected overlay shape ({IMAGE_SIZE}, {IMAGE_SIZE}, 3), "
            f"got {result['overlay'].shape}"
        )

    def test_target_class_returned(self, model, dummy_tensor):
        result = compute_gradcam(model, dummy_tensor, target_class=2)
        assert result["target_class"] == 2

    def test_unbatched_input_accepted(self, model):
        tensor_3d = torch.rand(3, IMAGE_SIZE, IMAGE_SIZE)
        result = compute_gradcam(model, tensor_3d)
        assert result["heatmap"].shape == (IMAGE_SIZE, IMAGE_SIZE)

    def test_returns_required_keys(self, model, dummy_tensor):
        result = compute_gradcam(model, dummy_tensor)
        for key in ("heatmap", "coverage_pct", "overlay", "target_class"):
            assert key in result, f"Missing key: {key}"


# ── compute_coverage_pct tests ────────────────────────────────────────────────

class TestComputeCoveragePct:

    def test_all_zeros_gives_zero(self):
        heatmap = np.zeros((IMAGE_SIZE, IMAGE_SIZE))
        assert compute_coverage_pct(heatmap) == 0.0

    def test_all_ones_gives_hundred(self):
        heatmap = np.ones((IMAGE_SIZE, IMAGE_SIZE))
        assert compute_coverage_pct(heatmap) == 100.0

    def test_half_activated(self):
        heatmap = np.zeros((IMAGE_SIZE, IMAGE_SIZE))
        heatmap[:IMAGE_SIZE // 2, :] = 1.0
        cov = compute_coverage_pct(heatmap)
        assert abs(cov - 50.0) < 0.1, f"Expected ~50.0, got {cov:.2f}"

    def test_custom_threshold(self):
        heatmap = np.full((IMAGE_SIZE, IMAGE_SIZE), 0.6)
        assert compute_coverage_pct(heatmap, threshold=0.5) == 100.0
        assert compute_coverage_pct(heatmap, threshold=0.7) == 0.0

    def test_output_type_is_float(self):
        heatmap = np.random.rand(IMAGE_SIZE, IMAGE_SIZE)
        result = compute_coverage_pct(heatmap)
        assert isinstance(result, float)

    def test_severity_signal_3_threshold(self):
        """coverage_pct > 40.0 triggers Tier escalation — verify boundary."""
        heatmap = np.zeros((IMAGE_SIZE, IMAGE_SIZE))
        heatmap[:, : int(IMAGE_SIZE * 0.41)] = 1.0
        cov = compute_coverage_pct(heatmap)
        assert cov > 40.0, "Expected coverage above 40% to trigger Signal 3"
