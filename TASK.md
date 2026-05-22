# TASK — Week 4 / Day 24
# Target date: May 22–23, 2026

## STARTING STATE
- Tests: 310/312 passing (2 pre-existing voice mock failures — unrelated to feature work)
- App: 5 tabs live (diagnosis, RAG chatbot, referral PDF, epidemiology map, doctor booking)
- BD-SkinNet checkpoint: still pending (bd_skinnet_best.pth) — _run_model() placeholder active
- HF Space: https://huggingface.co/spaces/rafilovestosuffer/skinai-bangladesh
- Submission deadline: July 1, 2026 (40 days remain)
- Days completed: 23 of 40

---

## PRIORITY 0 — Checkpoint Integration (do this FIRST if bd_skinnet_best.pth has arrived)

**Step 1:** Place file at `model/checkpoints/bd_skinnet_best.pth`

**Step 2:** Replace the entire `_run_model()` stub in `app.py`:
```python
# Replace stub body with:
model = BDSkinNet(num_classes=7)
model.load_state_dict(torch.load("model/checkpoints/bd_skinnet_best.pth", map_location="cpu"))
model = torch.quantization.quantize_dynamic(model, {nn.Linear}, dtype=torch.qint8)
model.eval()
result = compute_gradcam(model, preprocess(image))
probs = result["probs"]
top_class = DISEASE_LABELS[probs.argmax()]
confidence = float(probs.max())
top2 = [(DISEASE_LABELS[i], float(probs[i])) for i in probs.argsort()[-2:][::-1]]
return top_class, confidence, top2
```

**Step 3:** `pytest tests/ -q` — 310+ tests must still pass.

**Step 4:** Commit: `[w4/d24] real BD-SkinNet inference connected`

---

## TASK 1 — Project Report Skeleton

Write an 8-section report skeleton. Target: Google Docs or a Markdown file saved as `docs/report_skeleton.md`. Do NOT write final prose yet — headers + 2–3 bullet points per section.

**Report title:** "SkinAI Bangladesh: Multi-Signal AI Triage for Dermatological Care in Rural Bangladesh"

**Sections:**
1. Title + Abstract
2. Problem Statement (Bangladesh dermatology gap, Rahim story)
3. Related Work (existing tools, why they fail for Bangladesh)
4. System Architecture (pipeline overview, 5-tab app)
5. Dataset + Model (BD-SkinNet, 7 classes, Faridpur/Rangpur MCH)
6. Results (F1=92.46%, AUC=0.9937, triage engine accuracy)
7. Demo + Real-world Impact (1 derm per 250k stat, CHW mode, care loop)
8. Limitations + Conclusion + References

**Key numbers to include everywhere:**
- F1 = 92.46%, AUC = 0.9937, Accuracy = 92.37%
- 7 disease classes — Bangladeshi clinical data only
- 310+ tests passing across 11 test files
- 1 dermatologist per 250,000 people in Bangladesh
- Full pipeline: Voice → Image → Triage → Book → Video Call → PDF

---

## TASK 2 — Demo Video Recording

Record 3–5 min Rahim story demo following `docs/demo_script.md`.
Use the Demo Mode sidebar buttons — no checkpoint required.
Upload to YouTube (Unlisted) → add link to README.md and PROGRESS.md.

**New demo segments to include (not in original script — add them):**
- Show Tab 4 epidemiology map (15 seconds, show division circles)
- Show Tab 5 doctor booking flow:
  1. Click "Demo — Eczema (Tier 2)" sidebar button
  2. Go to Tab 5
  3. Select Tuesday date → pick 06:30 PM slot → enter name + phone
  4. Click Confirm → show green confirmation card + JOIN VIDEO CALL button
  5. Download PDF → show appointment block in Section 4
  6. Show Bengali TTS audio readout button (play it)

**Target timing:** 4–5 minutes total with the extended demo.

---

## TASK 3 — Session End (mandatory)

1. `pytest tests/ -q` — verify no regressions
2. Commit completed work with `[w4/d24]` prefix
3. Update `PROGRESS.md` — Day 24 session log entry
4. Rewrite `TASK.md` for Day 25

---

## DEFINITION OF DONE
- [ ] Checkpoint integrated (if bd_skinnet_best.pth received)
- [ ] Report skeleton written (8 sections, 2–3 bullets each)
- [ ] Demo video recorded OR explicitly deferred with stated reason
- [ ] `pytest tests/ -q` — no new failures
- [ ] Committed and pushed to GitHub
- [ ] PROGRESS.md updated, TASK.md rewritten for Day 25

---

## DAY 25 PREVIEW — Submission Package

- Flesh out Architecture + Results sections of report (from skeleton to full prose)
- Model & Data Card PDF (1 page — dataset, licenses, limitations, ethics)
- Final README review
- Keepalive verification (confirm GitHub Actions cron is firing)
- Submission dry run (open submission form, verify all 5 deliverables ready)
