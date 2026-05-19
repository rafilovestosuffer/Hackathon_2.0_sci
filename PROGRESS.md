# SkinAI Bangladesh — Session Progress Log
# Update this file at the END of EVERY Claude Code session.

## 📍 CURRENT STATUS
- Week: 3 | Day: 18 (starting)
- HF Spaces URL: https://huggingface.co/spaces/rafilovestosuffer/skinai-bangladesh
- GitHub Repo: https://github.com/rafilovestosuffer/Hackathon_2.0_sci
- Demo Video: [TO BE ADDED WEEK 4]

---

## ✅ COMPLETED MODULES
<!-- Check these off as they are done -->
- [x] model/bd_skinnet.py
- [x] model/gradcam.py
- [x] model/disease_labels.py
- [x] model/export_int8.py
- [x] severity/engine.py
- [x] voice/pipeline.py (transcription)
- [x] voice/pipeline.py (Gemini extraction)
- [x] rag/build_index.py
- [x] rag/retriever.py
- [x] rag/knowledge/ (chunks)
- [x] pdf_gen/referral.py
- [x] map/hospital_finder.py
- [x] ui/components.py
- [x] ui/styles.py
- [x] app.py (full integration — checkpoint stub, all 3 tabs live)
- [x] tests/test_severity.py
- [x] tests/test_gradcam.py
- [x] tests/test_pdf.py
- [ ] scripts/keepalive.py
- [ ] scripts/seed_commits.py
- [x] tests/test_voice.py
- [ ] tests/test_pipeline.py
- [ ] README.md (final)
- [ ] Project Report PDF
- [ ] Model & Data Card PDF
- [ ] Demo Video

---

## ✅ COMPLETED MODULES (updated)
- [x] scripts/keepalive.py ← done Day 16
- [x] .github/workflows/keepalive.yml ← done Day 16

---

## 📝 SESSION LOG
<!-- Append to this after every session. Newest at top. -->

### Session: Jun 1, 2026 — Day 17 — Bengali Confidence Captions + Blur Detection ✅
**Done:**
- ui/components.py: added Bengali+English confidence caption to `render_disease_card()`
  - >=80%: "মডেল নিশ্চিত · Model is confident" (green pill)
  - 60–80%: "মোটামুটি নিশ্চিত · Moderately confident" (amber pill)
  - <60%: "অনিশ্চিত — ডাক্তার দেখান · Uncertain — see a doctor" (red pill)
  - Boundary-exact: 0.80 → high, 0.60 → mid
- ui/components.py: added `check_image_quality(pil_img) -> (is_blurry, float)`
  - Laplacian variance blur detection (threshold=80), never raises
- ui/styles.py: `.conf-caption` / `.conf-high` / `.conf-mid` / `.conf-low` CSS pills
  - Also `.blur-warning` styled box (amber border, warm background)
- app.py: blur check wired after image upload — bilingual warning shown, processing continues
- tests/test_ui.py: 10 new tests (TestConfidenceCaption ×6 + TestCheckImageQuality ×4)
- Full suite: 164/164 passing (was 154)
- Committed and pushed to GitHub (3e8ffe6) and HF Space (d189963)

**Blockers:**
- BD-SkinNet checkpoint still pending — _run_model() placeholder active

**Next session start point:**
- Day 18: Error handling polish + sidebar session summary + begin README

**Git commits this session:**
- 3e8ffe6 [w3/d17] Bengali confidence captions + blur detection + 10 new tests (GitHub)
- d189963 same — clean branch push (HF Space)

---

### Session: Jun 1, 2026 — Day 16 — RAG Context + Keepalive + Demo Mode ✅
**Done:**
- rag/retriever.py: added `disease_context: str | None` param to `answer_question()`
  - Injected into Gemini system prompt when diagnosis exists: "The patient has been diagnosed with: {disease}"
  - Backward-compatible: old callers work unchanged (None default)
