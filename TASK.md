# TASK — Week 4 / Day 21
# Target date: Jun 7–8, 2026

## STARTING STATE
- Tests: 164/164 passing
- Week 4, Day 20 complete: spinners audited, mobile CSS added, demo script written
- Demo script: `docs/demo_script.md` (8 segments, 4 minutes, full narration)
- BD-SkinNet checkpoint: still pending (bd_skinnet_best.pth)
- Demo video: NOT yet recorded — this is today's primary task
- HF Space: live at https://huggingface.co/spaces/rafilovestosuffer/skinai-bangladesh

---

## CHECKPOINT INTEGRATION — do this FIRST if bd_skinnet_best.pth has arrived

**Step 1:** Place file at `model/checkpoints/bd_skinnet_best.pth`

**Step 2:** Replace the entire `_load_whisper` block through `_run_model` in app.py:
```python
from model.bd_skinnet import load_model, predict as bd_predict
from model.gradcam import compute_gradcam

CKPT = "model/checkpoints/bd_skinnet_best.pth"

@st.cache_resource(show_spinner="Loading BD-SkinNet model…")
def _load_bd_skinnet():
    return load_model(CKPT, device="cpu")

def _run_model(pil_img: Image.Image) -> dict:
    model = _load_bd_skinnet()
    # bd_predict() uses the correct albumentations normalization the model was trained with
    result = bd_predict(model, pil_img, device="cpu")
    # GradCAM: build tensor using the same albumentations pipeline as bd_predict()
    import numpy as np
    from model.bd_skinnet import inference_transform
    img_np = np.array(pil_img.convert("RGB"))
    tensor = inference_transform(image=img_np)["image"].unsqueeze(0)
    gc = compute_gradcam(model, tensor)
    return {
        "disease":      result["disease_class"],
        "confidence":   result["confidence"],
        # Normalise key name: bd_predict returns "class", app/PDF/UI expect "disease"
        "top2":         [{"disease": t["class"], "confidence": t["confidence"]}
                         for t in result["top2"]],
        "heatmap":      gc["overlay"],
        "coverage_pct": gc["coverage_pct"],
    }
```
NOTE: Do NOT use torchvision.transforms.Normalize inline — the model was trained with
albumentations normalization via `inference_transform`. Using a different pipeline
reduces accuracy. `load_model()` and `bd_predict()` handle everything correctly.

**Step 3:** `pytest tests/ -q` — all 164 must still pass.

**Step 4:** Run `streamlit run app.py`, upload test image, verify real class + GradCAM.

**Step 5:** Commit: `[w3/d13b] real BD-SkinNet inference connected`

---

## TASK 1 — Pre-Recording Setup

Read `docs/demo_script.md` fully before starting.

### Software setup:
- **OBS Studio** (recommended): Scene → Desktop capture, crop to browser window only. Audio: Mic input.
  - Output: MP4, 1920×1080, 30fps, CBR 8000 kbps
- **Loom** (alternative): Record screen + mic, crop to browser window
- Browser: Chrome, open HF Space, zoom to 100%, sidebar pinned open

### Files to prepare:
- A test skin image (any clear photo of a rash, blister, or discoloured skin patch — JPG, min 300×300px)
- Pre-record the Bengali sentence from Segment 2 as a separate WAV file first, listen back, confirm clarity:
  > **"আমার সারা শরীরে চুলকানি হচ্ছে। দশ দিন ধরে ছড়িয়ে পড়ছে। জ্বরও আছে এবং ব্যথা হচ্ছে।"**
- Name it `docs/demo_voice.wav` (gitignored — do not commit audio files)

### Warm-up run (before recording):
1. Load HF Space, click "Load Demo" button once — confirms all tabs work
2. Upload a test image — confirms Tab 1 pipeline works
3. Clear session state (refresh page)
4. Now record

---

## TASK 2 — Record the Demo Video

Follow `docs/demo_script.md` exactly. Key timings:

| Segment | Time | Action |
|---|---|---|
| 0 — Title | 0:00–0:15 | Static slide or black screen |
| 1 — Rahim's story | 0:15–0:45 | HF Space homepage, narrate only |
| 2 — Bengali voice | 0:45–1:20 | Record mic, transcription populates |
| 3 — Image → GradCAM | 1:20–2:10 | Upload image, disease card + heatmap |
| 4 — Triage badge | 2:10–2:35 | Tier badge + Bengali action text |
| 5 — Hospital map | 2:35–3:00 | Demo mode button → type "Rangpur" |
| 6 — PDF letter | 3:00–3:25 | Tab 3 → Generate → Download |
| 7 — RAG chatbot | 3:25–3:50 | Tab 2 → Bengali question → answer |
| 8 — Impact close | 3:50–4:00 | Title card + stats overlay |

### Tips:
- Move cursor slowly — judges are watching
- Pause 0.5–1 second after each UI element appears before narrating it
- If the real model is not connected yet, use Demo Mode for segments 3–8 as well
- Do not stop recording mid-take for minor mistakes — cut in post if needed
- If Whisper transcription takes > 15 seconds, it is still correct; narrate "This runs fully offline…"

---

## TASK 3 — Upload and Link

After recording:

1. **YouTube (recommended):** Upload → Visibility: Unlisted → Copy link
   OR
   **Google Drive:** Upload → Share → Anyone with link → Copy link

2. Test the link in an incognito browser window.

3. Add the link to `README.md`:
```markdown
🎬 **Demo Video:** [Watch on YouTube](YOUR_LINK_HERE)
```
   Replace the placeholder line: `🎬 **Demo Video:** _[To be added — Week 4]_`

4. Commit:
```
git add README.md
git commit -m "[w4/d21] add demo video link to README"
git push origin main
```

---

## TASK 4 — PROGRESS.md + TASK.md update

Update PROGRESS.md:
- Change current status to Week 4 / Day 22 (starting)
- Add Day 21 session log entry

Rewrite TASK.md for Day 22:
- Theme: project report skeleton
- Target: 8-page LaTeX or Google Docs report
- Sections: Abstract, Problem, Dataset, Architecture, Results, System Demo, Limitations, Conclusion
- Include BD-SkinNet numbers (F1=92.46%, AUC=0.9937) in the results section outline

---

## DEFINITION OF DONE
- [ ] Demo video recorded (3–5 minutes, Rahim story structure)
- [ ] Video uploaded (YouTube unlisted or Google Drive)
- [ ] Link tested from incognito browser
- [ ] README.md updated with video link
- [ ] Committed and pushed to GitHub
- [ ] PROGRESS.md updated
- [ ] TASK.md written for Day 22

---

## NEXT SESSION — Day 22 / Project Report
- Theme: project report skeleton (LaTeX or Google Docs, 8-page target)
- Sections: Abstract, Problem Statement, System Architecture, BD-SkinNet Model, Evaluation, Demo, Limitations, Conclusion
- Include all quantitative results: F1=92.46%, AUC=0.9937, 164 tests, 7 classes
- Day 23: flesh out Architecture and Results sections with diagrams
- Day 24: final submission package (report PDF, model card, README final review)
