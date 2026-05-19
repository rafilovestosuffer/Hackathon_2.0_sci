# TASK — Jun 2–3, 2026 | Week 3 / Day 17–18

## TODAY'S GOAL
1. Checkpoint plug-in (bd_skinnet_best.pth) — if received TODAY
2. Full E2E integration test — run the complete pipeline manually
3. UI polish: loading spinners, error messages, edge cases
4. Demo video script draft

## CONTEXT
- Day 16 complete: 154/154 tests, chat history UI, keepalive, demo mode
- Keepalive cron live on GitHub Actions (every 20 min)
- BD-SkinNet checkpoint still pending (~Jun 2) — _run_model() placeholder active
- Do NOT touch today: rag/retriever.py, scripts/, .github/, tests/ (unless checkpoint arrives)

---

## CHECKPOINT INTEGRATION (when bd_skinnet_best.pth arrives)
File: app.py — replace body of `_run_model(pil_img)`
```python
from model.bd_skinnet import BDSkinNet
from model.gradcam import compute_gradcam
import torch, torchvision.transforms as T

CKPT = "model/checkpoints/bd_skinnet_best.pth"

@st.cache_resource
def _load_bd_skinnet():
    model = BDSkinNet(num_classes=7)
    model.load_state_dict(torch.load(CKPT, map_location="cpu"))
    model.eval()
    return torch.quantization.quantize_dynamic(model, {torch.nn.Linear}, dtype=torch.qint8)

# In _run_model():
model = _load_bd_skinnet()
tfm = T.Compose([T.Resize((224,224)), T.ToTensor(),
                 T.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])])
tensor = tfm(pil_img).unsqueeze(0)
with torch.no_grad():
    probs = torch.softmax(model(tensor), dim=1)[0].tolist()
from model.disease_labels import CLASS_NAMES
indexed = sorted(enumerate(probs), key=lambda x: -x[1])
top2 = [{"disease": CLASS_NAMES[i], "confidence": p} for i, p in indexed[:2]]
gc = compute_gradcam(model, tensor)
return {"disease": top2[0]["disease"], "confidence": top2[0]["confidence"],
        "top2": top2, "heatmap": gc["overlay"], "coverage_pct": gc["coverage_pct"]}
```

---

## TASKS (in order)

### TASK 1 — E2E integration test (manual checklist)
Run the app locally and verify every feature:
```
streamlit run app.py
```
Check:
- [ ] Demo button in sidebar loads Scabies Tier 3 case
- [ ] Tab 1 shows disease card + triage badge + hospital district input
- [ ] Tab 2 shows disease context banner + chat input works
- [ ] Tab 3 shows PDF generate button + download works
- [ ] Chat history persists across questions in the same session
- [ ] Clear Chat button resets history

### TASK 2 — UI polish: loading spinners + edge cases
Add `st.spinner()` wrappers where missing:
- Hospital map query
- PDF generation (already has one — verify)
Add error messages for:
- Image upload fails (corrupt file)
- Overpass API timeout (graceful message — already in place, verify)
Add confidence-level caption in Bengali:
- >80%: "মডেল নিশ্চিত" (model is confident)
- 60-80%: "মোটামুটি নিশ্চিত" (moderately confident)
- <60%: "অনিশ্চিত — ডাক্তার দেখান" (uncertain — see doctor)
This goes inside render_disease_card() or app.py post-prediction.

### TASK 3 — Demo video script draft
Write the Rahim story narration (text only, no video yet):
- 0:00-0:30 — Rahim's problem (voice-over text)
- 0:30-1:00 — Demo: Bengali voice input
- 1:00-2:00 — Demo: image → classification → GradCAM
- 2:00-2:30 — Severity tier + Bengali triage badge
- 2:30-3:00 — Hospital map (Tier 3 scenario via demo mode)
- 3:00-3:30 — PDF referral letter generation
- 3:30-4:00 — RAG chatbot (ask in context)
- 4:00-4:30 — Impact slide + system diagram
Save as: DEMO_SCRIPT.md

### TASK 4 — Commit and push
```
git commit -m "[w3/d17] E2E test + UI polish + confidence captions"
git push origin main
```

---

## DEFINITION OF DONE
- [ ] Demo mode: all tabs populated with one sidebar click
- [ ] Confidence-level caption in Bengali shown under disease card
- [ ] All existing 154 tests still passing
- [ ] Committed and pushed to GitHub + HF Space

---

## NEXT SESSION (Day 18 — Jun 3–4)
- Polish Tab 1 image quality check (Laplacian blur detection)
- Polish sidebar: show session summary as it builds
- Begin project report structure (if Week 5 target allows)
