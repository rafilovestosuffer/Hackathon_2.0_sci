# SkinAI Bangladesh — Architecture Decision Log
# Record EVERY major decision here. Date it. Reason it.
# This protects you in Q&A when judges ask "why did you choose X?"

---

## DECISION LOG

### [2026-05-18] Use Streamlit instead of FastAPI+React
**Decision:** Streamlit for the full UI
**Reason:** HF Spaces has native Streamlit support. FastAPI+React needs separate frontend deploy. Streamlit is faster to build and judges evaluate in browser — Streamlit is sufficient.
**Trade-off:** Less customizable UI. Acceptable for competition scope.

### [2026-05-18] Use FAISS over ChromaDB/Pinecone
**Decision:** faiss-cpu for vector store
**Reason:** Free, no API key, runs on CPU, no external service dependency. Pinecone has a free tier but adds network latency. ChromaDB is heavier. FAISS is battle-tested.
**Trade-off:** No built-in metadata filtering. Solved with chunks_metadata.json.

### [2026-05-18] Use Gemini 1.5 Flash over GPT-4
**Decision:** Gemini 1.5 Flash for LLM
**Reason:** Free tier is generous. Large context window. Strong Bengali language support. Google AI Studio API key is free to get. OpenAI costs money per token.
**Trade-off:** Slightly less consistent than GPT-4. Acceptable for hackathon.

### [2026-05-18] Use faster-whisper over Google STT / WhisperAPI
**Decision:** faster-whisper base model
**Reason:** Open-source, runs locally on CPU, no API key, strong Bengali support, MIT license. Google STT would add API cost and network dependency.
**Trade-off:** Slightly slower than cloud STT. INT8 quantized base model is acceptable.

### [2026-05-18] Use INT8 quantization over ONNX
**Decision:** torch.quantization.quantize_dynamic for INT8
**Reason:** Easier integration with timm Swin model. No ONNX export complexity for Swin architecture. Achieves ~4x memory reduction. HF Spaces free CPU needs this.
**Trade-off:** Dynamic quantization, not static. Static would be faster but requires calibration data.

### [2026-05-18] Use Overpass API over Google Maps for hospital finder
**Decision:** Overpass API (OpenStreetMap)
**Reason:** Completely free, no API key, Bangladesh hospital data is good in OSM. Google Maps API has per-request cost. Folium renders OSM tiles natively.
**Trade-off:** OSM hospital data may be incomplete in very rural areas. Show user disclaimer.

### [2026-05-18] Multi-signal severity over model-only severity
**Decision:** 4-signal triage engine (disease class + confidence + GradCAM + voice)
**Reason:** Medical safety. Model alone can be wrong. Low confidence should escalate, not pass. GradCAM coverage reveals widespread disease not visible in class label alone.
**Trade-off:** More complex logic. But this is the INNOVATION that scores points on the rubric.

### [2026-05-18] No DermNet data — Faridpur + Rangpur clinical data only
**Decision:** Clinical hospital data only
**Reason:** Competition policy explicitly bans DermNet (AI-generated images). Hospital data is more authentic, more Bangladesh-representative, and stronger for the Impact narrative.
**Trade-off:** Smaller training set. Compensated by CBAM attention mechanism and careful augmentation.

---

### [2026-05-19] Severity tier mapping updated to match actual model output classes
**Decision:** Replace placeholder disease names (melanoma, psoriasis, tinea_corporis…) with the 7 actual BD-SkinNet output classes
**Reason:** The original CLAUDE.md severity spec was written before training. The real model outputs: Atopic_Dermatitis, Contact_Dermatitis, Eczema, Scabies, Seborrheic_Dermatitis, Tinea, Vitiligo. No Tier 3 base class exists in these 7 — Tier 3 is reached only via Signal 2 (low confidence), Signal 3 (high GradCAM coverage), or Signal 4 (urgent voice keywords). This is medically safe: the multi-signal escalation still catches urgent presentations.
**Trade-off:** No disease class directly maps to Tier 3 base. Judges may ask why. Answer: none of our 7 trained classes is inherently life-threatening in isolation — severity is contextual (spreading, low confidence, widespread lesion).

---

### [2026-05-26] Migrate from google-generativeai to google-genai SDK
**Decision:** Use `from google import genai` (new SDK) instead of deprecated `google-generativeai`
**Reason:** google-generativeai is deprecated. New google-genai SDK supports Gemini 2.5 Flash which is on the free tier. Gemini 2.5 Flash is faster and has better multilingual (Bengali) performance.
**Trade-off:** Breaking API change — `genai.Client()` instead of `genai.configure()`. All callers updated.

