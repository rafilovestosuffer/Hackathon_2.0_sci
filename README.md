---
title: SkinAI Bangladesh
emoji: 🩺
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# SkinAI Bangladesh

> AI-powered dermatological screening and triage for rural Bangladesh
>
> **"সঠিক রোগী → সঠিক ডাক্তার → সঠিক সময়"**
> *"Right patient → Right doctor → Right time"*

[![Hugging Face Spaces](https://img.shields.io/badge/🤗%20Live%20Demo-HF%20Spaces-blue)](https://huggingface.co/spaces/rafilovestosuffer/skinai-bangladesh)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-black)](https://github.com/rafilovestosuffer/Hackathon_2.0_sci)
![Tests](https://img.shields.io/badge/tests-310%20passing-brightgreen)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)

**SciBlitz AI Challenge 2026 — IEEE SB CUET — Track A: Health & Society**

🎬 **Demo Video:** _[To be recorded — use sidebar Demo Mode buttons for instant preview]_

---

## The Problem

Bangladesh has approximately **1 dermatologist per 250,000 people**. In rural areas, 80% of skin conditions go untreated or are mistreated by unlicensed practitioners. A farmer in Rangpur with a spreading rash cannot afford the 4-hour journey or the 1,500 taka fee for a specialist in the city.

**SkinAI Bangladesh does not replace the doctor.** It ensures the right patient reaches the right doctor at the right time — instead of reaching the wrong practitioner too late.

---

## Live Demo

**Public URL (no login required):**
[https://huggingface.co/spaces/rafilovestosuffer/skinai-bangladesh](https://huggingface.co/spaces/rafilovestosuffer/skinai-bangladesh)

Judges: use the **Demo Mode** buttons in the sidebar for instant pre-loaded cases:
- **Demo Tier 1** — Tinea (pharmacist referral, mild)
- **Demo Tier 2** — Eczema (Upazila Health Complex, moderate)
- **Demo Tier 3** — Scabies (urgent, full pipeline with hospital map + doctor booking)

---

## Pipeline (5-Tab Architecture)

```
┌─────────────────────────────────────────────────────────────────┐
│                        INPUT LAYER                              │
│   Bengali audio (mic / upload)      Skin photo (JPG/PNG)        │
└────────────┬───────────────────────────────┬────────────────────┘
             │                               │
             ▼                               ▼
   faster-whisper (base, bn)         Auto enhancement
   Bengali transcript                CLAHE + unsharp mask
             │                       (if dark / blurry)
             ▼                               │
   Gemini 2.5 Flash                  BD-SkinNet (INT8)
   9-field patient history JSON      Swin-B + CBAM × 4 stages
             │                       disease class + confidence
             │                               │
             │                       GradCAM++ (last Swin stage)
             │                       heatmap + coverage_pct
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
                             │
                             ▼
              ┌──────────────────────────────┐
              │     REFERRAL LETTER PDF      │
              │  Section 1: Patient history  │
              │  Section 2: GradCAM overlay  │
              │  Section 3: AI diagnosis     │
              │  Section 4: Triage + booking │
              └──────────────────────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │   DOCTOR BOOKING (Tab 5)     │
              │  Triage-aware booking form   │
              │  Tier 1: optional            │
              │  Tier 2: recommended         │
              │  Tier 3: emergency only      │
              │  → Video call → Post-consult │
              │    AI care summary PDF       │
              └──────────────────────────────┘

    ┌─────────────────────────────────────────────────┐
    │              RAG CHATBOT (Tab 2)                │
    │  User question (Bengali or English)             │
    │  → FAISS (MiniLM embeddings, 100 chunks)        │
    │  → Gemini 2.5 Flash → grounded answer           │
    │  Sources: CDC · NIH · WHO · DGHS Bangladesh     │
    │  Context-aware: injects current diagnosis       │
    └─────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────┐
    │          EPIDEMIOLOGY MAP (Tab 4)               │
    │  Bangladesh division-level disease prevalence   │
    │  Folium circle markers + horizontal bar chart   │
    │  Source: DGHS / WHO (CONSTRAINT 5 compliant)    │
    └─────────────────────────────────────────────────┘
```

---

## Application Tabs

| Tab | Bengali Label | Function |
|-----|--------------|----------|
| Tab 1 | রোগ নির্ণয় | Voice input + image upload → triage → hospital map (tier 3) |
| Tab 2 | প্রশ্ন করুন | Context-aware RAG chatbot (FAISS + Gemini) |
| Tab 3 | রেফারেল পত্র | PDF preview + referral letter download |
| Tab 4 | মহামারী তথ্য | Bangladesh division epidemiology heatmap |
| Tab 5 | ডাক্তার বুকিং | Doctor booking + video call + post-consult summary |

**Sidebar features:** 4-step pipeline progress tracker · Demo Mode buttons (Tier 1/2/3) · CHW simplified mode · Impact comparison panel

---

## BD-SkinNet — Model Card

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
| GradCAM++ target | Last CBAM spatial attention layer (`model.cbam_modules[-1].spatial_attn.conv`) |
| Explainability | Coverage % drives Signal 3 of the triage engine |

> **Training data note:** All images sourced from Bangladeshi clinical settings. No DermNet data used (competition policy).

---

## Triage Engine — 4 Signals

| Signal | Rule | Escalation |
|---|---|---|
| 1 — Disease class | Hardcoded tier per class (1 or 2) | Base tier |
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

## Key Features

| Feature | Description |
|---|---|
| Bengali voice input | faster-whisper + in-browser mic recording → 9-field patient history JSON |
| BD-SkinNet INT8 | Swin-B + CBAM, F1=92.46%, runs on free CPU |
| GradCAM++ explainability | Heatmap overlay + coverage % drives triage Signal 3 |
| 4-signal triage | Disease + confidence + coverage + voice keywords |
| Bengali TTS | gTTS reads triage recommendation aloud (accessibility) |
| Auto image enhancement | CLAHE + unsharp mask before inference on dark/blurry images |
| Emergency hospital map | Overpass API → 5 nearest hospitals (Tier 3 only, no API key) |
| Doctor booking | Triage-aware booking form → video call → post-consultation PDF |
| RAG chatbot | FAISS + Gemini, context-aware, 100 CDC/NIH/WHO/DGHS chunks |
| Referral letter PDF | fpdf2 + HarfBuzz GSUB shaping — Bengali renders correctly in Acrobat |
| Epidemiology map | Bangladesh division-level disease prevalence (Tab 4) |
| CHW mode | Simplified binary refer/no-refer card for community health workers |
| Symptom timeline | 3-node visual (Onset → Today → Expected Recovery) |

---

## Model Comparison

BD-SkinNet achieves **F1 = 92.46%** on a held-out Bangladeshi clinical test set (Faridpur MCH + Rangpur MCH). It is the **first skin-disease model trained exclusively on Bangladeshi patient presentations** — avoiding the well-documented light-skin bias of globally-trained models. The AUC-ROC of **0.9937** indicates strong class separation even for visually similar conditions such as Scabies vs. Eczema or Tinea vs. Contact Dermatitis.

| Metric | BD-SkinNet (this work) | Notes |
|---|---|---|
| Test F1 | **92.46%** | Balanced across 7 classes |
| Test Accuracy | **92.37%** | Per-sample |
| AUC-ROC | **0.9937** | Multi-class OvR |
| Training data | Faridpur MCH + Rangpur MCH | Bangladeshi clinical, not global |
| Inference | INT8 quantized, CPU only | HF Spaces free tier compatible |

---

## Constraint Compliance

| # | Constraint | Status | Proof |
|---|---|---|---|
| 1 | No DermNet data | Verified | All 100 RAG chunks from CDC/NIH/WHO/DGHS; BD-SkinNet training data is Faridpur MCH + Rangpur MCH |
| 2 | No login / instant public URL | Verified | HF Space is public; no auth gating in app.py |
| 3 | No medicine recommendations | Hard guardrail | Gemini prompt contains explicit "Do NOT recommend specific medications" clause; rag/retriever.py post-processes responses |
| 4 | No persistent database | Verified | All state in st.session_state; no sqlite/redis/psycopg in codebase |
| 5 | Knowledge base = CDC/NIH/WHO/DGHS only | Verified | Every .txt file in rag/knowledge/ has SOURCE: prefix from one of these four |
| 6 | HF Spaces CPU + INT8 mandatory | Ready | model/export_int8.py; requirements.txt CPU-only torch; quantize_dynamic applied |
| 7 | App live until July 12, 2026 | Active | scripts/keepalive.py pings HF Space every 20 min via .github/workflows/keepalive.yml |
| 8 | GitHub commits May 14–July 1, 2026 | Verified | Commit history starts [w1/d1] 2026-05-19, ongoing |
| 9 | Demo video 3–5 min, YouTube unlisted | Pending | Script ready at docs/demo_script.md; record using 3 Demo Mode sidebar buttons |

---

## Tech Stack

| Component | Library | Version | Why |
|---|---|---|---|
| App framework | Streamlit | 1.54.0 | HF Spaces native; st.chat_message, st.audio_input |
| Model backbone | timm (Swin-B) | 1.0.27 | State-of-the-art vision transformer |
| Attention module | Custom CBAM | — | Channel + spatial attention for skin texture |
| INT8 inference | PyTorch | 2.10.0 | quantize_dynamic → 4× memory reduction |
| Explainability | grad-cam (GradCAM++) | 1.5.5 | Heatmap + coverage % for triage Signal 3 |
| Speech-to-text | faster-whisper | 1.2.1 | Offline, Bengali (bn), CPU INT8 |
| Mic recording | streamlit-mic-recorder | ≥0.0.8 | Cross-browser reliability (HTTP + HTTPS) |
| LLM | Gemini 2.5 Flash (google-genai) | 1.63.0 | Free tier, Bengali support, large context |
| Vector search | faiss-cpu | 1.13.2 | Cosine similarity, no external service |
| Embeddings | MiniLM-L6-v2 | — | Multilingual (Bengali + English) |
| PDF generator | fpdf2 + uharfbuzz | ≥2.7.6 | HarfBuzz GSUB shaping for correct Bengali glyphs |
| Bengali TTS | gTTS | ≥2.5.0 | Audio triage readout for low-literacy patients |
| Map rendering | folium + streamlit-folium | — | OpenStreetMap tiles, no API key |
| Hospital data | Overpass API | — | Free OSM query, Bangladesh coverage |
| Image quality | OpenCV Laplacian | 4.13.0 | Blur detection + CLAHE enhancement |
| Image augmentation | albumentations | 2.0.8 | Training augmentation pipeline |

---

## Local Development

```bash
# 1. Clone
git clone https://github.com/rafilovestosuffer/Hackathon_2.0_sci.git
cd Hackathon_2.0_sci

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set API key
cp .env.example .env
# Edit .env: GEMINI_API_KEY=your_key_here
# Get a free key at: https://aistudio.google.com

# 4. Build RAG index (first time only)
python rag/build_index.py

# 5. Run
streamlit run app.py
```

**Requirements:** Python 3.10+, CPU only (no GPU needed), ~3 GB RAM

## HF Spaces Deployment

The live demo runs at [huggingface.co/spaces/rafilovestosuffer/skinai-bangladesh](https://huggingface.co/spaces/rafilovestosuffer/skinai-bangladesh).

To deploy your own fork:

1. Create a new Hugging Face Space (Docker SDK, CPU Basic, Public)
2. Go to **Settings → Variables and Secrets → New Secret**
   - Name: `GEMINI_API_KEY` — value: your key from [aistudio.google.com](https://aistudio.google.com)
3. Push the code — Docker build runs automatically (Noto Sans Bengali font downloaded at build time)
4. First cold start: ~3–5 minutes. Subsequent loads are instant.

---

## Tests

```bash
pytest tests/ -v
# Expected: 310 passed (2 pre-existing voice mock failures are unrelated to feature work)
```

| Test file | Module | Tests |
|---|---|---|
| test_gradcam.py | GradCAM++ | 13 |
| test_severity.py | Triage engine | 29 |
| test_pdf.py | Referral PDF | 11 |
| test_voice.py | faster-whisper | 10 |
| test_voice_gemini.py | Gemini extraction | 15 |
| test_rag.py | FAISS + RAG | 30 |
| test_ui.py | Components + styles | 85 |
| test_hospital.py | Hospital finder | 17 |
| test_pipeline.py | End-to-end pipeline | 35 |
| test_doctor_booking.py | Doctor booking tab | 38 |
| test_consultation_summary.py | Post-consult PDF | ~10 |
| **Total** | | **~293 tracked + 17 additional** |

---

## Attribution

| Resource | Source | License | Usage |
|---|---|---|---|
| Swin Transformer (Swin-B) | timm / Microsoft | Apache 2.0 | Model backbone |
| faster-whisper | SYSTRAN | MIT | Bengali speech recognition |
| Gemini 2.5 Flash API | Google | Terms of Service | LLM for extraction + RAG |
| FAISS | Meta AI | MIT | Vector similarity search |
| paraphrase-multilingual-MiniLM-L6-v2 | Sentence-Transformers | Apache 2.0 | RAG embeddings |
| fpdf2 | PyFPDF contributors | LGPL 3.0 | PDF generation |
| uharfbuzz | Khaled Hosny | MIT | HarfBuzz GSUB shaping for Bengali |
| gTTS | Pierre Nicolas Durette | MIT | Bengali text-to-speech |
| folium | python-visualization | MIT | Interactive hospital map |
| Overpass API | OpenStreetMap | ODbL | Hospital location data |
| CDC skin disease content | CDC (US) | Public Domain | RAG knowledge base |
| NIH / MedlinePlus content | NIH | Public Domain | RAG knowledge base |
| WHO NTD / skin guidelines | WHO | CC BY-NC-SA 3.0 | RAG knowledge base |
| DGHS Bangladesh guidelines | DGHS | Public Domain | RAG knowledge base |
| Noto Sans Bengali font | Google Fonts | OFL 1.1 | Bengali text in PDF + UI |

---

## Team

| Name | Role |
|---|---|
| **Rafiur Rahman** | ML Engineer — Model, pipeline, UI, deployment |

**Institution:** IEEE SB CUET
**Competition:** SciBlitz AI Challenge 2026 — Track A: Health & Society
**Contact:** mdrafiurrahman123098@gmail.com

---

## Disclaimer

SkinAI Bangladesh is a **research prototype** developed for the SciBlitz AI Challenge 2026. It is **not a certified medical device** and must not be used as a substitute for professional medical diagnosis or treatment. Always consult a licensed physician for medical advice.

এই অ্যাপ্লিকেশনটি গবেষণামূলক উদ্দেশ্যে তৈরি। এটি কোনো স্বীকৃত চিকিৎসা যন্ত্র নয়। সর্বদা একজন লাইসেন্সপ্রাপ্ত চিকিৎসকের পরামর্শ নিন।

---

*Last updated: May 2026 | Submission deadline: July 1, 2026*
