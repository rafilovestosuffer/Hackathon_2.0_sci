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
| Source institutions | Faridpur Medical College Hospital (FMCH), via SkinDiseaseBD; Rangpur & Kishoreganj Medical College Hospitals, via SkinDisNet |
| Country | Bangladesh |
| Classes | Research dataset: 7 (adds Vitiligo). Live checkpoint: 6 — Atopic Dermatitis, Contact Dermatitis, Eczema, Scabies, Seborrheic Dermatitis, Tinea |
| Age range | Adults ≥18 |
| Skin tone | Predominantly Fitzpatrick IV–VI (South Asian) |
| Sex | Both, approximately representative of the presenting clinic populations |

---

## Collection process

Photographs were captured by attending clinicians or trained assistants at the point of care, using standard smartphone cameras under hospital lighting. Each image was labelled by the diagnosing physician. No social-media scraping, no DermNet content.

**Synthetic augmentation.** After the 70/15/15 split of the 3,322 real images, Stable Diffusion v1.5 (img2img, DDIM 20 steps, guidance 7.5, strength 0.45) generated 1,039 images for three minority classes (Atopic Dermatitis, Seborrheic Dermatitis, Vitiligo) — **from training-split images only**. Validation and test sets contain real images only. FID 28.9–37.8 (details in the BD_SkinNet repo).

**Split unit.** The split is stratified by image, not by patient; no near-duplicate removal was applied.

---

## Preprocessing

- Resized to 224 × 224
- Standard ImageNet normalisation
- Train-time augmentation: horizontal flip, mild rotation, colour jitter
- Optional inference-time enhancement: CLAHE (low light) + unsharp mask (mild blur) applied automatically when the input fails a Laplacian-variance sharpness check

---

## Distribution

The trained checkpoint (`bd_skinnet_int8.pth`) is published on Hugging Face Hub at `rafilovestosuffer/bd-skinnet`. The training images come from two published datasets — SkinDiseaseBD (Faridpur MCH) and SkinDisNet (Rangpur & Kishoreganj MCH; Mendeley Data, DOI 10.17632/yj3md44hxg.2). This repository does not redistribute them; obtain them from the publishers under their terms.

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

This project did not collect any images. Patient consent and ethics procedures are those documented by the dataset publishers. No personally identifying metadata (name, MRN, geolocation) is used in training or associated with the published checkpoint.
