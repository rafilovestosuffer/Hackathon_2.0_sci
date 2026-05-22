# SkinAI Bangladesh — 40-Day Championship Plan
# SciBlitz AI Challenge 2026 | Submission: July 1 | Final: July 10

## 🗺️ OVERVIEW

| Week | Dates | Theme | Key Deliverable |
|------|-------|-------|-----------------|
| W1 | May 18–24 | Foundation + Model + PDF | HF Spaces live + severity engine |
| W2 | May 25–31 | Voice + LLM + RAG + Basic UI | Full pipeline code |
| W3 | Jun 1–7 | Full Integration | One-click working demo |
| W4 | Jun 8–14 | Polish + Map + Demo Video | Submission-grade demo video |
| W5 | Jun 15–21 | Report + Docs | Project report PDF + data card |
| W6 | Jun 22–Jul 1 | Stress Test + Submit | Final submission package |

---

## ⚡ WEEK 1 — FOUNDATION (May 18–24)

### Day 1 — May 18 | Repository + Project Structure
- [x] Create GitHub repo `skinai-bangladesh` (PUBLIC)
- [x] Push full folder skeleton (all dirs) with initial commit
- [x] Add CLAUDE.md, PLAN.md, PROGRESS.md, TASK.md, DECISIONS.md
- [x] Add .gitignore (exclude checkpoints, .env, __pycache__, *.bin if large)
- [x] Add requirements.txt skeleton
- [x] Verify: `git log` shows commits with today's date

### Day 2 — May 19 | Model Architecture + INT8 Export
- [x] Write model/bd_skinnet.py — Swin+CBAM class (timm-based)
- [x] Write model/disease_labels.py — English→Bengali disease name map
- [x] Write model/export_int8.py — INT8 quantization export script
- [x] Add dummy forward pass test (random tensor, correct output shape)
- [x] Commit: [w1/d2] BD-SkinNet architecture + INT8 export

### Day 3 — May 20 | GradCAM++ Implementation
- [x] Write model/gradcam.py — GradCAM++ on Swin last stage
- [x] Implement compute_coverage_pct(heatmap, threshold=0.5)
- [x] Write tests/test_gradcam.py — shape + coverage range assertions
- [x] All tests pass
- [x] Commit: [w1/d3] GradCAM++ + coverage computation + tests

### Day 4 — May 21 | Severity Engine (CRITICAL)
- [x] Write severity/engine.py — 4-signal triage engine
- [x] Write tests/test_severity.py — test all signals + edge cases:
  - melanoma → always Tier 3
  - confidence 0.35 → always Tier 3
  - coverage 45% + Tier 1 base → escalates to Tier 2
  - "জ্বর" in transcript + Tier 2 → Tier 3
  - tier never exceeds 3 (cap test)
- [x] All tests pass: pytest tests/test_severity.py -v
- [x] Commit: [w1/d4] multi-signal severity engine + full test suite

### Day 5 — May 22 | HF Spaces Skeleton Deploy
- [x] Create HF Space (Streamlit, Python 3.10)
- [x] Write minimal app.py (title + team name + "System loading...")
- [x] Add packages.txt with libsndfile1, ffmpeg
- [x] Push to HF Space — verify public URL loads
- [x] Test from incognito: zero login, instant access
- [x] RECORD PUBLIC URL IN PROGRESS.md
- [x] Commit: [w1/d5] HF Spaces deployed — public URL live

### Day 6 — May 23 | PDF Generator
- [x] Write pdf_gen/referral.py — 4-section PDF (fpdf2 + uharfbuzz for Bengali shaping)
- [x] Implement generate_referral_pdf(session_state) → bytes
- [x] Write tests/test_pdf.py — smoke test (file generates, size > 0)
- [x] Test Bengali font rendering in PDF (Noto Sans Bengali)
- [x] Commit: [w1/d6] referral letter PDF generator

### Day 7 — May 24 | W1 Review + Prep W2
- [x] Run all tests: pytest tests/ -v — all green
- [x] Update PROGRESS.md
- [x] Verify HF Space still live
- [x] Write next week TASK.md
- [x] W1 DONE: Model ✓ | GradCAM ✓ | Severity ✓ | PDF ✓ | HF Space ✓

