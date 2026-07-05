# Business Model — SkinAI Bangladesh

## Mission lock

**Screening, triage and the referral PDF are free at the patient endpoint, forever.** This covers the entire core pipeline — voice intake, image analysis, severity tier decision, hospital map, and the downloadable referral letter addressed to a licensed doctor. This is not a marketing line; it is encoded as a hard constraint in `CLAUDE.md`.

The only paid step in the product is the *optional* teleconsult booking (Tab 5). A patient who simply wants to know "what is this and where do I go?" pays nothing, ever.

---

## Three sustainability streams

### 1. Teleconsult service fee

**What.** When a patient opts to book a video consultation through Tab 5, a small platform service fee is added on top of the doctor's fixed consultation fee at booking time. Example: if the doctor's fixed fee is ৳600, the patient pays a single transparent price of ৳700; the doctor receives 100% of their ৳600 fee, and the platform retains the ৳100 service fee.

**Who pays.** The patient — but only if they choose to book a teleconsult. The screening, triage, and downloadable referral PDF remain free.

**Why this is the right structure, not a revenue-share.**

- **Doctors keep their full fixed fee.** No negotiation, no "what cut do you take" friction. Onboarding a new doctor is a 30-second conversation.
- **Patient sees one clean price.** The service fee is built into the booking total. There is no separate line item, no haggling, no upsell — the user experience matches what patients already expect from telemedicine apps like Doctime or Praava.
- **Higher funnel quality justifies the fee.** A SkinAI-referred patient arrives with a structured 4-section referral PDF (patient history + AI assessment + triage tier + recommended action). The consult is shorter, the no-show rate is lower, and the diagnosis quality is higher because the doctor isn't starting from a blank slate.

**Unit economics.** At a ৳100 service fee per booking (~$0.91 USD at current rates), break-even on the projected $40/month Phase 2 infrastructure cost is ~45 bookings per month — comfortably below the Phase 2 capacity of 8 districts × 1 booking/district/day. Even at conservative adoption, this stream alone covers operating cost; NRB and grants fund expansion, not survival.

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
