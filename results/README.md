# results/

Every number used in the pitch, README or submission comes from a JSON file in this folder, written by a script or exported from the app — never typed by hand. `python scripts/verify_numbers.py` prints them all; missing ones show as [TBD].

| File | Written by |
|---|---|
| `triage_safety.json` | `scripts/eval_triage_safety.py` (live checkpoint on a held-out test list) |
| `field_test_summary.json` | field-test sheet export (n_participants, completion_pct, median_seconds_to_decision, n_offline, mean_ease_1to5) |
| `doctor_review_summary.json` | `/doctor` stats export (n_doctors, n_cases, tier_agreement_pct, under_triage_overrides) |
| `lite_bandwidth.json` | `/lite` measurement (median_upload_kb, slow3g_upload_seconds) |
