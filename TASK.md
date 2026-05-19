# TASK — May 28, 2026 | Week 2 / Day 11

## TODAY'S GOAL
Write rag/retriever.py — FAISS query + Gemini answer.
Implement answer_question(question, context) → str.
Write tests/test_rag.py with mocked FAISS and Gemini.

## CONTEXT
- Day 10 complete: 100 knowledge chunks in rag/knowledge/, rag/build_index.py done
- Full suite: 78/78 passing
- HF Hub access blocked locally (network issue) — build_index.py tested via FAISS path only
- On HF Space, build_index.py will download the model and build the real index at startup
- Do NOT touch today: model/, severity/, pdf_gen/, voice/, app.py

---

## MODULE SPEC: rag/retriever.py

```python
# rag/retriever.py
# Provides: load_index(), answer_question(question, lang)

# Index is built at HF Space startup via build_index.py
# rag/faiss_index.bin + rag/chunks_metadata.json must exist before calling

import json, os, faiss, numpy as np
from sentence_transformers import SentenceTransformer  # or AutoModel fallback
from google import genai

INDEX_PATH = "rag/faiss_index.bin"
METADATA_PATH = "rag/chunks_metadata.json"
EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L6-v2"
TOP_K = 5

# Singletons
_index = None
_metadata = None
_embed_model = None
_gemini_client = None

def load_index() -> bool:
    """Load FAISS index + metadata. Returns True if successful."""
    ...

def _embed_query(text: str) -> np.ndarray:
    """Embed a single query string → normalized float32 array shape (1, dim)."""
    ...

def retrieve(question: str, top_k: int = TOP_K) -> list[dict]:
    """Return top_k chunks most relevant to question."""
    ...

def answer_question(question: str, lang: str = "en") -> str:
    """
    RAG pipeline: embed question → retrieve top-k → Gemini answer.
    lang: "en" or "bn" (Bengali) — match user's language.
    Always returns a string. Returns a fallback message if anything fails.
    """
    ...
```

### Gemini prompt for RAG answer:
```
You are a medical information assistant for a Bangladesh skin disease app.
Answer the patient's question using ONLY the provided context.
Do NOT recommend specific medications. Refer to a doctor for diagnosis.
If the answer is not in the context, say so honestly.
Answer in {lang_label} language.

Context:
{top_k_chunks_joined}

Question: {question}

Answer:
```

### Language detection:
Use langdetect or simple heuristic: if question contains Bengali Unicode characters
(range ঀ–৿), answer in Bengali (lang="bn"), else English (lang="en").

---

## TASKS (in order)

### TASK 1 — Write rag/retriever.py
Key requirements:
- Singleton pattern for index, metadata, embed_model, gemini_client (load once)
- load_index() returns False if index file doesn't exist (not an error — first run)
- answer_question() always returns a str — never raises
- 3-retry on Gemini call (same pattern as voice/pipeline.py)
- Fallback message: "দুঃখিত, এই প্রশ্নের উত্তর দিতে পারছি না।" (Bengali) or "Sorry, I could not find an answer." (English)
- Match voice/pipeline.py pattern for Gemini client singleton

### TASK 2 — Write tests/test_rag.py
Tests to write (all mocked — no real API calls, no real model download):
1. TestLoadIndex:
   - test_load_index_missing_files → returns False when files don't exist
   - test_load_index_success → returns True when files exist (mock faiss.read_index)
2. TestRetrieve:
   - test_retrieve_returns_list → returns list of dicts
   - test_retrieve_top_k → respects top_k parameter
   - test_retrieve_has_required_keys → each result has filename, source, topic, text
3. TestAnswerQuestion:
   - test_answer_returns_string → always returns str
   - test_answer_empty_question → handles empty string input
   - test_answer_bengali_detection → detects Bengali input and sets lang="bn"
   - test_answer_fallback_on_gemini_failure → returns fallback when Gemini fails
   - test_answer_fallback_on_index_missing → returns fallback when index not loaded
   - test_answer_no_medicine_recommendation → Gemini prompt contains "Do NOT recommend"
4. TestGeminiPrompt:
   - test_prompt_includes_context → retrieved chunks appear in prompt
   - test_prompt_includes_question → question appears in prompt

Target: 12+ tests, all passing.

### TASK 3 — Run tests
```
pytest tests/test_rag.py -v
```
All tests must pass. Do NOT run the full test suite today (FAISS model download required for integration).

### TASK 4 — Commit and push
```
git add rag/retriever.py tests/test_rag.py
git commit -m "[w2/d11] FAISS retriever + Gemini RAG + tests"
git push origin main
```
Push to HF Space using clean branch strategy.

---

## DEFINITION OF DONE
- [ ] rag/retriever.py implemented (load_index, retrieve, answer_question)
- [ ] answer_question always returns str, never raises
- [ ] Gemini prompt says "Do NOT recommend specific medications"
- [ ] 12+ tests in tests/test_rag.py, all passing
- [ ] Committed and pushed to GitHub and HF Space

---

## NEXT SESSION (Day 12 — May 29)
- Write ui/components.py — reusable Streamlit widgets
- Write ui/styles.py — Bengali Noto Sans CSS injection
- Commit: [w2/d12] UI components + styles
