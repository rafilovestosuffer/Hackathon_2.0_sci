# TASK — Week 4 / Day 24
# Target date: Jun 9–10, 2026

## STARTING STATE
- Tests: 310/312 passing (2 pre-existing voice mock failures, unrelated to feature work)
- Doctor booking tab: LIVE (Tab 5)
- BD-SkinNet checkpoint: still pending (bd_skinnet_best.pth)
- HF Space: live at https://huggingface.co/spaces/rafilovestosuffer/skinai-bangladesh
- Submission deadline: July 1, 2026

---

## CHECKPOINT INTEGRATION — do this FIRST if bd_skinnet_best.pth has arrived

**Step 1:** Place file at `model/checkpoints/bd_skinnet_best.pth`

**Step 2:** Replace the entire `_run_model` stub in app.py (see previous TASK.md).

**Step 3:** `pytest tests/ -q` — 310+ tests must still pass.

**Step 4:** Commit: `[w4/d24] real BD-SkinNet inference connected`

---

## TASK 1 — Project Report Skeleton

Write an 8-page report in Google Docs or LaTeX with all 8 section headers + 2–3 bullet points per section. Do NOT write final prose yet — this is the skeleton.

Report title: "SkinAI Bangladesh: Multi-Signal AI Triage for Dermatological Care in Rural Bangladesh"

Structure: Title+Abstract | Problem+Related Work | System Architecture | Dataset+Model | Results | Demo+Impact | Limitations+Conclusion

Key numbers to include everywhere:
- F1 = 92.46%, AUC = 0.9937, Accuracy = 92.37%
- 7 disease classes (BD clinical data: Faridpur MCH + Rangpur MCH)
- 310+ tests passing
- 1 derm per 250,000 people in Bangladesh
- Full pipeline: Voice → Image → Triage → Book → Video Call → PDF

---

## TASK 2 — Demo Video

Record 3–5 min Rahim story demo following `docs/demo_script.md`.
Use Demo Mode sidebar (no checkpoint required).
Upload to YouTube (Unlisted) → add link to README.md.

New demo addition: show Tab 5 doctor booking flow:
- Click "🟡 Demo — Eczema (Tier 2)" → go to Tab 5
- Select Tuesday date → pick 06:30 PM slot → enter name + phone → Confirm
- Show green confirmation card + JOIN VIDEO CALL button
- Download PDF → show appointment block in Section 4

---

## TASK 3 — PROGRESS.md + TASK.md update (end of session)

- Log Day 24 entry
- Rewrite TASK.md for Day 25

---

## DEFINITION OF DONE
- [ ] Report skeleton: 8 headers + bullets written
- [ ] Demo video recorded OR explicitly deferred with reason
- [ ] PROGRESS.md updated, TASK.md rewritten for Day 25
- [ ] Committed and pushed to GitHub

---

## NEXT SESSION — Day 25 / Submission Package
- Finalise report (flesh out Architecture + Results sections)
- Model & Data Card PDF
- Final README review
- Keepalive verification
- Submission dry run
