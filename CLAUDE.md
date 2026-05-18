# SkinAI Bangladesh — Claude Code Master Context
# ⚡ READ THIS FIRST. EVERY SESSION. NO EXCEPTIONS. ⚡

## 🏆 MISSION
Win SciBlitz AI Challenge 2026 — IEEE SB CUET — Track A: Health & Society.
Project: AI-powered dermatological screening + triage for rural Bangladesh.
Narrative: **"Right patient → Right doctor → Right time"**

## 📅 CRITICAL DEADLINES
| Milestone | Date |
|-----------|------|
| Submission | July 1, 2026 — 11:59 PM BST |
| Shortlist announced | July 3, 2026 |
| Final Presentation Day | July 10, 2026 — CUET, Chattogram |
| App must stay live until | July 12, 2026 |

## 🎯 JUDGING RUBRIC (optimize EVERY decision against this)
| Criterion | Weight | How we win it |
|-----------|--------|---------------|
| Innovation & Originality | 25% | BD-specific clinical data, multi-signal triage, Bengali voice, local hospital map |
| Technical Implementation | 25% | Swin+CBAM+GradCAM++, RAG, quantized CPU inference, all integrated |
| Real-world Impact | 20% | 1 derm per 250k people stat, Rahim story, no quacks narrative |
| Demo Quality | 20% | Zero-click public URL, instant load, Bengali UI, PDF output |
| Presentation | 10% | 5-min slot + 3-min Q&A — Rahim story opens, data closes |

---

## 🚫 HARD CONSTRAINTS — NEVER VIOLATE THESE

```
CONSTRAINT 1: NO DermNet data — forbidden (AI-generated images policy)
CONSTRAINT 2: NO login / NO user accounts — judges need instant public URL
CONSTRAINT 3: NO medicine recommendations — triage + referral ONLY
CONSTRAINT 4: NO persistent database — session_state only
CONSTRAINT 5: Knowledge base = CDC + NIH + WHO + DGHS Bangladesh ONLY
CONSTRAINT 6: HF Spaces free CPU — INT8 quantization MANDATORY
CONSTRAINT 7: App live until July 12, 2026 — keepalive script required
CONSTRAINT 8: GitHub commits must exist between May 14 – July 1, 2026
CONSTRAINT 9: Demo video = 3–5 min, YouTube unlisted or Google Drive
```

---

## 📁 REPOSITORY STRUCTURE

```
skinai-bangladesh/
├── CLAUDE.md              ← YOU ARE HERE — master context
├── PLAN.md                ← Full 40-day sprint plan
├── PROGRESS.md            ← Session log (update every session end)
├── DECISIONS.md           ← Architecture decisions + rationale
├── TASK.md                ← TODAY'S tasks ONLY (rewrite each session)
│
├── app.py                 ← Streamlit entry point (main)
├── requirements.txt       ← Python deps
├── packages.txt           ← System deps (libsndfile1 for audio etc.)
├── .env.example           ← GEMINI_API_KEY template (no real keys)
├── README.md              ← Public-facing, submission ready
│
├── model/
│   ├── bd_skinnet.py      ← Swin+CBAM INT8 inference wrapper
│   ├── gradcam.py         ← GradCAM++ on Swin last stage
│   ├── disease_labels.py  ← English + Bengali disease name map
│   ├── export_int8.py     ← One-time INT8 export script
│   └── checkpoints/       ← .pt files (gitignore if >100MB, use HF Hub)
│
├── severity/
│   └── engine.py          ← 4-signal triage engine
│
├── voice/
│   └── pipeline.py        ← faster-whisper → transcript → Gemini JSON
│
├── rag/
│   ├── build_index.py     ← One-time FAISS index builder
│   ├── retriever.py       ← FAISS query + Gemini answer
│   └── knowledge/         ← CDC/NIH/WHO/DGHS .txt chunks
│
├── pdf_gen/
│   └── referral.py        ← reportlab 4-section referral letter
│
├── map/
│   └── hospital_finder.py ← Overpass API + Folium hospital pins
│
├── ui/
│   ├── components.py      ← Reusable Streamlit widgets
│   └── styles.py          ← Bengali Noto Sans font + CSS injection
│
├── tests/
│   ├── test_severity.py   ← Unit tests for all 4 signals
│   ├── test_gradcam.py    ← GradCAM shape + coverage tests
│   ├── test_pdf.py        ← PDF generation smoke test
│   └── test_pipeline.py   ← End-to-end integration test
│
└── scripts/
    ├── keepalive.py       ← Ping HF Spaces every 20 min (cron/GitHub Actions)
    └── seed_commits.py    ← Utility to verify commit history
```

