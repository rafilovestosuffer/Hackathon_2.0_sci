"""
RAG retriever: keyword search + Gemini answer.

Primary path: BM25-lite keyword retrieval directly from .txt files (no downloads needed).
Optional upgrade: FAISS semantic search if faiss_index.bin exists.

Provides: load_index(), retrieve(), answer_question()
"""

import json
import logging
import math
import os
import re
from collections import Counter

from dotenv import load_dotenv
from google import genai

load_dotenv()

logger = logging.getLogger(__name__)

KNOWLEDGE_DIR = os.path.join(os.path.dirname(__file__), "knowledge")
INDEX_PATH = os.path.join(os.path.dirname(__file__), "faiss_index.bin")
METADATA_PATH = os.path.join(os.path.dirname(__file__), "chunks_metadata.json")
EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L6-v2"
TOP_K = 5

_BENGALI_FALLBACK = "দুঃখিত, এই প্রশ্নের উত্তর দিতে পারছি না।"
_ENGLISH_FALLBACK = "Sorry, I could not find an answer."

_PROMPT_TEMPLATE = """\
You are SkinAI Bangladesh — a helpful medical information assistant for rural Bangladesh.
A patient has asked: "{question}"

Your task:
1. Use the medical context below to give a clear, helpful answer about the skin condition mentioned.
2. The context is in English — if the patient asked in Bengali or asked for a Bengali answer, translate your answer into natural Bengali (বাংলা).
3. Always explain what the condition is, what causes it, and when to see a doctor.
4. Do NOT recommend specific medication names. Do NOT make a diagnosis.
5. Keep the answer concise — 3 to 5 sentences.

{disease_note}
Medical context (CDC · NIH · WHO · DGHS Bangladesh):
{context}

Answer in {lang_label}:\
"""

# Romanized Bengali keywords — signal Bengali reply AND are stripped before BM25 search
_ROMANIZED_BN_TRIGGERS = {
    "bangla", "banglai", "bengali", "bolo", "bolun", "ki",
    "ami", "apni", "amar", "apnar", "rog", "janai", "janate",
    "kora", "kore", "hobe", "hobey", "chai", "chahi", "bolte",
    "somporkay", "somporke", "niye", "keno", "kothay",
}

# ── Singletons ────────────────────────────────────────────────────────────────
_chunks: list[dict] = []          # raw chunks from .txt files — always populated
_index = None                     # faiss.Index — optional
_metadata: list[dict] | None = None
_embed_model = None
_gemini_client: genai.Client | None = None
_idf: dict[str, float] = {}       # precomputed IDF for BM25


# ── Keyword helpers ───────────────────────────────────────────────────────────

def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zঀ-৿]+", text.lower())


def _search_tokens(question: str) -> list[str]:
    """Return BM25 search tokens: strip Romanized Bengali filler so medical terms dominate."""
    tokens = _tokenize(question)
    cleaned = [t for t in tokens if t not in _ROMANIZED_BN_TRIGGERS]
    return cleaned if cleaned else tokens  # fallback: use all tokens if nothing remains


def _build_idf(chunks: list[dict]) -> dict[str, float]:
    N = len(chunks)
    df: Counter = Counter()
    for c in chunks:
        for tok in set(_tokenize(c.get("text", ""))):
            df[tok] += 1
    return {tok: math.log((N - f + 0.5) / (f + 0.5) + 1) for tok, f in df.items()}


def _bm25_score(query_tokens: list[str], chunk_text: str, k1: float = 1.5, b: float = 0.75) -> float:
    avg_dl = sum(len(_tokenize(c.get("text", ""))) for c in _chunks) / max(len(_chunks), 1)
    tokens = _tokenize(chunk_text)
    dl = len(tokens)
    tf_map = Counter(tokens)
    score = 0.0
    for tok in query_tokens:
        if tok not in _idf:
            continue
        tf = tf_map.get(tok, 0)
        score += _idf[tok] * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * dl / max(avg_dl, 1)))
    return score


# ── Load chunks from .txt files ───────────────────────────────────────────────

def _load_chunks_from_files() -> list[dict]:
    chunks = []
    if not os.path.isdir(KNOWLEDGE_DIR):
        return chunks
    for fname in sorted(os.listdir(KNOWLEDGE_DIR)):
        if not fname.endswith(".txt"):
            continue
        path = os.path.join(KNOWLEDGE_DIR, fname)
        try:
            with open(path, encoding="utf-8") as f:
                raw = f.read().strip()
        except Exception:
            continue
        source, topic, body = "", "", raw
        if "---" in raw:
            header, _, body = raw.partition("---")
            for line in header.splitlines():
                if line.startswith("SOURCE:"):
                    source = line.split(":", 1)[1].strip()
                elif line.startswith("TOPIC:"):
                    topic = line.split(":", 1)[1].strip()
        chunks.append({
            "filename": fname,
            "source": source,
            "topic": topic,
            "text": raw,
        })
    return chunks


