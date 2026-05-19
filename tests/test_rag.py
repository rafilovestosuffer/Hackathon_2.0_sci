"""
Tests for rag/retriever.py — all mocked, no real API calls, no model download.
"""

import json
import os
import types
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

import rag.retriever as retriever


# ── Fixtures ─────────────────────────────────────────────────────────────────

FAKE_METADATA = [
    {"filename": "cdc_tinea_01.txt", "source": "CDC", "topic": "Tinea Overview",
     "text": "SOURCE: CDC\nTOPIC: Tinea Overview\n---\nRingworm is a fungal infection."},
    {"filename": "who_scabies_01.txt", "source": "WHO", "topic": "Scabies NTD",
     "text": "SOURCE: WHO\nTOPIC: Scabies NTD\n---\nScabies is a neglected tropical disease."},
    {"filename": "dghs_tinea_bd_01.txt", "source": "DGHS", "topic": "Tinea in Bangladesh",
     "text": "SOURCE: DGHS\nTOPIC: Tinea BD\n---\nTinea is common in Bangladesh climate."},
]


def _make_fake_index(n=3, dim=384):
    """Return a real FAISS IndexFlatIP with random vectors."""
    import faiss
    idx = faiss.IndexFlatIP(dim)
    vecs = np.random.randn(n, dim).astype("float32")
    vecs /= np.linalg.norm(vecs, axis=1, keepdims=True)
    idx.add(vecs)
    return idx


def _install_fake_state():
    """Inject fake BM25 state so tests don't need real .txt files or a model download."""
    retriever._chunks = FAKE_METADATA.copy()
    retriever._idf = retriever._build_idf(FAKE_METADATA)
    # Also wire up FAISS state for tests that explicitly test the FAISS path
    retriever._index = _make_fake_index(len(FAKE_METADATA))
    retriever._metadata = FAKE_METADATA.copy()

    class _FakeEmbedModel:
        def encode(self, texts):
            dim = 384
            vecs = np.random.randn(len(texts), dim).astype("float32")
            vecs /= np.linalg.norm(vecs, axis=1, keepdims=True)
            return vecs

    retriever._embed_model = _FakeEmbedModel()


def _clear_state():
    retriever._index = None
    retriever._metadata = None
    retriever._embed_model = None
    retriever._gemini_client = None
    retriever._chunks = []
    retriever._idf = {}


# ── TestLoadIndex ─────────────────────────────────────────────────────────────

class TestLoadIndex:
    def setup_method(self):
        _clear_state()

    def _make_knowledge_dir(self, tmp_path) -> str:
        """Create a temp knowledge dir with fake .txt files."""
        kdir = tmp_path / "knowledge"
        kdir.mkdir()
        for i, chunk in enumerate(FAKE_METADATA):
            f = kdir / chunk["filename"]
            f.write_text(
                f"SOURCE: {chunk['source']}\nTOPIC: {chunk['topic']}\n---\n{chunk['text']}",
                encoding="utf-8",
            )
        return str(kdir)

    def test_load_index_missing_files_returns_false(self, tmp_path):
        empty_dir = tmp_path / "empty_knowledge"
        empty_dir.mkdir()
        with patch.object(retriever, "KNOWLEDGE_DIR", str(empty_dir)):
            assert retriever.load_index() is False

    def test_load_index_missing_index_only_returns_false(self, tmp_path):
        # Without FAISS index, load_index still returns True (BM25 works from .txt files)
        kdir = self._make_knowledge_dir(tmp_path)
        with patch.object(retriever, "KNOWLEDGE_DIR", kdir), \
             patch.object(retriever, "INDEX_PATH", str(tmp_path / "nope.bin")), \
             patch.object(retriever, "METADATA_PATH", str(tmp_path / "nope.json")):
            result = retriever.load_index()
        assert result is True  # BM25 path works without FAISS

    def test_load_index_success_returns_true(self, tmp_path):
        kdir = self._make_knowledge_dir(tmp_path)
        with patch.object(retriever, "KNOWLEDGE_DIR", kdir):
            result = retriever.load_index()
        assert result is True
        assert len(retriever._chunks) == len(FAKE_METADATA)

    def test_load_index_sets_metadata(self, tmp_path):
        kdir = self._make_knowledge_dir(tmp_path)
        with patch.object(retriever, "KNOWLEDGE_DIR", kdir):
            retriever.load_index()
        assert len(retriever._chunks) == len(FAKE_METADATA)


# ── TestRetrieve ──────────────────────────────────────────────────────────────

class TestRetrieve:
    def setup_method(self):
        _clear_state()
        _install_fake_state()

    def test_retrieve_returns_list(self):
        results = retriever.retrieve("How to treat ringworm?")
        assert isinstance(results, list)

    def test_retrieve_not_empty(self):
        results = retriever.retrieve("ringworm treatment")
        assert len(results) > 0

    def test_retrieve_top_k_respected(self):
        results = retriever.retrieve("skin disease", top_k=2)
        assert len(results) <= 2

    def test_retrieve_top_k_1(self):
        results = retriever.retrieve("fungal infection", top_k=1)
        assert len(results) == 1

    def test_retrieve_has_required_keys(self):
        results = retriever.retrieve("scabies in Bangladesh")
        for chunk in results:
            assert "filename" in chunk
            assert "source" in chunk
            assert "topic" in chunk
            assert "text" in chunk

    def test_retrieve_returns_empty_when_no_chunks(self):
        _clear_state()  # clears _chunks too
        results = retriever.retrieve("any question")
        assert results == []

    def test_retrieve_returns_dicts(self):
        results = retriever.retrieve("eczema treatment")
        for r in results:
            assert isinstance(r, dict)


