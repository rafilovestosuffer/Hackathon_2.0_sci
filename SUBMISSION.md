# SkinAI Bangladesh — Infinity AI BuildFest Submission

**Tagline:** সঠিক রোগী → সঠিক ডাক্তার → সঠিক সময় · *Right patient → Right doctor → Right time*
**Live app (no login):** https://huggingface.co/spaces/rafilovestosuffer/skinai-bangladesh
**GitHub:** https://github.com/rafilovestosuffer/Hackathon_2.0_sci · **Demo video:** _[YouTube link to be added on submission]_

---

### Problem
Bangladesh has ~1 dermatologist per 250,000 people. ~80% of rural skin cases go untreated or are mistreated by unlicensed practitioners. A farmer in Rangpur cannot afford the 4-hour journey or the 1,500-taka specialist fee — so the wrong practitioner is reached, too late.

### Project workflow

```
 Patient (Bengali voice + skin photo on smartphone or WhatsApp)
        │
        ├─► faster-whisper (Bengali ASR) ──► Gemini 1.5 Flash ──► 9-field patient history JSON
        │
        └─► BD-SkinNet (Swin-B + CBAM, INT8) ──► disease class + confidence + top-2 differential
                                       │
                                       ▼
        4-signal severity engine:  disease class + confidence + lesion coverage + Bengali symptom keywords
                                       │
                       ┌───────────────┼────────────────┐
                       ▼               ▼                ▼
              Tier 1 Pharmacist   Tier 2 UHC      Tier 3 District ER + live hospital map
                       │               │                │
                       └───────► 4-section referral PDF ◄┘   (addressed to a licensed doctor)
                                       │
                                       ▼
                       Optional teleconsult booking · RAG Q&A (CDC · NIH · WHO · DGHS)
```

### How it maps to the rubric

**Innovation (20%).** Multi-signal triage that fuses image, voice, and free-text into a single tier decision — not a classifier wrapped in a UI. Bengali voice → structured history is a missing primitive for South Asian health tech; the 4-signal engine is the first published combination for skin triage in this market.

**Technical Execution (20%).** Production-grade: real BD-SkinNet INT8 checkpoint (Swin-B + CBAM, F1 = 92.46%) served on free-tier CPU; FAISS RAG over CDC/NIH/WHO/DGHS chunks; dual-service Docker (nginx → Streamlit + FastAPI webhook) supporting WhatsApp and Telegram bots; **402 automated tests** including 12 new tests for the BuildFest tab. End-to-end demo loads in under 3 seconds with no login.

**Business Model + Global Readiness (20%).** Three sustainability streams keep the patient endpoint free forever: (1) 15% revenue share on in-app teleconsult bookings; (2) NRB Sponsor-a-District — diaspora pledges fund free screenings in named districts (working demo widget in-app; ~1.7M Bangladeshis abroad send >$20B/yr in remittances with no health-impact channel today); (3) anonymised epidemiology shared with MoHFW / DGHS / icddr,b under non-commercial licence, funded by Gates / USAID / WHO SEARO grants. Unit economics: $0.0003 / inference, $40 / month hosting at 10k MAU, break-even ~1,200 teleconsult shares / month. Phase 3 expands to Hindi and Urdu RAG corpora — South Asia ready.

**Real-World Impact + Ethical AI Compliance (20%).** Every output is a referral to a licensed clinician, never a diagnosis. No medicine recommendations (hard constraint). Bilingual fairness disclosure renders under every AI prediction in the live app — judges encounter ethics in the product flow, not buried in a PDF. Full model card, data card, and ethics statement committed in repo. Multi-signal engine itself is bias mitigation: low confidence auto-escalates to Tier 3, so out-of-distribution images get safer care, not worse care. Session-state only — no persistent database, no PII, no analytics.

**Scalability + NRB Collaboration (10%).** Concrete 12-month plan: Phase 1 pilot at 2 Upazila Health Complexes in Rangpur (<$50/mo), Phase 2 across 8 districts ($200/mo) with WhatsApp-first low-bandwidth flow already built, Phase 3 national + South Asian regional ($400/mo) with offline TFLite APK. HF Spaces → AWS ap-south-1 migration is a Dockerfile swap. NRB widget inside the app converts the diaspora pitch from words to something a judge can submit live.

**Presentation (10%).** 3-min video opens with the NRB hook, walks the Rahim flow live on the public URL, closes with the explicit ask: *"Help us reach eight districts in twelve months."*
