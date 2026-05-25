# Business Model — SkinAI Bangladesh

## Mission lock

The product is free at the patient endpoint, forever. This is not a marketing line — it is encoded as a hard constraint in `CLAUDE.md` and surfaced in the in-app model card. Every sustainability decision below is designed around that constraint, not in spite of it.

---

## Three sustainability streams

### 1. Telemedicine revenue share

**What.** 15% of each video consultation fee booked through the in-app doctor-booking flow (Tab 5).

**Who pays.** Partner doctors. The pilot demoes Dr. Nusrat Jahan; Phase 2 onboards an initial roster of 8–12 licensed dermatologists and general physicians.

**Why it works.** A doctor receiving a SkinAI referral gets a patient who is (a) pre-triaged to the right urgency tier, (b) arrives with a structured 4-section referral PDF including patient history, AI assessment, and triage recommendation, and (c) is already filtered for cases worth a teleconsult. The consult is shorter, conversion is higher, and the doctor is willing to share fee because the funnel quality is higher than what they can buy elsewhere.

**Unit economics.** At a typical ₹500 (~$4.50) teleconsult fee, 15% = $0.68 per booking. Break-even at the projected $40/month Phase 2 infrastructure cost is ~60 bookings/month — comfortably under the Phase 2 capacity of 8 districts × 1 booking/district/day.

### 2. NRB Sponsor-a-District

**What.** Bangladeshi diaspora pledges fund the free patient tier in a named district. Each pledge is reported back to the sponsor with district-level usage metrics every month.

**Who pays.** The ~1.7 million Bangladeshis living abroad. Bangladesh receives over $20 billion in annual remittances per recent World Bank figures — one of the highest GDP-share remittance flows in the world.

**Why it works.** Almost none of the diaspora remittance flow today routes into measurable health-system impact, because no infrastructure exists for an individual abroad to fund a specific district, see what was funded, and verify it was used. SkinAI's referral architecture provides this infrastructure as a natural side effect: every screening is geolocated, every referral has a marginal cost, every sponsorship can be reported back with anonymised usage metrics.

The in-app NRB widget (Tab 6 → NRB) is a working demo of the sponsorship UX. Real payment integration is a Phase 2 deliverable; the design is intentionally similar to existing diaspora-giving products (LaunchGood, GlobalGiving) so user-flow risk is low.

### 3. Public-health &amp; development grants

**What.** Anonymised, aggregated skin-disease epidemiology shared under a non-commercial license with the Ministry of Health and Family Welfare (MoHFW), DGHS Bangladesh, and icddr,b. National disease surveillance benefits directly from the data flow.

**Who pays.** Grant funders — likely candidates: Gates Foundation, USAID Bangladesh, WHO South-East Asia Regional Office, Wellcome Trust, BRAC.

**Why it works.** Skin-disease epidemiology at the upazila level is poorly captured in existing surveillance systems. A geolocated, condition-tagged data stream — even one limited to seven classes — is materially useful to public-health planners and is a natural grant-fundable initiative. The grant funds project operations; the data benefits the country; the patient pays nothing.

---

## Unit economics

| Item | Value |
|---|---|
| Marginal inference cost | ≈ $0.0003 / screening (INT8 dynamic-quantised Swin on CPU; HF Spaces free tier) |
| Hosting cost at 10k MAU | ≈ $40 / month on AWS ap-south-1 (Mumbai region) |
| Hosting cost at 100k MAU | ≈ $400 / month (estimate, Phase 3) |
| Phase 1 monthly burn | &lt; $50 (HF Spaces free + WhatsApp Cloud API free tier) |
| Phase 2 monthly burn | ≈ $200 (AWS migration, WhatsApp paid tier, modest sponsorship-platform fees) |
| Phase 3 monthly burn | ≈ $400 (national-scale infra; multi-region; mobile APK distribution) |
| Break-even (Phase 2) | ~1,200 paid teleconsult shares per month |
| Patient-side cost | $0 — mission-locked |

---

## Why this is competitive vs. alternatives

| Alternative | Why it fails the rural-Bangladesh case |
|---|---|
| Telemedicine app charging patients directly | The 1,500 BDT consultation fee is the original problem — Rahim cannot afford it |
| Pure NGO / grant-only | Single point of failure; collapses if one grant cycle is missed |
| Pure for-profit B2C SaaS | Mission incompatibility; would need to extract rent from the patient base it claims to serve |
| Hospital-side B2B SaaS | Upazila Health Complexes lack the procurement budget; the value would have to compete against medicines |

The three-stream model spreads risk: telemedicine revenue grows linearly with scale, NRB sponsorship is independent of clinic adoption, grants buffer the rest. Loss of any one stream is recoverable.

---

## What we will not do

- Charge patients for screening, referral, or triage. Ever.
- Sell anonymised data to commercial parties (advertisers, insurers, pharma).
- Recommend specific medicines or treatments — referral-only is a hard constraint.
- Operate without a licensed clinician in the loop — every output is addressed to a doctor.
