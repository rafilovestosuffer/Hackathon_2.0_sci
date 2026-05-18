# TASK — May 19, 2026 | Week 1 / Day 2

## TODAY'S GOAL
Write the BD-SkinNet model architecture (Swin+CBAM), disease label map, and INT8 export script.

## TASKS (in order)
1. [ ] Write model/bd_skinnet.py — Swin Transformer Base + CBAM (Channel+Spatial Attention) using timm
2. [ ] Write model/disease_labels.py — English → Bengali disease name map for all classes
3. [ ] Write model/export_int8.py — INT8 quantization script using torch.quantization.quantize_dynamic
4. [ ] Add dummy forward pass test inside bd_skinnet.py (random 224x224 tensor, assert output shape is correct)
5. [ ] git commit -m "[w1/d2] BD-SkinNet architecture + INT8 export"
6. [ ] git push origin main

## CONTEXT
- Last session left off at: Day 1 complete — repo live at https://github.com/rafilovestosuffer/Hackathon_2.0_sci
- Known issue to fix first: None
- Do NOT touch today: severity/, voice/, rag/, app.py

## DEFINITION OF DONE
- [ ] model/bd_skinnet.py loads without error and forward pass returns correct output shape
- [ ] model/disease_labels.py has English + Bengali name for every disease class
- [ ] model/export_int8.py runs and produces a quantized model
- [ ] Git committed and pushed
- [ ] PROGRESS.md updated
