# SkinAI Bangladesh — Claude Code Master Context
# READ THIS FIRST. EVERY SESSION. NO EXCEPTIONS.

## MISSION
Win SciBlitz AI Challenge 2026 — IEEE SB CUET — Track A: Health & Society.
Project: AI-powered dermatological screening + triage for rural Bangladesh.
Narrative: **"Right patient → Right doctor → Right time"**

---

## CRITICAL DEADLINES
| Milestone | Date |
|-----------|------|
| Submission | July 1, 2026 — 11:59 PM BST |
| Shortlist announced | July 3, 2026 |
| Final Presentation Day | July 10, 2026 — CUET, Chattogram |
| App must stay live until | July 12, 2026 |

---

## JUDGING RUBRIC — Optimise every decision against this
| Criterion | Weight | How we win it |
|-----------|--------|---------------|
| Innovation & Originality | 25% | BD-specific clinical data, multi-signal triage, Bengali voice, local hospital map, doctor booking |
| Technical Implementation | 25% | Swin+CBAM+GradCAM++, RAG, INT8 CPU inference, fully integrated |
| Real-world Impact | 20% | 1 derm per 250k people stat, Rahim story, no-quacks narrative, CHW mode |
| Demo Quality | 20% | Zero-click public URL, instant load, Bengali UI, PDF output, video call flow |
| Presentation | 10% | 5-min slot + 3-min Q&A — Rahim story opens, data closes |

---

## HARD CONSTRAINTS — NEVER VIOLATE

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

## REPOSITORY STRUCTURE (actual — as of Day 23)

```
Hackathon_2.0_sci/
├── CLAUDE.md                     ← YOU ARE HERE — master context
├── PLAN.md                       ← Full 40-day sprint plan
├── PROGRESS.md                   ← Session log (update every session end)
├── DECISIONS.md                  ← Architecture decisions + rationale
├── TASK.md                       ← TODAY'S tasks ONLY (rewrite each session)
├── SESSION_PROTOCOL.md           ← Startup/end checklist
│
├── app.py                        ← Streamlit entry point — 5-tab pipeline
├── requirements.txt              ← Python deps (pinned versions)
├── packages.txt                  ← System deps (libsndfile1 etc.)
├── Dockerfile                    ← HF Spaces Docker build
├── .env.example                  ← GEMINI_API_KEY template (no real keys)
├── README.md                     ← Public-facing, submission ready
│
├── assets/                       ← Static assets (fonts, images)
├── docs/
│   └── demo_script.md            ← 8-segment 4-min Rahim story demo script
│
├── model/
│   ├── bd_skinnet.py             ← Swin-B + CBAM INT8 inference wrapper
│   ├── gradcam.py                ← GradCAM++ on last Swin stage
│   ├── disease_labels.py         ← 7 classes: English + Bengali + tier map
│   ├── export_int8.py            ← One-time INT8 quantization script
│   └── checkpoints/              ← bd_skinnet_best.pth (gitignored >100MB)
│                                    STATUS: STILL PENDING — placeholder active
│
├── severity/
│   └── engine.py                 ← 4-signal triage engine → tier 1/2/3
│
├── voice/
│   └── pipeline.py               ← faster-whisper → Bengali transcript
│                                    → Gemini JSON patient_history extraction
│
├── rag/
│   ├── build_index.py            ← One-time FAISS index builder
│   ├── retriever.py              ← FAISS query + Gemini answer (context-aware)
│   ├── seed_knowledge.py         ← One-time knowledge base seeder
│   └── knowledge/                ← 100 CDC/NIH/WHO/DGHS .txt chunks (gittracked)
│
├── pdf_gen/
│   ├── referral.py               ← fpdf2 4-section referral letter
│   └── consultation_summary.py   ← fpdf2 post-consultation AI care summary
│
├── map/
│   ├── hospital_finder.py        ← Overpass API + Folium hospital pins
│   └── bd_heatmap.py             ← Bangladesh division epidemiology heatmap
│
├── ui/
│   ├── components.py             ← Reusable Streamlit widgets (12 functions)
│   ├── styles.py                 ← Medical-grade design system + Bengali CSS
│   ├── doctor_booking.py         ← Doctor booking tab (Tab 5)
│   └── consultation_room.py      ← Consultation room tab (video call embed)
│
├── tests/
│   ├── test_severity.py          ← 29 tests — all 4 signals + edge cases
│   ├── test_gradcam.py           ← 13 tests — shape, coverage, overlay
│   ├── test_pdf.py               ← 11 tests — referral PDF smoke tests
│   ├── test_rag.py               ← 30 tests — FAISS + Gemini + context injection
│   ├── test_ui.py                ← 85 tests — all 12 component functions
│   ├── test_hospital.py          ← 17 tests — Overpass mock, haversine, coords
│   ├── test_voice.py             ← 10 tests — Whisper transcription robustness
│   ├── test_voice_gemini.py      ← 15 tests — Gemini extraction, mocked
│   ├── test_pipeline.py          ← 35 tests — end-to-end interface compatibility
│   ├── test_doctor_booking.py    ← 38 tests — booking flow, validation, PDF
│   └── test_consultation_summary.py ← consultation summary smoke tests
│   TOTAL: 310/312 passing (2 pre-existing voice mock failures — unrelated)
│
├── scripts/
│   ├── keepalive.py              ← Ping HF Spaces every 20 min
│   ├── generate_demo_summary.py  ← Generate demo PDF sample
│   └── make_demo_clip.py         ← Demo video utility
│
└── .github/
    └── workflows/
        └── keepalive.yml         ← GitHub Actions cron: */20 * * * *
```