---

## 🔄 MASTER PIPELINE (data flow — never deviate)

```
VOICE INPUT:
  Bengali audio → faster-whisper (base, bn) → Bengali transcript
  Bengali transcript → Gemini 1.5 Flash → patient_history JSON:
    {
      chief_complaint: str,
      symptoms: list[str],
      affected_area: str,
      duration: str,
      progression: str,
      previous_treatment: str,
      associated_symptoms: list[str],
      patient_name: str,
      patient_age: str
    }

IMAGE INPUT:
  skin_image → BD-SkinNet (INT8) → {disease_class: str, confidence: float, top2: list}
  skin_image → GradCAM++ → {heatmap: np.ndarray, coverage_pct: float}

TRIAGE:
  [disease_class, confidence, coverage_pct, transcript] → severity_engine()
  → {tier: int(1|2|3), urgency_label: str, action: str, facility_type: str}

EMERGENCY BRANCH (tier == 3 only):
  → Overpass API (district coordinates) → top 5 nearest hospitals
  → Folium map rendered in Streamlit
  → hospital[0] injected into referral letter Section 4

PDF OUTPUT:
  session_state (all above) → referral.py → 4-section PDF
  Single button click. Zero manual input required.

RAG CHATBOT:
  user_question → FAISS retrieval (MiniLM embeddings)
  → top-k chunks → Gemini 1.5 Flash → Bengali/English answer
```

---

## 🧠 BD-SkinNet SPECIFICATION

| Property | Value |
|----------|-------|
| Architecture | Swin Transformer Base + CBAM (Channel+Spatial Attention) |
| Performance | F1 = 92.46% on Bangladeshi clinical test set |
| Training data | Faridpur Medical College Hospital + Rangpur Medical College Hospital |
| Deployment | INT8 quantized (torch.quantization.quantize_dynamic or ONNX) |
| GradCAM++ target | Last Swin stage (features before classification head) |
| Input size | 224×224 RGB |
| Output | softmax probabilities over N disease classes |

**Differential diagnosis rule:** If top2[1].confidence > 0.15 → show in referral Section 3.

---

## ⚖️ SEVERITY ENGINE — 4 SIGNALS

```python
# Signal 1: Disease class base tier (hardcoded lookup)
# Classes = actual BD-SkinNet output classes (7 classes from training)
DISEASE_TIER = {
    # Tier 2 — ROUTINE DOCTOR (Upazila Health Complex within 48h)
    "Atopic_Dermatitis":     2,  # chronic, needs prescription management
    "Eczema":                2,  # widespread presentation, needs doctor
    "Scabies":               2,  # infectious, needs prescription
    "Vitiligo":              2,  # chronic autoimmune, needs specialist
    # Tier 1 — PHARMACIST (within 3-5 days)
    "Contact_Dermatitis":    1,  # OTC antihistamines + avoid trigger
    "Seborrheic_Dermatitis": 1,  # OTC antifungal shampoo/cream
    "Tinea":                 1,  # OTC antifungal (clotrimazole)
}
# Note: No Tier 3 base class — Tier 3 is reached only via Signal 2/3/4 escalation
# (low confidence, high GradCAM coverage, or urgent voice keywords)

# Signal 2: Confidence modifier
if confidence < 0.40: tier = 3
elif confidence < 0.60: tier = max(tier, 2)

# Signal 3: GradCAM coverage modifier
if coverage_pct > 40.0: tier = min(tier + 1, 3)

# Signal 4: Bengali voice keyword modifier
ESCALATION_KEYWORDS = ["জ্বর", "ছড়িয়ে", "ব্যথা", "রক্ত"]
if any(kw in transcript for kw in ESCALATION_KEYWORDS): tier = min(tier + 1, 3)

# Tier actions
TIER_ACTIONS = {
    1: {"label": "NON-URGENT", "action": "Consult local pharmacist within 3-5 days",
        "facility": "Local Pharmacy", "bn": "৩-৫ দিনের মধ্যে নিকটস্থ ফার্মাসিস্টের সাথে পরামর্শ করুন"},
    2: {"label": "ROUTINE", "action": "Visit Upazila Health Complex within 48 hours",
        "facility": "Upazila Health Complex", "bn": "৪৮ ঘণ্টার মধ্যে উপজেলা স্বাস্থ্য কমপ্লেক্সে যান"},
    3: {"label": "URGENT", "action": "Seek emergency care TODAY at District Hospital",
        "facility": "District Hospital", "bn": "আজই জেলা হাসপাতালে জরুরি চিকিৎসা নিন — জরুরি চিকিৎসা প্রয়োজন"},
}
```

