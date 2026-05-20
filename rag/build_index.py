"""
Build FAISS index from rag/knowledge/ .txt files.
Run once: python rag/build_index.py
Outputs: rag/faiss_index.bin + rag/chunks_metadata.json
Both are gitignored — rebuilt at HF Space startup.
"""

import json
import os

import faiss
import numpy as np

KNOWLEDGE_DIR = os.path.join(os.path.dirname(__file__), "knowledge")
INDEX_PATH = os.path.join(os.path.dirname(__file__), "faiss_index.bin")
METADATA_PATH = os.path.join(os.path.dirname(__file__), "chunks_metadata.json")
EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L6-v2"


def _embed_with_sentence_transformers(texts: list[str]) -> np.ndarray:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(EMBED_MODEL)
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1, norms)
    return (embeddings / norms).astype("float32")


def _embed_with_automodel(texts: list[str]) -> np.ndarray:
    import torch
    import torch.nn.functional as F
    from transformers import AutoModel, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(EMBED_MODEL)
    model = AutoModel.from_pretrained(EMBED_MODEL)
    model.eval()

    all_embeddings = []
    batch_size = 32
    with torch.no_grad():
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            encoded = tokenizer(
                batch, padding=True, truncation=True, max_length=512, return_tensors="pt"
            )
            out = model(**encoded)
            token_emb = out.last_hidden_state
            mask = encoded["attention_mask"].unsqueeze(-1).expand(token_emb.size()).float()
            pooled = torch.sum(token_emb * mask, 1) / torch.clamp(mask.sum(1), min=1e-9)
            normed = F.normalize(pooled, p=2, dim=1)
            all_embeddings.append(normed.cpu().numpy())
            print(f"  Embedded {min(i+batch_size, len(texts))}/{len(texts)}", end="\r")
    print()
    return np.concatenate(all_embeddings, axis=0).astype("float32")


def embed_texts(texts: list[str]) -> np.ndarray:
    try:
        print("  Trying SentenceTransformer ...")
        return _embed_with_sentence_transformers(texts)
    except Exception as e:
        print(f"  SentenceTransformer failed ({e}), trying AutoModel ...")
        return _embed_with_automodel(texts)


def load_chunks(knowledge_dir: str) -> list[dict]:
    chunks = []
    for fname in sorted(os.listdir(knowledge_dir)):
        if not fname.endswith(".txt"):
            continue
        path = os.path.join(knowledge_dir, fname)
        with open(path, encoding="utf-8") as f:
            raw = f.read().strip()

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
            "text": body.strip(),
            "full_text": raw,
        })
    return chunks


def build():
    if not os.path.isdir(KNOWLEDGE_DIR):
        raise FileNotFoundError(
            f"Knowledge directory not found: {KNOWLEDGE_DIR}\n"
            "Run: python rag/seed_knowledge.py"
        )

    print(f"Loading chunks from {KNOWLEDGE_DIR} ...")
    chunks = load_chunks(KNOWLEDGE_DIR)
    if not chunks:
        raise ValueError("No .txt files found in knowledge directory.")
    print(f"  {len(chunks)} chunks loaded.")

    print(f"Loading embedding model: {EMBED_MODEL} ...")
    texts = [c["text"] for c in chunks]
    embeddings = embed_texts(texts)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    print(f"Saving FAISS index ({index.ntotal} vectors, dim={dim}) → {INDEX_PATH}")
    faiss.write_index(index, INDEX_PATH)

    metadata = [
        {
            "filename": c["filename"],
            "source": c["source"],
            "topic": c["topic"],
            "text": c["full_text"],
        }
        for c in chunks
    ]
    print(f"Saving metadata → {METADATA_PATH}")
    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"\nIndex built: {len(chunks)} chunks")


if __name__ == "__main__":
    build()
