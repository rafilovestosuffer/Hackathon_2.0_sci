# TASK — Week 3 / Day 18
# Target date: Jun 2–3, 2026

## STARTING STATE
- Tests: 164/164 passing
- Features live: Demo mode, hospital map, RAG chat history, PDF, blur detection,
  Bengali confidence captions, keepalive cron
- Checkpoint: bd_skinnet_best.pth NOT YET received (placeholder active)
- HF Space: live at https://huggingface.co/spaces/rafilovestosuffer/skinai-bangladesh

---

## CHECKPOINT INTEGRATION — when bd_skinnet_best.pth arrives (~Jun 2)
> Skip this entire block if the file has not been received yet.

**Step 1:** Place the file at `model/checkpoints/bd_skinnet_best.pth`

**Step 2:** Replace the body of `_run_model()` in app.py:
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

**Step 3:** Run `pytest tests/ -q` — all 164 must still pass.

**Step 4:** Verify heatmap renders in Tab 1 (coverage bar should reflect real GradCAM).

**Step 5:** Commit: `[w3/d13b] real BD-SkinNet inference connected`

---

## TASK 1 — Error handling polish in app.py

### 1a. Corrupt image upload
Wrap `Image.open()` in a try/except and show a bilingual error:
```python
try:
    pil_img = Image.open(image_file).convert("RGB")
except Exception:
    st.error(
        "⚠️ Could not read this image file. Please upload a valid JPG or PNG.\n\n"
        "ছবিটি পড়া যাচ্ছে না। অনুগ্রহ করে একটি বৈধ JPG বা PNG আপলোড করুন।"
    )
    st.stop()
```
Place the try/except immediately around the `Image.open()` line.

### 1b. Overpass API fallback message
In Tab 1, the `else` branch after `if hospitals:` currently shows a plain warning.
Make it bilingual:
```python
st.warning(
    "🏥 No hospitals found nearby. Please try a different or more specific district name.\n\n"
    "নিকটে কোনো হাসপাতাল পাওয়া যায়নি। অন্য জেলার নাম দিয়ে চেষ্টা করুন।"
)
```

### 1c. No tests needed for these — they are UI-only `st.error` / `st.warning` calls.

---

## TASK 2 — Sidebar session progress summary

Add a visual pipeline progress tracker in the sidebar, just above the Demo button section.
It must update dynamically as session_state fills in.

**Logic:**
- Step 1 ✅ if `st.session_state.transcript` is non-empty
- Step 2 ✅ if `st.session_state.prediction` is not None
- Step 3 ✅ if `st.session_state.tier_result` is not None
- Step 4 ✅ if `st.session_state.pdf_bytes` is not None

**HTML to inject (inside `with st.sidebar:`):**
```python
st.markdown("---")
st.markdown(
    '<div class="sidebar-stat"><strong>Pipeline Progress</strong></div>',
    unsafe_allow_html=True,
)
_steps = [
    ("🎙️ Voice recorded",   bool(st.session_state.transcript)),
    ("📷 Image analysed",    st.session_state.prediction is not None),
    ("🧠 Diagnosis ready",   st.session_state.tier_result is not None),
    ("📄 Referral ready",    st.session_state.pdf_bytes is not None),
]
for _label, _done in _steps:
    _icon = "✅" if _done else "⬜"
    _color = "#60a5fa" if _done else "#64748b"
    st.markdown(
        f'<div class="sidebar-stat" style="color:{_color} !important;">'
        f'{_icon} {_label}</div>',
        unsafe_allow_html=True,
    )
```

**Placement:** Between the current diagnosis/tier stat block and the existing `---` before Demo mode.

---

## TASK 3 — README.md (submission-grade)

Rewrite the current placeholder README.md with all required submission content.
Use the exact stats and data from CLAUDE.md. No fabrication.

**Required sections (in order):**

```markdown
# SkinAI Bangladesh 🩺
> AI-powered dermatological screening and triage for rural Bangladesh
> "সঠিক রোগী → সঠিক ডাক্তার → সঠিক সময়"

## 🔴 Live Demo
[HF Spaces badge] + link

## Problem
Bangladesh has approximately 1 dermatologist per 250,000 people.
80% of skin conditions in rural Bangladesh go untreated or are mistreated
by unlicensed practitioners. SkinAI Bangladesh does not replace the doctor —
it ensures the right patient reaches the right doctor at the right time.

## Solution — Pipeline
ASCII/text pipeline diagram showing the 5-stage flow:
  Bengali Voice → Transcript → Patient History (Gemini)
  Skin Image → BD-SkinNet INT8 → Disease + Confidence
  GradCAM++ → Coverage %
  4-Signal Triage Engine → Tier 1 / 2 / 3
  [Tier 3 only] → Overpass API → Hospital Map (Folium)
  → Referral Letter PDF (reportlab)
  RAG Chatbot → FAISS + Gemini

## Model — BD-SkinNet
| Property | Value |
|----------|-------|
| Architecture | Swin Transformer Base + CBAM (×4 stages) |
| Training data | Faridpur MCH + Rangpur MCH (Bangladesh clinical) |
| Test F1 | 92.46% |
| Test Accuracy | 92.37% |
| AUC-ROC | 0.9937 |
| Classes | 7 (Atopic Dermatitis, Contact Dermatitis, Eczema, Scabies, Seborrheic Dermatitis, Tinea, Vitiligo) |
| Deployment | INT8 quantized — torch.quantization.quantize_dynamic |
| Input | 224×224 RGB |

## Triage Engine — 4 Signals
Brief table of the 4 signals and their escalation rules.

## Tech Stack
Full table: Component | Library | Why

## Setup (Local Development)
```bash
git clone ...
pip install -r requirements.txt
cp .env.example .env  # add GEMINI_API_KEY
streamlit run app.py
```

## Attribution
| Resource | License | Usage |
table covering: timm, faster-whisper, google-genai, FAISS,
sentence-transformers, reportlab, folium, Overpass API, CDC/NIH/WHO/DGHS content

## Team
Rafiur Rahman — ML lead, IEEE SB CUET

## Disclaimer
SkinAI Bangladesh is a research prototype for the SciBlitz AI Challenge 2026.
It is not a certified medical device. Always consult a licensed physician.
```

Place `[Demo Video: TO BE ADDED — Week 4]` as a placeholder for the video link.

---

## TASK 4 — Commit and push

```
git add app.py ui/components.py README.md PROGRESS.md TASK.md
git commit -m "[w3/d18] error handling + sidebar progress + README draft"
git push origin main
```
Then push clean branch to HF Space (standard strategy).

---

## DEFINITION OF DONE
- [ ] Corrupt image upload → bilingual error, no crash, app continues
- [ ] Overpass no-result message is bilingual
- [ ] Sidebar shows 4-step progress tracker updating in real time
- [ ] README.md has all required submission sections (complete, no placeholders except video)
- [ ] All 164 tests still passing
- [ ] Committed and pushed to GitHub + HF Space

---

## DO NOT TOUCH TODAY
- severity/, rag/, voice/, map/ — all stable
- tests/ — only add tests if checkpoint plug-in happens
- pdf_gen/ — stable
- model/ — stable (until checkpoint arrives)

---

## NEXT SESSION — Day 19
- Full E2E test on live HF Space (fresh incognito browser, judge's perspective)
- W3 sign-off checklist: verify every W3 planned feature is live and working
- If checkpoint still not received: W3 is complete, move to Week 4 UI polish
- Week 4 target: loading spinners, mobile layout, demo video recording prep
