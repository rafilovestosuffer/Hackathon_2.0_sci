# TASK — May 30, 2026 | Week 2 / Day 13

## TODAY'S GOAL
Wire up full app.py — all 3 tabs fully functional end-to-end.
Do NOT write new modules today; only integrate what is already built.

## CONTEXT
- Day 12 complete: ui/styles.py + ui/components.py + 29/29 tests passing
- Full suite: 133/133 passing
- All backend modules done: voice/, rag/, severity/, pdf_gen/, model/, ui/
- Do NOT touch today: any module in model/, severity/, voice/, rag/, pdf_gen/, ui/

---

## app.py INTEGRATION SPEC

### Imports
```python
import streamlit as st
from ui.styles import inject_css
from ui.components import (
    render_triage_badge, render_gradcam_overlay,
    render_patient_history_table, render_disease_card,
    render_rag_answer, render_referral_download_button,
)
from voice.pipeline import transcribe_audio, extract_patient_history
from rag.retriever import load_index, answer_question
from severity.engine import compute_tier
from pdf_gen.referral import generate_referral_pdf
```

### Sidebar
```python
# Logo: "🩺 SkinAI Bangladesh"
# Tagline: "ত্বকের রোগ নির্ণয় · AI-চালিত"
# Stats: 7 diseases · Bengali voice · CDC/NIH/WHO/DGHS
# Disclaimer: "Not a substitute for medical advice"
```

### Session state keys
```python
st.session_state.setdefault("transcript", "")
st.session_state.setdefault("history", {})
st.session_state.setdefault("prediction", None)   # {disease, confidence, top2}
st.session_state.setdefault("gradcam", None)       # {heatmap, coverage_pct}
st.session_state.setdefault("tier_result", None)
st.session_state.setdefault("pdf_bytes", None)
st.session_state.setdefault("rag_answer", "")
st.session_state.setdefault("rag_lang", "en")
```

### Tab 1 — রোগ নির্ণয় (Diagnosis)
Layout: two columns (left: voice + history table | right: image + disease card + triage)

LEFT COLUMN:
- st.audio_input() or st.file_uploader() for Bengali audio
- On audio upload: transcribe_audio(audio_bytes) → transcript
- extract_patient_history(transcript) → history dict
- render_patient_history_table(history)

RIGHT COLUMN:
- st.file_uploader() for skin image (jpg/png)
- On image upload: run BD-SkinNet inference (try/except — checkpoint may be missing)
  - If checkpoint missing: show placeholder prediction for demo
- render_disease_card(disease, confidence, top2)
- compute_tier(disease, confidence, coverage_pct, transcript) → tier_result
- render_triage_badge(tier_result)
- render_gradcam_overlay(heatmap_img, coverage_pct)

### Tab 2 — প্রশ্ন করুন (RAG Chatbot)
- Text input for question (Bengali or English)
- On submit: answer_question(question) → answer
- render_rag_answer(answer, lang)
- Show st.info("ℹ️ Answers from CDC · NIH · WHO · DGHS Bangladesh only")

### Tab 3 — রেফারেল পত্র (PDF)
- Show summary of diagnosis + triage
- Button: generate_referral_pdf(session_data) → pdf_bytes
- render_referral_download_button(pdf_bytes)

---

## TASKS (in order)

### TASK 1 — Wire app.py
- Call inject_css() at top (before any st.* call)
- Call load_index() at startup (cached via @st.cache_resource)
- Build sidebar with logo + stats + disclaimer
- Build all 3 tabs per spec above
- Handle checkpoint-missing gracefully (placeholder mode for demo)

### TASK 2 — Smoke test manually
- Run: `streamlit run app.py`
- Verify: sidebar loads, all 3 tabs render, no ImportError
- Verify: RAG chatbot returns answer (needs GEMINI_API_KEY in .env)

### TASK 3 — Commit and push
```
git add app.py
git commit -m "[w2/d13] full app.py integration — 3-tab pipeline"
git push origin main
```
Push to HF Space via clean branch strategy.

---

## DEFINITION OF DONE
- [ ] app.py: 3 tabs fully wired — no placeholder st.write() remaining
- [ ] inject_css() called once at startup
- [ ] load_index() cached via @st.cache_resource
- [ ] Sidebar: logo + Bengali tagline + stats + disclaimer
- [ ] Tab 1: voice → history + image → disease card + triage badge
- [ ] Tab 2: RAG chatbot with styled answer box
- [ ] Tab 3: PDF download button
- [ ] No ImportError on `streamlit run app.py`
- [ ] Committed and pushed to GitHub and HF Space

---

## NEXT SESSION (Day 14 — May 31)
- W2 integration test: full end-to-end with real audio + real image (placeholder checkpoint)
- Fix any bugs found during manual smoke test
- Commit: [w2/d14] W2 integration test + bug fixes
