import numpy as np
import torch
from pytorch_grad_cam import GradCAMPlusPlus
from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget
from pytorch_grad_cam.utils.image import show_cam_on_image

from model.bd_skinnet import BDSkinNet, IMAGE_SIZE


def _get_target_layer(model: BDSkinNet):
    assert hasattr(model, "cbam_modules") and len(model.cbam_modules) > 0, \
        "BD-SkinNet is missing cbam_modules — architecture may have changed"
    return model.cbam_modules[-1].spatial_attn.conv


def compute_coverage_pct(heatmap: np.ndarray, threshold: float = 0.5) -> float:
    """
    Returns the percentage of heatmap pixels above threshold.
    High coverage means the lesion is widespread — used as Signal 3 in severity engine.
    """
    assert heatmap.ndim == 2, f"Expected 2D heatmap, got shape {heatmap.shape}"
    activated = (heatmap >= threshold).sum()
    return float(activated / heatmap.size * 100.0)


def compute_gradcam(
    model: BDSkinNet,
    image_tensor: torch.Tensor,
    target_class: int = None,
    threshold: float = 0.5,
) -> dict:
    """
    Runs GradCAM++ on a single image tensor.

    Args:
        model:        BDSkinNet instance (eval mode, any weights)
        image_tensor: shape (1, 3, H, W) or (3, H, W), values in [0, 1] or normalized
        target_class: class index to explain; if None uses predicted class
        threshold:    coverage threshold passed to compute_coverage_pct

    Returns:
        {
            heatmap:      np.ndarray shape (224, 224), values in [0, 1]
            coverage_pct: float, percentage of heatmap >= threshold
            overlay:      np.ndarray shape (224, 224, 3) uint8, heatmap on image
            target_class: int, class index that was explained
        }
    """
    model.eval()

    if image_tensor.ndim == 3:
        image_tensor = image_tensor.unsqueeze(0)

    target_layer = [_get_target_layer(model)]

    if target_class is None:
        with torch.no_grad():
            logits = model(image_tensor)
        target_class = int(logits.argmax(dim=1).item())

    targets = [ClassifierOutputTarget(target_class)]

    with GradCAMPlusPlus(model=model, target_layers=target_layer) as cam:
        grayscale_cam = cam(input_tensor=image_tensor, targets=targets)[0]

    heatmap = grayscale_cam  # shape (H, W), values in [0, 1]
    coverage_pct = compute_coverage_pct(heatmap, threshold=threshold)

    # Build RGB overlay for display — denormalize image to [0, 1]
    img_np = image_tensor.squeeze(0).permute(1, 2, 0).cpu().numpy()
    img_np = np.clip(img_np, 0, 1).astype(np.float32)
    overlay = show_cam_on_image(img_np, heatmap, use_rgb=True)

    return {
        "heatmap":      heatmap,
        "coverage_pct": coverage_pct,
        "overlay":      overlay,
        "target_class": target_class,
    }