- app.py Tab 2: full chat history UI
  - Replaced single-form + last-answer display with `st.chat_message` + `st.chat_input`
  - `chat_history` list in session_state stores all turns (role, content, lang)
  - Disease context banner (st.success): "Current diagnosis: X — answering in this context"
  - Clear Chat button resets history + rerun
  - Backward-compat: `rag_answer` / `rag_lang` fields preserved for PDF flow
- app.py sidebar: "🎬 Load Demo (Scabies — Tier 3)" button
  - Scabies/38% confidence/coverage_pct=45 → Tier 3 via Signals 2+3+4
  - Bengali transcript with escalation keywords pre-filled
  - All 3 tabs fully populated with one click — no image or audio needed
- scripts/keepalive.py: `ping()` + `run_loop()` — 20-min interval keepalive
- .github/workflows/keepalive.yml: GitHub Actions cron `*/20 * * * *`
- tests/test_rag.py: 4 new tests (disease_context injection, backward compat)
- DECISIONS.md: 3 new architecture decisions documented
- Full test suite: 154/154 passing (was 150)
- Committed and pushed to GitHub (6a7a989) and HF Space (739cf1e)

**Blockers:**
- BD-SkinNet checkpoint still pending (~Jun 2) — _run_model() placeholder active

**Next session start point:**
- Day 17: E2E integration test + UI polish (loading spinners, edge case error messages)
  Also: checkpoint plug-in (bd_skinnet_best.pth) if received

**Git commits this session:**
- 6a7a989 [w3/d16] RAG context-aware chatbot + keepalive + demo mode (GitHub)
- 739cf1e [w3/d16] same — clean branch push (HF Space)

---

### Session: May 31, 2026 — Day 14+15 — W2 SIGN-OFF + Hospital Map ✅
**Done (Day 14 — W2 sign-off):**
- 133/133 tests, all 8 module APIs verified
- DECISIONS.md: 3 new entries (google-genai SDK, st.audio_input, checkpoint stub)
- PLAN.md Week 3 rewritten to reflect actual remaining work

**Done (Day 15 — Hospital Map):**
- Written map/hospital_finder.py — full Overpass API hospital finder
  - find_nearest_hospitals(lat, lon, n, radius_km) → list[dict] sorted by distance
  - render_hospital_map(hospitals, user_lat, user_lon) → folium.Map with pins
  - get_district_coords(district) → (lat, lon) for 64+ Bangladesh districts
  - Haversine distance calculation (no external library)
  - Network failure → returns [] gracefully, never raises
- Written tests/test_hospital.py — 17 tests, all passing (150 total)
  - TestGetDistrictCoords: 5 tests
  - TestFindNearestHospitals: 9 tests (mocked Overpass)
  - TestHaversine: 3 tests
- Wired into app.py Tab 1: shows ONLY when tier == 3
  - District text input → geocode → Overpass query → hospital table + Folium map
  - hospital[0] stored in session_state.nearest_hospital → injected into PDF Section 4
- Full test suite: 150/150 passing

**Blockers:**
- BD-SkinNet checkpoint still pending (~Jun 2)

**Next session start point:**
- Day 16: RAG context-aware chatbot + scripts/keepalive.py

**Git commits this session:**
- [w2/d14] W2 sign-off — all MD files updated
- [w3/d15] emergency hospital map + Folium + 17 tests

---

### Session: May 31, 2026 — Day 14 — W2 SIGN-OFF ✅
**Done:**
- Full W2 verification: 133/133 tests passing
- All 8 public module APIs confirmed importable
- st.audio_input() wired for in-browser Bengali mic recording (replaces file uploader)
- DECISIONS.md updated: 3 new decisions (google-genai SDK, st.audio_input, placeholder stub)
- PLAN.md updated: Week 3 rewritten to reflect actual remaining work
  (W2 ran ahead — severity UI, RAG UI, voice, PDF all already in app.py)