---

## ⚡ WEEK 2 — PIPELINE (May 25–31)

### Day 8 — May 25 | Voice Transcription
- [x] Write voice/pipeline.py — faster-whisper base, Bengali language
- [x] Implement transcribe_audio(audio_bytes) → str
- [x] Handle mp3/wav/webm (Streamlit mic recorder outputs)
- [x] Test with sample Bengali audio
- [x] Commit: [w2/d8] faster-whisper Bengali transcription

### Day 9 — May 26 | Gemini Symptom Extraction
- [x] Add extract_patient_history(transcript) → dict to voice/pipeline.py
- [x] Prompt: force JSON output with all 9 fields, handle missing gracefully
- [x] Add 3-retry logic for Gemini API failures
- [x] Test with sample Bengali transcript
- [x] Commit: [w2/d9] Gemini JSON symptom extraction

### Day 10 — May 27 | Knowledge Base
- [x] Chunk CDC/NIH/WHO/DGHS content into rag/knowledge/ (100-300 words/chunk)
  - CDC: fungal, bacterial skin infections
  - NIH/MedlinePlus: eczema, psoriasis, dermatitis
  - WHO: NTDs (scabies, tinea, leprosy)
  - DGHS Bangladesh: official skin disease guidelines
- [x] Target: 100-200 chunks total — 100 chunks delivered
- [x] Commit: [w2/d10] knowledge base chunks (CDC/NIH/WHO/DGHS)

### Day 11 — May 28 | RAG Pipeline
- [x] Write rag/build_index.py — FAISS index from chunks (MiniLM embeddings)
- [x] Build and save faiss_index.bin + chunks_metadata.json
- [x] Write rag/retriever.py — query → top-k → Gemini answer
- [x] Implement answer_question(question, session_context) → str
- [x] Commit: [w2/d11] FAISS index + RAG retriever

### Day 12 — May 29 | Streamlit UI Layout
- [x] Write ui/components.py — reusable widgets
- [x] Write ui/styles.py — Bengali Noto Sans CSS injection
- [x] Write app.py — full layout:
  - Sidebar: About + Bengali instructions
  - Tab 1: "রোগ নির্ণয়" — voice + image upload placeholders
  - Tab 2: "প্রশ্ন করুন" — RAG chatbot placeholder
  - Tab 3: "রেফারেল পত্র" — PDF download placeholder
- [x] Commit: [w2/d12] Streamlit UI layout with Bengali tabs

### Day 13 — May 30 | Full app.py Integration
- [x] Wire all 3 tabs in app.py (voice → history, image → triage, RAG, PDF)
- [x] inject_css() + @st.cache_resource for RAG + Whisper
- [x] _run_model() placeholder stub — same API as real model, drops in when checkpoint arrives
- [x] NOTE: BD-SkinNet checkpoint not yet available — ETA ~Jun 2
      When checkpoint is provided: replace _run_model() body with real inference
      File: app.py lines starting with "def _run_model()"
- [x] Commit: [w2/d13] full app.py integration

### Day 13b — ~Jun 2 | Plug In Model Checkpoint  ← CHECKPOINT STILL PENDING
- [ ] Receive bd_skinnet_best.pth from training
- [ ] Place in model/checkpoints/bd_skinnet_best.pth
- [ ] Replace _run_model() stub with real BD-SkinNet + GradCAM++ forward pass
- [ ] Verify heatmap renders correctly in Tab 1
- [ ] Commit: [w2/d13b] real BD-SkinNet inference connected

### Day 14 — May 31 | W2 Integration Test
- [x] 133/133 tests passing — all modules verified
- [x] All public APIs confirmed importable (8 modules checked)
- [x] app.py syntax clean, pushed to GitHub + HF Space
- [x] st.audio_input() wired for in-browser Bengali mic recording
- [x] W2 DONE: Voice ✓ | Gemini ✓ | RAG ✓ | UI ✓ | app.py ✓ | Severity ✓ | PDF ✓

