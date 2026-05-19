# TASK — May 29, 2026 | Week 2 / Day 12

## TODAY'S GOAL
Write ui/components.py — reusable Streamlit widgets.
Write ui/styles.py — Bengali Noto Sans font + CSS injection.
Do NOT touch app.py integration today (that is Day 13).

## CONTEXT
- Day 11 complete: rag/retriever.py done, 104/104 tests passing
- Full pipeline: voice → triage → PDF → RAG all implemented
- Do NOT touch today: model/, severity/, pdf_gen/, voice/, rag/, app.py

---

## MODULE SPEC: ui/styles.py

```python
# ui/styles.py
# Provides: inject_css()
# Injects Bengali Noto Sans font and custom CSS into Streamlit via st.markdown

NOTO_SANS_BENGALI_URL = "https://fonts.googleapis.com/css2?family=Noto+Sans+Bengali:wght@400;600;700&display=swap"

def inject_css():
    """Inject Bengali font + app CSS into Streamlit. Call once at app startup."""
    st.markdown(f"""<style>...</style>""", unsafe_allow_html=True)
```

CSS requirements:
- Import Noto Sans Bengali from Google Fonts
- Apply font to all text elements (body, .stMarkdown, .stButton, etc.)
- Tier badge colours: tier-1 green (#28a745), tier-2 orange (#fd7e14), tier-3 red (#dc3545)
- Bengali disclaimer footer style (small, grey, italic)
- Sidebar style (light background)
- Card/metric style for GradCAM coverage and confidence display

---

## MODULE SPEC: ui/components.py

```python
# ui/components.py
# Reusable Streamlit widget functions

def render_triage_badge(tier_result: dict) -> None:
    """Render coloured tier badge + action text. tier_result = compute_tier() output."""

def render_gradcam_overlay(heatmap_img: np.ndarray | None, coverage_pct: float) -> None:
    """Render GradCAM heatmap image + coverage bar. heatmap_img may be None."""

def render_patient_history_table(history: dict) -> None:
    """Render voice-extracted patient history as a clean table."""

def render_disease_card(disease: str, confidence: float, top2: list) -> None:
    """Render disease name (English + Bengali), confidence bar, differential if top2[1] > 0.15."""

def render_rag_answer(answer: str, lang: str) -> None:
    """Render RAG chatbot answer with source citation style."""

def render_referral_download_button(pdf_bytes: bytes | None) -> None:
    """Render PDF download button. Disabled if pdf_bytes is None."""
```

---

## TASKS (in order)

### TASK 1 — Write ui/styles.py
- inject_css() using st.markdown with unsafe_allow_html=True
- Bengali font via Google Fonts CDN (no local file needed)
- Tier badge CSS classes: .badge-tier1, .badge-tier2, .badge-tier3
- Metric card CSS for confidence/coverage display

### TASK 2 — Write ui/components.py
- 6 component functions (spec above)
- Each function is standalone — no cross-dependencies
- render_disease_card: show Bengali name from disease_labels.py
- render_triage_badge: colour-code by tier (1=green, 2=orange, 3=red)
- render_patient_history_table: skip empty fields gracefully
- render_referral_download_button: st.download_button if bytes else disabled button

### TASK 3 — Write tests/test_ui.py
Tests (all mock Streamlit calls — patch st.markdown, st.image, etc.):
1. TestInjectCSS:
   - test_inject_css_calls_st_markdown
   - test_inject_css_contains_noto_sans
   - test_inject_css_contains_badge_classes
2. TestRenderTriageBadge:
   - test_badge_tier1_rendered
   - test_badge_tier2_rendered
   - test_badge_tier3_rendered
3. TestRenderPatientHistory:
   - test_empty_fields_skipped
   - test_nonempty_fields_rendered
4. TestRenderDiseaseCard:
   - test_disease_card_shows_english_name
   - test_disease_card_shows_bengali_name
   - test_differential_shown_when_above_threshold
   - test_differential_hidden_when_below_threshold
5. TestRenderReferralButton:
   - test_download_button_enabled_with_bytes
   - test_download_button_disabled_when_none

Target: 14+ tests, all passing.

### TASK 4 — Run tests
```
pytest tests/test_ui.py -v
```
All tests must pass.

### TASK 5 — Commit and push
```
git add ui/styles.py ui/components.py tests/test_ui.py
git commit -m "[w2/d12] UI components + Bengali styles"
git push origin main
```
Push to HF Space via clean branch strategy.

---

## DEFINITION OF DONE
- [ ] ui/styles.py: inject_css() with Bengali font + tier badge CSS
- [ ] ui/components.py: 6 component functions
- [ ] 14+ tests in tests/test_ui.py, all passing
- [ ] Committed and pushed to GitHub and HF Space

---

## NEXT SESSION (Day 13 — May 30)
- Wire up full app.py: Tab 1 (voice + image → triage), Tab 2 (RAG chatbot), Tab 3 (PDF)
- Call all real modules: voice/pipeline.py, rag/retriever.py, severity/engine.py, pdf_gen/referral.py
- Commit: [w2/d13] full app.py integration
