# TASK — May 27, 2026 | Week 2 / Day 10

## TODAY'S GOAL
Build the RAG knowledge base — write and chunk CDC, NIH, WHO, and DGHS Bangladesh
content into rag/knowledge/ as plain text files. This is offline work — no API
key needed today. The FAISS index is built on Day 11.

## CONTEXT
- Day 9 complete: voice/pipeline.py fully done (transcription + Gemini extraction)
- Full suite: 78/78 passing
- rag/knowledge/ directory does NOT exist yet — create it today
- Target: 100–200 chunks, 100–300 words each
- Sources allowed: CDC, NIH/MedlinePlus, WHO, DGHS Bangladesh ONLY
- FORBIDDEN source: DermNet (hard constraint from CLAUDE.md)
- Do NOT touch today: model/, severity/, pdf_gen/, voice/, app.py

---

## WHAT IS A CHUNK?
Each chunk = one plain .txt file in rag/knowledge/.
Format of each file:
```
SOURCE: CDC / NIH / WHO / DGHS
TOPIC: <topic name>
---
<150–300 words of factual content about the skin disease or condition>
```
Naming: `cdc_tinea_01.txt`, `nih_eczema_02.txt`, `who_scabies_01.txt`, etc.

---

## DISEASE COVERAGE (must cover all 7 BD-SkinNet classes)

| Disease | English | Bengali | Priority |
|---------|---------|---------|----------|
| Tinea | Ringworm / Tinea Corporis | দাদ | HIGH — most common in BD |
| Scabies | Scabies | খোস-পাঁচড়া | HIGH — WHO neglected tropical disease |
| Atopic Dermatitis | Atopic Dermatitis / Eczema | অ্যাটোপিক ডার্মাটাইটিস | HIGH |
| Eczema | Eczema | একজিমা | HIGH |
| Contact Dermatitis | Contact Dermatitis | কন্টাক্ট ডার্মাটাইটিস | MEDIUM |
| Seborrheic Dermatitis | Seborrheic Dermatitis | সেবোরিক ডার্মাটাইটিস | MEDIUM |
| Vitiligo | Vitiligo | শ্বেতী রোগ | MEDIUM |

---

## TASKS (in order)

### TASK 1 — Create rag/knowledge/ directory and write chunks

Write at least 5 chunks per disease × 7 diseases = 35 minimum.
Target 100+ chunks total by also covering general skin hygiene,
when to see a doctor, and Bangladesh-specific context.

#### CDC chunks (target: 30 chunks)
Topics to cover per disease:
- What is it / definition
- Causes and risk factors
- Symptoms and signs
- Treatment overview
- Prevention

Files: `cdc_tinea_01.txt` through `cdc_tinea_05.txt`, etc.

#### NIH / MedlinePlus chunks (target: 30 chunks)
Topics to cover:
- Clinical description
- Diagnosis
- When to see a doctor
- Living with the condition (eczema, vitiligo)

Files: `nih_atopic_dermatitis_01.txt`, etc.

#### WHO chunks (target: 20 chunks)
Focus on:
- Scabies as neglected tropical disease
- Tinea as neglected tropical disease
- Global burden and Bangladesh context
- WHO treatment guidelines (ivermectin for scabies, antifungals for tinea)

Files: `who_scabies_01.txt`, `who_tinea_01.txt`, etc.

#### DGHS Bangladesh chunks (target: 20 chunks)
Focus on:
- Bangladesh-specific prevalence data
- National skin disease guidelines
- Upazila Health Complex referral protocol
- Common skin conditions in rural Bangladesh
- Heat and humidity as risk factors in BD climate

Files: `dghs_tinea_bd_01.txt`, `dghs_scabies_bd_01.txt`, etc.

---

### TASK 2 — Write rag/build_index.py

Script that reads all .txt files from rag/knowledge/ and builds a FAISS index.

```python
# rag/build_index.py
# Run once: python rag/build_index.py
# Outputs: rag/faiss_index.bin + rag/chunks_metadata.json

from sentence_transformers import SentenceTransformer
import faiss, json, os, numpy as np

KNOWLEDGE_DIR = "rag/knowledge"
INDEX_PATH = "rag/faiss_index.bin"
METADATA_PATH = "rag/chunks_metadata.json"
EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L6-v2"

def build():
    # 1. Load all .txt files
    # 2. Embed with SentenceTransformer
    # 3. Build faiss.IndexFlatIP (inner product / cosine)
    # 4. Save index as faiss_index.bin
    # 5. Save chunk texts + sources as chunks_metadata.json
    ...

if __name__ == "__main__":
    build()
```

### TASK 3 — Run build_index.py locally
```
python rag/build_index.py
```
- Confirm: faiss_index.bin created, chunks_metadata.json created
- Print: "Index built: N chunks" (N should be 100+)
- faiss_index.bin and chunks_metadata.json are in .gitignore ✓
  (they are rebuilt at HF Space startup)

### TASK 4 — Verify chunk quality
Spot-check 5 random chunks:
- [ ] Each file has SOURCE, TOPIC, and --- header
- [ ] Content is 100–300 words
- [ ] No DermNet content anywhere
- [ ] All 7 diseases represented
- [ ] Bangladesh-specific context present in DGHS files

### TASK 5 — Commit and push
```
git add rag/knowledge/ rag/build_index.py
git commit -m "[w2/d10] knowledge base chunks (CDC/NIH/WHO/DGHS)"
git push origin main
```
Note: faiss_index.bin and chunks_metadata.json are gitignored — do NOT commit them.

---

## DEFINITION OF DONE
- [ ] rag/knowledge/ exists with 100+ .txt chunk files
- [ ] All 7 BD-SkinNet disease classes covered (min 5 chunks each)
- [ ] All 4 sources represented: CDC, NIH, WHO, DGHS
- [ ] No DermNet content
- [ ] rag/build_index.py runs without error
- [ ] FAISS index builds successfully (N chunks confirmed)
- [ ] Committed and pushed (chunks only — not the .bin files)

---

## NEXT SESSION (Day 11 — May 28)
- Write rag/retriever.py — FAISS query + Gemini answer
- Implement answer_question(question, context) → str
- Build final index on HF Space at startup
- Commit: [w2/d11] FAISS index + RAG retriever
- Needs: GEMINI_API_KEY ✓ (already set)