---

## ⚡ WEEK 3 — FULL INTEGRATION (Jun 1–7)
## NOTE: W2 ran ahead of schedule. Severity UI, RAG chatbot UI, voice wiring,
## and PDF integration are already done in app.py. Week 3 focuses on:
## hospital map, model checkpoint plug-in, keepalive, and demo polish.

### Day 15 — Jun 1 | Emergency Hospital Map ✅ DONE (Day 14+15)
- [x] Write map/hospital_finder.py — Overpass API query, no API key needed
- [x] find_nearest_hospitals(lat, lon, n=5) → list[dict]
- [x] Render folium map with hospital pins in Streamlit (streamlit-folium)
- [x] Wire into app.py Tab 1: show map only when tier == 3
- [x] Inject hospital[0] name+address into PDF Section 4
- [x] Write tests/test_hospital.py — mock Overpass responses, 17 tests
- [x] Commit: [w3/d15] emergency hospital map + Folium

### Day 16 — Jun 3 | RAG Context Awareness + Chat History ✅ DONE
- [x] Pass current disease to RAG system prompt as context
- [x] Add st.chat_message style conversation history (st.session_state list)
- [x] Show disease context banner above chat: "Asking about: Tinea"
- [x] Commit: [w3/d16] RAG context-aware chatbot

### Day 17 — Jun 4 | Scripts + Keepalive ✅ DONE
- [x] Write scripts/keepalive.py — ping HF Space every 20 min
- [x] Add GitHub Actions workflow for keepalive (CONSTRAINT 7)
- [x] Bengali confidence captions (≥80% / 60–80% / <60%)
- [x] Blur detection via Laplacian variance (threshold=80, OpenCV)
- [x] Commit: [w3/d17] Bengali confidence captions + blur detection + 10 new tests

### Day 18 — Jun 5 | Demo Mode + UI Polish ✅ DONE
- [x] Add demo mode: pre-loaded sample case (Scabies, Tier 3) for judges
- [x] Add image quality warning (blur detection via Laplacian variance)
- [x] Sidebar 4-step pipeline progress tracker
- [x] Bilingual error handling for corrupt image uploads
- [x] README.md full submission-grade rewrite
- [x] Commit: [w3/d18] error handling + sidebar progress tracker + README

### Day 19 — Jun 6 | W3 Sign-Off ✅ DONE
- [x] W3 sign-off checklist verified manually (all items ✅)
- [x] PLAN.md W3 items marked complete
- [x] DECISIONS.md updated with W3-ahead-of-schedule entry
- [x] TASK.md written for Day 20 (Week 4 start)
- [x] Commit: [w3/d19] W3 sign-off

### W3 COMPLETE ✅ — All features delivered by Day 19 (ahead of Day 21 target)
- [x] Hospital map (Tier 3, Overpass + Folium)
- [x] RAG context-aware chatbot (chat history, disease context banner)
- [x] Keepalive script + GitHub Actions cron
- [x] Demo mode (Scabies Tier 3, one-click)
- [x] Bengali confidence captions
- [x] Image blur detection
- [x] Sidebar pipeline progress tracker
- [x] Error handling (corrupt image, bilingual fallbacks)
- [x] README.md (submission-grade)
- [x] Tests: 164/164 passing

---

## ⚡ WEEK 4 — POLISH + FEATURES + VIDEO (Jun 8–14)

### Day 20 — Jun 6 | Loading States + Mobile CSS + Demo Script ✅ DONE
- [x] Loading spinners for all 6 slow operations (st.spinner wrappers)
- [x] Mobile CSS breakpoints — responsive layout for small screens
- [x] Write docs/demo_script.md — 8-segment, 4-min Rahim story script
- [x] Commit: [w4/d20] loading spinners + mobile CSS + demo script

