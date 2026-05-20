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

## PENDING DECISIONS (evaluate during build)
- [ ] Should we support Bangla-English code-switching in voice?
