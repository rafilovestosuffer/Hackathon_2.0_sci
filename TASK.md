# TASK — Week 4 / Day 22
# Target date: Jun 8–9, 2026

## STARTING STATE
- Tests: 245/245 passing
- UI overhaul complete: medical-grade design system live
- Demo video: NOT yet recorded (pending checkpoint or demo-mode-only recording)
- BD-SkinNet checkpoint: still pending (bd_skinnet_best.pth)
- HF Space: live at https://huggingface.co/spaces/rafilovestosuffer/skinai-bangladesh
- Submission deadline: July 1, 2026

---

## CHECKPOINT INTEGRATION — do this FIRST if bd_skinnet_best.pth has arrived

**Step 1:** Place file at `model/checkpoints/bd_skinnet_best.pth`

**Step 2:** Replace the entire `_run_model` stub in app.py:
```python
from model.bd_skinnet import load_model, predict as bd_predict
from model.gradcam import compute_gradcam

CKPT = "model/checkpoints/bd_skinnet_best.pth"

@st.cache_resource(show_spinner="Loading BD-SkinNet model…")
def _load_bd_skinnet():
    return load_model(CKPT, device="cpu")

def _run_model(pil_img: Image.Image) -> dict:
    model = _load_bd_skinnet()
    result = bd_predict(model, pil_img, device="cpu")
    import numpy as np
    from model.bd_skinnet import inference_transform
    img_np = np.array(pil_img.convert("RGB"))
    tensor = inference_transform(image=img_np)["image"].unsqueeze(0)
    gc = compute_gradcam(model, tensor)
    return {
        "disease":      result["disease_class"],
        "confidence":   result["confidence"],
        "top2":         [{"disease": t["class"], "confidence": t["confidence"]}
                         for t in result["top2"]],
        "heatmap":      gc["overlay"],
        "coverage_pct": gc["coverage_pct"],
    }
```

**Step 3:** `pytest tests/ -q` — all 245 must still pass.
**Step 4:** `streamlit run app.py`, upload test image, verify real disease + GradCAM.
**Step 5:** Commit: `[w4/d22] real BD-SkinNet inference connected`

---

## TASK 1 — Project Report Skeleton

Write an 8-page report in Google Docs or LaTeX. Structure below. Fill in each section header and 2–3 bullet points of what belongs there — do not write final prose yet. This is the skeleton for Day 23 to flesh out.

### Report structure:

**Page 1 — Title + Abstract (½ page)**
- Title: "SkinAI Bangladesh: Multi-Signal AI Triage for Dermatological Care in Rural Bangladesh"
- Authors: team names, institution, IEEE SB CUET affiliation
- Abstract: 150–200 words. Problem → System → Key results → Impact.
  - Must include: F1=92.46%, AUC=0.9937, 245 tests, 7 disease classes, Bangladesh-specific dataset

**Page 2 — Problem Statement + Related Work**
- Bangladesh stats: 1 derm per 250,000, 80% untreated/mistreated
- Gap: no Bangladesh-specific triage tool, all existing tools trained on DermNet (non-BD data)
- Related work: brief 3–4 citations (general dermoscopy AI, telemedicine in LMICs)
- Our novelty: BD clinical data + multi-signal triage + Bengali voice + referral letter

**Page 3–4 — System Architecture**
- High-level pipeline diagram (voice → image → triage → referral)
- BD-SkinNet architecture: Swin-B + CBAM + GradCAM++
- Severity engine: 4-signal design (justify each signal medically)
- RAG chatbot: FAISS + Gemini 2.5 Flash, knowledge base sources
- Deployment: HF Spaces free CPU, INT8 quantization, Docker

**Page 5 — Dataset + Model**
- Training data: Faridpur Medical College + Rangpur Medical College
- 7 disease classes with class distribution
- Augmentation strategy
- INT8 quantization rationale (HF Spaces constraint)
- BD-SkinNet vs baseline models (if numbers available)

**Page 6 — Results + Evaluation**
- BD-SkinNet: F1=92.46%, AUC=0.9937 per class breakdown
- Severity engine: 245 tests passing, escalation scenarios validated
- GradCAM++: coverage_pct correlation with severity
- RAG: qualitative Bengali answer quality

**Page 7 — Demo + Impact**
- Demo video link
- Rahim story walkthrough (matches demo video structure)
- Deployment metrics: HF Spaces load time, keepalive status
- Social impact: correct referral vs quack practitioner cost comparison

**Page 8 — Limitations + Conclusion**
- Limitations: placeholder checkpoint until training completes, OSM hospital data gaps, Whisper accuracy on heavy dialect
- Conclusion: "Right patient → Right doctor → Right time" — restate the narrative
- Future work: model update pipeline, Android app, district health authority integration

---

## TASK 2 — Demo Video (if checkpoint not yet arrived, use Demo Mode)

Record the 3–5 min Rahim story demo using `docs/demo_script.md`. Demo Mode in the sidebar pre-fills all session state — no checkpoint required.

Recording checklist:
- [ ] OBS or Loom set up, 1920×1080, 30fps
- [ ] HF Space open in Chrome, zoom 100%
- [ ] Demo audio clip `docs/demo_voice.wav` ready (pre-recorded Bengali sentence)
- [ ] One warm-up run before recording (click "Load Demo" → verify all tabs)
- [ ] Record following `docs/demo_script.md` timing exactly
- [ ] Upload to YouTube (Unlisted) or Google Drive
- [ ] Add link to README.md

---

## TASK 3 — PROGRESS.md + TASK.md update (end of session)

- Add Day 22 session log entry
- Update current status to Week 4 / Day 23 (starting)
- Rewrite TASK.md for Day 23: flesh out Architecture and Results sections with diagrams

---

## DEFINITION OF DONE
- [ ] Report skeleton: all 8 section headers + bullet points written
- [ ] If checkpoint arrived: real model connected, 245 tests still pass
- [ ] Demo video recorded OR explicitly deferred to Day 23 with reason
- [ ] PROGRESS.md updated
- [ ] TASK.md written for Day 23
- [ ] Committed and pushed to GitHub

---

## NEXT SESSION — Day 23 / Report: Architecture + Results
- Fill Architecture section with ASCII or draw.io diagram
- Fill Results section with all quantitative numbers (F1, AUC, test count, class breakdown)
- Day 24: final submission package (report PDF export, model card, README final review)
- Day 25: submission + keepalive verification