### Day 21 — Jun 7 | Medical-Grade UI Overhaul ✅ DONE
- [x] Full design system in ui/styles.py (colour tokens, typography, card styles)
- [x] 7 new component functions in ui/components.py (metric cards, triage banner, etc.)
- [x] app.py restructured to use new design system throughout
- [x] 245 total tests passing
- [x] Commit: [w4/d21] medical-grade UI design system

### Day 22 — May 20+22 | 7 High-Value Features ✅ DONE
- [x] F1: Bengali TTS — gTTS reads triage recommendation aloud in Bengali audio
- [x] F2: Treatment cost estimate card — static taka ranges per tier (Tier 1/2/3)
- [x] F3: CHW / Shasthya Seboika simplified mode — sidebar toggle, large-font binary
       refer/no-refer display, CHW referral slip PDF
- [x] F4: Epidemiology tab (Tab 4) — Bangladesh division-level disease prevalence map
       (folium circle markers) + bar chart; map/bd_heatmap.py
- [x] F5: Auto image enhancement — CLAHE + unsharp mask before inference if dark/blurry
- [x] F6: Symptom duration timeline — 3-node visual: Onset → Today → Expected Recovery
- [x] F7: Impact comparison panel in sidebar (Without SkinAI vs With SkinAI)
- [x] Voice fix: audio stream exhaustion bug fixed; file upload set as primary tab
- [x] Commit: [w4/d22] 7 high-value features

### Day 23 — May 23 | Doctor Booking Tab ✅ DONE
- [x] ui/doctor_booking.py — Tab 5 doctor booking UI
- [x] tests/test_doctor_booking.py — 38 tests; 310/312 total tests passing
- [x] PDF booking injection — booking details written into referral letter
- [x] Tier 3 disables booking, shows emergency hotline only (medically responsible)
- [x] Commit: [w4/d23] doctor booking tab + PDF injection + tests

### Day 24 — May 23+ | Project Report Skeleton + Demo Video ← NEXT
- [ ] Write project report skeleton (8-page, 8 section headers + bullets)
- [ ] Record demo video (OBS/Loom, 3-5 min, Rahim story structure)
  - 0:00-0:30 — Hook: Rahim's problem (narration, no code)
  - 0:30-1:00 — Demo: voice input in Bengali
  - 1:00-2:00 — Demo: image upload → classification → GradCAM
  - 2:00-2:30 — Demo: severity tier display + Bengali triage
  - 2:30-3:00 — Demo: hospital map (Tier 3 scenario)
  - 3:00-3:30 — Demo: PDF referral letter generation
  - 3:30-4:00 — Demo: RAG chatbot Q&A + doctor booking
  - 4:00-4:30 — Impact slide + system diagram + close
- [ ] Upload: YouTube unlisted OR Google Drive with link sharing

### Day 25 — Jun+ | Finalise Report + Model & Data Card
- [ ] Flesh out Architecture + Results sections of project report
- [ ] Include: system architecture diagram, GradCAM heatmap examples
- [ ] Write model & data card (1-page PDF)
  - Dataset(s): Faridpur MCH + Rangpur MCH (N images, N classes)
  - Pre-trained models: Swin-B (timm, Apache 2.0), faster-whisper (MIT)
  - Third-party APIs: Gemini 1.5 Flash (Google), Overpass API (ODbL)
  - Known limitations: BD-only clinical data, limited class coverage
  - Ethical concerns: not a medical device, requires doctor confirmation, data privacy
- [ ] Export both as PDF

### Day 26 — Jun+ | Final README + Keepalive Verify + Submission Dry Run
- [ ] Final README review — confirm all submission-required fields present
- [ ] Verify keepalive GitHub Actions cron is firing (already deployed — confirm logs)
- [ ] Submission dry run: open form, check all fields, do NOT submit yet
- [ ] Commit: [w4/d26] submission dry run verified

### Day 13b — ONGOING | Plug In BD-SkinNet Checkpoint  ← STILL PENDING
- [ ] Receive bd_skinnet_best.pth from training pipeline
- [ ] Place in model/checkpoints/bd_skinnet_best.pth
- [ ] Replace _run_model() stub in app.py with real BD-SkinNet + GradCAM++ forward pass
- [ ] Verify heatmap renders in Tab 1, coverage_pct flows to triage
- [ ] Commit: [w4/d13b] real BD-SkinNet inference connected

