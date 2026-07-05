# Ethics Statement — SkinAI Bangladesh

## Purpose

This statement makes explicit the ethical commitments embedded in the SkinAI Bangladesh codebase, and the design decisions that enforce them. Where a commitment is enforced by code, the enforcing file is named.

---

## 1. The AI never replaces a clinician

Every output of the system is structured as a **referral to a licensed clinician**, not a diagnosis. The generated PDF is addressed to a doctor (`pdf_gen/referral.py`), the in-app result card states "AI-assisted triage, not a diagnosis," and the model card surfaces this on the same screen as the prediction. The patient never receives a final diagnostic claim.

---

## 2. No medicine recommendations, ever

Encoded as Constraint 3 in `CLAUDE.md`. The RAG knowledge base (`rag/knowledge/`) excludes medication-recommendation content by source filter; the answering prompt explicitly forbids prescribing language. This is reviewed in the test suite (`tests/test_rag.py`).

---

## 3. Bias and fairness disclosure inside the product

The training data is predominantly Fitzpatrick IV–VI South Asian skin tones, adults ≥18, and seven specific disease classes. The product surfaces this scope in three places:

1. **In-flow disclosure.** A bilingual fairness banner renders directly under every AI diagnosis result, before the user makes any downstream decision.
2. **Model card tab.** A dedicated "Impact &amp; Ethics" tab inside the app summarises training data, demographic coverage, known limitations, and "when NOT to use."
3. **`docs/MODEL_CARD.md`** and **`docs/DATA_CARD.md`** provide the full machine-readable documentation.

A user cannot use this product without seeing its limitations.

---

## 4. "When NOT to use" is enforced, not just documented

The following cases are out of scope for the model:

- Suspected melanoma or other pigmented malignancies
- Burns
- Open or bleeding wounds
- Post-surgical sites
- Mucous membrane involvement
- Eye-area lesions
- Pediatric cases (patients under 18)

The severity engine (`severity/engine.py`) treats low model confidence as a Tier 3 escalation signal, so out-of-distribution images are routed to the highest level of care rather than misclassified. This is bias mitigation by *system design*, not by policy.

---

## 5. Multi-signal safety as bias mitigation

The 3-signal severity engine combines:

1. Disease class (model output)
2. Model confidence
3. Bengali voice symptom keywords (e.g., জ্বর, ছড়িয়ে, ব্যথা, রক্ত — fever, spreading, pain, blood)

No single signal decides the tier on its own: low model confidence escalates the case regardless of the predicted class, and urgent symptom keywords escalate further. This is a design measure — a biased model output (e.g., low confidence on a Fitzpatrick I patient) cannot single-handedly route someone to inadequate care.

---

## 6. Human-in-the-loop, always

Every output is a referral letter intended for a doctor. The teleconsult booking flow connects the patient to a licensed clinician for the actual diagnosis. There is no path through the product where an AI prediction becomes the patient's final answer.

---

## 7. Data minimisation

- **No persistent database.** All state lives in `st.session_state` for the duration of the user's session and is discarded when the session ends.
- **No analytics tracking.** No Google Analytics, no Sentry user identification, no third-party trackers.
- **No PII persistence.** Patient name, age, and history are captured in session state only; they appear in the generated PDF (which the patient downloads), not in any server-side store.
- **Image leaves the session only on opt-in.** The skin image is held in session memory and never written to disk unless the patient explicitly books a teleconsult, in which case it is forwarded to the consulting doctor.

---

## 8. Knowledge-base provenance

The RAG knowledge base sources are strictly limited to:

- US CDC (Centers for Disease Control)
- US NIH (National Institutes of Health)
- WHO (World Health Organization)
- DGHS Bangladesh (Directorate General of Health Services)

DermNet is **forbidden** (Constraint 1 in `CLAUDE.md`) under its AI-image policy. No scraped social-media content. No AI-generated synthetic content. This is enforced at index-build time in `rag/build_index.py`.

---

## 9. Mission lock on the patient-side cost

The product is free at the patient endpoint, forever. This is encoded in `CLAUDE.md` and surfaced in the model card. The three sustainability streams (telemedicine revenue share, NRB sponsorship, public-health grants — see `docs/BUSINESS_MODEL.md`) are designed around this constraint, not in tension with it.

---

## 10. Escalation policy

The severity engine is intentionally conservative — it escalates more readily than it relaxes:

- Confidence < 0.40 → Tier 3 (urgent), even if the predicted class is otherwise low-tier
- Lesion coverage > 40% → escalate one tier
- Any urgent Bengali symptom keyword detected → escalate one tier (capped at Tier 3)

A false positive in this system sends a patient to a clinic they didn't strictly need. A false negative leaves a patient with worse care than they needed. The asymmetry favours over-referral. This is documented in `severity/engine.py` and reviewed in `tests/test_severity.py`.

---

## Contact for ethical concerns

Rafiur Rahman — `mdrafiurrahman123098@gmail.com`. Issues, concerns, or reports of harm should be opened on the GitHub repository or sent to the address above.
