# TASK — May 24, 2026 | Week 1 / Day 7

## TODAY'S GOAL
Week 1 review day — run the full test suite, verify the HF Space is live and
rebuilding correctly with the Dockerfile, and write the Week 2 TASK.md so the
next session can start coding immediately.

## CONTEXT
- Day 6 complete: pdf_gen/referral.py + tests/test_pdf.py (11/11 passing)
- Total tests so far: test_gradcam (13) + test_severity (29) + test_pdf (11) = 53
- HF Space: font now downloaded via Dockerfile wget — Space is rebuilding
- Do NOT start any new feature code today — this is review + prep only

---

## TASKS (in order)

### TASK 1 — Run full test suite
```
pytest tests/ -v
```
- [ ] All 53 tests must pass (test_gradcam + test_severity + test_pdf)
- [ ] If any test fails — fix it before moving on
- [ ] Screenshot or copy the final pytest summary line

### TASK 2 — Verify HF Space
- [ ] Open https://huggingface.co/spaces/rafilovestosuffer/skinai-bangladesh in incognito
- [ ] Confirm green "Running" badge
- [ ] Confirm Bengali tabs visible: রোগ নির্ণয় | প্রশ্ন করুন | রেফারেল পত্র
- [ ] Confirm no login prompt
- [ ] Check build logs — confirm font wget line ran without error

### TASK 3 — W1 completion checklist
Tick off every item below — if anything is missing, fix it now:
- [ ] model/bd_skinnet.py — Swin+CBAM architecture ✓
- [ ] model/gradcam.py — GradCAM++ wrapper ✓
- [ ] model/disease_labels.py — 7 classes + Bengali names + tiers ✓
- [ ] model/export_int8.py — INT8 quantization script ✓
- [ ] severity/engine.py — 4-signal triage engine ✓
- [ ] pdf_gen/referral.py — 4-section referral letter ✓
- [ ] app.py — Bengali 3-tab skeleton ✓
- [ ] Dockerfile — Docker build for HF Space ✓
- [ ] tests/test_gradcam.py — 13 tests ✓
- [ ] tests/test_severity.py — 29 tests ✓
- [ ] tests/test_pdf.py — 11 tests ✓
- [ ] HF Space live at public URL ✓
- [ ] GitHub commits from May 18–24 ✓

### TASK 4 — Write TASK.md for Week 2 Day 8
Week 2 starts with voice transcription (Day 8 — May 25).
Rewrite TASK.md for Day 8 based on PLAN.md:
- faster-whisper Bengali transcription
- transcribe_audio(audio_bytes) → str
- Handle mp3/wav/webm formats

### TASK 5 — Final commit
```
git add TASK.md PROGRESS.md
git commit -m "[w1/d7] W1 review complete — all tests green, Week 2 ready"
git push origin main
```

---

## DEFINITION OF DONE
- [ ] pytest tests/ -v → 53/53 passed
- [ ] HF Space green and Bengali UI visible in incognito
- [ ] PROGRESS.md updated with Day 7 session log
- [ ] TASK.md rewritten for Day 8
- [ ] Committed and pushed

---

## W1 MILESTONE SUMMARY (for PROGRESS.md)
```
Week 1 complete:
  Model      ✓  Swin-B + CBAM, 7 classes, INT8 export
  GradCAM    ✓  GradCAM++ wrapper, coverage_pct computation
  Severity   ✓  4-signal triage engine, all edge cases tested
  HF Space   ✓  Live public URL, Bengali skeleton UI, Dockerfile
  PDF        ✓  4-section referral letter, Bengali font, all tiers
  Tests      ✓  53 total — 13 + 29 + 11 — all passing
```

---

## NEXT SESSION (Day 8 — May 25) PREVIEW
Week 2 begins — voice pipeline:
- Write voice/pipeline.py — faster-whisper (base model, Bengali language)
- Implement transcribe_audio(audio_bytes) → str
- Handle mp3/wav/webm (Streamlit mic recorder output formats)
- Test with a sample Bengali audio clip
- Commit: [w2/d8] faster-whisper Bengali transcription
