# International AI Builders Congress 2026 — submission text (draft)

Copy each section into the platform form. Every `[TBD]` must be filled with a real value or deleted before submitting; numbers come only from `python scripts/verify_numbers.py`.

---

## 1. Basics

- **Project name:** SkinAI Bangladesh — CareAnywhere
- **One-line pitch:** Offline-first Bangla voice-and-photo skin triage that sends rural patients to the right level of care, with a doctor reviewing shared cases.
- **Domain / challenge:** HealthSphere AI → CareAnywhere
- **Primary language:** Bangla + English
- **Public summary:** SkinAI takes a patient's photo of a skin problem, their spoken Bengali complaint and a few warning signs, and returns an explainable triage tier (pharmacy, Upazila Health Complex, or hospital today) with a referral letter addressed to a doctor. It works on the web, on Telegram, and as an offline page that saves the case on the phone and sends it when signal returns. With the patient's consent, a doctor reviews the case, confirms or corrects the AI, and the patient is told. The AI is one of three triage signals; uncertainty and warning signs always push the patient toward more care, never less.

## 2. Problem statement

- **User:** adults in rural and peri-urban Bangladesh with a skin complaint and a basic smartphone or Telegram; community health workers; Upazila doctors who review cases.
- **Today:** low-income countries average 0.37 dermatologists per 100,000 people against a sufficiency benchmark of 5.63 (158-country study, JAMA Dermatology 2026 — confirm against the paper). Bangladesh has 7.9 doctors of any kind per 10,000 people (Lancet Public Health, 2023), and about 6 in 10 people live in rural areas (World Bank, 2024). Specialist skin care sits in teaching and district hospitals and private clinics, so patients travel far or go untreated.
- **Why existing tools fail:** symptom apps are English-first, need steady internet, and are mostly trained on lighter skin tones; none route a Bangladeshi patient to the right level of the public health system or put a local doctor in the loop.
- **Measurable outcome we change:** time from first symptom report to a correct-level referral decision; share of urgent cases told to go the same day; under-triage rate (patients sent to a lower level of care than needed), measured by doctor review.

## 3. Solution

**Product:** web app (7 tabs), Telegram bot, offline `/lite` page, Doctor Queue, referral and care-summary PDFs, MCP server.

**AI system:**

| Layer | Component |
|---|---|
| Vision | BD-SkinNet (Swin-B + CBAM on 4 stages, INT8, CPU) — live checkpoint: 6 classes, validation F1 0.816 |
| Speech | faster-whisper `small` (INT8) Bengali, 3-pass with script-leak correction |
| Extraction | Gemini 2.5 Flash-Lite → 9-field patient history (JSON, validated) |
| Triage | rule engine: class base tier + confidence (<0.40 → urgent, <0.60 → ≥ routine) + Bengali warning words (+1 tier); `explain_tier` gives a reason per signal |
| Knowledge | 104-chunk CDC/NIH/WHO/DGHS corpus — ChromaDB → FAISS → BM25 cascade + Kuzu Graph-RAG; code-enforced no-medicine filter |
| Human in loop | Doctor Queue: confirm/override with audit log, patient notification, live agreement/under-triage KPIs |
| Offline | `/lite` service-worker page: offline red-flag advice, on-phone JPEG compression, IndexedDB queue, auto-sync to `/api/cases` |

**Winning-signal mapping:**

| CareAnywhere asks for | SkinAI evidence |
|---|---|
| Safe | uncertainty and warning signs only escalate; no medicine names ever (regex filter); "go today" advice never downgraded |
| Explainable | "why this tier" reasons on every result, PDF and bot reply; transparent rule engine |
| Human-in-loop | Doctor Queue with audit trail; patient notified of the doctor's decision |
| Offline / low-bandwidth | `/lite` works with no network; upload size [TBD] KB median |
| Measurable access expansion | field test [TBD]; doctor agreement [TBD]; under-triage [TBD] |

**Origin (disclosure):** version 1 was built for the SciBlitz AI Challenge 2026 (July 2026; frozen at git tag `v1-sciblitz`). Congress work: shared model service (fixed a label-mapping bug in the live model and removed placeholder predictions), Doctor Queue, offline `/lite`, case API, triage explanations, corrected model/data documentation, evaluation scripts.

## 4. Demo & links

- Live app: https://huggingface.co/spaces/rafilovestosuffer/skinai-bd
- Offline page: https://rafilovestosuffer-skinai-bd.hf.space/lite/
- Doctor Queue: https://rafilovestosuffer-skinai-bd.hf.space/doctor — **Judge Access Note:** PIN given in the access note field (not in this public file).
- Telegram bot: https://t.me/SkinAIBDBot
- GitHub: https://github.com/rafilovestosuffer/Hackathon_2.0_sci
- YouTube (3:00, unlisted): [TBD]
- Slides: [TBD]

## 5. Data & AI provenance

- **Images:** SkinDiseaseBD (Faridpur MCH) and SkinDisNet (Rangpur & Kishoreganj MCH; Mendeley Data, DOI 10.17632/yj3md44hxg.2) — published datasets; consent per the publishers. Research model: 3,322 real images, image-level stratified 70/15/15 split; Stable Diffusion v1.5 img2img augmentation (1,039 images) for 3 minority classes on the training split only; real-only test set. The live checkpoint's training split is [TBD — confirm which notebook/run produced `bd_skinnet_int8.pth`].
- **Knowledge corpus:** CDC and NIH (public domain), WHO (CC BY-NC-SA 3.0 — non-commercial; the paid teleconsult stream must not serve WHO text, or WHO chunks are replaced before any commercial use), DGHS Bangladesh.
- **Foundation models:** Gemini 2.5 Flash-Lite (Google API), faster-whisper small (MIT), intfloat/multilingual-e5-small (MIT), Swin-B backbone (timm, Apache 2.0).
- **Personal data:** web and bot sessions in memory only; shared cases (consent only) keep a ≤256 px EXIF-stripped thumbnail, AI output, warning signs and district — no name, phone or transcript — deleted after 7 days. Telegram chat id kept only until the doctor's decision is sent. Analytics are anonymous counters.

## 6. Tooling, IDE and memory files

[TBD — list exactly what the team used, e.g. Claude Code (with CLAUDE.md / rules files), VS Code, Cursor, Kaggle T4 notebooks, Hugging Face Spaces, GitHub.]

## 7. MCP usage

- The product exposes an MCP server (`mcp_server/skinai_server.py`, FastMCP, stdio) with 3 tools: `triage_skin_condition`, `ask_skin_question` (medicine filter enforced), `find_emergency_hospitals`.
- MCP servers used while building: [TBD].

## 8. Prompt library

| Prompt | Purpose | Where |
|---|---|---|
| Patient-history extraction | Bengali/English/romanized speech → 9 JSON fields, no guessing | `voice/pipeline.py` |
| Grounded RAG answer | 3–5 sentence answer from retrieved CDC/NIH/WHO/DGHS chunks, language-matched | `rag/retriever.py` |
| Medicine guardrail | regex denylist applied after generation | `rag/retriever.py` |
| Key build prompts | [TBD] | — |

## Team roles

| Role | Member |
|---|---|
| Team leader / coordinator | [TBD] |
| Business analyst / data scientist | [TBD] |
| UI/UX / frontend | [TBD] |
| Backend / data engineer | [TBD] |
| Presentation / communication | [TBD] |
| NRB / global advisor (if confirmed) | [TBD] |

## Mentor engagement notes

[TBD — date, mentor, what was discussed, what changed.]
