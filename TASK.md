# TASK — Jun 2–3, 2026 | Week 3 / Day 18

## TODAY'S GOAL
1. Checkpoint plug-in (bd_skinnet_best.pth) — ONLY if file received
2. Error handling polish + edge case messages
3. Sidebar session summary as it builds
4. Begin README.md (public-facing, submission-ready draft)

## CONTEXT
- Day 17 complete: 164/164 tests, confidence captions, blur detection live
- BD-SkinNet checkpoint still pending (~Jun 2)
- All features working: Demo mode, hospital map, RAG chat, PDF, blur check
- Do NOT touch today: severity/, rag/, voice/, map/, tests/ (unless checkpoint arrives)

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

### TASK 1 — Error handling polish
Handle edge cases gracefully:
- Corrupt image file → `Image.open()` fails → catch exception, show:
  "⚠️ Could not read image. Please upload a valid JPG or PNG file."
- Overpass API timeout (already handled, verify message is bilingual)
- PDF generation failure → already caught, verify error message clear

### TASK 2 — Sidebar session summary
Add dynamic session summary in sidebar that builds as user completes steps:
```
Step 1: 🎙️ Voice recorded ✅ / ⬜ Pending
Step 2: 📷 Image analysed ✅ / ⬜ Pending
Step 3: 🧠 Diagnosis ready ✅ / ⬜ Pending
Step 4: 📄 Referral ready ✅ / ⬜ Pending
```
Shows progress at a glance — judges see the pipeline unfold.

### TASK 3 — README.md (submission-grade draft)
Per PLAN.md Day 32 checklist:
- [ ] Project title + one-line description
- [ ] Problem statement (2-3 sentences with stats)
- [ ] Live demo URL + HF Spaces badge
- [ ] Demo video link placeholder [TO BE ADDED]
- [ ] Full tech stack table
- [ ] Pipeline diagram (text/ASCII)
- [ ] Setup instructions (local dev)
- [ ] Attribution table (all third-party resources)
- [ ] Team section
- [ ] Disclaimer (not a medical device)

### TASK 4 — Commit and push
```
git commit -m "[w3/d18] error handling + sidebar summary + README draft"
git push origin main
```
Push clean branch to HF Space.

---

## DEFINITION OF DONE
- [ ] Corrupt image upload shows bilingual error message, no crash
- [ ] Sidebar session summary shows step completion status
- [ ] README.md has all required submission sections
- [ ] All 164 tests still passing
- [ ] Committed and pushed to GitHub + HF Space

---

## NEXT SESSION (Day 19 — Jun 4–5)
- Full E2E test on live HF Space (from a fresh incognito browser)
- W3 sign-off: verify all 7 planned W3 features are complete
- Begin Week 4: UI polish pass (loading animations, mobile layout)