# ── Optional FAISS upgrade ────────────────────────────────────────────────────

def _try_load_faiss() -> bool:
    global _index, _metadata, _embed_model
    if not os.path.exists(INDEX_PATH) or not os.path.exists(METADATA_PATH):
        return False
    try:
        import faiss as _faiss
        import numpy as np
        from sentence_transformers import SentenceTransformer

        _index = _faiss.read_index(INDEX_PATH)
        with open(METADATA_PATH, encoding="utf-8") as f:
            _metadata = json.load(f)

        class _STWrapper:
            def __init__(self):
                self._model = SentenceTransformer(EMBED_MODEL)
            def encode(self, texts):
                emb = self._model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
                norms = np.linalg.norm(emb, axis=1, keepdims=True)
                norms = np.where(norms == 0, 1, norms)
                return (emb / norms).astype("float32")

        _embed_model = _STWrapper()
        logger.info("FAISS semantic search loaded: %d vectors.", _index.ntotal)
        return True
    except Exception as exc:
        logger.warning("FAISS/ST load failed (%s) — using BM25 keyword search.", exc)
        _index = None
        _metadata = None
        _embed_model = None
        return False


# ── Gemini ────────────────────────────────────────────────────────────────────

def _get_gemini_client() -> genai.Client:
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY", ""))
    return _gemini_client


# ── Public API ────────────────────────────────────────────────────────────────

def load_index() -> bool:
    """
    Load knowledge base. Always returns True if any .txt files exist.
    Optionally upgrades to FAISS semantic search if index files are present.
    Never raises.
    """
    global _chunks, _idf

    try:
        _chunks = _load_chunks_from_files()
        if not _chunks:
            logger.warning("No knowledge .txt files found in %s", KNOWLEDGE_DIR)
            return False
        _idf = _build_idf(_chunks)
        logger.info("BM25 index ready: %d chunks from knowledge files.", len(_chunks))
    except Exception as exc:
        logger.error("Failed to load knowledge files: %s", exc)
        return False

    # Try to upgrade to FAISS (best-effort, non-blocking)
    _try_load_faiss()
    return True


def _detect_lang(text: str) -> str:
    # Unicode Bengali script — definitive
    if any("ঀ" <= ch <= "৿" for ch in text):
        return "bn"
    # Romanized Bengali: user typed in Latin script but wants Bengali reply
    words = set(re.findall(r"[a-z]+", text.lower()))
    if words & _ROMANIZED_BN_TRIGGERS:
        return "bn"
    return "en"


def retrieve(question: str, top_k: int = TOP_K) -> list[dict]:
    """
    Return top_k most relevant chunks for question.
    Uses FAISS if available, otherwise BM25 keyword search.
    """
    if not question.strip():
        return []

    # FAISS path
    if _index is not None and _metadata is not None and _embed_model is not None:
        try:
            import numpy as np
            qvec = _embed_model.encode([question]).reshape(1, -1)
            k = min(top_k, len(_metadata))
            _scores, indices = _index.search(qvec, k)
            return [_metadata[i] for i in indices[0] if 0 <= i < len(_metadata)]
        except Exception as exc:
            logger.warning("FAISS search failed, falling back to BM25: %s", exc)

    # BM25 keyword path — always works
    if not _chunks:
        return []
    query_tokens = _search_tokens(question)  # strips Romanized Bengali filler words
    scored = [(
        _bm25_score(query_tokens, c.get("text", "")),
        i,
        c,
    ) for i, c in enumerate(_chunks)]
    scored.sort(key=lambda x: -x[0])
    return [c for _, _, c in scored[:top_k] if _ > 0] or [c for _, _, c in scored[:top_k]]


def answer_question(
    question: str,
    lang: str | None = None,
    disease_context: str | None = None,
) -> str:
    """
    Full RAG pipeline: retrieve top-k chunks → Gemini answer.
    Always returns a str. Never raises.
    """
    if not question or not question.strip():
        return _ENGLISH_FALLBACK

    if lang is None:
        lang = _detect_lang(question)

    fallback = _BENGALI_FALLBACK if lang == "bn" else _ENGLISH_FALLBACK
    lang_label = "Bengali (বাংলা)" if lang == "bn" else "English"

    if not _chunks:
        logger.warning("answer_question called before load_index().")
        return fallback

    chunks = retrieve(question)
    if not chunks:
        return fallback

    context = "\n\n---\n\n".join(
        f"[{c.get('source', '')} | {c.get('topic', '')}]\n{c.get('text', '')}"
        for c in chunks
    )
    disease_note = (
        f"The patient has been diagnosed with: {disease_context}\n"
        if disease_context
        else ""
    )
    prompt = _PROMPT_TEMPLATE.format(
        lang_label=lang_label,
        context=context,
        question=question.strip(),
        disease_note=disease_note,
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