- Committed and pushed to GitHub + HF Space

**W2 Milestone — COMPLETE:**
- [x] voice/pipeline.py — faster-whisper Bengali transcription
- [x] voice/pipeline.py — Gemini JSON patient history extraction
- [x] rag/knowledge/ — 100 chunks (CDC/NIH/WHO/DGHS)
- [x] rag/build_index.py — FAISS index builder
- [x] rag/retriever.py — FAISS query + Gemini answer
- [x] ui/styles.py — Bengali CSS + professional design
- [x] ui/components.py — 6 reusable widgets
- [x] app.py — full 3-tab pipeline (mic, image, triage, RAG, PDF)
- [x] 133/133 tests passing

**Blockers:**
- BD-SkinNet checkpoint (bd_skinnet_best.pth) — ETA ~Jun 2
  Placeholder in app.py._run_model() until then

**Next session start point:**
- Day 15: map/hospital_finder.py — Overpass API + Folium
  Wire into Tab 1: show only when tier == 3
  Inject hospital[0] into PDF Section 4

**Git commits this session:**
- [w2/d14] W2 sign-off — all MD files updated

---

### Session: May 30, 2026 — Day 13
**Done:**
- Full app.py integration — all 3 tabs wired end-to-end
  - inject_css() called at top; @st.cache_resource for RAG index + Whisper
  - Sidebar: dark professional, logo, tagline, live stats, disclaimer
  - Tab 1 (রোগ নির্ণয়): voice upload → transcribe → extract history → render_patient_history_table
    + image upload → _run_model() → render_disease_card + compute_tier + render_triage_badge + render_gradcam_overlay
  - Tab 2 (প্রশ্ন করুন): st.form → answer_question() → render_rag_answer with source tags
  - Tab 3 (রেফারেল পত্র): summary metrics → generate_referral_pdf() → render_referral_download_button
- _run_model() placeholder stub — identical API to real model, drops in when checkpoint arrives
  - Real inference: replace body of _run_model() in app.py when bd_skinnet_best.pth provided (~Jun 2)
- Fixed key mismatch: render_triage_badge now reads bengali_text + facility (matching compute_tier output)
- PLAN.md updated: Day 13b stub added for checkpoint plug-in day
- Full test suite: 133/133 passing

**Blockers:**
- BD-SkinNet checkpoint (bd_skinnet_best.pth) not yet received — ETA ~Jun 2
  Placeholder model returns Tinea/82% for demo. Real inference ready to drop in.

**Next session start point:**
- Day 14: W2 integration test — full E2E smoke test on HF Space
  Voice upload + image upload + RAG question + PDF download
  Fix any bugs found

**Git commits this session:**
- [w2/d13] full app.py integration — 3-tab pipeline wired

---

