# TASK — May 21, 2026 | Week 1 / Day 4

## TODAY'S GOAL
Build the 4-signal severity triage engine and write full test coverage for all signals and edge cases.

## TASKS (in order)
1. [ ] Write severity/engine.py — compute_tier(disease_class, confidence, coverage_pct, transcript) → dict
2. [ ] Implement all 4 signals exactly per CLAUDE.md spec:
       - Signal 1: DISEASE_TIER lookup from model.disease_labels (7 real classes)
       - Signal 2: confidence < 0.40 → tier 3 | confidence < 0.60 → max(tier, 2)
       - Signal 3: coverage_pct > 40.0 → min(tier + 1, 3)
       - Signal 4: ESCALATION_KEYWORDS ["জ্বর","ছড়িয়ে","ব্যথা","রক্ত"] → min(tier + 1, 3)
3. [ ] Return dict: {tier, urgency_label, action, facility, bengali_text}
4. [ ] Write tests/test_severity.py — cover every signal and edge case:
       - Tinea + high confidence + low coverage + no keywords → Tier 1
       - Scabies + high confidence + low coverage + no keywords → Tier 2
       - Any class + confidence 0.35 → Tier 3 (Signal 2)
       - Tier 1 class + coverage_pct 45.0 → escalates to Tier 2 (Signal 3)
       - Tier 2 class + "জ্বর" in transcript → escalates to Tier 3 (Signal 4)
       - Tier 2 class + coverage 45% + keyword → Tier 3 (combined escalation, cap at 3)
       - tier never exceeds 3 (cap test)
       - unknown class defaults to Tier 2
5. [ ] Run: pytest tests/test_severity.py -v — all tests must pass
6. [ ] git commit -m "[w1/d4] multi-signal severity engine + full test suite"
7. [ ] git push origin main

## CONTEXT
- Last session left off at: Day 3 complete — gradcam.py + test_gradcam.py pushed
- DISEASE_TIER is already defined in model/disease_labels.py — import from there, do NOT redefine
- TIER_ACTIONS labels/text/Bengali are in CLAUDE.md severity section — copy exactly
- Do NOT touch today: model/, voice/, rag/, app.py

## DEFINITION OF DONE
- [ ] severity/engine.py has compute_tier() returning all required keys
- [ ] All test cases in tests/test_severity.py pass with pytest -v
- [ ] Tier cap at 3 confirmed by test
- [ ] Git committed and pushed
- [ ] PROGRESS.md updated
