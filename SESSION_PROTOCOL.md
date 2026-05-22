# SkinAI Bangladesh — Claude Code Session Protocol
# Follow this exactly every session.

---

## SESSION STARTUP (First 2 minutes — do this before writing any code)

### Step 1: Open Claude Code in your project folder
```bash
cd Hackathon_2.0_sci
claude
```

### Step 2: Paste this exact opening prompt every session:
```
Read CLAUDE.md, PROGRESS.md, and TASK.md in order.
Then tell me:
1. What was the last completed task?
2. What is today's TASK.md task?
3. Any blockers from last session?

Then begin working on today's task immediately.
```

### Step 3: Let Claude Code orient itself — do NOT interrupt
Claude Code will read the 3 files and summarise. If it misses something, correct it.
This 2-minute investment saves 30+ minutes of re-explanation.

---

## TASK.md FORMAT (Rewrite at every session end for next session)

```markdown
# TASK — Week [N] / Day [N]
# Target date: [DATE]

## STARTING STATE
- Tests: [N]/[N] passing
- HF Space: live at [URL]
- BD-SkinNet checkpoint: [pending / connected]

## TASK [N] — [Name]
[Specific tasks with file paths]

## DEFINITION OF DONE
- [ ] All tasks checked off
- [ ] pytest tests/ -q passes with no new failures
- [ ] Committed and pushed to GitHub
- [ ] PROGRESS.md updated, TASK.md rewritten for next session
```

---

## HOW TO PROMPT CLAUDE CODE EFFECTIVELY

### DO: Be file-and-function specific
```
"Write the compute_tier() function in severity/engine.py.
It takes: disease_class (str), confidence (float), coverage_pct (float), transcript (str).
Returns: dict with keys tier, urgency_label, action, facility, bengali_text.
Follow the 4-signal logic in CLAUDE.md Section 'SEVERITY ENGINE'."
```

### DON'T: Be vague
```
"Make the severity engine"  ← produces different output every time
```

### DO: Reference CLAUDE.md sections explicitly
```
"Implement the hospital finder per CLAUDE.md section 'EMERGENCY HOSPITAL MAP'.
Use Overpass API. No API key needed. Save to map/hospital_finder.py."
```

### DO: Ask for tests alongside code
```
"Write severity/engine.py AND tests/test_severity.py together.
Run the tests at the end. Show me the pytest output."
```

### DO: Paste real errors in full
```
"Getting this error: [paste full traceback]
File is at: model/bd_skinnet.py line 47
Fix it and explain what was wrong."
```

---

## MID-SESSION: When Claude Code gets lost

### Reset prompt:
```
Stop. Read CLAUDE.md again, specifically the section [NAME].
We are building [specific module]. The constraint is [constraint].
Ignore everything from the last 5 messages. Start fresh from: [specific point].
```

### When Claude uses wrong technology:
```
REMINDER — correct tech stack for this project:
- UI: Streamlit (NOT FastAPI / React)
- Vector store: faiss-cpu (NOT Pinecone / ChromaDB)
- LLM API: google-genai SDK with from google import genai (NOT google-generativeai, NOT LangChain)
- PDF: fpdf2 + uharfbuzz (NOT reportlab)
- Embeddings: sentence-transformers paraphrase-multilingual-MiniLM-L6-v2
- Mic recording: streamlit-mic-recorder (NOT st.audio_input — unreliable on HTTP)

Redo the last step with the correct stack.
```

---

## SESSION END (Last 5 minutes — MANDATORY)

### Step 1: Run tests
```bash
pytest tests/ -q
# 310+ must pass. Investigate any new failures before committing.
```

### Step 2: Commit specific files (never git add -A blindly)
```bash
git status
git add path/to/changed/file.py path/to/other/file.py
git commit -m "[wX/dY] descriptive message"
git push -u origin <branch>
```

### Step 3: Prompt Claude Code to update PROGRESS.md
```
Update PROGRESS.md with:
- What we completed today (specific files and functions)
- Any blockers or known issues
- The exact line/function to start from next session
- Check off completed modules in the checklist
```

### Step 4: Prompt Claude Code to write next TASK.md
```
Write tomorrow's TASK.md based on PLAN.md Day [N+1].
Be specific about file paths and function names.
Include the current test count in STARTING STATE.
```

### Step 5: Verify HF Spaces (every 3 days minimum)
```bash
curl -I https://huggingface.co/spaces/rafilovestosuffer/skinai-bangladesh
# Should return HTTP 200
```

---

## EMERGENCY PROTOCOLS

### "HF Space is sleeping":
1. Visit the URL in browser — click anywhere to wake it
2. Long-term: GitHub Actions keepalive is active (scripts/keepalive.py + .github/workflows/keepalive.yml)

### "Claude Code is writing something wrong":
1. Stop immediately (Ctrl+C)
2. "Stop. Read CLAUDE.md constraint [NUMBER] again. This violates it."
3. Restate the constraint explicitly
4. "Start over for that function only."

### "I broke something that was working":
```bash
git log --oneline -10         # find last good commit
git stash                     # save current broken work
git checkout [hash] -- path/to/file.py   # restore specific file
git stash pop                 # bring back other current work
```

### "Running out of context / Claude Code getting confused":
1. Start a new Claude Code session
2. Open with: "Read CLAUDE.md, PROGRESS.md, and TASK.md."
3. Fresh context = fresh performance

---

## WEEKLY RHYTHM

| Day | Focus |
|-----|-------|
| Monday | Heavy coding — most important module of the week |
| Tuesday | Continue heavy coding |
| Wednesday | Integration — connect this week's module to existing code |
| Thursday | Testing + bug fixing |
| Friday | Deploy to HF Spaces + document |
| Saturday | Review + write next week's PLAN |
| Sunday | Light — documentation or README only |

---

## FILES CLAUDE CODE MUST KNOW ABOUT

```
Every session:        CLAUDE.md + PROGRESS.md + TASK.md
Model work:           model/bd_skinnet.py + model/disease_labels.py + model/gradcam.py
Severity/triage:      severity/engine.py + tests/test_severity.py
RAG pipeline:         rag/retriever.py + rag/build_index.py + rag/knowledge/
UI components:        app.py + ui/components.py + ui/styles.py
Doctor booking:       ui/doctor_booking.py + ui/consultation_room.py
PDF generation:       pdf_gen/referral.py + pdf_gen/consultation_summary.py
Voice pipeline:       voice/pipeline.py
Epidemiology map:     map/bd_heatmap.py
Hospital finder:      map/hospital_finder.py
Keepalive:            scripts/keepalive.py + .github/workflows/keepalive.yml
```

---

## TOKEN OPTIMISATION RULES

1. **CLAUDE.md is always loaded first** — no re-explaining the project
2. **TASK.md is specific** — one module at a time, not "build everything"
3. **One file per task** — "write severity/engine.py" not "write all the backend"
4. **Always paste errors** — don't describe errors, paste the full traceback
5. **Use function signatures** — tell Claude the exact function signature you want
6. **Never ask for architecture decisions in-session** — those are in DECISIONS.md
7. **Reference CLAUDE.md sections** — "per the severity engine spec in CLAUDE.md" is faster than repeating the spec

---

*This protocol is how you ship a championship-grade product in 40 days.*
