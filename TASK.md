# TASK — Week 4 / Day 20
# Target date: Jun 5–6, 2026

## STARTING STATE
- Tests: 164/164 passing
- Week 3: fully complete and signed off (all 7 W3 features + sign-off checklist)
- Week 4 theme: Polish + Demo Video
- BD-SkinNet checkpoint: still pending (bd_skinnet_best.pth not yet received)
- Demo video: NOT yet recorded (record only after full feature completion)
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

## TASK 1 — Loading Spinners Audit

All slow operations must be wrapped in `st.spinner()`. Audit app.py for any gaps.

### Known slow operations — verify each is wrapped:

| Operation | Expected spinner text | Location in app.py |
|---|---|---|
| faster-whisper transcription | "🎙️ Transcribing audio..." | Tab 1, audio processing |
| BD-SkinNet inference + GradCAM | "🔍 Analysing image..." | Tab 1, image processing |
| Gemini patient history extraction | "📋 Extracting patient history..." | Tab 1, voice post-processing |
| Overpass API hospital query | "🗺️ Finding nearest hospitals..." | Tab 1, Tier 3 map section |
| FAISS + Gemini RAG answer | "💬 Searching knowledge base..." | Tab 2, chat input handler |
| PDF generation (reportlab) | "📄 Generating referral letter..." | Tab 3, generate button |

### Implementation pattern:
```python
with st.spinner("🔍 Analysing image..."):
    result = _run_model(pil_img)
```

### After fixing gaps:
- `pytest tests/ -q` — still 164/164 (spinners don't affect logic, but verify)
- Run `streamlit run app.py` locally, go through each tab, confirm no slow op runs naked (without a spinner visible)

---

## TASK 2 — Mobile / Narrow Layout Check

Open the running app at `http://localhost:8501` and resize the browser window to ~375px wide (phone width). Note any broken layout. Fix the worst offenders only — do not over-engineer.

### Common issues to check:
- [ ] Sidebar: does it collapse cleanly or overlap main content?
- [ ] Tab bar: do tab labels fit at narrow width, or overflow?
- [ ] Disease card: do the two columns (image + text) stack or overlap?
- [ ] GradCAM overlay: does the image scale down correctly?
- [ ] Triage badge: does the text wrap cleanly?
- [ ] Hospital table: does it scroll horizontally or overflow?
- [ ] PDF download button: full width or cut off?

### Fix strategy (CSS in ui/styles.py):
Add responsive breakpoints only where needed. Example pattern:
```css
@media (max-width: 480px) {
    .sk-card { padding: 0.75rem 1rem; }
    .badge-urgency { font-size: 1.1rem; }
    .disease-name-en { font-size: 1.1rem; }
}
```

Keep changes surgical — do not refactor the layout. Note any issues that cannot be fixed via CSS (Streamlit limitations) in DECISIONS.md.

---

## TASK 3 — Demo Video Script (Writing only — NOT recording yet)

Write the final demo video script as a markdown file at `docs/demo_script.md`.

Structure (target: 4 minutes):

```
## 0:00–0:30 — Rahim's Story (voice-over, no screen action)
"Rahim is a farmer in Rangpur..."
[Full narrative — write it out word for word]

## 0:30–1:00 — Bengali Voice Input
Screen: Tab 1, sidebar visible
Action: Click mic input → speak Bengali sentence (write the sentence to say)
Expected: Transcription appears, patient history table populates

## 1:00–2:00 — Image Upload → Classification → GradCAM
Screen: Tab 1 (continuing)
Action: Upload scabies test image
Expected: Disease card, confidence caption, GradCAM heatmap, triage badge

## 2:00–2:30 — Severity Tier + Bengali Triage Badge
Screen: Tab 1, triage section
Action: None (auto-populates from above)
Expected: Tier 2 or Tier 3 badge with Bengali action text

## 2:30–3:00 — Hospital Map (Tier 3 via Demo Mode)
Screen: Sidebar → click Demo button
Action: "Load Demo (Scabies — Tier 3)" → Tab 1 → type "Rangpur" in district input
Expected: Folium map with 5 hospital pins, table with distances

## 3:00–3:30 — PDF Referral Letter
Screen: Tab 3
Action: Click "Generate Referral Letter"
Expected: PDF downloads, show 4-section contents briefly

## 3:30–4:00 — RAG Chatbot Q&A
Screen: Tab 2
Action: Type "স্ক্যাবিসের চিকিৎসা কী?" (What is the treatment for scabies?)
Expected: Grounded Bengali answer with source tags

## 4:00 — Impact Slide + Close (voice-over)
"1 dermatologist per 250,000 people..."
"Right patient → Right doctor → Right time"
```

Write every word of narration fully. Include the exact Bengali sentence to speak during the voice demo.

---

## TASK 4 — PROGRESS.md + TASK.md update

Update PROGRESS.md:
- Change current status to Week 4 / Day 20 (starting)
- Add Day 20 session log entry at the top of the session log

Rewrite TASK.md for Day 21:
- Theme: demo video recording (Rahim story, 3–5 min, OBS or Loom)
- Include the `docs/demo_script.md` path as the script source
- Include recording checklist (resolution, audio, screen layout, one-take vs edit)

---

## TASK 5 — Commit and push

```
git add app.py ui/styles.py docs/demo_script.md PROGRESS.md TASK.md
git commit -m "[w4/d20] loading spinners audit + mobile CSS + demo video script"
git push origin main
```

HF Space push: yes — spinner changes are visible to judges.
Use clean-branch strategy (binary font file is in git history on GitHub, not on HF):
```
git checkout -b hf-push hf/main
git checkout main -- app.py ui/styles.py ui/components.py
git commit -m "[w4/d20] loading spinners + mobile CSS"
git push hf hf-push:main
git checkout main && git branch -d hf-push
```

---

## DEFINITION OF DONE
- [ ] All slow operations confirmed wrapped in `st.spinner()`
- [ ] `pytest tests/ -q` — 164/164 still pass (no regressions)
- [ ] Mobile layout tested at ~375px width — worst issues fixed
- [ ] `docs/demo_script.md` written (all 8 segments, full narration)
- [ ] PROGRESS.md updated
- [ ] TASK.md written for Day 21
- [ ] Committed and pushed to GitHub + HF Space

---

## NEXT SESSION — Day 21 / Demo Video Recording
- Theme: record the 3–5 min Rahim story demo video using `docs/demo_script.md`
- Tools: OBS Studio (screen capture) or Loom — user's choice
- Resolution: 1920×1080 recommended; HF Space loaded in Chrome at full width
- After recording: upload to YouTube (unlisted) or Google Drive; add link to README.md
- Day 22: project report skeleton (LaTeX or Google Docs, 8-page target)
