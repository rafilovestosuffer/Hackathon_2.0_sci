# Data Card — BD-SkinNet Training Set

*Format adapted from Gebru et al., "Datasheets for Datasets" (CACM 2021).*

---

## Motivation

The dataset was assembled to train a skin-disease classifier suitable for triaging adult skin complaints in rural Bangladesh. Existing public dermatology datasets (e.g., DermNet, ISIC) over-represent Fitzpatrick I–III skin tones and Western clinical contexts; none capture the disease mix, lighting, and camera conditions typical of a Bangladeshi Upazila Health Complex.

---

## Composition

| Field | Value |
|---|---|
| Modality | RGB clinical photographs (smartphone-grade) |
| Source institutions | Faridpur Medical College Hospital (FMCH); Rangpur Medical College Hospital (RMCH) |
| Country | Bangladesh |
| Classes (7 + control) | Atopic Dermatitis, Eczema, Scabies, Vitiligo, Contact Dermatitis, Seborrheic Dermatitis, Tinea; Normal control |
| Age range | Adults ≥18 |
| Skin tone | Predominantly Fitzpatrick IV–VI (South Asian) |
| Sex | Both, approximately representative of the presenting clinic populations |

---

## Collection process

Photographs were captured by attending clinicians or trained assistants at the point of care, using standard smartphone cameras under hospital lighting. Each image was labelled by the diagnosing physician. No social-media scraping, no synthetic generation, no DermNet content.

---

## Preprocessing

- Resized to 224 × 224
- Standard ImageNet normalisation
- Train-time augmentation: horizontal flip, mild rotation, colour jitter
- Optional inference-time enhancement: CLAHE (low light) + unsharp mask (mild blur) applied automatically when the input fails a Laplacian-variance sharpness check

---

## Distribution

The trained checkpoint (`bd_skinnet_int8.pth`) is published on Hugging Face Hub at `rafilovestosuffer/bd-skinnet`. The raw training images are **not** redistributed — they remain with the source institutions under their patient-consent agreements. Researchers interested in the training corpus should contact the source institutions directly.

---

## Maintenance &amp; updates

The deployed checkpoint will be re-evaluated quarterly against newly collected pilot-site data once Phase 1 (Rangpur Division Upazila Health Complexes) is active. Material accuracy regressions will trigger a model card revision and, if necessary, a checkpoint refresh.

---

## Known gaps

- **Pediatric cases:** not represented; do not use for patients under 18.
- **Fitzpatrick I–III:** under-represented; performance not formally evaluated.
- **Hair-bearing scalp, nail, mucous membrane, eye-area lesions:** under-represented.
- **Pigmented / melanocytic lesions:** explicitly excluded — suspected melanoma must be referred immediately, not screened by this model.
- **Burns, post-surgical wounds, open bleeding lesions:** out of distribution; the app surfaces these as Tier 3 escalations.

---

## Ethical sourcing

Patient consent was obtained at the source institutions following their standard clinical-photography consent procedures. No image carries identifiable face data unless the affected lesion required it, in which case the image is cropped to the lesion at preprocessing time. No personally identifying metadata (name, MRN, geolocation) is associated with the published checkpoint.
