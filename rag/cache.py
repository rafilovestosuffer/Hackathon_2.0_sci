"""
rag/cache.py
SHA-256 keyed disk cache for RAG answers.

Stores (question_hash → answer_text) in rag/rag_cache.json.
Reduces Gemini API calls for repeated questions — identical question +
disease context + language always returns the cached answer instantly.

No patient data stored — only (hash → answer_string) mappings.
Cache is bounded to MAX_ENTRIES; oldest 10% pruned when full.
"""
import hashlib
import json
import logging
import os

logger = logging.getLogger(__name__)

_CACHE_PATH = os.path.join(os.path.dirname(__file__), "rag_cache.json")
_MAX_ENTRIES = 500


def _load() -> dict:
    if not os.path.exists(_CACHE_PATH):
        return {}
    try:
        with open(_CACHE_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save(cache: dict) -> None:
    try:
        with open(_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception as exc:
        logger.debug("cache._save skipped (non-critical): %s", exc)


def make_key(question: str, disease_context: str = "", lang: str = "en") -> str:
    """SHA-256 of normalised (question | disease_context | lang)."""
    raw = f"{question.strip().lower()}|{disease_context.strip().lower()}|{lang}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def get(key: str) -> str | None:
    """Return cached answer string, or None if not cached."""
    return _load().get(key)


def put(key: str, value: str) -> None:
    """Store answer. Prunes oldest 10% if MAX_ENTRIES reached."""
    cache = _load()
    if len(cache) >= _MAX_ENTRIES:
        prune_count = _MAX_ENTRIES // 10
        for k in list(cache.keys())[:prune_count]:
            del cache[k]
    cache[key] = value
    _save(cache)


def size() -> int:
    """Return number of cached entries."""
    return len(_load())
