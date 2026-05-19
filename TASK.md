# TASK — May 26, 2026 | Week 2 / Day 9

## TODAY'S GOAL
Add Gemini 1.5 Flash symptom extraction to voice/pipeline.py —
Bengali transcript in, structured 9-field patient history JSON out.
This completes the full voice pipeline (transcription + extraction).

## CONTEXT
- Day 8 complete: voice/pipeline.py (transcribe_audio) + tests/test_voice.py (10/10)
- Full suite: 63/63 passing
- TODAY adds extract_patient_history() to the SAME voice/pipeline.py file
- GEMINI_API_KEY is required — must be in .env before starting
- Do NOT touch today: model/, severity/, pdf_gen/, rag/, app.py

---

## PRE-FLIGHT CHECK (do this before writing any code)
- [ ] Confirm .env file exists with GEMINI_API_KEY=your_key_here
- [ ] Run: python -c "import google.generativeai; print('ok')"
  If ModuleNotFoundError → python -m pip install google-generativeai

---

## PIPELINE SPEC (from CLAUDE.md — implement EXACTLY)

```
Bengali transcript → Gemini 1.5 Flash → patient_history JSON:
{
  "chief_complaint":      str,
  "symptoms":             list[str],
  "affected_area":        str,
  "duration":             str,
  "progression":          str,
  "previous_treatment":   str,
  "associated_symptoms":  list[str],
  "patient_name":         str,
  "patient_age":          str
}
```

---

## TASKS (in order)

### TASK 1 — Add extract_patient_history() to voice/pipeline.py

#### Function signature:
```python
def extract_patient_history(transcript: str) -> dict:
```
Returns: dict with all 9 fields. Missing fields default to `""` or `[]`.

#### Requirements:

**Gemini setup:**
- Load API key from environment: `os.getenv("GEMINI_API_KEY")`
- Model: `gemini-1.5-flash`
- Configure once at module level: `genai.configure(api_key=...)`

**Prompt — force JSON output with all 9 fields:**
```
You are a medical assistant. Extract patient history from this Bengali transcript.
Return ONLY valid JSON with exactly these keys:
{
  "chief_complaint": "",
  "symptoms": [],
  "affected_area": "",
  "duration": "",
  "progression": "",
  "previous_treatment": "",
  "associated_symptoms": [],
  "patient_name": "",
  "patient_age": ""
}
Fill each field from the transcript. Use empty string "" or empty list []
if information is not mentioned. Do not add any text outside the JSON.

Transcript: {transcript}
```

**3-retry logic:**
```python
for attempt in range(3):
    try:
        response = model.generate_content(prompt)
        data = json.loads(response.text.strip())
        return _validate_fields(data)
    except Exception as exc:
        logger.warning("Gemini attempt %d failed: %s", attempt + 1, exc)
        if attempt == 2:
            return _empty_history()
```

**_validate_fields(data):** ensure all 9 keys exist — fill missing ones with
`""` or `[]`. Never let a missing key crash downstream code.

**_empty_history():** returns the dict with all 9 keys set to `""` / `[]`.
Used as fallback on total API failure.

**JSON extraction:** Gemini sometimes wraps JSON in ```json ... ``` fences.
Strip them before `json.loads()`:
```python
text = response.text.strip()
if text.startswith("```"):
    text = text.split("```")[1]
    if text.startswith("json"):
        text = text[4:]
text = text.strip()
```

### TASK 2 — Write tests/test_voice_gemini.py

Use `unittest.mock.patch` to mock the Gemini API — no real API calls in tests.

```python
# Test 1: extract_patient_history returns dict
# Test 2: all 9 required keys present in return value
# Test 3: symptoms and associated_symptoms are lists
# Test 4: valid JSON from Gemini is parsed correctly
# Test 5: JSON wrapped in ```json fences is handled
# Test 6: Gemini returns invalid JSON → returns _empty_history() (no crash)
# Test 7: Gemini raises exception → retries → returns _empty_history()
# Test 8: missing keys in Gemini response are filled with defaults
# Test 9: empty transcript → returns _empty_history() gracefully
# Test 10: patient_name and patient_age are strings (not lists)
```

Mock target: `google.generativeai.GenerativeModel.generate_content`

### TASK 3 — Run tests
```
pytest tests/test_voice_gemini.py -v
```
All 10 tests must pass (mocked — no real API calls, no key needed for tests).

### TASK 4 — Manual smoke test (requires real API key)
```python
python -c "
from voice.pipeline import extract_patient_history
result = extract_patient_history('আমার হাতে চুলকানি এবং লাল দাগ আছে, দুই সপ্তাহ ধরে')
print(result)
"
```
Confirm: chief_complaint, affected_area, duration filled from the Bengali input.

### TASK 5 — Run full suite
```
pytest tests/ -v
```
Must show 63 + 10 new = 73 tests all passing.

### TASK 6 — Commit and push
```
git add voice/pipeline.py tests/test_voice_gemini.py
git commit -m "[w2/d9] Gemini JSON symptom extraction"
git push origin main
# HF push via clean branch (same pattern as previous days)
```

---

## DEFINITION OF DONE
- [ ] extract_patient_history(transcript) → dict in voice/pipeline.py
- [ ] All 9 fields always present in output (no KeyError possible downstream)
- [ ] 3-retry logic implemented
- [ ] JSON fence stripping implemented
- [ ] _empty_history() fallback on total failure
- [ ] tests/test_voice_gemini.py — 10/10 passing (mocked)
- [ ] Full suite 73/73 passing
- [ ] Committed and pushed

---

## NEXT SESSION (Day 10 — May 27)
- Build the RAG knowledge base — chunk CDC/NIH/WHO/DGHS text into rag/knowledge/
- Target: 100–200 chunks, 100–300 words each
- No API key needed for Day 10 (chunking is offline)
- Commit: [w2/d10] knowledge base chunks (CDC/NIH/WHO/DGHS)