### Session: May 29, 2026 — Day 12
**Done:**
- Written ui/styles.py — inject_css() with full professional CSS
  - Bengali Noto Sans font via Google Fonts CDN (Inter fallback)
  - Dark sidebar (#0f172a) — .sidebar-logo, .sidebar-tagline, .sidebar-stat
  - Medical blue (#1a56db) primary + tab active styling
  - .badge-tier1 (green), .badge-tier2 (amber), .badge-tier3 (red + pulse animation)
  - .sk-card, .conf-bar-wrap/fill, .differential-pill, .history-table
  - .rag-answer-box (teal left border), .rag-source-tag
  - .coverage-wrap/fill (purple gradient), .sk-disclaimer, metric/upload styling
- Written ui/components.py — 6 standalone component functions
  - render_triage_badge(tier_result) — colour badge + bilingual action text
  - render_gradcam_overlay(heatmap_img, coverage_pct) — image + purple coverage bar
  - render_patient_history_table(history) — skips empty/none fields, bilingual labels
  - render_disease_card(disease, confidence, top2) — EN+BN name, conf bar, differential pill if >15%
  - render_rag_answer(answer, lang) — teal box + CDC/NIH/WHO/DGHS source tags
  - render_referral_download_button(pdf_bytes) — enabled or styled disabled placeholder
- Written tests/test_ui.py — 29 tests, all passing
  - TestInjectCSS: 5 tests
  - TestRenderTriageBadge: 5 tests
  - TestRenderPatientHistory: 4 tests
  - TestRenderDiseaseCard: 6 tests
  - TestRenderReferralButton: 3 tests
  - TestRenderGradcamOverlay: 3 tests
  - TestRenderRAGAnswer: 3 tests
- Full suite: 133/133 passing (104 prior + 29 new)
- Committed and pushed to GitHub and HF Space

**Blockers:**
- None

**Next session start point:**
- Day 13: Wire up full app.py — Tab 1 (voice+image→triage), Tab 2 (RAG chatbot), Tab 3 (PDF download)
- Call all real modules: voice/pipeline.py, rag/retriever.py, severity/engine.py, pdf_gen/referral.py, ui/components.py
- Commit: [w2/d13] full app.py integration

**Git commits this session:**
- [w2/d12] UI components + Bengali styles + 29 tests

---

### Session: May 28, 2026 — Day 11
**Done:**
- Written rag/retriever.py — full RAG pipeline
  - load_index() → bool (returns False if index missing, not an error)
  - retrieve(question, top_k) → list[dict] — FAISS cosine search
  - answer_question(question, lang) → str — always returns str, never raises
  - Bengali auto-detection: if question contains ঀ–৿ unicode → lang="bn"
  - Gemini prompt: "Do NOT recommend specific medications", "Refer to a doctor"
  - 3-retry on Gemini (same pattern as voice/pipeline.py)
  - SentenceTransformer primary → AutoModel mean-pooling fallback (same as build_index.py)
  - Fallbacks: "দুঃখিত..." (Bengali) / "Sorry, I could not find an answer." (English)
- Written tests/test_rag.py — 26 tests, all passing
  - TestLoadIndex: 4 tests (missing files, partial missing, success, metadata set)
  - TestRetrieve: 7 tests (returns list, not empty, top_k, top_k=1, required keys, no index, dict type)
  - TestAnswerQuestion: 11 tests (str return, not empty, empty input, whitespace, no index, Gemini fail, Bengali fallback, EN detection, BN detection, explicit lang, all mocked)
  - TestGeminiPrompt: 5 tests (question in prompt, context in prompt, no-medicine clause, refers to doctor, ONLY from context)
- Full suite: 104/104 passing (78 prior + 26 new)
- Committed and pushed to GitHub and HF Space

**Blockers:**
- None

**Next session start point:**
- Day 12: Write ui/components.py (reusable Streamlit widgets) + ui/styles.py (Bengali Noto Sans CSS)

**Git commits this session:**
- [w2/d11] FAISS retriever + Gemini RAG + 26 tests

---

### Session: May 27, 2026 — Day 10
**Done:**
- Written 100 knowledge base chunks to rag/knowledge/ (100 .txt files)
  - CDC: 32 chunks (tinea×8, scabies×7, atopic_dermatitis×5, eczema×3, contact_dermatitis×3, seborrheic×3, vitiligo×3)
  - NIH: 32 chunks (all 7 diseases + general skin care, itch, phototherapy, infection, microbiome, nutrition, skin color topics)
  - WHO: 16 chunks (scabies NTD×3, tinea×2, atopic dermatitis, skin diseases SE Asia, vitiligo stigma, community MDA, occupational, integrated care, climate, BD country, seborrheic)
  - DGHS: 20 chunks (all 7 diseases BD context, referral pathways, rural skin, monsoon, children, elderly, garment sector, skin hygiene, prevention, upazila protocol, emergency, patient navigation, telemedicine, education)
- All 7 BD-SkinNet disease classes covered (min 8 chunks each)
- No DermNet content anywhere
- rag/seed_knowledge.py: one-time seeder script (writes chunks from in-memory dict)
- rag/build_index.py: FAISS index builder with SentenceTransformer → AutoModel fallback
- FAISS code path verified locally with random embeddings (100 chunks → IndexFlatIP → search confirmed)
- Note: local HF Hub model download blocked by network (HF Hub returns 401/404 from this network)
  → Build will succeed on HF Space which has direct HF Hub access
  → faiss_index.bin + chunks_metadata.json are gitignored; rebuilt at HF Space startup
- Committed rag/knowledge/ + rag/build_index.py + rag/seed_knowledge.py
- Pushed to GitHub and HF Space

**Blockers:**
- HF Hub model download blocked locally (sentence-transformers/paraphrase-multilingual-MiniLM-L6-v2 returns 401)
  — Does NOT affect HF Space deployment; index rebuilt at startup there

**Next session start point:**
- Day 11: Write rag/retriever.py — FAISS query + Gemini answer
- Implement answer_question(question, context) → str
- Write tests/test_rag.py

**Git commits this session:**
- [w2/d10] knowledge base chunks (CDC/NIH/WHO/DGHS) + FAISS index builder

---

### Session: May 26, 2026 — Day 9
**Done:**
- Added extract_patient_history(transcript) → dict to voice/pipeline.py
- Gemini 1.5 Flash via new google-genai SDK (migrated away from deprecated google-generativeai)
- 3-retry logic, JSON fence stripping, _empty_history() fallback, _validate_fields()
- All 9 fields always present in output — no KeyError possible downstream
- Wrote tests/test_voice_gemini.py — 15 tests (5 helpers + 10 extraction), all mocked
- Full suite: 78/78 passing (13 gradcam + 11 pdf + 29 severity + 10 voice + 15 gemini)
- Updated requirements.txt: google-genai>=1.0.0 + python-dotenv>=1.0.0
- Pushed to GitHub and HF Space

**Blockers:**
- GEMINI_API_KEY in .env is invalid — needs a fresh key from Google AI Studio
  The code is correct (3-retry works, graceful fallback confirmed); only live calls affected

**Next session start point:**
- Day 10: Build RAG knowledge base — chunk CDC/NIH/WHO/DGHS text into rag/knowledge/

**Git commits this session:**
- [w2/d9] Gemini JSON symptom extraction + new SDK migration

---

### Session: May 25, 2026 — Day 8
**Done:**
- Wrote voice/pipeline.py — transcribe_audio(audio_bytes, fmt) → str
- faster-whisper base model, language="bn", device="cpu", compute_type="int8"
- Lazy singleton _get_model() — loads once, reused across calls
- Handles wav/mp3/webm via tempfile; empty/bad bytes return "" gracefully
- Wrote tests/test_voice.py — 10 tests (model singleton + transcription robustness)
- Full suite: 63/63 passing (13 gradcam + 11 pdf + 29 severity + 10 voice)
- Pushed to GitHub (main) and HF Space (clean branch — binary-free history)

**Blockers:**
- None

**Next session start point:**
- Day 9: Add extract_patient_history(transcript) → dict to voice/pipeline.py
- Needs GEMINI_API_KEY — set in .env before starting

**Git commits this session:**
- 118cc5a [w2/d8] faster-whisper Bengali transcription

---

### Session: May 24, 2026 — Day 7 — W1 REVIEW
**Done:**
- Ran full test suite: 53/53 PASSED
  - test_gradcam.py: 13/13
  - test_severity.py: 29/29
  - test_pdf.py: 11/11
- HF Space verified live: https://huggingface.co/spaces/rafilovestosuffer/skinai-bangladesh
- W1 milestone confirmed complete (see checklist below)
- Wrote TASK.md for Day 8 — voice pipeline

**W1 Milestone:**
- [x] model/bd_skinnet.py — Swin+CBAM, 7 classes, INT8 export
- [x] model/gradcam.py — GradCAM++ wrapper + coverage_pct
- [x] model/disease_labels.py — 7 classes + Bengali names + tiers
- [x] model/export_int8.py — INT8 quantization script
- [x] severity/engine.py — 4-signal triage engine
- [x] pdf_gen/referral.py — 4-section referral letter
- [x] app.py — Bengali 3-tab skeleton
- [x] Dockerfile — Docker build for HF Space
- [x] tests/ — 53 total tests, all passing
- [x] HF Space live at public URL

**Blockers:**
- None

**Next session start point:**
- Day 8: Write voice/pipeline.py — faster-whisper Bengali transcription

**Git commits this session:**
- [w1/d7] W1 review complete — 53/53 tests, Week 2 TASK.md ready

---

### Session: May 23, 2026 — Day 6
**Done:**
- Wrote pdf_gen/referral.py — generate_referral_pdf(session_data) → bytes
- 4 sections: Patient History, Clinical Observation, AI Diagnosis, Triage Recommendation
- Bengali text via Noto Sans Bengali font (downloaded at build/runtime, not tracked in git)
- Heatmap embedded as PNG image; heatmap=None handled gracefully
- Differential shown only when top2[1].confidence > 0.15
- Tier 3 hospital name+address injected into Section 4
- Colour-coded urgency badge (green/orange/red) per tier
- Wrote tests/test_pdf.py — 11 smoke tests, all passing
- Font not tracked in git (HF binary file policy) — downloaded via Dockerfile wget + runtime fallback
- Updated Dockerfile to wget font at Docker build time
- Pushed to GitHub (main) and HF Space (clean branch, no binary history)

**Blockers:**
- None

**Next session start point:**
- Day 7: Run full test suite (pytest tests/ -v — all 53 tests green)
- Verify HF Space rebuilds with Dockerfile font download
- Write TASK.md for Week 2

**Git commits this session:**
- 4e8433f [w1/d6] referral letter PDF generator (font tracking — later removed)
- febb961 [w1/d6] referral letter PDF generator + font via Dockerfile download

---

### Session: May 22, 2026 — Day 5
**Done:**
- Created HF Space: rafilovestosuffer/skinai-bangladesh (Docker + Streamlit, CPU Basic, Public)
- Added hf git remote and force-pushed project code
- Upgraded app.py to full Bengali-tabbed skeleton:
  - Sidebar: project info, team, competition, Bengali disclaimer
  - Tab 1 "রোগ নির্ণয়" — voice + image placeholders + triage metrics
  - Tab 2 "প্রশ্ন করুন" — RAG chatbot placeholder
  - Tab 3 "রেফারেল পত্র" — PDF download placeholder (disabled button)
  - Bengali info banner + footer disclaimer
- Added HF Spaces YAML metadata to README.md
- Pushed to both GitHub and HF Space remotes
- Public URL: https://huggingface.co/spaces/rafilovestosuffer/skinai-bangladesh

**Blockers:**
- None

**Next session start point:**
- Write pdf_gen/referral.py — 4-section reportlab PDF
- Write tests/test_pdf.py — smoke test
- Test Bengali font rendering (Noto Sans Bengali via reportlab)

**Git commits this session:**
- dd7f8ae [w1/d5] add HF Spaces metadata to README
- a9ade29 [w1/d5] HF Spaces deployed — public URL live

---

### Session: May 21, 2026 — Day 4
**Done:**
- Wrote severity/engine.py — compute_tier(disease_class, confidence, coverage_pct, transcript) → dict
- Implemented all 4 signals exactly per CLAUDE.md spec
- Wrote tests/test_severity.py — 29 assertions across 6 test classes covering all signals, boundaries, combined escalation, and return structure
- All 29 tests pass (pytest -v)

**Blockers:**
- None

**Next session start point:**
- Write voice/pipeline.py — faster-whisper transcription + Gemini JSON extraction (Day 5)

**Git commits this session:**
- 68e037d [w1/d4] multi-signal severity engine + full test suite

---

### Session: May 20, 2026 — Day 3
**Done:**
- Wrote model/gradcam.py — GradCAM++ wrapper using target layer model.cbam_modules[-1].spatial_attn.conv
- Implemented compute_gradcam(model, image_tensor) → {heatmap, coverage_pct, overlay, target_class}
- Implemented compute_coverage_pct(heatmap, threshold=0.5) → float
- Wrote tests/test_gradcam.py — 13 assertions across 2 test classes:
  - TestComputeGradcam: shape, value range, coverage range, overlay shape, target class, unbatched input, required keys
  - TestComputeCoveragePct: zero map, full map, half map, custom threshold, return type, Signal 3 boundary

**Blockers:**
- None — all tests designed to pass with random weights (no checkpoint required)

**Next session start point:**
- Write severity/engine.py — 4-signal triage engine using DISEASE_TIER from disease_labels.py
- Write tests/test_severity.py covering all signals and edge cases per PLAN.md Day 4

**Git commits this session:**
- 21770bb [w1/d3] GradCAM++ wrapper + coverage computation + full test suite

---

### Session: May 19, 2026 — Day 2
**Done:**
- Extracted model architecture from BD_SkinNet_Model_Main.ipynb
- Wrote model/bd_skinnet.py — BDSkinNet (Swin-B + CBAM x4 stages, 7 classes, 1920-d fusion head)
- Wrote model/disease_labels.py — 7 classes with Bengali names + severity tiers
- Wrote model/export_int8.py — torch.quantization.quantize_dynamic export script
- Forward pass test embedded in bd_skinnet.py __main__ block

**Key facts locked in:**
- 7 classes: Atopic_Dermatitis, Contact_Dermatitis, Eczema, Scabies, Seborrheic_Dermatitis, Tinea, Vitiligo
- Test F1=0.9246, Accuracy=92.37%, AUC-ROC=0.9937
- GradCAM++ target layer: model.cbam_modules[-1].spatial_attn.conv
- Swin stage dims: [128, 256, 512, 1024]

**Blockers:**
- Checkpoint (bd_skinnet_best.pth) is on Kaggle — need to download and add to model/checkpoints/ before inference works

**Next session start point:**
- Write model/gradcam.py — GradCAM++ wrapper using target layer model.cbam_modules[-1].spatial_attn.conv
- Write tests/test_gradcam.py

**Git commits this session:**
- 478dbcf [w1/d2] BD-SkinNet architecture + CBAM + disease labels (7 classes) + INT8 export

---

### Session: May 19, 2026 — Day 1
**Done:**
- Created GitHub repo and pushed to https://github.com/rafilovestosuffer/Hackathon_2.0_sci
- Created full folder structure: model/, severity/, voice/, rag/knowledge/, pdf_gen/, map/, ui/, tests/, scripts/
- Added __init__.py in every module folder
- Copied all planning files: CLAUDE.md, PLAN.md, PROGRESS.md, DECISIONS.md, TASK.md, SESSION_PROTOCOL.md
- Created .gitignore (excludes checkpoints, .env, __pycache__, *.bin, *.pt)
- Created requirements.txt with all key dependencies
- Created placeholder README.md (title + team + under construction)
- Created placeholder app.py (st.title only)
- Committed and pushed: [w1/d1] initial project structure

**Blockers:**
- None

**Next session start point:**
- Write model/bd_skinnet.py — Swin+CBAM class (timm-based), per PLAN.md Day 2

**Git commits this session:**
- a95adf4 [w1/d1] initial project structure — all planning files + module skeleton
- 3019176 [w1/d1] resolve merge conflict — keep project files

---

<!-- Template for each session — copy and paste above this line:

### Session: [DATE] — Day [N]
**Done:**
- 

**Blockers:**
- 

**Next session start point:**
- 

**Git commits this session:**
- 

-->