---

## APPLICATION ARCHITECTURE — 5 Tabs

| Tab | Bengali Label | Contents |
|-----|--------------|----------|
| Tab 1 | রোগ নির্ণয় | Voice input + image upload → triage → hospital map (tier 3 only) |
| Tab 2 | প্রশ্ন করুন | Context-aware RAG chatbot (FAISS + Gemini) |
| Tab 3 | রেফারেল পত্র | PDF preview + referral letter download |
| Tab 4 | মহামারী তথ্য | Bangladesh division-level epidemiology heatmap |
| Tab 5 | ডাক্তার বুকিং | Doctor booking + video call (complete care loop) |

**Sidebar extras:**
- Animated 4-step pipeline progress tracker
- "🎬 Load Demo" buttons (Scabies Tier 3 / Eczema Tier 2)
- CHW / Shasthya Seboika simplified mode toggle
- Impact comparison panel (Without SkinAI vs With SkinAI)

---

## MASTER PIPELINE (data flow — never deviate)

```
VOICE INPUT:
  Bengali audio → faster-whisper (base, bn, CPU int8) → Bengali transcript
  Bengali transcript → Gemini 2.5 Flash → patient_history JSON:
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
  skin_image → CLAHE + unsharp_mask (auto enhancement if dark/blurry)
  skin_image → BD-SkinNet (INT8) → {disease_class: str, confidence: float, top2: list}
  skin_image → GradCAM++ → {heatmap: np.ndarray, coverage_pct: float}

TRIAGE:
  [disease_class, confidence, coverage_pct, transcript] → severity_engine()
  → {tier: int(1|2|3), urgency_label: str, action: str, facility_type: str,
     bengali_text: str}

EMERGENCY BRANCH (tier == 3 only):
  → Overpass API (district coordinates) → 5 nearest hospitals
  → Folium map rendered in Streamlit
  → hospital[0] injected into referral letter Section 4

DOCTOR BOOKING (Tab 5):
  → triage-aware booking form (tier 1: optional, tier 2: recommended, tier 3: emergency only)
  → booking_confirmed + booking_details → injected into PDF Section 4
  → JOIN VIDEO CALL button (consultation_room.py)

PDF OUTPUT:
  session_state → referral.py → fpdf2 + HarfBuzz shaping → 4-section PDF
  Single button click. Zero manual input required.
  Section 4 appended with appointment block if booking_confirmed == True.

POST-CONSULTATION PDF:
  session_state → consultation_summary.py → 6-section AI care summary
  Generated after video call ends.

RAG CHATBOT:
  user_question → FAISS retrieval (MiniLM embeddings)
  → top-k chunks → Gemini (with disease_context injection if diagnosis exists)
  → Bengali/English answer (language auto-detected from Unicode range)

BENGALI TTS:
  triage tier text → gTTS (Bengali) → audio readout in Streamlit player
```

