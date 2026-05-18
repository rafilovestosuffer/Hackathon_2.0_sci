"""
One-time script: exports bd_skinnet_best.pth → bd_skinnet_int8.pth
Run on a machine with the trained checkpoint before deploying to HF Spaces.

Usage:
    python model/export_int8.py --checkpoint model/checkpoints/bd_skinnet_best.pth
"""

import argparse
import torch
from pathlib import Path
from model.bd_skinnet import BDSkinNet, IMAGE_SIZE
from model.disease_labels import NUM_CLASSES


def export_int8(checkpoint_path: str, output_path: str = None):
    if output_path is None:
        output_path = str(Path(checkpoint_path).parent / "bd_skinnet_int8.pth")

    print(f"Loading checkpoint: {checkpoint_path}")
    ckpt  = torch.load(checkpoint_path, map_location="cpu")
    model = BDSkinNet(num_classes=NUM_CLASSES)
    model.load_state_dict(ckpt.get("model_state", ckpt))
    model.eval()

    fp32_params = sum(p.numel() for p in model.parameters())
    print(f"FP32 parameters: {fp32_params:,}")

    # Dynamic INT8 quantization — no calibration data needed
    # Targets Linear layers (classification head + CBAM MLP)
    quantized = torch.quantization.quantize_dynamic(
        model,
        qconfig_spec={torch.nn.Linear},
        dtype=torch.qint8,
    )

    # Verify output shape unchanged
    dummy = torch.randn(1, 3, IMAGE_SIZE, IMAGE_SIZE)
    with torch.no_grad():
        out = quantized(dummy)
    assert out.shape == (1, NUM_CLASSES), f"Shape mismatch: {out.shape}"
    print(f"INT8 output shape: {out.shape} — OK")

    torch.save({
        "model_state":  quantized.state_dict(),
        "num_classes":  NUM_CLASSES,
        "quantized":    True,
        "val_f1":       ckpt.get("val_f1", None),
        "epoch":        ckpt.get("epoch", None),
    }, output_path)

    in_mb  = Path(checkpoint_path).stat().st_size / 1e6
    out_mb = Path(output_path).stat().st_size / 1e6
    print(f"Saved INT8 model: {output_path}")
    print(f"Size: {in_mb:.1f} MB → {out_mb:.1f} MB ({100*(1-out_mb/in_mb):.0f}% reduction)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", required=True,
                        help="Path to bd_skinnet_best.pth")
    parser.add_argument("--output", default=None,
                        help="Output path (default: same dir as checkpoint)")
    args = parser.parse_args()
    export_int8(args.checkpoint, args.output)
