import torch
import torch.nn as nn
import torch.nn.functional as F
import timm
import numpy as np
from PIL import Image
import albumentations as A
from albumentations.pytorch import ToTensorV2
import cv2

from model.disease_labels import CLASS_NAMES, NUM_CLASSES

IMAGE_SIZE = 224
MEAN = [0.485, 0.456, 0.406]
STD  = [0.229, 0.224, 0.225]

inference_transform = A.Compose([
    A.Resize(IMAGE_SIZE, IMAGE_SIZE),
    A.Normalize(mean=MEAN, std=STD),
    ToTensorV2(),
])


class ChannelAttention(nn.Module):
    def __init__(self, in_channels, reduction=16):
        super().__init__()
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        self.max_pool = nn.AdaptiveMaxPool2d(1)
        mid = max(1, in_channels // reduction)
        self.mlp = nn.Sequential(
            nn.Flatten(),
            nn.Linear(in_channels, mid, bias=False),
            nn.ReLU(inplace=True),
            nn.Linear(mid, in_channels, bias=False),
        )
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        avg_out = self.mlp(self.avg_pool(x))
        max_out = self.mlp(self.max_pool(x))
        scale   = self.sigmoid(avg_out + max_out)
        return x * scale.view(scale.size(0), scale.size(1), 1, 1)


class SpatialAttention(nn.Module):
    def __init__(self, kernel_size=7):
        super().__init__()
        self.conv    = nn.Conv2d(2, 1, kernel_size=kernel_size,
                                 padding=kernel_size // 2, bias=False)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        avg_out = torch.mean(x, dim=1, keepdim=True)
        max_out, _ = torch.max(x, dim=1, keepdim=True)
        spatial = torch.cat([avg_out, max_out], dim=1)
        return x * self.sigmoid(self.conv(spatial))


class CBAM(nn.Module):
    def __init__(self, in_channels, reduction=16, kernel_size=7):
        super().__init__()
        self.channel_attn = ChannelAttention(in_channels, reduction)
        self.spatial_attn  = SpatialAttention(kernel_size)

    def forward(self, x):
        x = self.channel_attn(x)
        x = self.spatial_attn(x)
        return x


class BDSkinNet(nn.Module):
    """
    Swin Transformer Base + CBAM attention on all 4 stages.
    Stage dims: [128, 256, 512, 1024] → concat 1920-d → classification head.
    GradCAM++ target: model.cbam_modules[-1].spatial_attn.conv
    """
    STAGE_DIMS = [128, 256, 512, 1024]

    def __init__(self, num_classes=NUM_CLASSES, dropout=0.4):
        super().__init__()
        self.swin = timm.create_model(
            "swin_base_patch4_window7_224",
            pretrained=False,
            features_only=True,
            out_indices=(0, 1, 2, 3),
        )
        self.cbam_modules = nn.ModuleList([
            CBAM(in_channels=dim) for dim in self.STAGE_DIMS
        ])
        self.gap     = nn.AdaptiveAvgPool2d(1)
        self.flatten = nn.Flatten()

        total_dim  = sum(self.STAGE_DIMS)  # 1920
        hidden_dim = 512

        self.head = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(total_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout / 2),
            nn.Linear(hidden_dim, num_classes),
        )

    def forward(self, x):
        stage_features = self.swin(x)
        pooled = []
        for feat, cbam in zip(stage_features, self.cbam_modules):
            feat = feat.permute(0, 3, 1, 2).contiguous()
            feat = cbam(feat)
            feat = self.gap(feat)
            feat = self.flatten(feat)
            pooled.append(feat)
        fused  = torch.cat(pooled, dim=1)
        return self.head(fused)


def load_model(checkpoint_path: str, device: str = "cpu") -> BDSkinNet:
    """Loads FP32 or INT8 quantized checkpoint."""
    ckpt = torch.load(checkpoint_path, map_location=device)
    is_quantized = ckpt.get("quantized", False)

    model = BDSkinNet()
    if is_quantized:
        model = torch.quantization.quantize_dynamic(
            model, qconfig_spec={torch.nn.Linear}, dtype=torch.qint8
        )
    model.load_state_dict(ckpt.get("model_state", ckpt))
    model.eval()
    return model


@torch.no_grad()
def predict(model: BDSkinNet, image, device: str = "cpu") -> dict:
    """
    Args:
        image: PIL.Image, np.ndarray (H,W,3 RGB), or file path str
    Returns:
        {disease_class, confidence, top2: [{class, confidence}]}
    """
    if isinstance(image, str):
        image = cv2.cvtColor(cv2.imread(image), cv2.COLOR_BGR2RGB)
    elif isinstance(image, Image.Image):
        image = np.array(image.convert("RGB"))

    tensor = inference_transform(image=image)["image"].unsqueeze(0).to(device)
    logits = model(tensor)
    probs  = F.softmax(logits, dim=1).squeeze().cpu().numpy()

    top2_idx = probs.argsort()[::-1][:2]
    return {
        "disease_class": CLASS_NAMES[top2_idx[0]],
        "confidence":    float(probs[top2_idx[0]]),
        "top2": [
            {"class": CLASS_NAMES[i], "confidence": float(probs[i])}
            for i in top2_idx
        ],
    }


if __name__ == "__main__":
    print("Running BD-SkinNet forward pass test...")
    model = BDSkinNet(num_classes=NUM_CLASSES)
    model.eval()
    dummy = torch.randn(2, 3, IMAGE_SIZE, IMAGE_SIZE)
    with torch.no_grad():
        out = model(dummy)
    assert out.shape == (2, NUM_CLASSES), f"Expected (2,{NUM_CLASSES}), got {out.shape}"
    print(f"Output shape: {out.shape}")
    print(f"Forward pass test PASSED.")
