"""
RAG retriever: FAISS query + Gemini answer.
Provides: load_index(), retrieve(), answer_question()

Index is built at HF Space startup via build_index.py.
rag/faiss_index.bin + rag/chunks_metadata.json must exist before calling load_index().
"""

import json
import logging
import os

import faiss
import numpy as np
from dotenv import load_dotenv
from google import genai

load_dotenv()

logger = logging.getLogger(__name__)

INDEX_PATH = os.path.join(os.path.dirname(__file__), "faiss_index.bin")
METADATA_PATH = os.path.join(os.path.dirname(__file__), "chunks_metadata.json")
EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L6-v2"
TOP_K = 5

_BENGALI_FALLBACK = "দুঃখিত, এই প্রশ্নের উত্তর দিতে পারছি না।"
_ENGLISH_FALLBACK = "Sorry, I could not find an answer."

_PROMPT_TEMPLATE = """\
You are a medical information assistant for a Bangladesh skin disease app.
Answer the patient's question using ONLY the provided context.
Do NOT recommend specific medications. Refer to a doctor for diagnosis.
If the answer is not in the context, say so honestly.
Answer in {lang_label} language.

Context:
{context}

Question: {question}

Answer:\
"""

# ── Singletons ────────────────────────────────────────────────────────────────
_index: faiss.Index | None = None
_metadata: list[dict] | None = None
_embed_model = None          # SentenceTransformer or AutoModel wrapper
_gemini_client: genai.Client | None = None


# ── Internal helpers ──────────────────────────────────────────────────────────

def _get_gemini_client() -> genai.Client:
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY", ""))
    return _gemini_client


def _load_embed_model():
    """Load embedding model; try SentenceTransformer first, fall back to AutoModel."""
    global _embed_model

    # SentenceTransformer path (preferred — works on HF Space)
    try:
        from sentence_transformers import SentenceTransformer

        class _STWrapper:
            def __init__(self):
                self._model = SentenceTransformer(EMBED_MODEL)

            def encode(self, texts: list[str]) -> np.ndarray:
                emb = self._model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
                norms = np.linalg.norm(emb, axis=1, keepdims=True)
                norms = np.where(norms == 0, 1, norms)
                return (emb / norms).astype("float32")

        _embed_model = _STWrapper()
        logger.info("Embedding model loaded via SentenceTransformer.")
        return
    except Exception as e:
        logger.warning("SentenceTransformer failed (%s); trying AutoModel.", e)

    # AutoModel fallback (works when sentence-transformers has version issues)
    import torch
    import torch.nn.functional as F
    from transformers import AutoModel, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(EMBED_MODEL)
    hf_model = AutoModel.from_pretrained(EMBED_MODEL)
    hf_model.eval()

    class _AutoModelWrapper:
        def __init__(self, tok, mod):
            self._tok = tok
            self._mod = mod

        def encode(self, texts: list[str]) -> np.ndarray:
            with torch.no_grad():
                enc = self._tok(texts, padding=True, truncation=True,
                                max_length=512, return_tensors="pt")
                out = self._mod(**enc)
                mask = enc["attention_mask"].unsqueeze(-1).expand(
                    out.last_hidden_state.size()).float()
                pooled = torch.sum(out.last_hidden_state * mask, 1) / \
                         torch.clamp(mask.sum(1), min=1e-9)
                normed = F.normalize(pooled, p=2, dim=1)
                return normed.cpu().numpy().astype("float32")

    _embed_model = _AutoModelWrapper(tokenizer, hf_model)
    logger.info("Embedding model loaded via AutoModel fallback.")


def _detect_lang(text: str) -> str:
    """Return 'bn' if text contains Bengali Unicode characters, else 'en'."""
    return "bn" if any("ঀ" <= ch <= "৿" for ch in text) else "en"


# ── Public API ────────────────────────────────────────────────────────────────

def load_index() -> bool:
    """
    Load FAISS index + chunk metadata into module singletons.
    Returns True on success, False if files don't exist yet.
    Never raises.
    """
    global _index, _metadata

    if not os.path.exists(INDEX_PATH) or not os.path.exists(METADATA_PATH):
        logger.warning("FAISS index or metadata not found — run build_index.py first.")
        return False

    try:
        _index = faiss.read_index(INDEX_PATH)
        with open(METADATA_PATH, encoding="utf-8") as f:
            _metadata = json.load(f)
        _load_embed_model()
        logger.info("RAG index loaded: %d chunks.", len(_metadata))
        return True
    except Exception as exc:
        logger.error("load_index failed: %s", exc)
        _index = None
        _metadata = None
        return False


def _embed_query(text: str) -> np.ndarray:
    """Embed a single query → float32 array shape (1, dim)."""
    emb = _embed_model.encode([text])
    return emb.reshape(1, -1)


def retrieve(question: str, top_k: int = TOP_K) -> list[dict]:
    """
    Return up to top_k chunks most semantically relevant to question.
    Returns empty list if index not loaded or on any error.
    """
    if _index is None or _metadata is None or _embed_model is None:
        return []
    try:
        query_vec = _embed_query(question)
        k = min(top_k, len(_metadata))
        _scores, indices = _index.search(query_vec, k)
        return [_metadata[i] for i in indices[0] if 0 <= i < len(_metadata)]
    except Exception as exc:
        logger.error("retrieve failed: %s", exc)
        return []


def answer_question(question: str, lang: str | None = None) -> str:
    """
    Full RAG pipeline: embed → retrieve top-k → Gemini answer.
    - lang: 'en' or 'bn'; if None, auto-detected from question.
    - Always returns a str. Never raises.
    """
    if not question or not question.strip():
        return _ENGLISH_FALLBACK

    if lang is None:
        lang = _detect_lang(question)

    fallback = _BENGALI_FALLBACK if lang == "bn" else _ENGLISH_FALLBACK
    lang_label = "Bengali (বাংলা)" if lang == "bn" else "English"

    if _index is None:
        logger.warning("answer_question called before load_index().")
        return fallback

    chunks = retrieve(question)
    if not chunks:
        return fallback

    context = "\n\n---\n\n".join(
        f"[{c.get('source', '')} | {c.get('topic', '')}]\n{c.get('text', '')}"
        for c in chunks
    )
    prompt = _PROMPT_TEMPLATE.format(
        lang_label=lang_label,
        context=context,
        question=question.strip(),
    )

    client = _get_gemini_client()
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            return response.text.strip()
        except Exception as exc:
            logger.warning("Gemini attempt %d failed: %s", attempt + 1, exc)

    return fallback
