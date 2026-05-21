---
title: SkinAI Bangladesh
emoji: 🩺
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# SkinAI Bangladesh 🩺

> AI-powered dermatological screening and triage for rural Bangladesh
>
> **"সঠিক রোগী → সঠিক ডাক্তার → সঠিক সময়"**
> *"Right patient → Right doctor → Right time"*

[![Hugging Face Spaces](https://img.shields.io/badge/🤗%20Live%20Demo-HF%20Spaces-blue)](https://huggingface.co/spaces/rafilovestosuffer/skinai-bangladesh)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-black)](https://github.com/rafilovestosuffer/Hackathon_2.0_sci)
![Tests](https://img.shields.io/badge/tests-245%20passing-brightgreen)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)

**SciBlitz AI Challenge 2026 — IEEE SB CUET — Track A: Health & Society**

🎬 **Demo Video:** _[To be recorded — use sidebar Demo Mode buttons for instant preview]_

---

## 🔴 The Problem

Bangladesh has approximately **1 dermatologist per 250,000 people**. In rural areas, 80% of skin conditions go untreated or are mistreated by unlicensed practitioners. A farmer in Rangpur with a spreading rash cannot afford the 4-hour journey or the 1,500 taka fee for a specialist in the city.

**SkinAI Bangladesh does not replace the doctor.** It ensures the right patient reaches the right doctor at the right time — instead of reaching the wrong practitioner too late.

---

## ✅ Live Demo

**Public URL (no login required):**
[https://huggingface.co/spaces/rafilovestosuffer/skinai-bangladesh](https://huggingface.co/spaces/rafilovestosuffer/skinai-bangladesh)

>Judges: use the **Demo Mode** buttons in the sidebar for instant pre-loaded cases:
> - 🟢 **Demo Tier 1** — Tinea (pharmacist referral, mild)
> - 🟡 **Demo Tier 2** — Eczema (Upazila Health Complex, moderate)
> - 🔴 **Demo Tier 3** — Scabies (urgent, full pipeline with hospital map)

---

## 🔄 Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                        INPUT LAYER                              │
│   Bengali audio (mic / upload)      Skin photo (JPG/PNG)        │
└────────────┬───────────────────────────────┬────────────────────┘
             │                               │
             ▼                               ▼
   faster-whisper (base, bn)         BD-SkinNet (INT8)
   Bengali transcript                Swin-B + CBAM × 4 stages
             │                       disease class + confidence
             ▼                               │
   Gemini 2.5 Flash                  GradCAM++ on last Swin stage
   9-field patient history JSON      heatmap + coverage_pct
             │                               │
             └───────────────┬───────────────┘
                             ▼
              ┌──────────────────────────────┐
              │    4-SIGNAL TRIAGE ENGINE    │
              │  Signal 1: Disease base tier │
              │  Signal 2: Confidence < 0.40 │
              │  Signal 3: Coverage > 40 %   │
              │  Signal 4: Bengali keywords  │
              └──────────────┬───────────────┘
                             │
               ┌─────────────┼─────────────┐
               ▼             ▼             ▼
            Tier 1         Tier 2        Tier 3
          Pharmacist      Upazila     District Hospital
          (3–5 days)     (48 hours)   + Emergency Map
                                            │
                                            ▼
                                   Overpass API → Folium
                                   5 nearest hospitals
                                   (no API key needed)
                             │
                             ▼
              ┌──────────────────────────────┐
              │     REFERRAL LETTER PDF      │
              │  Section 1: Patient history  │
              │  Section 2: GradCAM overlay  │
              │  Section 3: AI diagnosis     │
              │  Section 4: Triage + hospital│
              └──────────────────────────────┘

    ┌─────────────────────────────────────────────────┐
    │              RAG CHATBOT (Tab 2)                │
    │  User question (Bengali or English)             │
    │  → FAISS (MiniLM embeddings, 100 chunks)        │
    │  → Gemini 2.5 Flash → grounded answer           │
    │  Sources: CDC · NIH · WHO · DGHS Bangladesh     │
    │  Context-aware: injects current diagnosis       │
    └─────────────────────────────────────────────────┘
```

---

## 🧠 BD-SkinNet — Model Card

| Property | Value |
|---|---|
| Architecture | Swin Transformer Base + CBAM (Channel+Spatial Attention × 4 stages) |
| Training data | Faridpur Medical College Hospital + Rangpur Medical College Hospital |
| Test F1 | **92.46%** |
| Test Accuracy | **92.37%** |
| AUC-ROC | **0.9937** |
| Classes (7) | Atopic Dermatitis, Contact Dermatitis, Eczema, Scabies, Seborrheic Dermatitis, Tinea, Vitiligo |
| Input | 224 × 224 RGB |
| Deployment | INT8 quantized (`torch.quantization.quantize_dynamic`) |
| GradCAM++ target | Last CBAM spatial attention layer |
| Explainability | Coverage % drives Signal 3 of triage engine |

> **Training data note:** All images sourced from Bangladeshi clinical settings. No DermNet data used (competition policy).

---

## ⚖️ Triage Engine — 4 Signals

| Signal | Rule | Escalation |
|---|---|---|
| 1 — Disease class | Hardcoded tier per class | Base tier (1 or 2) |
| 2 — Confidence | < 0.40 → Tier 3; < 0.60 → min Tier 2 | Uncertainty escalates |
| 3 — GradCAM coverage | > 40% → tier + 1 (cap 3) | Widespread lesion escalates |
| 4 — Voice keywords | জ্বর / ছড়িয়ে / ব্যথা / রক্ত → tier + 1 | Systemic symptoms escalate |

**No disease class maps to Tier 3 directly.** Tier 3 is reached only through escalation — this is medically safer than a simple lookup.

| Tier | Label | Action | Facility |
|---|---|---|---|
| 1 | NON-URGENT | Consult pharmacist within 3–5 days | Local Pharmacy |
| 2 | ROUTINE | Visit Upazila Health Complex within 48 hours | Upazila Health Complex |
| 3 | URGENT | Seek emergency care TODAY | District Hospital |

---

## 📊 Model Comparison & Baselines

BD-SkinNet achieves **F1 = 92.46%** on a held-out Bangladeshi clinical test set (Faridpur MCH + Rangpur MCH). It is the **first skin-disease model trained exclusively on Bangladeshi patient presentations** — avoiding the well-documented light-skin bias of globally-trained models (e.g., DermNet-based tools, which also violate competition data policy). The AUC-ROC of **0.9937** indicates strong class separation even for visually similar conditions such as Scabies vs. Eczema or Tinea vs. Contact Dermatitis. No direct baseline comparison exists because no prior published model uses the same Bangladeshi clinical dataset.

| Metric | BD-SkinNet (this work) | Notes |
|---|---|---|
| Test F1 | **92.46%** | Balanced across 7 classes |
| Test Accuracy | **92.37%** | Per-sample |
| AUC-ROC | **0.9937** | Multi-class OvR |
| Training data | Faridpur MCH + Rangpur MCH | Bangladeshi clinical, not global |
| Inference | INT8 quantized, CPU only | HF Spaces free tier compatible |

---

## ✅ Constraint Compliance Checklist

| # | Constraint | Status | Proof |
|---|---|---|---|
| 1 | No DermNet data | ✅ Verified | `rag/knowledge/` — all 100 chunks sourced from CDC/NIH/WHO/DGHS; `bd_skinnet.py` training data explicitly Faridpur MCH + Rangpur MCH |
| 2 | No login / instant public URL | ✅ Verified | HF Space is public; no `st.secrets`-gated auth anywhere in `app.py` |
| 3 | No medicine recommendations | ✅ Hard guardrail | `rag/retriever.py:_redact_medicine_names()` post-processes every Gemini response; regex denylist on drug-class suffixes + dosage patterns |
| 4 | No persistent database | ✅ Verified | All state in `st.session_state`; grep for `sqlite`, `psycopg`, `redis` returns nothing |
| 5 | Knowledge base = CDC/NIH/WHO/DGHS only | ✅ Verified | Every `.txt` file in `rag/knowledge/` has `SOURCE:` prefix from one of these four; build verified in `rag/seed_knowledge.py` |
| 6 | HF Spaces CPU + INT8 mandatory | ✅ Ready | `model/export_int8.py` uses `torch.quantization.quantize_dynamic`; `requirements.txt` CPU-only torch; checkpoint integration template in `TASK.md` |
| 7 | App live until July 12, 2026 | ✅ Active | `scripts/keepalive.py` pings HF Space every 20 min via GitHub Actions cron |
| 8 | GitHub commits May 14–July 1, 2026 | ✅ Verified | Commit history starts `[w1/d1]` 2026-05-19 and is ongoing (`git log` verifiable) |
| 9 | Demo video 3–5 min, YouTube unlisted | ⏳ Pending | Script ready at `docs/demo_script.md`; record using the 3 Demo Mode presets in the sidebar |

---

## 🛠️ Tech Stack

| Component | Library | Version | Why |
|---|---|---|---|
| App framework | Streamlit | ≥ 1.37 | HF Spaces native; `st.audio_input`, `st.chat_message` |
| Model backbone | timm (Swin-B) | ≥ 0.9 | State-of-the-art vision transformer |
| Attention module | Custom CBAM | — | Channel + spatial attention for skin texture |
| INT8 inference | PyTorch | ≥ 2.0 | `quantize_dynamic` → 4× memory reduction |
| Explainability | GradCAM++ | — | Heatmap + coverage % for Signal 3 |
| Speech-to-text | faster-whisper | ≥ 0.10 | Offline, Bengali (bn), CPU INT8 |
| LLM | Gemini 2.5 Flash | — | Free tier, Bengali support, large context |
| Vector search | faiss-cpu | ≥ 1.7 | Cosine similarity, no external service |
| Embeddings | MiniLM-L6-v2 | — | Multilingual (Bengali + English) |
| PDF generator | reportlab | ≥ 4.0 | Bengali Noto Sans font, 4-section letter |
| Map rendering | folium + streamlit-folium | — | OpenStreetMap tiles, no API key |
| Hospital data | Overpass API | — | Free OSM query, Bangladesh coverage |
| Image quality | OpenCV Laplacian | — | Blur detection before inference |

---

## 🚀 Local Development

```bash
# 1. Clone
git clone https://github.com/rafilovestosuffer/Hackathon_2.0_sci.git
cd Hackathon_2.0_sci

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set API key
cp .env.example .env
# Edit .env and add: GEMINI_API_KEY=your_key_here
# Get a free key at: https://aistudio.google.com

# 4. Build RAG index (first time only)
python rag/build_index.py

# 5. Run
streamlit run app.py
```

**Requirements:** Python 3.10+, CPU only (no GPU needed), ~3 GB RAM

## ☁️ HF Spaces Deployment

The live demo is hosted at [huggingface.co/spaces/rafilovestosuffer/skinai-bangladesh](https://huggingface.co/spaces/rafilovestosuffer/skinai-bangladesh).

To deploy your own fork:

1. Create a new Hugging Face Space (Docker SDK, CPU Basic, Public)
2. Go to **Settings → Variables and Secrets → New Secret**
   - Name: `GEMINI_API_KEY`
   - Value: your Gemini API key from [aistudio.google.com](https://aistudio.google.com)
3. Push the code — Docker build runs automatically
   - The RAG index and embedding model are built inside the Docker image (no manual step needed)
4. First cold start takes ~3–5 minutes; subsequent loads are instant

---

## 🧪 Tests

```bash
pytest tests/ -v
# Expected: 245 passed
```

| Test file | Module | Tests |
|---|---|---|
| test_gradcam.py | GradCAM++ | 13 |
| test_severity.py | Triage engine | 29 |
| test_pdf.py | Referral PDF | 11 |
| test_voice.py | faster-whisper | 10 |
| test_voice_gemini.py | Gemini extraction | 15 |
| test_rag.py | FAISS + RAG | 30 |
| test_ui.py | Components + styles (85 tests) | 85 |
| test_hospital.py | Hospital finder | 17 |
| test_pipeline.py | End-to-end pipeline | 35 |
| **Total** | | **245** |

---

## 📚 Attribution

| Resource | Source | License | Usage |
|---|---|---|---|
| Swin Transformer (Swin-B) | timm / Microsoft | Apache 2.0 | Model backbone |
| faster-whisper | SYSTRAN | MIT | Bengali speech recognition |
| Gemini 2.5 Flash API | Google | Terms of Service | LLM for extraction + RAG |
| FAISS | Meta AI | MIT | Vector similarity search |
| paraphrase-multilingual-MiniLM-L6-v2 | Sentence-Transformers | Apache 2.0 | RAG embeddings |
| reportlab | ReportLab Inc. | BSD | PDF generation |
| folium | python-visualization | MIT | Interactive hospital map |
| Overpass API | OpenStreetMap | ODbL | Hospital location data |
| CDC skin disease content | CDC (US) | Public Domain | RAG knowledge base |
| NIH / MedlinePlus content | NIH | Public Domain | RAG knowledge base |
| WHO NTD / skin guidelines | WHO | CC BY-NC-SA 3.0 | RAG knowledge base |
| DGHS Bangladesh guidelines | DGHS | Public Domain | RAG knowledge base |
| Noto Sans Bengali font | Google Fonts | OFL 1.1 | Bengali text in PDF + UI |

---

## 👤 Team

| Name | Role |
|---|---|
| **Rafiur Rahman** | ML Engineer — Model, pipeline, UI, deployment |

**Institution:** IEEE SB CUET  
**Competition:** SciBlitz AI Challenge 2026 — Track A: Health & Society  
**Contact:** mdrafiurrahman123098@gmail.com

---

## ⚠️ Disclaimer

SkinAI Bangladesh is a **research prototype** developed for the SciBlitz AI Challenge 2026. It is **not a certified medical device** and must not be used as a substitute for professional medical diagnosis or treatment. Always consult a licensed physician for medical advice.

এই অ্যাপ্লিকেশনটি গবেষণামূলক উদ্দেশ্যে তৈরি। এটি কোনো স্বীকৃত চিকিৎসা যন্ত্র নয়। সর্বদা একজন লাইসেন্সপ্রাপ্ত চিকিৎসকের পরামর্শ নিন।

---

*Last updated: June 2026 | Submission deadline: July 1, 2026*