---

## BD-SkinNet SPECIFICATION

| Property | Value |
|----------|-------|
| Architecture | Swin Transformer Base + CBAM (Channel + Spatial Attention, 4 stages) |
| Performance | F1 = 92.46%, Accuracy = 92.37%, AUC-ROC = 0.9937 |
| Training data | Faridpur Medical College Hospital + Rangpur Medical College Hospital |
| Stage dims | [128, 256, 512, 1024] — fusion head: 1920-d |
| Deployment | INT8 quantized via torch.quantization.quantize_dynamic |
| GradCAM++ target | `model.cbam_modules[-1].spatial_attn.conv` |
| Input size | 224×224 RGB |
| Output | softmax probabilities over 7 disease classes |
| Checkpoint | `model/checkpoints/bd_skinnet_best.pth` — **PENDING** |

**Differential diagnosis rule:** If `top2[1].confidence > 0.15` → show in referral Section 3.

**Checkpoint stub:** `_run_model()` in `app.py` returns `("Tinea", 0.82, [...])` until the real `.pth` is placed. Replace stub body when checkpoint arrives.

---

## SEVERITY ENGINE — 4 SIGNALS

```python
# Signal 1: Disease class base tier
# 7 classes from BD-SkinNet training — no Tier 3 base class
DISEASE_TIER = {
    # Tier 2 — ROUTINE (Upazila Health Complex within 48h)
    "Atopic_Dermatitis":     2,
    "Eczema":                2,
    "Scabies":               2,
    "Vitiligo":              2,
    # Tier 1 — NON-URGENT (local pharmacist within 3-5 days)
    "Contact_Dermatitis":    1,
    "Seborrheic_Dermatitis": 1,
    "Tinea":                 1,
}

# Signal 2: Model confidence modifier
if confidence < 0.40:   tier = 3          # very uncertain → escalate
elif confidence < 0.60: tier = max(tier, 2)

# Signal 3: GradCAM coverage modifier (widespread lesion)
if coverage_pct > 40.0: tier = min(tier + 1, 3)

# Signal 4: Bengali voice keyword modifier (systemic/emergency symptoms)
ESCALATION_KEYWORDS = ["জ্বর", "ছড়িয়ে", "ব্যথা", "রক্ত"]
if any(kw in transcript for kw in ESCALATION_KEYWORDS):
    tier = min(tier + 1, 3)

# Tier output actions
TIER_ACTIONS = {
    1: {
        "label":    "NON-URGENT",
        "action":   "Consult local pharmacist within 3-5 days",
        "facility": "Local Pharmacy",
        "bn":       "৩-৫ দিনের মধ্যে নিকটস্থ ফার্মাসিস্টের সাথে পরামর্শ করুন"
    },
    2: {
        "label":    "ROUTINE",
        "action":   "Visit Upazila Health Complex within 48 hours",
        "facility": "Upazila Health Complex",
        "bn":       "৪৮ ঘণ্টার মধ্যে উপজেলা স্বাস্থ্য কমপ্লেক্সে যান"
    },
    3: {
        "label":    "URGENT",
        "action":   "Seek emergency care TODAY at District Hospital",
        "facility": "District Hospital",
        "bn":       "আজই জেলা হাসপাতালে জরুরি চিকিৎসা নিন — জরুরি চিকিৎসা প্রয়োজন"
    },
}
```

---

## REFERRAL LETTER — 4 SECTIONS

