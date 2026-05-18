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

## PENDING DECISIONS (evaluate during build)
- [ ] Should we support Bangla-English code-switching in voice?
- [ ] Should we add a demo mode with pre-loaded sample case (for slow HF Spaces)?
- [ ] Should we add image quality check (blur detection) before inference?
