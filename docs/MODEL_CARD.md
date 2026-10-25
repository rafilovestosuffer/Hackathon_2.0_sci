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
| Output | Softmax over 6 classes: Atopic Dermatitis · Contact Dermatitis · Eczema · Scabies · Seborrheic Dermatitis · Tinea (order read from the checkpoint's `class_to_idx`) |
| Primary file | `bd_skinnet_int8.pth` (hosted on Hugging Face Hub: `rafilovestosuffer/bd-skinnet`) |
| License | Research and humanitarian use; not for commercial diagnostic claims |
| Contact | Rafiur Rahman — `mdrafiurrahman123098@gmail.com` |

---

## Intended use

**Primary purpose.** Assist non-clinician users in rural Bangladesh in routing skin complaints to the correct level of care: pharmacist (Tier 1), Upazila Health Complex (Tier 2), or District Hospital emergency (Tier 3). The model is one signal of three in a multi-signal triage engine — it is never used as a standalone diagnostic.

**Intended users.** Adults (≥18) in Bangladesh self-screening on a smartphone or feature phone (via the WhatsApp/Telegram bot), and Community Health Workers (Shasthya Seboika, ASHA equivalents) using the simplified CHW mode.

**Out of scope.** Final diagnosis, prescription, replacing a dermatologist consultation, screening for melanoma or other malignancies, pediatric cases, post-surgical wound assessment.

---

## Training data

| Source | Faridpur Medical College Hospital, Rangpur Medical College Hospital, Kishoreganj Medical College Hospital |
|---|---|
| Country | Bangladesh |
| Image type | In-clinic photographs of presenting skin complaints |
| Consent | As documented by the dataset publishers: SkinDiseaseBD (Faridpur MCH) and SkinDisNet (Rangpur & Kishoreganj MCH; Mendeley Data, DOI 10.17632/yj3md44hxg.2) |
| Classes | Live checkpoint: Atopic Dermatitis, Contact Dermatitis, Eczema, Scabies, Seborrheic Dermatitis, Tinea. (The research model adds Vitiligo.) |
| Synthetic data | Stable Diffusion v1.5 image-to-image augmentation for three minority classes (Atopic Dermatitis, Seborrheic Dermatitis, Vitiligo): 1,039 generated images, added to the **training split only**. The test set is real images only. |
| Excluded | DermNet (forbidden under their AI-image policy), social-media scraped images |

See `docs/DATA_CARD.md` for the full data card.

---

## Performance

- **Live checkpoint:** 6 classes, INT8, validation F1 **0.816** at epoch 34 (stored in the checkpoint). Held-out test metrics for this checkpoint are produced by `scripts/eval_triage_safety.py` and recorded in `results/`.
- **Research model (not deployed):** the 7-class BD-SkinNet in the BD_SkinNet repo reports 92.46% macro-F1 on 499 real test images (image-level stratified 70/15/15 split, mean of 3 seeds). That checkpoint is not the one served here.
- **Split caveat:** the split is by image, not by patient — the source datasets were not grouped by patient and no near-duplicate removal was applied, so the test score may be optimistic for unseen patients.
- **Inference latency:** ~1.8 seconds per image on HF Spaces free CPU tier
- **Not covered by the live model:** Vitiligo and healthy skin. Any image is mapped to one of the 6 classes; low confidence (< 0.40) escalates to Tier 3.

---

## Bias analysis &amp; limitations

**Geographic.** All training data originates from three Bangladeshi medical college hospitals (Faridpur, Rangpur, Kishoreganj). Performance on other Bangladeshi districts is expected to be comparable (similar genetic and environmental profiles) but has not been formally evaluated. Performance on non-South-Asian populations is expected to degrade.

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
- **Multi-signal cross-check.** The model is one of three severity signals (disease class, model confidence, voice symptom keywords). Single-point failure is mitigated by design.
- **Data minimisation.** Inferences run server-side in session state. Nothing is saved unless the patient consents to doctor review; then a small thumbnail and the AI output (no name, phone or transcript) are kept for 7 days. Analytics are anonymous counters.
- **Free at the patient endpoint forever.** Mission-locked. Sustainability comes from telemedicine revenue share, NRB sponsorship, and grants — never from patient charges.

---

## Caveats

This model card describes the deployed checkpoint as of this submission. Performance numbers reflect the held-out test set the model was originally evaluated on; real-world deployment in additional districts will require periodic re-evaluation. Adoption in new geographies (India, Pakistan, Nepal, Sri Lanka — Phase 3 of the roadmap) will require a new model card per locale.