| Section | Source | Key Content |
|---------|--------|-------------|
| 1. Patient History | Gemini JSON from voice | chief_complaint, symptoms, affected area, duration, progression, previous treatment |
| 2. Clinical Observation | GradCAM++ output | Heatmap image (embedded), coverage%, assessment datetime |
| 3. AI Diagnostic Assessment | BD-SkinNet output | Disease (English + Bengali), confidence, differential if top2 > 15%, model name, disclaimer |
| 4. Triage Recommendation | Severity engine + booking | Tier, urgency label, action, facility type + name (EN+BN). If booking_confirmed: appended appointment subsection (doctor, date, time, join link, booking ID, fee) |

**Rendering:** fpdf2 + uharfbuzz (HarfBuzz GSUB shaping) — Bengali renders correctly in Adobe Acrobat. Noto Sans Bengali font downloaded at Dockerfile build time, runtime fallback if missing.

**Zero manual input. Single button. All from session_state.**

---

## POST-CONSULTATION SUMMARY — 6 SECTIONS

Generated by `pdf_gen/consultation_summary.py` after a video call ends.

| Section | Content |
|---------|---------|
| 1. Consultation Details | Doctor, date, time, booking ID |
| 2. Patient History | Pulled from session voice history |
| 3. AI Pre-Consultation Assessment | BD-SkinNet diagnosis + triage tier |
| 4. Consultation Notes | Gemini-extracted summary from transcript |
| 5. Care Plan | Next steps, follow-up timeline |
| 6. Disclaimer | AI-assisted, not a prescription |

---

## RAG CHATBOT

| Component | Spec |
|-----------|------|
| Embeddings | `sentence-transformers/paraphrase-multilingual-MiniLM-L6-v2` |
| Fallback embedder | `AutoModel` mean-pooling (when SentenceTransformer unavailable) |
| Vector store | `faiss-cpu` (cosine similarity, IndexFlatIP) |
| Index location | `rag/faiss_index.bin` + `rag/chunks_metadata.json` (gitignored, rebuilt at HF startup) |
| LLM | Gemini 2.5 Flash via `google-genai` SDK |
| Disease context | Injected into Gemini system prompt when Tab 1 diagnosis exists |
| Knowledge sources | CDC, NIH, WHO, DGHS Bangladesh — 100 text chunks |
| Forbidden source | DermNet — NEVER |
| Answer language | Auto-detected: Bengali unicode range `ঀ–৿` → `lang="bn"` |
| Retry logic | 3 attempts with exponential backoff before returning bilingual fallback |

---

## EMERGENCY HOSPITAL MAP

```
Trigger:  severity tier == 3 (Tab 1 only)
API:      Overpass API (free, no key needed)
Query:    amenity=hospital within district bounding box
Display:  Folium map + table — Name | Distance (km) | Address
Output:   hospital[0] → session_state.nearest_hospital → referral Section 4
Fallback: Returns [] gracefully on network error (never raises)
District lookup: get_district_coords(district) covers all 64 BD districts
```

---

## DOCTOR BOOKING — SPECIFICATION

**Module:** `ui/doctor_booking.py`

| Behaviour | Detail |
|-----------|--------|
| DEMO_DOCTOR | Dr. Nusrat Jahan, MBBS DDV, Chittagong Medical College Hospital |
| Available days | Sunday, Tuesday, Thursday |
| Slots | 8 slots per day (morning + evening, 2×4 grid) |
| Bengali time | `_time_to_bn()` — "06:30 PM" → "সন্ধ্যা ৬:৩০" |
| Tier 1 | Booking form shown, labelled "optional" |
| Tier 2 | Booking form shown, amber banner "বিশেষজ্ঞ ডাক্তারের পরামর্শ প্রয়োজন" |
| Tier 3 | No booking form — emergency hotline 16789 shown instead |
| Tier None | Preview mode — confirm button disabled |
| Phone validation | Must start with `01` + 10 total digits (BD mobile standard) |
| Session state keys | `booking_confirmed`, `booking_details`, `selected_date`, `selected_slot`, `booking_patient_name` |

---

## KEY DEPENDENCIES (actual — from requirements.txt)

