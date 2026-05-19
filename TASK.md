# TASK — May 25, 2026 | Week 2 / Day 8

## TODAY'S GOAL
Write the voice transcription pipeline using faster-whisper — Bengali audio in,
clean Bengali transcript out. This is the first half of the voice pipeline
(transcription only — Gemini extraction comes Day 9).

## CONTEXT
- Week 1 complete: Model ✓ | GradCAM ✓ | Severity ✓ | HF Space ✓ | PDF ✓ | 53 tests green
- voice/pipeline.py does NOT exist yet — voice/__init__.py is the only file
- faster-whisper is already in requirements.txt ✓
- packages.txt already has ffmpeg ✓ (needed by faster-whisper)
- Gemini API key NOT needed today — transcription only, no LLM yet
- Do NOT touch today: model/, severity/, pdf_gen/, rag/, app.py

---

## PIPELINE SPEC (from CLAUDE.md — implement EXACTLY)

```
Bengali audio → faster-whisper (base model, language="bn") → Bengali transcript string
```

The transcript feeds into:
- Signal 4 of severity engine (keyword escalation)
- Gemini extraction (Day 9)
- Referral Section 1 (via patient_history JSON)

---

## TASKS (in order)

### TASK 1 — Write voice/pipeline.py (transcription function only)

#### Function signature:
```python
def transcribe_audio(audio_bytes: bytes, fmt: str = "wav") -> str:
```
Returns: Bengali transcript string (may be empty string if silent/failed).

#### Requirements:
- Model: `faster-whisper` — use `WhisperModel("base", device="cpu", compute_type="int8")`
- Language: force `language="bn"` (Bengali) — do NOT use auto-detect
- Input: raw audio bytes (from Streamlit mic recorder or file upload)
- Supported formats: wav, mp3, webm — write bytes to a temp file, pass path to whisper
- Use `tempfile.NamedTemporaryFile` with correct suffix (`.wav`, `.mp3`, `.webm`)
- Return concatenated transcript from all segments: `" ".join(seg.text for seg in segments)`
- On any exception: log the error, return `""` — never crash
- Model loading: use module-level lazy load (load once, reuse) — wrap in a
  function `_get_model()` so it only loads when first called

#### File structure:
```python
# voice/pipeline.py

from faster_whisper import WhisperModel
import tempfile, os, logging

logger = logging.getLogger(__name__)

_model = None

def _get_model() -> WhisperModel:
    # load once, reuse across calls
    ...

def transcribe_audio(audio_bytes: bytes, fmt: str = "wav") -> str:
    # write bytes to temp file, run whisper, return transcript
    ...
```

#### Do NOT add today:
- `extract_patient_history()` — that's Day 9 (needs Gemini API key)
- Any Streamlit UI wiring — that's Day 12

### TASK 2 — Install faster-whisper locally for testing
```
python -m pip install faster-whisper
```
Note: faster-whisper downloads the model (~150MB) on first use — this is expected.
The model is cached in ~/.cache/huggingface/ and NOT committed to git.

### TASK 3 — Write tests/test_voice.py

Test cases (no real audio needed — use synthetic silent WAV bytes):

```python
# Helper: generate a minimal valid WAV file in memory (silent, 1 second)
# Use Python's built-in `wave` module — no external deps needed

# Test 1: transcribe_audio returns str type
# Test 2: transcribe_audio with silent audio returns str (not None, not crash)
# Test 3: transcribe_audio with wav format — no exception raised
# Test 4: transcribe_audio with mp3 format bytes — no exception raised
# Test 5: transcribe_audio with webm format bytes — no exception raised
# Test 6: transcribe_audio with empty bytes — returns "" gracefully (no crash)
# Test 7: _get_model() returns a WhisperModel instance
# Test 8: _get_model() called twice returns the same object (singleton)
```

**Important:** faster-whisper model downloads ~150MB on first test run.
Mark slow tests with `@pytest.mark.slow` so they can be skipped in CI:
```
pytest tests/test_voice.py -v -m "not slow"   # skip model download
pytest tests/test_voice.py -v                  # run everything
```

### TASK 4 — Run tests
```
pytest tests/test_voice.py -v
```
All tests must pass.

### TASK 5 — Run full suite to confirm no regressions
```
pytest tests/ -v
```
Must still show 53 + new voice tests all passing.

### TASK 6 — Commit and push
```
git add voice/pipeline.py tests/test_voice.py
git commit -m "[w2/d8] faster-whisper Bengali transcription"
git push origin main
git push hf main
```
Note: for HF push use the token as password (no binary files today, should push cleanly).

---

## DEFINITION OF DONE
- [ ] voice/pipeline.py exists with transcribe_audio(audio_bytes, fmt) → str
- [ ] faster-whisper base model, language="bn", device="cpu", compute_type="int8"
- [ ] Handles wav / mp3 / webm via temp file
- [ ] Empty/bad audio returns "" — never raises
- [ ] _get_model() singleton — loads once
- [ ] tests/test_voice.py — all tests pass
- [ ] Full suite (pytest tests/ -v) still green
- [ ] Committed and pushed to GitHub + HF Space

---

## NEXT SESSION (Day 9 — May 26)
- Add extract_patient_history(transcript) → dict to voice/pipeline.py
- Uses Gemini 1.5 Flash to extract 9-field patient JSON from Bengali transcript
- 3-retry logic for API failures
- **Needs: GEMINI_API_KEY** — set in .env before starting Day 9
- Commit: [w2/d9] Gemini JSON symptom extraction