### [2026-05-29] Use st.audio_input() over file uploader for voice recording
**Decision:** `st.audio_input()` (Streamlit ≥ 1.37) for in-browser mic recording
**Reason:** Judges and rural users should not need to pre-record audio files. One-click recording in browser is dramatically better UX. Required bumping streamlit to ≥1.37.0.
**Trade-off:** Requires browser microphone permission. Slightly larger Streamlit version requirement.

### [2026-05-29] _run_model() placeholder stub until checkpoint arrives
**Decision:** Clean placeholder in app.py returning Tinea/82% until bd_skinnet_best.pth is provided (~Jun 2)
**Reason:** Full pipeline (voice, triage, PDF, RAG, UI) can be built, tested, and demonstrated without the checkpoint. Placeholder has identical return shape — swap is one function body change.
**Trade-off:** Demo shows fixed disease until checkpoint. Documented clearly in app.py and PLAN.md Day 13b.

---

### [2026-06-01] Inject disease context into RAG system prompt
**Decision:** Add optional `disease_context` parameter to `answer_question()` in `rag/retriever.py`. When a diagnosis exists in `session_state`, the current disease name + confidence is prepended to the Gemini prompt.
**Reason:** Grounded, contextual answers beat generic ones. A patient asking "how serious is this?" after a Scabies diagnosis should get a Scabies-specific answer, not a generic skin-disease answer. This is a scoring differentiator under Innovation (25%) and Real-world Impact (20%).
**Trade-off:** Slightly longer prompt → marginally higher token usage. Negligible on Gemini 2.5 Flash free tier.

### [2026-06-01] st.chat_message style history for RAG chatbot
**Decision:** Replace single-form + last-answer display with full `st.chat_message` conversation history (`chat_history` list in session_state) and `st.chat_input` widget.
**Reason:** Judges and rural users expect a chat interface for Q&A, not a single-question form. History improves follow-up question UX dramatically. `st.chat_message` + `st.chat_input` are Streamlit's native chat primitives — no extra dependencies.
**Trade-off:** `st.rerun()` needed after each message. Acceptable performance cost.

### [2026-06-01] Demo mode: pre-loaded Scabies Tier 3 case
**Decision:** Sidebar "Load Demo" button pre-fills `session_state` with a Scabies/38% confidence/coverage_pct=45 case, triggering Tier 3 via Signals 2+3+4.
**Reason:** CONSTRAINT 2 (no login) + Demo Quality (20% rubric weight) demand zero-friction judge access. HF Spaces can be slow to respond for the first image upload. Demo mode gives judges instant access to all features (hospital map, PDF, context RAG) in one click.
**Trade-off:** Fake data until checkpoint. Clearly marked "(Demo)" in patient name.

### [2026-06-05] W3 delivered ahead of PLAN.md schedule
**Decision:** All W3 features (hospital map, RAG chat history, keepalive, demo mode,
confidence captions, blur detection, progress tracker, README) completed by Day 18
instead of Day 21.
**Why:** W2 also ran ahead — early completion frees W4 for polish and demo video.
**Impact:** W4 can focus entirely on demo video, project report, and UI polish.
No architecture changes required.