---

## 📄 REFERRAL LETTER — 4 SECTIONS

| Section | Source | Key Content |
|---------|--------|-------------|
| 1. Patient History | Gemini JSON from voice | chief_complaint, symptoms, area, duration, progression, previous treatment |
| 2. Clinical Observation | GradCAM++ output | Heatmap image embedded, coverage%, assessment datetime |
| 3. AI Diagnostic Assessment | BD-SkinNet output | Disease (English+Bengali), confidence, differential if top2>15%, model name, disclaimer |
| 4. Triage Recommendation | Severity engine | Tier, urgency label, action, facility type+name, English+Bengali instructions |

**Zero manual input. Single button. All from session_state.**

---

## 🤖 RAG CHATBOT

| Component | Spec |
|-----------|------|
| Embeddings | `sentence-transformers/paraphrase-multilingual-MiniLM-L6-v2` |
| Vector store | `faiss-cpu` (cosine similarity) |
| LLM | Gemini 1.5 Flash (via `google-generativeai`) |
| Knowledge sources | CDC, NIH, WHO, DGHS Bangladesh — text chunks only |
| Forbidden source | DermNet (NEVER) |
| Answer language | Match user's language (Bengali or English) |

---

## 🗺️ EMERGENCY HOSPITAL MAP

```
Trigger: severity tier == 3
API: Overpass API (free, no key needed)
Query: amenity=hospital within district bounding box
Display: folium map with 5 nearest pins
Output: Name | Distance (km) | Address
Inject: hospital[0] name+address → referral Section 4
```

---

## 📦 KEY DEPENDENCIES

```txt
# requirements.txt essentials
streamlit>=1.32.0
torch>=2.0.0             # CPU only for HF Spaces
timm>=0.9.0              # Swin Transformer
faster-whisper>=0.10.0
google-generativeai>=0.5.0
faiss-cpu>=1.7.4
sentence-transformers>=2.6.0
reportlab>=4.0.0
folium>=0.15.0
streamlit-folium>=0.18.0
Pillow>=10.0.0
opencv-python-headless>=4.9.0
numpy>=1.24.0
requests>=2.31.0         # Overpass API
```

---

## 🎙️ IMPACT NARRATIVE (use in demo, report, presentation)

> "Bangladesh has approximately 1 dermatologist per 250,000 people. 80% of skin conditions in rural Bangladesh go untreated or are mistreated by unlicensed practitioners. SkinAI Bangladesh does not replace the doctor. It ensures the right patient reaches the right doctor at the right time — instead of reaching the wrong practitioner too late."

**Opening story (demo video + final presentation):**
> "Rahim is a farmer in Rangpur. He notices a spreading rash. The nearest dermatologist is 4 hours away and costs 1,500 taka he cannot spare. He opens SkinAI Bangladesh. He speaks in Bengali. He takes a photo. In seconds: Tinea Corporis, mild, Tier 1. The system tells him in Bengali — go to your local pharmacist. If it spreads in 3 days, here is your referral letter for Rangpur Medical College Hospital. Rahim has a plan. He does not need to go to Dhaka."

---

## 📋 SESSION STARTUP PROTOCOL (Claude Code runs this automatically)

1. Read `CLAUDE.md` — understand full context
2. Read `PROGRESS.md` — know what is done and what is blocked
3. Read `TASK.md` — know exactly what to build TODAY
4. Run `git status` — verify clean working state
5. Begin coding — no re-explanation required

## 📋 SESSION END PROTOCOL

1. `git add -A && git commit -m "[week-X/day-Y] descriptive message"`
2. Update `PROGRESS.md` — completed tasks, blockers, next entry point
3. Rewrite `TASK.md` for next session (if known)
4. Confirm HF Spaces build status (if deployed)

---

## 🔖 CURRENT SPRINT

```
# UPDATE THIS BLOCK EVERY WEEK
Current Week: 1 (May 18–24)
Focus: Repository setup + BD-SkinNet INT8 export + HF Spaces skeleton
Owner this week: ML lead (me)
```

---
*This file is the single source of truth for all Claude Code sessions.*
*Last updated: [DATE] — Update timestamp at end of each week.*
