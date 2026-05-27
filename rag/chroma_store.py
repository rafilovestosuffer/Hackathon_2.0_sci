"""
rag/chroma_store.py
ChromaDB persistent vector store for SkinAI Bangladesh knowledge chunks.

Builds and queries a ChromaDB collection from CDC/NIH/WHO/DGHS .txt files.
Persists to rag/chroma_db/ — survives HF Spaces restarts.
Falls back silently if chromadb is not installed or collection fails to load.

Collection : skinai_knowledge
Embeddings : intfloat/multilingual-e5-small (same model as FAISS path)
Distance   : cosine similarity (HNSW index)
"""
import logging
import os

logger = logging.getLogger(__name__)

_CHROMA_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")
_COLLECTION_NAME = "skinai_knowledge"
_EMBED_MODEL = "intfloat/multilingual-e5-small"
_BATCH_SIZE = 50

_client = None
_collection = None


def _get_collection():
    """
    Initialise ChromaDB PersistentClient + SentenceTransformer embedding function.
    Singleton — created once per process.
    """
    global _client, _collection
    if _collection is not None:
        return _collection

    import chromadb
    from chromadb.utils import embedding_functions

    os.makedirs(_CHROMA_PATH, exist_ok=True)
    _client = chromadb.PersistentClient(path=_CHROMA_PATH)

    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=_EMBED_MODEL,
        device="cpu",
    )
    _collection = _client.get_or_create_collection(
        name=_COLLECTION_NAME,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )
    return _collection


def build_from_chunks(chunks: list[dict]) -> bool:
    """
    Populate ChromaDB from loaded knowledge chunks.
    Idempotent — skips if collection already has >= len(chunks) documents.
    Returns True on success, False on any failure.
    """
    try:
        col = _get_collection()
        existing = col.count()
        if existing >= len(chunks):
            logger.info("ChromaDB: collection up-to-date (%d docs).", existing)
            return True

        ids = [f"chunk_{i}" for i in range(len(chunks))]
        texts = [c["text"] for c in chunks]
        metadatas = [
            {"source": c.get("source", ""), "topic": c.get("topic", "")}
            for c in chunks
        ]

        # Batch upsert to avoid OOM on HF Spaces free CPU
        for start in range(0, len(chunks), _BATCH_SIZE):
            end = start + _BATCH_SIZE
            col.upsert(
                ids=ids[start:end],
                documents=texts[start:end],
                metadatas=metadatas[start:end],
            )

        logger.info("ChromaDB: indexed %d knowledge chunks → %s", len(chunks), _CHROMA_PATH)
        return True

    except Exception as exc:
        logger.warning("ChromaDB build failed — falling back to BM25/FAISS: %s", exc)
        return False


def query(question: str, top_k: int = 5) -> list[dict]:
    """
    Semantic search: returns top_k chunk dicts [{text, source, topic}].
    Returns [] on any error — caller falls back to BM25.
    """
    try:
        col = _get_collection()
        n = min(top_k, col.count())
        if n == 0:
            return []
        results = col.query(query_texts=[question], n_results=n)
        chunks = []
        for i, doc in enumerate(results["documents"][0]):
            meta = results["metadatas"][0][i]
            chunks.append({
                "text":   doc,
                "source": meta.get("source", ""),
                "topic":  meta.get("topic", ""),
            })
        return chunks
    except Exception as exc:
        logger.warning("ChromaDB query failed — falling back to BM25: %s", exc)
        return []


def is_available() -> bool:
    """True if chromadb is installed and collection has at least 1 document."""
    try:
        import chromadb  # noqa: F401
        col = _get_collection()
        return col.count() > 0
    except Exception:
        return False