---

## ⚡ WEEK 5 — DOCUMENTATION (Jun 15–21)

### Day 29-30 — Jun 15-16 | Project Report (8 pages max)
Report structure:
1. Title + Abstract (0.5 page)
2. Problem Statement — Bangladesh dermatology gap (1 page, use real stats)
3. Proposed Solution — system overview + pipeline diagram (1 page)
4. Methodology — BD-SkinNet architecture + training (1.5 pages)
5. AI/ML Approach — GradCAM++, severity engine, RAG, voice (1.5 pages)
6. Results — F1=92.46%, confusion matrix, GradCAM examples (1 page)
7. Limitations & Future Work (0.5 page)
8. References (not counted in pages)

- [ ] Write report in LaTeX or Google Docs
- [ ] Include: system architecture diagram, GradCAM heatmap examples
- [ ] Export as PDF
- [ ] Verify: min 10pt font, max 8 pages

### Day 31 — Jun 17 | Model & Data Card (1 page)
Required content:
- Dataset(s): Faridpur MCH + Rangpur MCH (N images, N classes)
- Pre-trained models: Swin-B (timm, Apache 2.0), faster-whisper (MIT)
- Third-party APIs: Gemini 1.5 Flash (Google), Overpass API (ODbL)
- Known limitations: BD-only clinical data, limited class coverage
- Ethical concerns: not a medical device, requires doctor confirmation, data privacy

### Day 32 — Jun 18 | README Finalize
README.md must contain:
- [ ] Project title + one-line description
- [ ] Problem statement (2-3 sentences)
- [ ] Live demo URL (HF Spaces link)
- [ ] Demo video link
- [ ] Full tech stack table
- [ ] Setup instructions (for local dev)
- [ ] Attribution table (all third-party resources)
- [ ] Team section
- [ ] Disclaimer (not a medical device)

### Day 33-35 — Jun 19-21 | Buffer + Polish
- [ ] Re-read rulebook — verify every checklist item
- [ ] Re-run all tests — pytest tests/ -v
- [ ] Check all 5 submission deliverables ready
- [ ] Prepare Q&A answers for Final Day judges (15 likely questions)
- [ ] Rehearse 5-minute presentation with Rahim story opening

---

## ⚡ WEEK 6 — SUBMISSION (Jun 22–Jul 1)

### Day 36-37 — Jun 22-23 | Stress Test
- [ ] Simulate 20 concurrent users (Locust or manual parallel sessions)
- [ ] Test with low-quality images (blurry, dark)
- [ ] Test with heavy Bengali accent voice
- [ ] Test all disease classes from the label map
- [ ] Fix any crashes — commit all fixes

### Day 38 — Jun 24 | Keep-Alive Script
- [x] Write scripts/keepalive.py — pings HF Space URL every 20 min (DONE Day 17)
- [x] Set up GitHub Actions cron job to run keepalive from Jul 1–12 (DONE Day 17)
  - schedule: '*/20 * * * *'
  - step: curl GET the HF Space URL
- [x] Test cron job fires correctly
- [x] Commit: [w3/d17] keepalive GitHub Action deployed (already live — verify logs in W6)
- NOTE: Keepalive already deployed in W3/Day 17. W6 task = confirm it is still running.

### Day 39 — Jun 28 | Final Submission Package Check
- [ ] ✅ Live public URL — test from incognito
- [ ] ✅ Project report PDF — max 8 pages, min 10pt
- [ ] ✅ GitHub repo — public, README complete, commits from May 14
- [ ] ✅ Demo video — 3-5 min, YouTube/Drive link works
- [ ] ✅ Model & Data Card — 1 page PDF
- [ ] ✅ HF Space stays live — keepalive active

### Day 40 — Jul 1 | SUBMIT BY 11:59 PM BST
- [ ] Open official submission form
- [ ] Paste HF Spaces URL
- [ ] Upload project report PDF
- [ ] Paste GitHub repo URL
- [ ] Paste demo video link
- [ ] Upload Model & Data Card PDF
- [ ] Screenshot the submitted form
- [ ] DONE — wait for shortlist July 3

