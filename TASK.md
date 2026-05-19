# TASK — May 23, 2026 | Week 1 / Day 6

## TODAY'S GOAL
Write the 4-section PDF referral letter generator and a smoke test that confirms
the PDF builds correctly — Bengali font included, zero manual input required.

## CONTEXT
- Day 5 complete: HF Space live at https://huggingface.co/spaces/rafilovestosuffer/skinai-bangladesh
- pdf_gen/__init__.py exists — pdf_gen/referral.py does NOT exist yet
- reportlab is already in requirements.txt ✓
- The PDF must work from session_state data only — single button, zero manual input
- Bengali font: Noto Sans Bengali — must be registered with reportlab
- Do NOT touch today: model/, severity/, voice/, rag/, app.py

---

## REFERRAL LETTER SPEC (from CLAUDE.md — implement EXACTLY)

4 sections, each sourced from a different pipeline stage:

| Section | Data Source | Key Fields |
|---------|-------------|------------|
| 1. Patient History | Gemini JSON (voice pipeline) | chief_complaint, symptoms, affected_area, duration, progression, previous_treatment |
| 2. Clinical Observation | GradCAM++ output | heatmap image (embedded), coverage_pct, assessment datetime |
| 3. AI Diagnostic Assessment | BD-SkinNet output | disease (English+Bengali), confidence %, differential if top2 > 15%, model name, disclaimer |
| 4. Triage Recommendation | Severity engine | tier, urgency_label, action, facility, Bengali instruction text |

**Differential diagnosis rule:** If top2[1].confidence > 0.15 → show differential in Section 3.
**Tier 3 only:** inject nearest hospital name+address into Section 4.

---

## TASKS (in order)

### TASK 1 — Write pdf_gen/referral.py

#### Function signature:
```python
def generate_referral_pdf(session_data: dict) -> bytes:
```
Returns raw PDF bytes (use `io.BytesIO` — no file written to disk).

#### session_data keys it must accept:
```python
{
    # Section 1 — Patient History
    "patient_name": str,
    "patient_age": str,
    "chief_complaint": str,
    "symptoms": list[str],
    "affected_area": str,
    "duration": str,
    "progression": str,
    "previous_treatment": str,

    # Section 2 — Clinical Observation
    "heatmap": np.ndarray | None,   # H×W×3 uint8 overlay image (or None)
    "coverage_pct": float,

    # Section 3 — AI Diagnostic Assessment
    "disease_class": str,           # e.g. "Tinea"
    "disease_bengali": str,         # e.g. "দাদ (টিনিয়া)"
    "confidence": float,            # 0.0–1.0
    "top2": list[dict],             # [{"class": str, "confidence": float}, ...]

    # Section 4 — Triage Recommendation
    "tier": int,                    # 1 | 2 | 3
    "urgency_label": str,
    "action": str,
    "facility": str,
    "bengali_text": str,
    "hospital_name": str | None,    # Tier 3 only
    "hospital_address": str | None, # Tier 3 only
}
```

#### PDF structure requirements:
- **Header:** "SkinAI Bangladesh — AI Referral Letter" + generation datetime
- **Section 1 — Patient History**
  - Table: field label (Bengali + English) | value
  - Fields: Name, Age, Chief Complaint, Symptoms (comma-joined), Affected Area,
    Duration, Progression, Previous Treatment
- **Section 2 — Clinical Observation**
  - GradCAM heatmap image embedded (if heatmap is not None, resize to ~300px wide)
  - If heatmap is None: placeholder text "Image not provided"
  - Bengali caption: "লাল এলাকা মডেলের মনোযোগের কেন্দ্র"
  - Coverage: "Lesion coverage: {coverage_pct:.1f}%"
  - Assessment datetime
- **Section 3 — AI Diagnostic Assessment**
  - Primary: "{disease_class} ({disease_bengali}) — {confidence:.1%} confidence"
  - Differential: if top2[1]["confidence"] > 0.15 → show "Differential: {class} ({conf:.1%})"
  - Model: "Model: BD-SkinNet (Swin-B + CBAM, INT8) | F1 = 92.46%"
  - Disclaimer: "This is an AI-assisted screening tool, not a medical diagnosis."
- **Section 4 — Triage Recommendation**
  - Tier badge: NON-URGENT (green) | ROUTINE (orange) | URGENT (red)
  - English action text
  - Bengali instruction text
  - Facility type
  - If tier == 3 and hospital_name: "Nearest Hospital: {name} — {address}"
- **Footer:** "Not a medical device. Always consult a licensed physician."

#### Technical requirements:
- Use `reportlab.platypus` (SimpleDocTemplate, Table, Paragraph, Image, Spacer)
- Register Noto Sans Bengali font for Bengali text rendering
  - Font file: download at runtime if not present, or use a fallback
  - Simplest approach: use `reportlab`'s built-in fonts for English sections,
    register `NotoSansBengali-Regular.ttf` for Bengali strings only
  - Font download: https://fonts.google.com/download?family=Noto+Sans+Bengali
    → save to pdf_gen/fonts/NotoSansBengali-Regular.ttf
- Return `io.BytesIO.getvalue()` as bytes

### TASK 2 — Download Noto Sans Bengali font
- [ ] Create pdf_gen/fonts/ directory
- [ ] Download NotoSansBengali-Regular.ttf into pdf_gen/fonts/
- [ ] Add pdf_gen/fonts/*.ttf to .gitignore? NO — keep it tracked so HF Space has it

### TASK 3 — Write tests/test_pdf.py
Test cases (smoke tests — no real model output needed, use dummy session_data):

```python
# Test 1: PDF generates without error, returns bytes, size > 0
# Test 2: Returns bytes type (not str, not None)
# Test 3: Tier 1 case — NON-URGENT PDF generates
# Test 4: Tier 3 case with hospital — hospital name appears in output
# Test 5: heatmap=None case — PDF still generates (no crash)
# Test 6: top2 differential > 0.15 — no crash
# Test 7: top2 differential <= 0.15 — no crash
```

Use dummy data — no model, no checkpoint, no real image required.

### TASK 4 — Run tests
```
pytest tests/test_pdf.py -v
```
All tests must pass.

### TASK 5 — Commit and push
```
git add pdf_gen/referral.py pdf_gen/fonts/ tests/test_pdf.py
git commit -m "[w1/d6] referral letter PDF generator"
git push origin main
git push hf main
```

---

## DEFINITION OF DONE
- [ ] pdf_gen/referral.py exists with generate_referral_pdf(session_data) → bytes
- [ ] All 4 sections present in output
- [ ] Bengali text renders (Noto Sans Bengali font registered)
- [ ] Differential shown only when top2[1].confidence > 0.15
- [ ] Tier 3 hospital injection works
- [ ] heatmap=None does not crash
- [ ] tests/test_pdf.py — all tests pass with pytest -v
- [ ] Committed and pushed to GitHub + HF Space

---

## NEXT SESSION (Day 7 — May 24)
- Run full test suite: pytest tests/ -v — all green across all modules
- Verify HF Space still live and showing Bengali UI
- Write TASK.md for Week 2
- W1 DONE: Model ✓ | GradCAM ✓ | Severity ✓ | HF Space ✓ | PDF ✓
