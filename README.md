---
title: SkinAI Bangladesh
emoji: 🩺
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
license: mit
---

<div align="center">

# 🩺 SkinAI Bangladesh

### AI-powered skin screening, triage & care-routing for rural Bangladesh

**সঠিক রোগী → সঠিক ডাক্তার → সঠিক সময়**
*Right patient → Right doctor → Right time*

[![Live Demo](https://img.shields.io/badge/🤗_Live_Demo-Open_App-2563eb?style=for-the-badge)](https://huggingface.co/spaces/rafilovestosuffer/skinai-bd)
[![Demo Video](https://img.shields.io/badge/YouTube-Demo_Video-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://youtu.be/9zOjfBBU4qg)
[![Telegram Bot](https://img.shields.io/badge/Telegram-@SkinAIBDBot-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/SkinAIBDBot)
[![GitHub](https://img.shields.io/badge/GitHub-Source-181717?style=for-the-badge&logo=github)](https://github.com/rafilovestosuffer/Hackathon_2.0_sci)

![Tests](https://img.shields.io/badge/tests-366_passing-brightgreen)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Inference](https://img.shields.io/badge/inference-INT8_·_CPU-orange)
![No login](https://img.shields.io/badge/access-no_login-success)
![License](https://img.shields.io/badge/license-MIT-green)

[**▶ Try it**](#-try-it-in-10-seconds) · [**How it works**](#-how-it-works) · [**Deep dives**](#-under-the-hood--deep-dives) · [**Tech stack**](#-complete-tech-stack) · [**Impact**](#-business-model--impact)

</div>

---

## 💡 In one sentence

SkinAI Bangladesh takes a patient's **spoken Bengali complaint** and **one skin photo**, and returns a **safe, explainable, doctor-addressed referral** — then can route them all the way to a **video consultation** and a **take-home care summary**. It runs **free, on CPU, with no login**, and reaches people over the **web, WhatsApp, and Telegram**.

> It is **not** a classifier in a web page. It is an **end-to-end clinical triage system** — engineered to always fail *toward* a doctor, never away from one.

---

## 🔴 The problem

Bangladesh has roughly **one dermatologist per 250,000 people**. In rural areas, an estimated **80% of skin conditions are untreated or mistreated** by unlicensed practitioners.

<div align="center">

> 🧑‍🌾 **Rahim** is a farmer in Rangpur. He notices a spreading rash. The nearest specialist is **4 hours away** and costs **1,500 taka** he can't spare.
>
> He opens SkinAI, **speaks in Bengali**, **takes one photo**. In seconds: *Tinea · mild · non-urgent* → "go to your local pharmacist; if it spreads, here's your referral letter for Rangpur Medical College Hospital."
>
> **Rahim has a plan. He doesn't need to go to Dhaka.**

</div>

---

## ▶ Try it in 10 seconds

**Live app (no login):** **[huggingface.co/spaces/rafilovestosuffer/skinai-bd](https://huggingface.co/spaces/rafilovestosuffer/skinai-bd)**

Open **Tab 1 → "⚡ Quick Start"** and click a pre-filled case — each runs the **full pipeline** (inference → triage → hospital map → referral PDF) in one click:

| Click this | You'll see |
|---|---|
| 🟢 **Tinea · Tier 1** | Non-urgent → pharmacist referral |
| 🟡 **Eczema · Tier 2** | Routine → Upazila Health Complex |
| 🔴 **Scabies · Tier 3** | Urgent → emergency hospital map + full referral |
| 💚 **Normal · Healthy** | Tier 0 → no referral needed |

> 💾 **Tab 3** also has a one-click **"Download a sample referral letter"** — a fully-populated PDF, no pipeline run needed. Perfect for judges in a silent room.

---

## 🎬 Demo video

<div align="center">

[![SkinAI Bangladesh — demo video](https://i.ytimg.com/vi/9zOjfBBU4qg/maxresdefault.jpg)](https://youtu.be/9zOjfBBU4qg)

**[▶ Watch the full walkthrough on YouTube](https://youtu.be/9zOjfBBU4qg)** — voice → photo → triage → referral PDF, end to end.

</div>

---

## 📸 What it looks like

![Home — seven tabs, voice + photo inputs, one-click demo cases](assets/screenshots/home-quickstart.jpg)

| Voice-filled history → AI diagnosis | Triage verdict → Bengali readout → hospital finder |
|---|---|
| ![Auto-filled Bengali patient form beside the AI diagnosis card](assets/screenshots/diagnosis-card.jpg) | ![Urgent tier banner with Bengali audio player and emergency hospital search](assets/screenshots/triage-output.jpg) |

<sub>Live Space, Scabies · Tier 3 demo case. Note the diagnosis card saying **"Uncertain — see a doctor"** at 38% confidence — low confidence escalates the patient to safer care instead of guessing.</sub>

---

## 🩺 What it does — the full care loop

SkinAI implements the **whole journey from symptom to specialist**, not just the diagnosis:

```
 Screen  →  Diagnose  →  Triage  →  Refer  →  Book  →  Consult  →  Care Summary
 (voice    (BD-SkinNet  (3-signal  (4-section (in-app   (video +    (take-home
 + photo)   INT8)        engine)    PDF)       booking)   transcript)  PDF)
```

The app is organized into **seven working tabs**:

| # | Tab | What it delivers |
|---|---|---|
| 1 | **Diagnosis** | Bengali/English voice → auto-extracted patient history; photo → BD-SkinNet; severity banner + Bengali voice readout; clinical knowledge-graph context; nearest-facility map |
| 2 | **Ask AI** | Bilingual chatbot grounded in **CDC · NIH · WHO · DGHS**, aware of your diagnosis, with a hard **no-medicine** guardrail |
| 3 | **Referral** | One-click **4-section bilingual PDF** (or simplified **CHW slip**), addressed to a doctor |
| 4 | **Insights** | Bangladesh **prevalence heatmap** + prevention tips |
| 5 | **DocTime** | **Telemedicine handoff** via deep-link + QR + WhatsApp + referral PDF |
| 6 | **Phase 2 · Network** | **In-app doctor booking** + post-booking **consultation room** → Care Summary PDF |
| 7 | **Impact & Ethics** | Business model, model card, architecture, scalability, diaspora (NRB) pitch |

---

## 🏛 How it works

The core pipeline fuses **three independent inputs** — image, voice, free text — into one safety-biased triage decision.

```
   🎙 Bengali/English audio                         📷 Skin photo
            │                                             │
            ▼                                             ▼
   faster-whisper (small, INT8)              Blur check → auto-enhance
   3-pass robust transcription                (Laplacian · CLAHE + unsharp)
            │                                             │
            ▼                                             ▼
   Gemini 2.5 Flash-Lite                        BD-SkinNet (INT8)
   → 9-field patient history                    Swin-B + CBAM ×4
            │                                    → disease · confidence · top-2
            └───────────────────┬───────────────────────┘
                                ▼
              ┌──────────────────────────────────────┐
              │           TRIAGE ENGINE               │
              │  Tier 0  ← confident "Normal"         │
              │  Signal 1: disease-class base tier    │
              │  Signal 2: confidence (<0.40 → Tier 3)│
              │  Signal 3: Bengali symptom keywords   │
              │  Rule: no class is Tier 3 by itself   │
              └───────────────────┬───────────────────┘
                                  ▼
        Tier 0 ·  Tier 1  ·  Tier 2  ·  Tier 3 → + emergency hospital map
        Healthy   Pharmacy   Upazila      District ER     (Overpass → Folium)
                                  │
                                  ▼
                4-section bilingual referral PDF  +  grounded RAG chatbot
```

> **The big idea — *safety by escalation*.** The AI classifier is **one signal of three**, never the final word. Low confidence or urgent symptom words **escalate** the patient to a higher level of care, so an uncertain case gets *safer* care, not a confidently wrong label.

---

## 🔬 Under the hood — deep dives

<sub>Each section is collapsed for easy scanning. **Click any title to expand the full detail.**</sub>

<details>
<summary><b>🧠 BD-SkinNet — the vision model (Swin-B + CBAM, INT8)</b></summary>

<br>

A custom model built specifically for **Bangladeshi clinical dermatology** — [`model/bd_skinnet.py`](model/bd_skinnet.py).

```
Input 224×224×3
   │
   ▼  Swin-B backbone (swin_base_patch4_window7_224, 4 feature stages)
   ├── Stage 0 → 128 ch ─┐
   ├── Stage 1 → 256 ch  │  each stage → its own CBAM (channel + spatial
   ├── Stage 2 → 512 ch  │  attention) → Global Average Pool
   └── Stage 3 → 1024 ch─┘
            concat → 1920-d → Dropout → Linear(512) → LayerNorm → GELU
                            → Dropout → Linear(8 classes) → softmax
```

- **Swin Transformer Base** — hierarchical vision transformer with shifted-window attention; captures both fine texture (scale, burrows) and overall lesion shape.
- **CBAM (Convolutional Block Attention Module)** on **all 4 stages** — *channel* attention learns *which* features matter (redness vs. scale), *spatial* attention learns *where* to look (the lesion, not the background). This is the model's built-in focus + interpretability mechanism, and the reason it generalizes well from a modest clinical dataset.
- **Multi-scale fusion** — pooling + concatenating all four stages lets the head reason over coarse and fine evidence at once.

**8 classes** (7 conditions + a `Normal` control): Atopic Dermatitis · Contact Dermatitis · Eczema · Normal · Scabies · Seborrheic Dermatitis · Tinea · Vitiligo — each with a Bengali name.

| Property | Value |
|---|---|
| Test F1 | **92.46%** (held-out Bangladeshi clinical set) |
| Accuracy / AUC-ROC | 92.37% / 0.9937 (reported) |
| Parameters | ~88M (FP32); **INT8** weights for serving |
| Quantization | `torch.quantization.quantize_dynamic` → ~4× smaller, within ~1.5 F1 of FP32 |
| Latency | ~1.8 s/image on **free CPU** |
| Checkpoint | Hugging Face Hub `rafilovestosuffer/bd-skinnet`, downloaded & cached at runtime |
| Training data | **Faridpur, Rangpur & Kishoreganj Medical College Hospitals** — 3,322 real clinical images; no DermNet, no scraped, no web images (rare classes rebalanced with diffusion synthesis) |

> Full [Model Card](docs/MODEL_CARD.md) + [Data Card](docs/DATA_CARD.md) in the repo. If the checkpoint can't download (cold Space / offline), inference returns a deterministic demo result with the identical schema, so the demo always works.

</details>

<details>
<summary><b>🎙 Bengali voice pipeline — robust ASR for noisy, code-switched speech</b></summary>

<br>

Turning rural Bengali speech into structured medical data is hard. The pipeline ([`voice/pipeline.py`](voice/pipeline.py)) is built for it.

**Stage 1 — Speech-to-text** (faster-whisper `small`, INT8, CPU):
- **Format-agnostic** decode via PyAV — reads WAV/WebM/MP4/OGG/MP3/M4A from magic bytes (no `ffmpeg` on PATH, no temp files).
- **Silence/quality gate** — rejects clips that are too short or too quiet, with a helpful Bengali message instead of a hallucinated transcript.
- **3-pass transcription:** ① VAD-filtered + `no_speech_prob` segment filtering → ② no-VAD retry for longer clips → ③ **Bengali script correction** (the `small` model sometimes writes Bengali speech in Devanagari/Hindi; we detect the script leak and re-run forced to Bengali).
- **Hallucination detection** — discards output with box/garbage glyphs or a token repeated 4× in a row.

**Stage 2 — Structured extraction** (Gemini 2.5 Flash-Lite, `google-genai` SDK):
- Handles Bengali, English, **and romanized Bengali** (*"amar gaye khuj hocche"*).
- Returns exactly **9 JSON fields** (complaint, symptoms, area, duration, progression, prior treatment, associated symptoms, name, age) with 3 retries + strict validation + a "don't hallucinate" instruction. The result **auto-fills the editable patient form** and flows into the referral PDF.

</details>

<details>
<summary><b>⚖️ Triage engine — transparent, rule-based, auditable</b></summary>

<br>

The clinical heart of the system ([`severity/engine.py`](severity/engine.py)) — every line is readable and verifiable by a clinician. A **healthy short-circuit** + **three escalation signals**:

```python
if disease_class == "Normal" and confidence >= 0.60:    # Tier 0 — healthy
    return Tier 0

tier = base_tier(disease_class)                          # Signal 1

if confidence < 0.40:   tier = 3                         # Signal 2 — uncertainty
elif confidence < 0.60: tier = max(tier, 2)

if any(kw in transcript for kw in                        # Signal 3 — Bengali keywords
       ["জ্বর","ছড়িয়ে","ব্যথা","রক্ত"]):                #  fever/spreading/pain/blood
    tier = min(tier + 1, 3)
```

| Tier | Label | Action | Facility | Est. cost |
|---|---|---|---|---|
| 0 | HEALTHY | No treatment needed | — | ৳0 |
| 1 | NON-URGENT | Pharmacist within 3–5 days | Local Pharmacy | ৳50–200 |
| 2 | ROUTINE | Upazila Health Complex within 48 h | Upazila Health Complex | ৳0–100 (gov't) |
| 3 | URGENT | Emergency care **today** | District Hospital | ৳0–500 (subsidised) |

> **Safety property:** **no disease class maps to Tier 3 directly.** Emergency is reached *only* by escalation — the model signalling low confidence, or the patient's own urgent words. Out-of-distribution images get safer care, not a wrong label.

</details>

<details>
<summary><b>🔎 RAG chatbot — grounded answers, 4-tier retrieval, hard no-medicine guardrail</b></summary>

<br>

The "Ask AI" tab ([`rag/retriever.py`](rag/retriever.py)) answers in Bengali or English, grounded **only** in trusted public-health sources.

**Knowledge base — 104 curated chunks, four sources only:**

| Source | Chunks | | Source | Chunks |
|---|---:|---|---|---:|
| CDC | 32 | | WHO | 17 |
| NIH / MedlinePlus | 34 | | DGHS Bangladesh | 21 |

Every chunk carries `SOURCE:`/`TOPIC:` provenance. **No DermNet, ever.**

**4-tier retrieval cascade** (fast → semantic, never hard-fails):

```
question → 1. disk cache (SHA-256)        instant repeats
         → 2. ChromaDB (HNSW, cosine)     best semantic match   } embeddings:
         → 3. FAISS (flat inner-product)  semantic fallback     } multilingual-e5-small
         → 4. BM25 (custom IDF)           ALWAYS works, no downloads
```

**Graph RAG** — when a diagnosis is active, the **Kuzu** graph injects structured facts (linked symptoms with ⚠ escalation flags, plus differential diseases sharing ≥2 symptoms) into the prompt, turning generic answers into grounded, differential-aware ones.

**Generation** — Gemini 2.5 Flash-Lite, concise (3–5 sentences), language-matched, 3 retries.

**🚫 Medicine guardrail (enforced in code):** every response passes a regex denylist — dosages (`500 mg`), forms (tablet/cream/…), drug-class suffixes (`-cillin`, `-mycin`, `-zole`, `-cortisone`, …), Bengali medicine phrases. Any match is **replaced** with a "consult a licensed pharmacist/doctor" message. The system *physically cannot* recommend a medication.

</details>

<details>
<summary><b>🕸 Clinical knowledge graph (Kuzu)</b></summary>

<br>

An embedded **Kuzu** property graph ([`graph/store.py`](graph/store.py)) of hand-curated clinical relationships (no patient data ever enters it), built idempotently at startup.

```
(Disease) ──HAS_SYMPTOM──────▶ (Symptom {is_escalation})
(Disease) ──MAPS_TO──────────▶ (TierAction)
(Disease) ──COMMONLY_AFFECTS─▶ (BodyPart)
(Disease) ──DOCUMENTED_BY────▶ (KnowledgeSource: CDC/NIH/WHO/DGHS)
(Symptom) ──ESCALATES_TO─────▶ (TierAction: Tier 3)

7 diseases · 20 symptoms · 12 body parts · 3 tiers · 4 sources
```

Powers the **"Signs to Monitor"** panel (normal vs. ⚠ escalation symptoms, in Bengali) and the Graph RAG context above. Differential diagnosis is a live Cypher query.

</details>

<details>
<summary><b>📄 Bilingual PDF (fpdf2 + HarfBuzz) — Bengali that renders correctly in Acrobat</b></summary>

<br>

The referral letter is **addressed to a doctor, not the patient** — [`pdf_gen/referral.py`](pdf_gen/referral.py).

> **Why fpdf2 + uharfbuzz, not ReportLab?** ReportLab embeds raw code-points with no glyph shaping, so Bengali conjuncts render *broken* in Adobe Acrobat. **fpdf2 pre-shapes text through HarfBuzz (GSUB/GPOS)** before embedding glyph IDs → Bengali is correct in every viewer.

**4-section referral letter:**

| Section | Content |
|---|---|
| 1 · Patient History | Name, age, complaint, symptoms, area, duration, progression, prior treatment (bilingual table) |
| 2 · Clinical Observation | Notes image was analysed by BD-SkinNet; assessment timestamp |
| 3 · AI Diagnostic Assessment | Disease (EN + BN), confidence, **differential** if top-2 > 15%, model provenance, "not a diagnosis" disclaimer |
| 4 · Triage Recommendation | Color-coded urgency badge, action, facility, Bengali instruction, nearest hospital (Tier 3), and a **Scheduled Appointment** block if booked |

Also generates a **one-page CHW slip** (with cost estimate) and a **6-section Care Summary PDF** ([`pdf_gen/consultation_summary.py`](pdf_gen/consultation_summary.py)) extracted from a post-consult transcript.

</details>

<details>
<summary><b>🗺 Emergency hospital finder & epidemiology map</b></summary>

<br>

[`map/hospital_finder.py`](map/hospital_finder.py):
- Queries the **OpenStreetMap Overpass API** (`amenity=hospital`) — **free, no API key** — and ranks by **Haversine distance** from a table of **70 Bangladesh districts** (with alternate spellings: chittagong/chattogram, bogra/bogura…).
- **Resilient:** if Overpass times out, a static **DGHS division-hospital fallback** (with phone numbers) guarantees the PDF always names a real facility. Renders ranked cards + an interactive **Folium** map (user pin + ranked hospital pins, auto-fit), tier-aware as pharmacies / Upazila complexes / emergency hospitals.

[`map/bd_heatmap.py`](map/bd_heatmap.py): a division-level **prevalence heatmap** per disease (qualitative burden from WHO SEARO patterns + literature) with RAG-generated prevention tips.

</details>

<details>
<summary><b>🌐 Multi-channel access — Web · WhatsApp · Telegram · MCP (one container)</b></summary>

<br>

The same clinical pipeline behind multiple front doors, served from a single container via **nginx + supervisor**:

```
   Browser ─────▶┌──────────────────────────┐
   WhatsApp ────▶│  nginx (port 7860)       │──▶ Streamlit UI (:8501)
   Telegram ────▶└──────────────────────────┘──▶ FastAPI webhook (:8000)
                                                     │
                              platform-agnostic ROUTER + per-user STATE MACHINE
```

**WhatsApp & Telegram bot** ([`whatsapp/`](whatsapp/), [`webhook/`](webhook/)):
- **Live on Telegram: [@SkinAIBDBot](https://t.me/SkinAIBDBot)** — try the full district → photo → voice → triage flow from any phone.
- **Meta WhatsApp Cloud API** (HMAC-SHA256 `X-Hub-Signature-256` verification + subscribe handshake) and **Telegram Bot API**, normalized into one router.
- **7-state conversation machine**: `NEW → district → image → voice → processing → result → RAG chat`.
- Hardened: **idempotency** (dedupe 100 msg IDs), **rate limiting** (10/min), **TTL eviction** (10-min idle), blur gate. All sessions **in-memory only** — no DB, no PII.

**MCP server** ([`mcp_server/skinai_server.py`](mcp_server/skinai_server.py)) exposes the engine as **3 tools** to Claude Desktop / Cursor: `triage_skin_condition`, `ask_skin_question` (medicine redaction enforced), `find_emergency_hospitals`.

</details>

<details>
<summary><b>🤝 Telemedicine handoff & in-app care loop</b></summary>

<br>

A typed **provider abstraction** ([`telemedicine/providers.py`](telemedicine/providers.py)) — *"adding a partner is one Python file."*

- **DocTime (Phase 1, live)** — an **honest co-branded handoff**: UTM-tagged deep-link + **QR code** + prefilled bilingual **WhatsApp** message + the referral PDF. **No fabricated booking IDs, no fake API calls** — all URLs are locally synthesized.
- **Phase-3 stubs** (Praava, MediCal, Maya) are registered as `available=False` and raise if called — the roadmap is backed by real code.

**In-app booking + consultation** ([`ui/doctor_booking.py`](ui/doctor_booking.py), [`ui/consultation_room.py`](ui/consultation_room.py)): 6 demo dermatologists → session-only booking (ID, meet link, fee) that flows into the referral PDF → a consultation room (demo / live audio→Whisper / manual notes) → a **Care Summary PDF**.

</details>

<details>
<summary><b>🔐 Privacy, analytics & the /docs dashboard</b></summary>

<br>

- **No patient data is ever persisted** — web app uses `session_state`; the bot uses in-memory sessions with TTL eviction. No images, transcripts, or names touch disk.
- **Anonymized aggregate telemetry only** ([`analytics/db.py`](analytics/db.py)): a local SQLite table of *counters* — event type, disease class, tier, language, confidence bucket. **No identifiers, no content.** Best-effort writes that can never crash the app.
- **`/docs` dashboard** ([`pages/docs.py`](pages/docs.py)) shows knowledge-graph stats + the anonymized usage summary.

</details>

---

## 🧰 Complete tech stack

| Layer | Technology | Why |
|---|---|---|
| **UI** | Streamlit `1.54` | Native HF Spaces; custom medical design system |
| **Model** | timm Swin-B + custom **CBAM** | SOTA backbone + attention focus/interpretability |
| **Quantization** | PyTorch `quantize_dynamic` (INT8) | ~4× smaller — free-CPU & future-offline ready |
| **Image** | Albumentations, OpenCV (Laplacian, CLAHE + unsharp) | Quality gate + auto-enhancement |
| **Speech** | faster-whisper `small` (INT8) + PyAV | Offline Bengali ASR, format-agnostic |
| **LLM** | **Gemini 2.5 Flash-Lite** (`google-genai`) | Free tier, strong Bengali, JSON + RAG |
| **Vectors** | ChromaDB (HNSW) + FAISS + custom **BM25** | Semantic search + zero-dependency fallback |
| **Embeddings** | `intfloat/multilingual-e5-small` | Bengali + English |
| **Graph** | **Kuzu** (embedded Cypher) | Disease–symptom–triage relationships, Graph RAG |
| **PDF** | **fpdf2 + uharfbuzz** | Correct Bengali shaping in Acrobat |
| **Maps** | folium + **Overpass API** | OSM hospitals, no API key |
| **Bots** | Meta WhatsApp Cloud API · Telegram Bot API | Reach rural patients where they are |
| **Server** | **FastAPI + Uvicorn**, nginx + supervisor | Async webhooks, dual-service container |
| **Agents** | **MCP** (FastMCP) | Exposes tools to Claude Desktop / Cursor |
| **Extras** | gTTS (Bengali readout) · qrcode · SQLite (anon analytics) | |
| **Ops** | Docker · GitHub Actions keepalive · pytest (366 tests) | Always-on, well-tested |

---

## 📁 Repository structure

<details>
<summary><b>Click to expand the full repo map</b></summary>

<br>

```
skinai-bangladesh/
├── app.py                      # Streamlit entry point — 7-tab clinical app
├── Dockerfile                  # python:3.10-slim · nginx + supervisor dual-service
├── requirements.txt            # deps (CPU-only torch installed in Dockerfile)
├── packages.txt                # system deps (libsndfile1, ffmpeg)
│
├── model/
│   ├── bd_skinnet.py           # Swin-B + CBAM ×4 + INT8 loader + predict()
│   └── disease_labels.py       # 8 classes · Bengali names · base tiers
├── severity/engine.py          # Tier 0 + 3-signal triage engine
├── voice/pipeline.py           # 3-pass Whisper ASR → Gemini 9-field history
├── rag/
│   ├── retriever.py            # cache→ChromaDB→FAISS→BM25 + Graph RAG + redaction
│   ├── chroma_store.py · build_index.py · cache.py
│   └── knowledge/              # 104 chunks: CDC×32 · NIH×34 · WHO×17 · DGHS×21
├── graph/store.py              # Kuzu disease–symptom–triage graph
├── pdf_gen/
│   ├── referral.py             # 4-section referral + CHW slip (fpdf2 + HarfBuzz)
│   └── consultation_summary.py # 6-section Care Summary PDF
├── map/
│   ├── hospital_finder.py      # Overpass + Haversine + DGHS fallback (70 districts)
│   └── bd_heatmap.py           # prevalence heatmap
├── telemedicine/               # provider Protocol + DocTime Phase-1 handoff
├── whatsapp/ · webhook/        # bot router, state machine, clients, FastAPI server
├── mcp_server/skinai_server.py # MCP server — 3 tools over stdio
├── ui/                         # components, styles, booking, consultation room, tabs
├── analytics/db.py             # anonymized aggregate telemetry (no PII)
├── pages/docs.py               # /docs live ops dashboard
├── scripts/ · .github/workflows/keepalive.yml
├── tests/                      # 16 modules · 366 tests
└── docs/                       # MODEL_CARD · DATA_CARD · ETHICS · BUSINESS_MODEL · …
```

</details>

---

## 🚀 Run it yourself

<details>
<summary><b>Local development</b></summary>

<br>

```bash
git clone https://github.com/rafilovestosuffer/Hackathon_2.0_sci.git
cd Hackathon_2.0_sci

pip install torch torchvision --extra-index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt          # CPU only, ~3 GB RAM, Python 3.10+

cp .env.example .env                      # then set GEMINI_API_KEY=...
                                          # free key: https://aistudio.google.com
python rag/build_index.py                 # first run only (ChromaDB/BM25 auto-build too)

streamlit run app.py
```

**Optional services:**
```bash
uvicorn webhook.server:app --port 8000    # WhatsApp + Telegram webhooks
python -m mcp_server.skinai_server        # MCP server (Claude Desktop / Cursor)
```

</details>

<details>
<summary><b>Deploy to Hugging Face Spaces (Docker)</b></summary>

<br>

The container is self-contained: the Dockerfile installs the **CPU-only torch wheel** (avoids a 700 MB CUDA download), downloads the Bengali font, pre-caches the embedding model, and **builds the RAG index at build time**. At runtime, **supervisor** runs **nginx on port 7860** (HF requirement), proxying to **Streamlit (:8501)** and the **FastAPI webhook (:8000)**.

1. Create a Space → **Docker SDK · CPU Basic · Public**
2. **Settings → Variables and Secrets** → add `GEMINI_API_KEY` (and bot tokens if used)
3. Push — Docker builds automatically (first cold start ~3–5 min)
4. A **GitHub Actions keepalive** pings the Space every 20 min to keep it awake

</details>

---

## 🧪 Testing & reliability

```bash
pytest tests/ -v
```

**366 tests across 16 modules** cover every layer — severity, RAG + redaction, voice + extraction, PDF, hospital finder, booking, bot state/router/clients, webhooks, telemedicine, end-to-end. All green.

**Graceful degradation is a design invariant** — every external dependency has a fallback:

| If this fails… | …the system does this |
|---|---|
| Model checkpoint download | Deterministic demo prediction (same schema) |
| ChromaDB / FAISS | Falls back to BM25 keyword search |
| Kuzu graph | Skips graph context; RAG still answers |
| Overpass API | DGHS division-hospital fallback |
| Bengali font | Downloads it, else Helvetica |
| Analytics write | Swallowed silently — app continues |

---

## 🧭 Responsible AI & constraint compliance

<details>
<summary><b>Safety principles + the full compliance checklist</b></summary>

<br>

- **Never a diagnosis** — every output is a *referral to a licensed clinician*; the PDF is addressed to a doctor.
- **Never a medicine** — enforced in code (regex redaction over every LLM response).
- **Uncertainty escalates** — confidence < 40% → Tier 3 by design.
- **Bias disclosed in the product** — a bilingual fairness note renders under every prediction (training data is predominantly Fitzpatrick IV–VI, adults ≥18, 7 conditions; pediatric / melanoma / mucosal / Fitzpatrick I–III are out of scope).
- **Data minimization** — no PII persisted; only anonymized aggregate counters.

| # | Constraint | Status | Evidence |
|---|---|---|---|
| 1 | No DermNet data | ✅ | Clinical training data + 104 chunks all CDC/NIH/WHO/DGHS |
| 2 | No login / instant public URL | ✅ | Public HF Space, no auth |
| 3 | No medicine recommendations | ✅ | `_redact_medicine_names()` on every RAG response |
| 4 | No persistent patient database | ✅ | `session_state` + in-memory bot sessions; only anonymized non-PII counters on disk |
| 5 | Knowledge = CDC/NIH/WHO/DGHS only | ✅ | Every chunk has a `SOURCE:` header |
| 6 | INT8 quantization on CPU | ✅ | `quantize_dynamic`; CPU-only torch wheel |
| 7 | Live through the event window | ✅ | GitHub Actions keepalive every 20 min |
| 8 | Commit history in window | ✅ | Dated commit log |
| 9 | Demo video (3–5 min) | ✅ | [YouTube walkthrough](https://youtu.be/9zOjfBBU4qg) |

Full [Model Card](docs/MODEL_CARD.md) · [Data Card](docs/DATA_CARD.md) · [Ethics Statement](docs/ETHICS_STATEMENT.md).

</details>

---

## 💰 Business model & impact

<details>
<summary><b>How it stays free for patients — and still sustainable</b></summary>

<br>

**Mission lock:** *screening, triage, and the referral PDF are **free at the patient endpoint, forever.*** ([`docs/BUSINESS_MODEL.md`](docs/BUSINESS_MODEL.md))

Three independent revenue streams (losing any one is survivable):

1. **Teleconsult service fee** — a small, transparent platform fee added *only* if a patient chooses to book; the doctor keeps 100% of their fee. SkinAI-referred patients arrive with a structured PDF → shorter consults, fewer no-shows.
2. **NRB "Sponsor-a-District"** — the ~1.7 M-strong diaspora (>$20 B/yr in remittances) funds the free tier in a named district, with monthly usage reporting. A working demo widget is in the app.
3. **Public-health grants** — anonymized upazila-level epidemiology shared with MoHFW / DGHS / icddr,b under a non-commercial license.

**Unit economics:** ≈ **$0.0003/inference**, ≈ **$40/month** hosting at 10k MAU, break-even ≈ 45 bookings/month.

</details>

<details>
<summary><b>Scalability roadmap</b></summary>

<br>

| Phase | Scope | Cost/mo | Lever |
|---|---|---|---|
| **1 — Pilot** | 2 Upazila complexes, Rangpur | < $50 | HF Spaces + WhatsApp free tier (built) |
| **2 — Regional** | 8 districts | ≈ $200 | HF → AWS `ap-south-1` is a Dockerfile swap |
| **3 — National + South Asia** | + Hindi/Urdu RAG | ≈ $400 | **Offline ONNX/TFLite APK**, SMS triage, CHW mode |

**Last-mile vision:** only ~40% of rural Bangladesh has reliable 4G. The INT8 model (< 50 MB) is already small enough to bundle in an offline APK — the hardest first step is **done**. ([`docs/SCALABILITY_ROADMAP.md`](docs/SCALABILITY_ROADMAP.md))

</details>

---

## 📚 Attribution

<details>
<summary><b>Libraries, models & data sources (with licenses)</b></summary>

<br>

| Resource | Source | License |
|---|---|---|
| Swin Transformer (timm) | Microsoft | Apache 2.0 |
| faster-whisper | SYSTRAN / OpenAI Whisper | MIT |
| Gemini 2.5 Flash-Lite | Google (`google-genai`) | API ToS |
| ChromaDB · FAISS | Chroma · Meta AI | Apache 2.0 · MIT |
| `multilingual-e5-small` | intfloat (Microsoft) | MIT |
| Kuzu | Kuzu Inc. | MIT |
| fpdf2 · uharfbuzz | fpdf2 · HarfBuzz | LGPL · MIT-style |
| folium · Overpass / OSM | python-visualization · OSM | MIT · ODbL |
| FastAPI · Uvicorn · httpx | — | MIT · BSD |
| MCP (FastMCP) | Anthropic / community | MIT |
| CDC · NIH content | US Gov | Public Domain |
| WHO content | WHO | CC BY-NC-SA 3.0 |
| DGHS Bangladesh | DGHS | Public sector info |
| Noto Sans Bengali | Google Fonts | OFL 1.1 |

</details>

---

## 📱 Try it on Telegram — [@SkinAIBDBot](https://t.me/SkinAIBDBot)

The **same clinical pipeline, live inside Telegram** — no app install, no login, works on any phone. Send your district, one photo, and a Bengali voice note; the bot replies with a bilingual diagnosis, triage tier, and next steps.

<div align="center">

<table>
<tr>
<th>Live bot conversation</th>
<th>Scan to open the bot</th>
</tr>
<tr>
<td align="center"><img src="assets/screenshots/telegram-bot-chat.jpg" width="300" alt="SkinAI Bangladesh Telegram bot guiding a patient in Bengali — district, skin photo, then a voice-note request"></td>
<td align="center"><img src="assets/screenshots/telegram-qr.png" width="280" alt="QR code linking to the @SkinAIBDBot Telegram bot"></td>
</tr>
<tr>
<td align="center"><sub>District → photo → voice note, guided in Bengali + English</sub></td>
<td align="center"><sub>Or open <a href="https://t.me/SkinAIBDBot"><b>t.me/SkinAIBDBot</b></a> directly</sub></td>
</tr>
</table>

</div>

> The bot runs the identical BD-SkinNet → triage → referral engine as the web app, through a 7-state conversation machine — see the [multi-channel deep dive](#-under-the-hood--deep-dives) above.

---

## 📬 Contact

**Rafiur Rahman** · mdrafiurrahman123098@gmail.com
**Live app:** [huggingface.co/spaces/rafilovestosuffer/skinai-bd](https://huggingface.co/spaces/rafilovestosuffer/skinai-bd) · **Source:** [github.com/rafilovestosuffer/Hackathon_2.0_sci](https://github.com/rafilovestosuffer/Hackathon_2.0_sci)

---

## ⚠️ Medical disclaimer

SkinAI Bangladesh is a **research prototype** — **not a certified medical device**. It must not replace professional diagnosis or treatment. Every output is a *referral to a licensed physician*; always consult one.

> এই অ্যাপ্লিকেশনটি গবেষণামূলক উদ্দেশ্যে তৈরি। এটি কোনো স্বীকৃত চিকিৎসা যন্ত্র নয়। সর্বদা একজন লাইসেন্সপ্রাপ্ত চিকিৎসকের পরামর্শ নিন।

<div align="center">

---

*সঠিক রোগী → সঠিক ডাক্তার → সঠিক সময় · Right patient → Right doctor → Right time*

[**▶ Open the live app**](https://huggingface.co/spaces/rafilovestosuffer/skinai-bd)

</div>