```txt
streamlit==1.54.0
torch==2.10.0                    # CPU only
timm==1.0.27                     # Swin Transformer
albumentations==2.0.8
grad-cam==1.5.5                  # GradCAM++ (pytorch-grad-cam)
faster-whisper==1.2.1
streamlit-mic-recorder>=0.0.8    # Cross-browser mic recording
google-genai==1.63.0             # Gemini API (new SDK — NOT google-generativeai)
python-dotenv==1.2.1
faiss-cpu==1.13.2
sentence-transformers==5.2.2
fpdf2>=2.7.6                     # PDF generation (NOT reportlab)
uharfbuzz>=0.30.0                # HarfBuzz shaping for Bengali glyphs in PDF
folium>=0.15.0
streamlit-folium>=0.18.0
Pillow==11.3.0
opencv-python-headless==4.13.0.92
numpy==2.2.6
requests==2.32.5
gTTS>=2.5.0                      # Bengali TTS audio readout
pytest>=7.0.0
```

**Critical notes:**
- Use `google-genai` (new SDK), NOT the deprecated `google-generativeai`
- Use `fpdf2` + `uharfbuzz`, NOT `reportlab` — Bengali shaping requires HarfBuzz GSUB
- Noto Sans Bengali font: downloaded via `Dockerfile` `wget` at build time, not git-tracked

---

## IMPACT NARRATIVE (use in demo, report, presentation)

> "Bangladesh has approximately 1 dermatologist per 250,000 people. 80% of skin conditions in rural Bangladesh go untreated or are mistreated by unlicensed practitioners. SkinAI Bangladesh does not replace the doctor. It ensures the right patient reaches the right doctor at the right time — instead of reaching the wrong practitioner too late."

**Opening story (demo video + final presentation):**
> "Rahim is a farmer in Rangpur. He notices a spreading rash. The nearest dermatologist is 4 hours away and costs 1,500 taka he cannot spare. He opens SkinAI Bangladesh. He speaks in Bengali. He takes a photo. In seconds: Tinea Corporis, mild, Tier 1. The system tells him in Bengali — go to your local pharmacist. If it spreads in 3 days, here is your referral letter for Rangpur Medical College Hospital. Rahim has a plan. He does not need to go to Dhaka."

---

## SESSION STARTUP PROTOCOL

1. Read `CLAUDE.md` — understand full context
2. Read `PROGRESS.md` — know what is done and what is blocked
3. Read `TASK.md` — know exactly what to build today
4. Run `git status` — verify clean working state
5. Run `pytest tests/ -q` — confirm baseline passing tests
6. Begin coding — no re-explanation required

## SESSION END PROTOCOL

1. `pytest tests/ -q` — confirm no regressions
2. `git add <specific files> && git commit -m "[wX/dY] descriptive message"`
3. `git push -u origin <branch>`
4. Update `PROGRESS.md` — completed tasks, blockers, next entry point
5. Rewrite `TASK.md` for next session
6. Confirm HF Spaces build status

---

## CURRENT SPRINT

```
Current Week:  4 (May 18 – Jun 10 rolling)
Current Day:   24 (starting)
Focus:         Project report skeleton + demo video recording
App status:    5 tabs live, 310/312 tests passing
HF Space:      https://huggingface.co/spaces/rafilovestosuffer/skinai-bangladesh
GitHub:        https://github.com/rafilovestosuffer/Hackathon_2.0_sci
Critical blocker: BD-SkinNet checkpoint (bd_skinnet_best.pth) still pending
                  → _run_model() stub returns ("Tinea", 0.82, [...]) for now
Remaining:     Project report, demo video, model+data card, final README, submission dry run
```

---

## KNOWN ISSUES

| Issue | File | Status |
|-------|------|--------|
| BD-SkinNet checkpoint missing | model/checkpoints/ | Pending — placeholder active |
| 2 voice mock test failures | tests/test_voice.py | Pre-existing, unrelated to feature work |
| GEMINI_API_KEY in .env | .env | Needs valid key from Google AI Studio for live calls |
| HF Hub model download blocked locally | rag/ | Not an issue on HF Space — index rebuilt at startup |

---

*This file is the single source of truth for all Claude Code sessions.*
*Last updated: 2026-05-22 — Week 4, Day 24 — full architecture sync*