---

## 🏆 FINAL DAY PREP (Jul 3–10)

### After Shortlist Notification (Jul 3):
- [ ] Finalize 5-minute presentation slides
- [ ] Practice Q&A with 15 likely judge questions
- [ ] Prepare backup: demo video on USB + local demo if available

### July 9 (Day Before):
- [ ] Check live demo URL — wake up HF Space if sleeping
- [ ] Test demo on venue laptop if possible
- [ ] Bring USB with: slides, demo video, backup screenshots

### July 10 — FINAL DAY:
- [ ] Open Rahim story — emotional hook
- [ ] Live demo the product (not slides first)
- [ ] Close with Bangladesh impact narrative
- [ ] WIN

---

## 📋 JUDGE Q&A PREPARATION (18 Questions)

1. "Why Swin Transformer over ResNet/EfficientNet?" → Self-attention captures global patterns critical for skin texture analysis. F1 = 92.46% validates the choice.
2. "How did you collect the training data?" → Clinical collaboration with Faridpur and Rangpur Medical College Hospitals. IRB-approved image collection.
3. "Why is the severity multi-signal, not just model output?" → Medical safety. Low confidence or widespread lesion overrides class prediction. Avoids under-triaging.
4. "What if the model is wrong?" → Disclaimer shown. System escalates on uncertainty (<60% confidence → Tier 2 minimum). Not a replacement for doctors.
5. "Why faster-whisper over Google STT?" → Offline capable, lower latency, open-source, better Bengali support on local/CPU.
6. "What are the limitations?" → Limited to trained disease classes. Rural image quality varies. No real-time video. Class imbalance in training data.
7. "How does the RAG chatbot avoid hallucination?" → FAISS retrieval grounds answers in vetted sources (CDC/NIH/WHO/DGHS). Gemini only generates from retrieved context.
8. "Why not recommend medicines?" → Not a licensed medical device. Triage to correct care level is the safe, legal, and responsible role.
9. "How does INT8 quantization work?" → Reduces weights from 32-bit float to 8-bit integer. Minimal accuracy loss (<1%), ~4x memory reduction, faster CPU inference.
10. "Can this scale nationally?" → Yes. Stateless (no DB), runs on free CPU, any smartphone with camera + mic can use it.
11. "What about data privacy?" → No data stored. Session-only state. PDF generated locally. No image uploaded to any server permanently.
12. "Why Streamlit over mobile app?" → Accessible from any smartphone browser. No install required. Judges can test instantly. Future: PWA wrapper.
13. "How do you handle unknown diseases?" → Unknown class defaults to Tier 2 (see doctor). Model outputs confidence; low confidence auto-escalates.
14. "What's the clinical validation?" → Model tested on held-out clinical test set from same hospitals. F1 = 92.46%. Real clinician feedback informed severity tiers.
15. "What's next after the competition?" → Clinical trial with a hospital partner, mobile PWA wrapper, expansion to more disease classes, DGHS official integration.
16. "Why did you add a doctor booking feature?" → Completes the care loop: Screen → Diagnose → Triage → Book → Consult → PDF. Tier 3 disables booking and shows the emergency hotline only — medically responsible design that prevents users in urgent situations from wasting time booking an appointment.
17. "How does the Bengali TTS work?" → gTTS (Google Text-to-Speech) converts the Bengali triage recommendation text to an audio file played in-browser. No API key needed for basic use. Rural patients who cannot read Bengali script still receive the triage recommendation in spoken form.
18. "Why fpdf2 instead of reportlab for PDF?" → fpdf2 + uharfbuzz applies HarfBuzz GSUB shaping to Bengali glyphs before rendering. ReportLab does not apply OpenType shaping — Bengali characters render as disconnected boxes in Acrobat and most PDF viewers. fpdf2 + uharfbuzz is the correct solution for Unicode-complex scripts like Bengali.
