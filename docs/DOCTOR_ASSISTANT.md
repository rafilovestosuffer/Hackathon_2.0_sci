# SkinAI for Clinicians — the Doctor-Facing "Second Pair of Eyes"

> **One line:** SkinAI already routes the *right patient to the right doctor*.
> This document frames the natural next step — helping that **doctor** once the
> patient arrives — as an *augmented-intelligence* tool: **a second pair of
> eyes, never the final word.**

This is a **positioning + framing** document, not a rewrite of the product. It
explains how to describe, pitch, and (optionally) build a doctor-facing mode
**without breaking a single one of SkinAI's existing safety commitments.** In
fact, the doctor-facing use case is the *most defensible* thing the system can
do, because the whole product is already engineered around "the AI never
replaces a clinician."

---

## 1. Why this framing is honest, not a marketing pivot

SkinAI's entire ethics posture is already **human-in-the-loop**:

- *"The AI never replaces a clinician"* — every output is a referral to a doctor (`docs/ETHICS_STATEMENT.md` §1, §6).
- *"AI is one signal of three, never the final word"* — the 3-signal triage engine (`severity/engine.py`).
- The **referral PDF is already addressed to a doctor**, not the patient (`pdf_gen/referral.py`).

So the doctor-facing product is not a new philosophy bolted on top — it is the
**same philosophy, pointed at the doctor.** The patient app answers *"where do I
go?"* The clinician mode answers *"here is the structured context and a
second opinion, so the doctor decides faster and safer."*

That is the difference between an honest frame and an over-claim:

| ❌ Do **not** say | ✅ Say instead |
|---|---|
| "AI that diagnoses skin disease for doctors" | "A decision-support second opinion the doctor confirms or overrides" |
| "Replaces the dermatologist" | "Extends the one dermatologist per 250,000 people to more patients" |
| "Automated triage" | "Augmented triage — the doctor is always the final authority" |
| "99% accurate diagnosis" | "A calibrated suggestion with confidence, differential, and the evidence behind it" |

The industry term for the good column is **augmented intelligence** — the
American Medical Association deliberately uses "augmented," not "artificial,"
to signal *AI assists the physician, it is not autonomous.* Adopt that word.

---

## 2. Who the "doctor" actually is in rural Bangladesh

The realism of this pitch depends on naming the *real* clinician personas —
because in this setting the person holding the phone is usually **not** a
dermatologist. That is precisely the gap.

### Persona A — the Upazila MBBS generalist *(primary target)*
The doctor at an Upazila Health Complex (Tier 2 in your engine) is a **general
MBBS physician, not a dermatologist.** They see skin cases daily with little
specialist training and no specialist to consult. For them, SkinAI is:
- a **structured second opinion** on a case outside their specialty,
- a **differential-diagnosis prompt** ("have you considered scabies vs. eczema? these two share ≥2 symptoms"),
- a **when-to-escalate signal** they can trust and document.

This is the single highest-value user. Evidence: a prospective trial across 36
Swedish primary-care centres found AI decision support **measurably increased
the physician's diagnostic accuracy** on skin lesions — the value of these
tools is largest for the *non-specialist*, exactly your Persona A.

### Persona B — the Community Health Worker / village "doctor"
The frontline health worker or paramedic who is often the *first and only*
contact. Your existing **CHW slip** (`pdf_gen/referral.py`) already speaks to
this persona. SkinAI gives them a **structured checklist and an escalation
flag** so they know *which* patients genuinely need to be sent up the chain —
raising the quality of who gets referred, not just the quantity.

### Persona C — the remote dermatologist doing teledermatology
The scarce specialist, reachable by store-and-forward. For them SkinAI is a
**pre-triaged, pre-charted worklist**: each case arrives with history, image,
model suggestion, confidence, and differential already attached, so a 10-minute
review becomes a 3-minute one. Published teledermatology programmes show this
pattern **cuts referral volume and wait times** (e.g. an Austrian store-and-
forward service where only 17% of triaged patients still needed an in-person
specialist visit).

> **Framing takeaway:** don't pitch "an AI for dermatologists." Pitch **"a
> dermatology co-pilot for the 99% of frontline clinicians who are *not*
> dermatologists,"** plus a **triage inbox that makes the one real
> dermatologist go further.**

---

## 3. You already built most of it — reframe, don't rebuild

The strongest, most realistic pitch is that the doctor-facing value is
**already latent in the current system.** Nearly every existing component is a
doctor-facing feature that today happens to be shown to the patient.

