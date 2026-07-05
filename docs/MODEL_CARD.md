# Model Card — BD-SkinNet (INT8)

*Format: Mitchell et al., "Model Cards for Model Reporting" (FAT* 2019).*

---

## Model details

| Field | Value |
|---|---|
| Name | BD-SkinNet |
| Version | 1.0 (INT8 dynamic-quantised) |
| Architecture | Swin Transformer Base + CBAM (Channel + Spatial Attention) |
| Parameters | ~88M (full precision); INT8 weights for CPU deployment |
| Input | 224 × 224 RGB skin photograph |
| Output | Softmax over 7 disease classes + Normal |
| Primary file | `bd_skinnet_int8.pth` (hosted on Hugging Face Hub: `rafilovestosuffer/bd-skinnet`) |
| License | Research and humanitarian use; not for commercial diagnostic claims |
| Contact | Rafiur Rahman — `mdrafiurrahman123098@gmail.com` |

---

## Intended use

**Primary purpose.** Assist non-clinician users in rural Bangladesh in routing skin complaints to the correct level of care: pharmacist (Tier 1), Upazila Health Complex (Tier 2), or District Hospital emergency (Tier 3). The model is one signal of four in a multi-signal triage engine — it is never used as a standalone diagnostic.

**Intended users.** Adults (≥18) in Bangladesh self-screening on a smartphone or feature phone (via the WhatsApp/Telegram bot), and Community Health Workers (Shasthya Seboika, ASHA equivalents) using the simplified CHW mode.

**Out of scope.** Final diagnosis, prescription, replacing a dermatologist consultation, screening for melanoma or other malignancies, pediatric cases, post-surgical wound assessment.

---

## Training data

| Source | Faridpur Medical College Hospital, Rangpur Medical College Hospital |
|---|---|
| Country | Bangladesh |
| Image type | In-clinic photographs of presenting skin complaints |
| Consent | Patient consent obtained at point of care; institutional review documented at source institutions |
| Classes | Atopic Dermatitis, Eczema, Scabies, Vitiligo, Contact Dermatitis, Seborrheic Dermatitis, Tinea (+ Normal control) |
| Excluded | DermNet (forbidden under their AI-image policy), social-media scraped images, AI-generated synthetic data |

See `docs/DATA_CARD.md` for the full data card.

---

## Performance

- **F1 score:** 92.46% on held-out Bangladeshi clinical test set
- **INT8 vs FP32:** within 1.5 F1 points; tradeoff accepted for free-CPU deployment feasibility
- **Inference latency:** ~1.8 seconds per image on HF Spaces free CPU tier
- **Per-class performance:** documented in the training repository; lowest-performing class (Vitiligo) is auto-escalated by the severity engine when confidence < 0.40

---

## Bias analysis &amp; limitations

**Geographic.** All training data originates from Faridpur and Rangpur divisions. Performance on other Bangladeshi divisions is expected to be comparable (similar genetic and environmental profiles) but has not been formally evaluated. Performance on non-South-Asian populations is expected to degrade.

**Skin tone.** Training data is predominantly Fitzpatrick IV–VI. The model has not been evaluated on Fitzpatrick I–III. The in-app fairness disclosure surfaces this limitation to every user.

**Age.** Adults only (≥18). Pediatric presentations of the same conditions can differ morphologically and are explicitly out of scope.

**Disease coverage.** Seven classes only. Any presentation outside this set will be mapped to the nearest learned class with low confidence — which the severity engine treats as a Tier 3 escalation signal, sending the patient to a higher level of care rather than misclassifying.

**Anatomical limitations.** Hair-bearing scalp, nail beds, mucous membranes, and eye-involvement cases are not well represented in training data and should not be relied on.

**Image quality.** Performance degrades on blurry or poorly lit images. The app runs CLAHE + unsharp-mask auto-enhancement before inference and warns the user when input quality is low.

---

## Ethical considerations

- **No medicine recommendations, ever.** Encoded as a hard constraint in `CLAUDE.md`.
- **No final diagnosis claims.** The output is structured as a *referral to a licensed clinician* — the generated PDF is addressed to a doctor, not the patient.
- **Auto-escalation on uncertainty.** Low confidence (<40%) → Tier 3, by design.
- **Multi-signal cross-check.** The model is one of four severity signals (disease class, model confidence, lesion coverage, voice symptom keywords). Single-point failure is mitigated by design.
- **Data minimisation.** Inferences run server-side in session state; no PII is persisted, no analytics tracking, no database. Images leave the session only if the patient explicitly books a teleconsult.
- **Free at the patient endpoint forever.** Mission-locked. Sustainability comes from telemedicine revenue share, NRB sponsorship, and grants — never from patient charges.

---

## Caveats

This model card describes the deployed checkpoint as of the BuildFest submission. Performance numbers reflect the held-out test set the model was originally evaluated on; real-world deployment in additional districts will require periodic re-evaluation. Adoption in new geographies (India, Pakistan, Nepal, Sri Lanka — Phase 3 of the roadmap) will require a new model card per locale.
