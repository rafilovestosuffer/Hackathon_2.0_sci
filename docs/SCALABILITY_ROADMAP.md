# Scalability Roadmap — 12 months

## Phase 1 — Pilot (Months 1–3)

**Reach.** 2 Upazila Health Complexes in Rangpur Division (target: Rangpur Sadar UHC + one neighbouring upazila).

**Ships.** What's already built:
- Live web app on HF Spaces with no-login zero-friction access
- WhatsApp and Telegram bots (already integrated, tested, deployed)
- INT8 BD-SkinNet checkpoint (already in production)
- 4-section referral PDF generation (already in production)
- Bengali voice → patient history extraction (already in production)

**Pilot deliverables.**
- 200+ patient screenings completed
- 50+ referrals followed up at UHC (manual audit of outcomes)
- Baseline accuracy + tier-appropriateness metrics for the pilot population
- Letters of support from the two pilot UHCs

**Cost.** &lt; $50 / month (HF Spaces free tier + WhatsApp Cloud API free tier + Gemini free tier).

---

## Phase 2 — Divisional (Months 4–8)

**Reach.** 8 districts across Rangpur and Rajshahi divisions: Rangpur, Rajshahi, Bogura, Dinajpur, Pabna, Naogaon, Kurigram, Joypurhat. These are the same 8 districts surfaced in the in-app NRB Sponsor-a-District widget.

**Ships.**
- Low-bandwidth WhatsApp-first flow promoted as primary channel (the web app stays as the doctor/CHW interface)
- 8 partner-doctor onboarding for the teleconsult flow (revenue-share stream activates)
- Partnership MoUs with the eight district hospitals
- NRB sponsorship platform with real payment integration (Stripe + bKash bridge)
- Monthly transparency report to sponsors

**Phase 2 deliverables.**
- 5,000+ patient screenings completed
- ~1,200 paid teleconsult shares per month (revenue break-even)
- 3+ active NRB sponsorship campaigns
- First public-health grant submission (Gates / USAID / WHO SEARO)

**Cost.** ≈ $200 / month — AWS ap-south-1 migration, WhatsApp paid tier above free-cap, sponsorship-platform fees.

---

## Phase 3 — National &amp; regional (Months 9–12)

**Reach.** Bangladesh-wide via the existing WhatsApp/Telegram channels; RAG knowledge corpus opened to South Asian adapters (India, Pakistan, Nepal, Sri Lanka).

**Ships.**
- Offline-capable mobile APK (TFLite INT8 export of the existing checkpoint — same architecture, ahead-of-time compiled). Targets rural users with intermittent connectivity.
- Hindi and Urdu RAG corpora added to the knowledge base (the embedding model is already multilingual — `paraphrase-multilingual-MiniLM-L6-v2`).
- Model card and data card published in machine-readable form for external adaptation.
- South Asian partnership exploration: WHO SEARO regional coordination, AIIMS Delhi telemedicine collaborations.

**Cost.** ≈ $400 / month — multi-region AWS, mobile APK distribution and update infrastructure, increased Gemini usage.

---

## Infrastructure migration path

| Stage | Host | Why |
|---|---|---|
| Now (pre-pilot) | HF Spaces (CPU Basic, free) | Zero-cost, zero-login public URL — perfect for hackathon judging and pilot bootstrapping |
| Phase 2 | AWS ap-south-1 (Mumbai), single-region auto-scale | Lowest latency to Bangladesh; mature Docker auto-scaling; supports the existing dual-service routing (nginx → Streamlit + FastAPI webhook) without architectural change |
| Phase 3 | AWS multi-region (ap-south-1 + ap-southeast-1) | South Asian breadth; failover; reduced cold-start for non-BD users |

**Zero architectural rework required.** The existing Docker image and dual-service nginx routing port directly. The model checkpoint already lives on Hugging Face Hub and is downloaded lazily by the container at boot — no special model-serving infrastructure is needed.

---

## NRB integration into the roadmap

The NRB Sponsor-a-District widget is the Phase 1 demo of what becomes the Phase 2 platform. Each phase increases NRB depth:

| Phase | NRB integration |
|---|---|
| 1 | Demo widget in app (Tab 6) — shows the UX, gathers interest, no real payments |
| 2 | Real payment integration (Stripe for US/UK/EU/AU/JP/SG diaspora; bKash bridge for direct BDT settlement); monthly transparency report to sponsors |
| 3 | Diaspora-org partnerships executed: BMANA chapter campaigns, JABEN co-marketing, Probashi Kallyan Bank product integration, Sadqah/Zakat channel hooks during Ramadan |

---

## Risk register

| Risk | Mitigation |
|---|---|
| HF Spaces free tier deprecates or rate-limits | AWS migration is pre-planned and the Docker image ports directly; cost is bounded |
| Pilot UHC adoption is slow | WhatsApp/Telegram bots already work standalone; reach is not gated on UHC sign-off |
| Doctor revenue-share stream lags forecast | NRB sponsorship and grants are independent streams — single-stream failure is recoverable |
| Diaspora payments fail compliance | Phase 1 widget is demo-only; Phase 2 uses established processors (Stripe, bKash) with clear KYC paths |
| Model accuracy degrades on new geographies | Quarterly re-evaluation; new model card per locale before Phase 3 expansion |

---

## What this roadmap does not promise

This is a 12-month plan with named partners and concrete cost estimates. It is not a finished business that exists today. Phase 1 begins after BuildFest. Phase 2 is contingent on Phase 1 outcome metrics. Phase 3 is aspirational and contingent on Phase 2 traction. The numbers are honest projections, not forecasts.