| Existing component | Patient-facing role today | Doctor-facing reframe |
|---|---|---|
| **4-section referral PDF** (`pdf_gen/referral.py`) | The patient's "letter to bring" | It is *already addressed to a doctor* → the doctor's **structured intake note / pre-chart** |
| **9-field voice history** (`voice/pipeline.py`) | Auto-fills the patient form | **Pre-charting** — saves the doctor the history-taking transcription |
| **BD-SkinNet + confidence + top-2** (`model/`) | Shown as a result banner | The **"second reader" suggestion** with a calibrated confidence and differential |
| **CBAM attention** (built into the model) | Interpretability claim | An **explainability overlay** — *where the model looked* — so the doctor can review the basis, not just the label |
| **Knowledge graph** (`graph/store.py`) | "Signs to monitor" panel | **Differential support** — diseases sharing ≥2 symptoms, escalation flags, live Cypher differential |
| **Grounded RAG, no-medicine guardrail** (`rag/`) | Patient Q&A | A **cited reference desk** (CDC/NIH/WHO/DGHS) at the point of care |
| **3-signal triage engine** (`severity/`) | Routes the patient | A **documented, auditable escalation rationale** the doctor can accept or override |

So the doctor mode is roughly: **the same pipeline, plus one new primitive —
the doctor's confirm / override.** That single addition is what turns a
patient screening tool into a clinician decision-support tool.

---

## 4. The one feature that makes it real: **the doctor's override loop**

If you build *one* thing, build this. It is small, and it is the linchpin of
the entire honest framing.

```
 Patient submits ──▶ SkinAI suggests ──▶ Doctor reviews ──▶ Doctor CONFIRMS / OVERRIDES ──▶ Final record
   (image+voice)      (class, conf,        (sees the         (one tap; can edit           (doctor's
                       differential,        evidence,          diagnosis + tier)            decision,
                       triage tier)         attention,                                      AI as input)
                                            sources)
```

Why this single loop carries the whole positioning:

1. **It makes "the doctor is the final authority" literally true in code**, not just in a disclaimer. The stored record is the *doctor's* decision; the AI output is an input to it.
2. **It creates a data flywheel.** Every override is a free, expert-labelled correction on real Bangladeshi clinical data — the exact scarce asset your model card says is hard to get. Model improvement becomes a by-product of use. (State this carefully: opt-in, de-identified, governed — consistent with your data-minimisation stance.)
3. **It is the regulatory dividing line** (see §5). A tool the clinician *reviews and can override*, with the basis exposed, is decision *support*. A tool that acts on its own is a medical device. You want to be firmly on the support side.

---

## 5. The realism anchor: regulatory & liability framing

"Realistic" means it survives a hospital procurement officer or a skeptical
clinician asking *"is this a regulated medical device, and who is liable?"*
Your answer, and it is a strong one:

**SkinAI is positioned as non-autonomous clinical decision support — the class
of software regulators treat most leniently — because it satisfies the
"clinician can independently review the basis" test.**

The US FDA's Clinical Decision Support guidance draws the key line at whether
the software lets the clinician **independently review the basis** for its
recommendation, so they don't *rely primarily* on the AI. To sit on the safe
side of that line, a tool should:

1. **not omit material information** — you show the full history + image;
2. **describe the quality/limits of the data** — you already ship a Model Card, Data Card, and an in-product bias banner (Fitzpatrick IV–VI, adults, 7 classes);
3. **explain how it reached *this* patient's result** — you have confidence, top-2 differential, source provenance, *and* CBAM attention showing where the model looked.

You are, almost uniquely for a hackathon project, **already compliant with the
"reviewable basis" criterion.** Lead with that. Also note the FDA's *time-
sensitivity* caveat: tools for a "critical, time-sensitive" decision can't meet
the review criterion — which is another reason to frame this as **triage and
routine review support, not emergency autonomous decisioning.**

On **liability**, mirror the AMA position: liability should fall on whoever is
best placed to avert harm; the physician retains professional judgment and the
final decision. In practice: *the doctor signs off; the AI is a documented,
cited input.* Never let the pitch imply the doctor can defer to the machine.

> **Two sentences for the deck:** "SkinAI for Clinicians is *augmented
> intelligence*, not an autonomous device: the physician reviews the evidence —
> image, history, confidence, differential, and even where the model looked —
> and confirms or overrides every result. That keeps the doctor the final
> authority and keeps the tool on the decision-*support* side of the line."

---

## 6. Concrete, buildable doctor-mode features (ranked by effort/impact)

Realistic = shippable on top of what exists. Ranked so a hackathon team knows
where to start.

