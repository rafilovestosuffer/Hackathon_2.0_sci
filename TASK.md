# TASK — May 20, 2026 | Week 1 / Day 3

## TODAY'S GOAL
Implement GradCAM++ on BD-SkinNet and write tests for heatmap shape and coverage.

## TASKS (in order)
1. [ ] Write model/gradcam.py — GradCAM++ wrapper using target layer model.cbam_modules[-1].spatial_attn.conv
2. [ ] Implement compute_gradcam(model, image_tensor) → {heatmap: np.ndarray, coverage_pct: float}
3. [ ] Implement compute_coverage_pct(heatmap, threshold=0.5) → float (0.0–100.0)
4. [ ] Write tests/test_gradcam.py — two tests:
       - shape test: heatmap.shape == (224, 224)
       - coverage range test: 0.0 <= coverage_pct <= 100.0
5. [ ] git commit -m "[w1/d3] GradCAM++ + coverage computation + tests"
6. [ ] git push origin main

## CONTEXT
- Last session left off at: Day 2 complete — bd_skinnet.py, disease_labels.py, export_int8.py all pushed
- No checkpoint needed — tests use random tensors and BDSkinNet() with random weights
- Target layer from notebook: model.cbam_modules[-1].spatial_attn.conv
- GradCAM++ library: pytorch_grad_cam (already in requirements.txt as grad-cam>=1.4.8)
- Do NOT touch today: severity/, voice/, rag/, app.py, export_int8.py

## DEFINITION OF DONE
- [ ] model/gradcam.py written with compute_gradcam() and compute_coverage_pct()
- [ ] Output of compute_gradcam() matches CLAUDE.md spec: {heatmap: np.ndarray, coverage_pct: float}
- [ ] Both tests in tests/test_gradcam.py pass
- [ ] Git committed and pushed
- [ ] PROGRESS.md updated