### [2026-06-07] Medical-grade UI overhaul via CSS injection only
**Decision:** Full design system rewrite in `ui/styles.py` + 7 new component functions in `ui/components.py`. Zero changes to model/*, severity/*, voice/*, rag/*, pdf_gen/*, map/* modules.
**Reason:** Demo Quality is 20% of the rubric. Judges see the UI in the first 5 seconds. A medical-grade visual (dark sidebar, teal accents, tier banners, chat bubbles) signals professionalism and domain awareness. CSS injection via `st.markdown(unsafe_allow_html=True)` is the only mechanism Streamlit offers for deep visual customization.
**Trade-off:** Streamlit's CSS targeting (`[data-testid]` selectors) is fragile — Streamlit version upgrades can break it. Pinned `streamlit>=1.37.0` in requirements.txt. Column-as-card CSS trick may not work on all Streamlit themes.

### [2026-06-07] Confidence caption boundary: separate bar colour from label thresholds
**Decision:** Bar colour threshold (≥0.60 = green, ≥0.40 = amber, <0.40 = red) is separate from caption label threshold (≥0.80 = confident, ≥0.60 = moderate, <0.60 = uncertain).
**Reason:** Bar colour reflects model certainty for triage (actionable above 60%). Caption label provides patient-facing clinical communication — "Moderately confident" at 60–79% is medically honest and appropriate. Collapsing them into one threshold (as was done during the overhaul) caused 2 test failures and was clinically incorrect.
**Trade-off:** None — this is the correct behavior. The distinction is intentional.

### [2026-06-07] Blur detection added, decision: always continue (never block)
**Decision:** `check_image_quality()` runs after image upload. If blurry (Laplacian variance < 80), show bilingual warning but continue to inference.
**Reason:** In rural Bangladesh, patients may only have one image. Blocking inference on a blurry image is worse than warning + proceeding. CONSTRAINT 3 (no medicine recommendation) is not violated — we only flag image quality.
**Trade-off:** Inference on blurry images may produce less accurate results. Mitigated by the confidence-based triage escalation (Signal 2 in the severity engine).

### [2026-06-06] Replace reportlab with fpdf2 + uharfbuzz for PDF generation
**Decision:** Migrate pdf_gen/referral.py and pdf_gen/consultation_summary.py from reportlab to fpdf2 + uharfbuzz (HarfBuzz GSUB shaping).
**Reason:** ReportLab does not apply OpenType GSUB ligature shaping to Bengali — characters render as disconnected boxes in Adobe Acrobat and most PDF readers. fpdf2 with uharfbuzz applies proper HarfBuzz GSUB shaping, producing correctly connected Bengali glyphs. This is a correctness issue, not a preference.
**Trade-off:** uharfbuzz is a C extension — adds ~2 MB to the Docker image. Acceptable.

---

### [2026-06-06] Loading spinners for all 6 slow operations
**Decision:** Wrap all 6 slow operations in st.spinner(): transcription, Gemini extraction, model inference, Overpass hospital query, Folium map render, PDF generation.
**Reason:** HF Spaces free CPU is slow. Without spinners, judges see a frozen UI and assume the app is broken. Spinners communicate progress and set expectations. Demo Quality is 20% of rubric.
**Trade-off:** Trivial — spinners are a Streamlit built-in with zero performance cost.

---

### [2026-06-06] Mobile-first CSS breakpoints
**Decision:** Add @media (max-width: 480px) breakpoints in ui/styles.py for card padding, font sizes, tab label sizes, history table cell padding.
**Reason:** Judges at the final day (July 10, CUET) may view the app on phones. Bangladesh rural health workers will primarily access via smartphones. Responsive layout is required for the real-world impact narrative.
**Trade-off:** Streamlit's data-testid CSS selectors are version-sensitive. Pinned streamlit==1.54.0 to stabilise.

---

### [2026-06-07] Bengali TTS audio readout via gTTS
**Decision:** Use gTTS (Google Text-to-Speech) to read the Bengali triage recommendation aloud after classification (F1 feature).
**Reason:** A significant portion of rural Bangladesh patients are functionally illiterate. Audio delivery of the triage recommendation ("৪৮ ঘণ্টার মধ্যে উপজেলা স্বাস্থ্য কমপ্লেক্সে যান") directly serves the target demographic. gTTS requires no API key for standard use, is free, and produces clear Bengali audio.
**Trade-off:** gTTS makes a network request to Google TTS. No offline fallback. Acceptable for HF Spaces (always online).

---

### [2026-06-07] Treatment cost estimate card (static data, zero medical risk)
**Decision:** Show a static taka-range cost estimate card per tier (F2 feature): Tier 1 ৳50-200, Tier 2 ৳0-100 (govt), Tier 3 ৳0-500 (govt emergency).
**Reason:** Cost is the primary reason rural Bangladeshi patients delay treatment. Showing approximate costs reduces a key barrier to seeking care. Data is from publicly known Bangladesh health system costs — not a medical recommendation.
**Trade-off:** Costs are approximate and may change. Clearly labelled "approximate" in the UI.

---

### [2026-06-07] CHW / Shasthya Seboika simplified mode
**Decision:** Sidebar toggle for "CHW Mode" (F3 feature) that shows a large-font, binary refer/no-refer card and generates a simplified 1-page referral slip (no jargon).
**Reason:** Bangladesh's Shasthya Seboika (community health workers) are a primary access point in rural areas. They need a clear binary decision, not a clinical confidence score. CHW mode directly addresses the last-mile healthcare delivery gap. This is a strong differentiator for the Innovation (25%) and Real-world Impact (20%) rubric criteria.
**Trade-off:** CHW mode is a UI layer only — no changes to underlying model or triage logic.

---

### [2026-06-07] Epidemiology tab with Bangladesh division-level disease map
**Decision:** Add Tab 4 (মহামারী তথ্য) with a Folium circle-marker map of disease prevalence by Bangladesh division, plus a horizontal bar chart (F4 feature). Module: map/bd_heatmap.py.
**Reason:** Division-level epidemiological data contextualises the clinical output for judges and health workers. It demonstrates domain knowledge of Bangladesh's health geography. DGHS/WHO data used (CONSTRAINT 5 compliant). Visual impact is high for Demo Quality (20% rubric).
**Trade-off:** Data is static (no real-time updates). Clearly sourced to DGHS/WHO.

---

### [2026-06-07] Auto image enhancement (CLAHE + unsharp mask) before inference
**Decision:** Apply CLAHE (contrast-limited adaptive histogram equalisation) + unsharp mask before BD-SkinNet inference when the image is detected as dark or blurry (F5 feature). Before/after preview shown.
**Reason:** Rural Bangladesh patients take photos in low light with cheap phones. Without enhancement, dark/blurry images produce low-confidence outputs → unnecessary Tier 3 escalations. Enhancement improves model confidence on real-world input. This strengthens the clinical reliability narrative.
**Trade-off:** Enhancement may alter colour-sensitive diagnostic features in edge cases (e.g., erythema). Mitigated by keeping the blur warning visible and always showing the original alongside the enhanced image.

---

### [2026-06-07] Symptom duration visual timeline
**Decision:** Render a 3-node visual timeline (Onset → Today → Expected Recovery) parsed from the Bengali/English voice duration field in patient_history (F6 feature).
**Reason:** Visual timelines communicate disease progression at a glance. Doctors scanning a referral letter benefit from a visual summary. Improves Demo Quality and shows clinical UX sophistication.
**Trade-off:** Duration parsing is heuristic (regex on Bengali/English text). Edge cases fall back to a generic "Unknown" node without crashing.

---

### [2026-06-07] Impact comparison panel in sidebar
**Decision:** Add a sidebar panel showing two cards side-by-side: "Without SkinAI" (wrong practitioner, delayed, worsened) vs "With SkinAI" (correct triage, right facility, right time) (F7 feature).
**Reason:** Judges who skim the sidebar during a live demo need to immediately understand the value proposition. This panel delivers the core narrative in 5 seconds without any narration. Directly supports Real-world Impact (20%) and Demo Quality (20%).
**Trade-off:** Static content, no interactivity. Acceptable — it is a narrative element, not a functional feature.

---

### [2026-05-23] Doctor booking tab completes the care loop (Tab 5)
**Decision:** Add Tab 5 (ডাক্তার বুকিং) with a full doctor booking + video call flow. Module: ui/doctor_booking.py. DEMO_DOCTOR: Dr. Nusrat Jahan, MBBS DDV, Chittagong Medical College Hospital.
**Reason:** The full care loop is: Screen → Diagnose → Triage → Book → Video Consult → PDF. Without booking, the app stops at triage — a referral letter without a reachable doctor. The booking tab closes the loop. Tier-aware behaviour (Tier 3 disables form, shows emergency hotline 16789) ensures medical responsibility.
**Trade-off:** Demo doctor is hardcoded (Dr. Nusrat Jahan). Real deployment would require a doctor API. For competition scope, a convincing demo doctor is sufficient and judges understand this.

---

### [2026-05-23] Post-consultation AI care summary PDF
**Decision:** Add pdf_gen/consultation_summary.py — a 6-section fpdf2 PDF generated after a video call ends, summarising the consultation with Gemini-extracted notes.
**Reason:** Completes the paper trail: referral letter before the visit, care summary after. Demonstrates full clinical workflow coverage, not just screening. Strengthens Real-world Impact (20%) and Innovation (25%).
**Trade-off:** Gemini extraction of "consultation notes" is simulated in demo mode (no real video call transcript available). Clearly marked as AI-assisted summary.

---

### [2026-05-23] streamlit-mic-recorder for cross-browser mic recording
**Decision:** Use streamlit-mic-recorder instead of st.audio_input() for in-browser microphone recording.
**Reason:** st.audio_input() was unreliable in Chrome over HTTP (browser security restriction). streamlit-mic-recorder uses the MediaRecorder API with a proper permission request flow and works on both HTTP and HTTPS. Judges and rural users should not need to upload pre-recorded files.
**Trade-off:** Extra dependency (streamlit-mic-recorder). Minor.

---

## PENDING DECISIONS (evaluate during build)
- [x] Should we support Bangla-English code-switching in voice? → Yes, handled automatically: Gemini extraction tolerates mixed input; RAG auto-detects Bengali unicode range.
- [ ] Should we add more disease classes beyond the trained 7? → Post-competition only. Adding classes requires retraining.
