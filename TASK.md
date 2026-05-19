# TASK — Week 3 / Day 19
# Target date: Jun 3–4, 2026

## STARTING STATE
- Tests: 164/164 passing
- All W3 planned features delivered:
  ✅ Hospital map (Tier 3, Overpass + Folium)
  ✅ RAG context-aware chatbot (chat history, disease context banner)
  ✅ Keepalive script + GitHub Actions cron
  ✅ Demo mode (Scabies Tier 3, one-click)
  ✅ Bengali confidence captions
  ✅ Image blur detection
  ✅ Sidebar pipeline progress tracker
  ✅ Error handling (corrupt image, bilingual fallbacks)
  ✅ README.md (submission-grade)
- Checkpoint: bd_skinnet_best.pth still pending (ETA ~Jun 2–3)
- HF Space: live at https://huggingface.co/spaces/rafilovestosuffer/skinai-bangladesh

---

## CHECKPOINT INTEGRATION — do this FIRST if bd_skinnet_best.pth has arrived

**Step 1:** Place file at `model/checkpoints/bd_skinnet_best.pth`

**Step 2:** Replace `_run_model()` body in app.py:
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
    return torch.quantization.quantize_dynamic(
        model, {torch.nn.Linear}, dtype=torch.qint8
    )

def _run_model(pil_img: Image.Image) -> dict:
    model = _load_bd_skinnet()
    tfm = T.Compose([
        T.Resize((224, 224)),
        T.ToTensor(),
        T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
    tensor = tfm(pil_img).unsqueeze(0)
    with torch.no_grad():
        probs = torch.softmax(model(tensor), dim=1)[0].tolist()
    from model.disease_labels import CLASS_NAMES
    indexed = sorted(enumerate(probs), key=lambda x: -x[1])
    top2 = [{"disease": CLASS_NAMES[i], "confidence": p} for i, p in indexed[:2]]
    gc = compute_gradcam(model, tensor)
    return {
        "disease":      top2[0]["disease"],
        "confidence":   top2[0]["confidence"],
        "top2":         top2,
        "heatmap":      gc["overlay"],
        "coverage_pct": gc["coverage_pct"],
    }
```

**Step 3:** `pytest tests/ -q` — all 164 must still pass.

**Step 4:** Run `streamlit run app.py`, upload a test skin image, verify:
- Disease card shows real class (not "Tinea")
- GradCAM heatmap renders (not "No heatmap available")
- Coverage % flows into triage (Tier may change vs placeholder)
- Confidence caption correct for real confidence value

**Step 5:** Commit: `[w3/d13b] real BD-SkinNet inference connected`

---

## TASK 1 — W3 Sign-Off Checklist

Run through this checklist manually. Mark each item ✅ or ❌.

### Code quality
- [ ] `pytest tests/ -v` — 164/164 pass, zero failures
- [ ] `python -c "import ast; ast.parse(open('app.py', encoding='utf-8').read())"` — no syntax error
- [ ] All module imports work: `python -c "from severity.engine import compute_tier; from rag.retriever import answer_question; from pdf_gen.referral import generate_referral_pdf; from map.hospital_finder import find_nearest_hospitals; print('OK')"`

### Feature checklist (run `streamlit run app.py` locally)
- [ ] Demo button in sidebar loads Scabies Tier 3 case instantly
- [ ] Sidebar progress tracker shows ✅ steps updating correctly
- [ ] Tab 1: voice upload triggers transcription + history table
- [ ] Tab 1: image upload triggers disease card + confidence caption
- [ ] Tab 1: Tier 3 shows hospital district input + Folium map (via demo mode)
- [ ] Tab 1: blurry image shows amber warning (test with a plain-colour image)
- [ ] Tab 1: corrupt file (.txt renamed to .jpg) shows bilingual error, no crash
- [ ] Tab 2: disease context banner shown after diagnosis
- [ ] Tab 2: chat input works, conversation history persists
- [ ] Tab 2: Clear Chat button resets history
- [ ] Tab 3: Generate Referral Letter button works, PDF downloads
- [ ] Tab 3: PDF contains Bengali text and all 4 sections
- [ ] Keepalive: `python scripts/keepalive.py` runs one ping and prints status

### GitHub / HF Space
- [ ] `git log --oneline -8` — commits from May 18 to present
- [ ] HF Space URL loads from incognito browser
- [ ] `.github/workflows/keepalive.yml` is visible on GitHub Actions tab

---

## TASK 2 — W3 Complete: Plan Week 4

W3 is done. Cross off completed items in PLAN.md and document W4 scope.

Week 4 target (Jun 8–14 per PLAN.md) — pull forward if time allows:
1. **Loading spinners** — `st.spinner()` already on model/RAG; verify all slow ops covered
2. **Mobile layout check** — open HF Space on a phone/narrow browser, note any broken layout
3. **Demo video recording** — record 3–5 min Rahim story walkthrough (OBS / Loom)
   Script structure (from PLAN.md Day 25):
   - 0:00–0:30 Rahim's problem (voice-over)
   - 0:30–1:00 Bengali voice input demo
   - 1:00–2:00 Image → classification → GradCAM
   - 2:00–2:30 Severity tier + Bengali triage badge
   - 2:30–3:00 Hospital map (Tier 3 via demo mode)
   - 3:00–3:30 PDF referral letter
   - 3:30–4:00 RAG chatbot Q&A
   - 4:00–4:30 Impact slide + close
4. **Project report outline** — start skeleton (LaTeX or Google Docs)

---

## TASK 3 — PLAN.md + DECISIONS.md update

Update PLAN.md: mark all W3 items as complete.

Add one DECISIONS.md entry:
```
### [2026-06-02] W3 delivered ahead of PLAN.md schedule
Decision: All W3 features (hospital map, RAG chat history, keepalive, demo mode,
confidence captions, blur detection, progress tracker, README) completed by Day 18
instead of Day 21.
Why: W2 also ran ahead — early completion frees W4 for polish and demo video.
Impact: W4 can focus entirely on demo video, project report, and UI polish.
No architecture changes required.
```

---

## TASK 4 — Commit and push

```
git add PLAN.md DECISIONS.md PROGRESS.md TASK.md
git commit -m "[w3/d19] W3 sign-off + PLAN.md + DECISIONS.md updated"
git push origin main
```

No HF Space push needed for markdown-only changes.

---

## DEFINITION OF DONE
- [ ] W3 sign-off checklist fully verified (all ✅)
- [ ] PLAN.md W3 section marked complete
- [ ] DECISIONS.md updated
- [ ] PROGRESS.md updated
- [ ] TASK.md written for Day 20 (start of Week 4 polish)
- [ ] If checkpoint received: real model connected, 164 tests still pass

---

## NEXT SESSION — Day 20 / Week 4 Start
- Week 4 theme: Polish + Demo Video
- Day 20: loading spinners audit + mobile layout check + demo video script finalisation
- Day 21: demo video recording (Rahim story, 3–5 min)
- Day 22: project report skeleton (LaTeX or Google Docs, 8-page target)