# ── TestAnswerQuestion ────────────────────────────────────────────────────────

class TestAnswerQuestion:
    def setup_method(self):
        _clear_state()
        _install_fake_state()

    def _mock_gemini(self, text="This is a helpful answer about skin disease."):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = text
        mock_client.models.generate_content.return_value = mock_response
        retriever._gemini_client = mock_client
        return mock_client

    def test_answer_returns_string(self):
        self._mock_gemini()
        result = retriever.answer_question("What is ringworm?")
        assert isinstance(result, str)

    def test_answer_not_empty(self):
        self._mock_gemini("Ringworm is caused by a fungus.")
        result = retriever.answer_question("What is ringworm?")
        assert len(result) > 0

    def test_answer_empty_question_returns_fallback(self):
        result = retriever.answer_question("")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_answer_whitespace_question_returns_fallback(self):
        result = retriever.answer_question("   ")
        assert isinstance(result, str)

    def test_answer_fallback_when_no_chunks(self):
        _clear_state()  # clears _chunks — no knowledge loaded
        result = retriever.answer_question("What is scabies?")
        assert isinstance(result, str)
        assert result in (retriever._ENGLISH_FALLBACK, retriever._BENGALI_FALLBACK)

    def test_answer_fallback_on_gemini_failure(self):
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = Exception("API error")
        retriever._gemini_client = mock_client
        result = retriever.answer_question("What is eczema?")
        assert isinstance(result, str)
        assert result == retriever._ENGLISH_FALLBACK

    def test_answer_bengali_input_returns_bengali_fallback_on_error(self):
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = Exception("fail")
        retriever._gemini_client = mock_client
        result = retriever.answer_question("এই রোগ কী?")
        assert result == retriever._BENGALI_FALLBACK

    def test_answer_english_input_detects_english(self):
        self._mock_gemini("English answer.")
        mock_client = retriever._gemini_client
        retriever.answer_question("What causes scabies?")
        call_args = mock_client.models.generate_content.call_args
        prompt = call_args[1]["contents"] if "contents" in call_args[1] else call_args[0][1]
        assert "English" in prompt

    def test_answer_bengali_input_detects_bengali(self):
        self._mock_gemini("বাংলায় উত্তর।")
        mock_client = retriever._gemini_client
        retriever.answer_question("দাদ রোগের চিকিৎসা কী?")
        call_args = mock_client.models.generate_content.call_args
        prompt = call_args[1]["contents"] if "contents" in call_args[1] else call_args[0][1]
        assert "Bengali" in prompt

    def test_answer_explicit_lang_overrides_detection(self):
        self._mock_gemini("Bengali answer.")
        mock_client = retriever._gemini_client
        retriever.answer_question("What is ringworm?", lang="bn")
        call_args = mock_client.models.generate_content.call_args
        prompt = call_args[1]["contents"] if "contents" in call_args[1] else call_args[0][1]
        assert "Bengali" in prompt

    def test_answer_with_disease_context_returns_string(self):
        self._mock_gemini("Scabies is treated by a doctor.")
        result = retriever.answer_question(
            "How serious is this?", disease_context="Scabies (38% confidence)"
        )
        assert isinstance(result, str)
        assert len(result) > 0

    def test_answer_none_disease_context_works(self):
        self._mock_gemini("Generic skin answer.")
        result = retriever.answer_question("What is eczema?", disease_context=None)
        assert isinstance(result, str)

    def test_answer_without_disease_context_no_injection(self):
        self._mock_gemini("Answer without context.")
        mock_client = retriever._gemini_client
        retriever.answer_question("What is tinea?", disease_context=None)
        call_args = mock_client.models.generate_content.call_args
        prompt = call_args[1]["contents"] if "contents" in call_args[1] else call_args[0][1]
        assert "The patient has been diagnosed with:" not in prompt


# ── TestGeminiPrompt ──────────────────────────────────────────────────────────

class TestGeminiPrompt:
    def setup_method(self):
        _clear_state()
        _install_fake_state()

    def _capture_prompt(self, question: str, lang: str = "en") -> str:
        """Call answer_question and capture the prompt sent to Gemini."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "test answer"
        mock_client.models.generate_content.return_value = mock_response
        retriever._gemini_client = mock_client
        retriever.answer_question(question, lang=lang)
        call_args = mock_client.models.generate_content.call_args
        return call_args[1]["contents"] if "contents" in call_args[1] else call_args[0][1]

    def test_prompt_contains_question(self):
        prompt = self._capture_prompt("What is scabies?")
        assert "What is scabies?" in prompt

    def test_prompt_contains_context(self):
        prompt = self._capture_prompt("tinea treatment")
        # At least one chunk's source or topic should appear
        assert any(c["source"] in prompt or c["topic"] in prompt for c in FAKE_METADATA)

    def test_prompt_no_medicine_recommendation(self):
        prompt = self._capture_prompt("What medicine for ringworm?")
        assert "Do NOT recommend" in prompt

    def test_prompt_refers_to_doctor(self):
        prompt = self._capture_prompt("Is this serious?")
        assert "doctor" in prompt.lower() or "Doctor" in prompt

    def test_prompt_only_from_context(self):
        prompt = self._capture_prompt("skin question")
        assert "ONLY the provided context" in prompt

    def test_prompt_contains_disease_context_when_provided(self):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "test answer"
        mock_client.models.generate_content.return_value = mock_response
        retriever._gemini_client = mock_client
        retriever.answer_question("Is this serious?", disease_context="Scabies (38% confidence)")
        call_args = mock_client.models.generate_content.call_args
        prompt = call_args[1]["contents"] if "contents" in call_args[1] else call_args[0][1]
        assert "Scabies (38% confidence)" in prompt
