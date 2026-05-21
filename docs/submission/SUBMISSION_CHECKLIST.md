# SkinAI Bangladesh — Submission Checklist
# SciBlitz AI Challenge 2026 · IEEE SB CUET · Track A: Health & Society
# Deadline: July 1, 2026 — 11:59 PM BST

## Required Deliverables

| Item | Status | Link / Location |
|---|---|---|
| Live public demo URL (no login) | ✅ Live | https://huggingface.co/spaces/rafilovestosuffer/skinai-bangladesh |
| GitHub repository with commits May 14–July 1 | ✅ Active | https://github.com/rafilovestosuffer/Hackathon_2.0_sci |
| Demo video (3–5 min, YouTube unlisted) | ⏳ Record | Use sidebar Demo Mode buttons — script in `docs/demo_script.md` |
| Project report (6–8 pages) | ⏳ Write | Template in TASK.md lines 53–100; save as `docs/submission/REPORT.pdf` |
| Team information | ✅ | Rafiur Rahman — mdrafiurrahman123098@gmail.com |

## Constraint Compliance

| Constraint | Verified | Evidence |
|---|---|---|
| No DermNet data | ✅ | `rag/knowledge/` sources are CDC/NIH/WHO/DGHS only |
| No login required | ✅ | HF Space is fully public |
| No medicine recommendations | ✅ | `rag/retriever._redact_medicine_names()` + prompt guard |
| No persistent database | ✅ | `st.session_state` only |
| Knowledge base = CDC/NIH/WHO/DGHS | ✅ | All 100 knowledge chunks verified |
| INT8 quantization | ✅ | `model/export_int8.py` ready; checkpoint pending |
| App live until July 12, 2026 | ✅ | `scripts/keepalive.py` + GitHub Actions cron |
| GitHub commits in window | ✅ | Commits from 2026-05-19 onwards |
| Demo video 3–5 min | ⏳ | To record |

## Judging Rubric Self-Assessment

| Criterion | Weight | Our Strengths |
|---|---|---|
| Innovation & Originality | 25% | First BD-specific clinical model, multi-signal triage, Bengali voice, hard medicine guardrail |
| Technical Implementation | 25% | Swin+CBAM+GradCAM++, RAG with BM25+FAISS, INT8 quantization, 245 tests |
| Real-world Impact | 20% | 1 derm/250k stat, Rahim narrative, zero quacks pathway |
| Demo Quality | 20% | 3 demo presets, no login, instant PDF, hospital map, bilingual UI |
| Presentation | 10% | Rahim story → data → live demo → Q&A — 5 min slot script ready |

## Final Steps Before July 1

1. [ ] Download `bd_skinnet_best.pth` from Kaggle → `model/checkpoints/` → wire `_run_model` (TASK.md:14)
2. [ ] Record 3–5 min demo video following `docs/demo_script.md`
3. [ ] Upload video to YouTube (unlisted) → paste link in README + submission form
4. [ ] Write `docs/submission/REPORT.pdf` (use TASK.md skeleton)
5. [ ] Run `pytest tests/ -q` → confirm all tests pass
6. [ ] Push final commit: `[w6/d42] submission-ready: all features live`
7. [ ] Verify HF Space loads in incognito, on mobile, within 5 s
8. [ ] Submit on SciBlitz platform before 11:59 PM BST July 1

## Presentation Day (July 10, CUET)

- Open: Rahim story (30 s voiceover — CLAUDE.md impact narrative)
- Live demo: Demo Tier 3 → PDF download → hospital map
- Data slide: F1=92.46%, AUC=0.9937, 1 derm/250k
- Close: "Right patient → Right doctor → Right time"
- Q&A prep: Why CBAM? Why 4 signals? Why Bengali voice? Why no medicine recs?