| # | Feature | Build cost | Reuses | Impact |
|---|---|---|---|---|
| 1 | **Confirm / Override panel** on the result card (doctor picks final class + tier; stored as *doctor's* decision) | **Low** | result card, triage engine | ★★★ makes the whole framing real |
| 2 | **"Clinician view" toggle** — one flag that swaps patient-friendly copy for a dense clinical summary (confidence, differential %, escalation rationale, sources) | **Low** | existing UI + data | ★★★ instantly reframes the same screen for a doctor |
| 3 | **Teledermatology worklist / inbox** — patient submissions queue for a doctor to review (store-and-forward) | **Medium** | bot state machine, session model | ★★★ this is Persona C's whole product |
| 4 | **Attention overlay** — render the CBAM heatmap over the lesion so the doctor sees *where* the model looked | **Medium** | model already computes it | ★★ trust + "reviewable basis" |
| 5 | **Pre-chart export** — the 9-field history + assessment as a clean clinical note (not just the patient PDF) | **Low** | referral PDF generator | ★★ saves consult time |
| 6 | **Override-driven feedback log** — opt-in, de-identified store of `{AI suggestion → doctor's final}` for model improvement | **Medium** | analytics DB pattern | ★★ data flywheel (frame carefully) |

Start with **#1 + #2**: together they turn the *current* app into a credible
clinician tool in a day, and they are exactly what a live demo needs to show a
judge the doctor is in control.

---

## 7. Does this break the "free for patients" mission or the ethics? No.

- **Mission lock is intact.** Screening, triage, and the referral PDF stay free
  at the patient endpoint. A clinician mode is a *different endpoint* — the
  natural home for the sustainability streams already in `docs/BUSINESS_MODEL.md`
  (a clinic/teleconsult can pay for the worklist; the patient never does).
- **Every ethics commitment still holds:** no medicine recommendations (the
  guardrail applies to doctor mode too), no persistent PII by default, bias
  disclosure in-product, escalation-biased triage. The doctor mode *strengthens*
  "human-in-the-loop" by making the human's confirmation an explicit, stored
  step.
- **New commitments to add** (keep the ethics doc honest): (a) the override
  record is the clinical source of truth, not the AI; (b) any feedback-loop data
  is opt-in and de-identified; (c) doctor mode is decision *support*, and the
  product says so on the clinician screen just as it says "not a diagnosis" on
  the patient screen.

---

## 8. Ready-to-use language (pitch, README, deck)

**Elevator (patient + doctor together):**
> "SkinAI gets the right patient to the right doctor — and now gives that
> doctor a second pair of eyes when the patient arrives. For the millions who
> are seen by a *general* physician or health worker rather than one of
> Bangladesh's few dermatologists, it's a cited, calibrated second opinion the
> clinician confirms or overrides. Augmented intelligence, never autonomous."

**Tagline extension of the existing motto:**
> *সঠিক রোগী → সঠিক ডাক্তার → সঠিক সময় → সঠিক সিদ্ধান্ত*
> *Right patient → Right doctor → Right time → **Right decision.***

**The single defensible claim to repeat everywhere:**
> "A second pair of eyes, never the final word."

**For a skeptical clinician:**
> "It doesn't tell you the answer — it hands you a structured history, a
> calibrated suggestion with its confidence and differential, the sources
> behind it, and where the model looked. You decide. Your decision is what's
> recorded."

---

## 9. Sources / evidence base

- Augmented intelligence as the assistive framing (AMA): [Augmented intelligence in medicine — AMA](https://www.ama-assn.org/practice-management/digital-health/augmented-intelligence-medicine) · [AMA AI principles (PDF)](https://www.ama-assn.org/system/files/ama-ai-principles.pdf)
- AI decision support measurably raised physicians' accuracy in **primary care** (Swedish multicentre trial): [Evaluation of an AI-based decision support for melanoma in primary care — *British Journal of Dermatology*](https://academic.oup.com/bjd/article/191/1/125/7564904) · [Feasibility / mixed-method study — PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10851794/)
- AI as a **"second reader" / assistive tool, not replacement** (dermatologist + GP views): [Towards successful implementation of AI in skin cancer care — PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC9734890/) · [Augmented intelligence and dermatology, Part II — *JAAD*](https://www.sciencedirect.com/science/article/abs/pii/S0190962225004402)
- **Teledermatology triage** reduces referrals & wait times, uplifts local providers: [Teledermatology reduces referrals & improves specialist access — PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC7788431/) · [Teledermatology in rural, underserved, isolated settings — PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC9589860/) · [Five years of teledermatology triage in Styria — *JDDG*](https://onlinelibrary.wiley.com/doi/10.1111/ddg.70097)
- **Regulatory "reviewable basis" line** for non-device CDS (FDA 2022 final guidance): [FDA Final CDS Software Guidance — Goodwin](https://www.goodwinlaw.com/en/insights/publications/2022/10/10_17-fda-issues-final-clinical-decision) · [Federal Register notice](https://www.federalregister.gov/documents/2022/09/28/2022-20993/clinical-decision-support-software-guidance-for-industry-and-food-and-drug-administration-staff)

> **Note:** these sources are US/EU regulatory and clinical-evidence anchors used
> to *frame* the positioning. SkinAI remains a research prototype and is not a
> certified medical device in any jurisdiction; doctor mode does not change that
> disclaimer (`README.md` → Medical disclaimer).
