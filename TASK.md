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
