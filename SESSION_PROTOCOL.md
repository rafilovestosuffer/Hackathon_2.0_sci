# SkinAI Bangladesh — Daily Claude Code Session Protocol
# Follow this EXACTLY every session. This is how you win.

---

## ⚡ SESSION STARTUP (First 2 minutes — do this before writing any code)

### Step 1: Open Claude Code in your project folder
```bash
cd skinai-bangladesh
claude  # or claude code
```

### Step 2: Paste this EXACT opening prompt every session:
```
Read CLAUDE.md, PROGRESS.md, and TASK.md in order.
Then tell me:
1. What was the last completed task?
2. What is today's TASK.md task?
3. Any blockers from last session?

Then begin working on today's task immediately.
```

### Step 3: Let Claude Code orient itself — do NOT interrupt this
Claude Code will read the 3 files and summarize. If it misses something, correct it.
This 2-minute investment saves 30+ minutes of re-explanation.

---

## 📋 TASK.md FORMAT (Rewrite this every session end for next session)

```markdown
# TASK — [DATE] | Week [N] / Day [N]

## TODAY'S GOAL (one sentence)
[e.g., "Implement the 4-signal severity engine with full test coverage"]

## TASKS (in order)
1. [ ] [Specific task with file path]
2. [ ] [Specific task with file path]
3. [ ] [Specific task with file path]

## CONTEXT
- Last session left off at: [specific line/function/file]
- Known issue to fix first: [if any]
- Do NOT touch today: [files to leave alone]

## DEFINITION OF DONE
- [ ] All tasks checked off
- [ ] Relevant tests pass
- [ ] Git committed
- [ ] PROGRESS.md updated
```

---

## 🧠 HOW TO TALK TO CLAUDE CODE FOR MAXIMUM SPEED

### ✅ DO: Be file-and-function specific
```
"Write the compute_tier() function in severity/engine.py.
It takes: disease_class (str), confidence (float), coverage_pct (float), transcript (str).
Returns: dict with keys tier, urgency_label, action, facility, bengali_text.
Follow the 4-signal logic in CLAUDE.md Section 'SEVERITY ENGINE'."
```

### ❌ DON'T: Be vague
```
"Make the severity engine" ← Claude will make something different every time
```

### ✅ DO: Reference CLAUDE.md sections explicitly
```
"Implement the hospital finder per CLAUDE.md section 'EMERGENCY HOSPITAL MAP'.
Use Overpass API. No API key needed. Save to map/hospital_finder.py."
```

### ✅ DO: Ask for tests alongside code
```
"Write severity/engine.py AND tests/test_severity.py together.
Run the tests at the end. Show me the pytest output."
```

### ✅ DO: Paste real errors
```
"Getting this error: [paste full traceback]
File is at: model/bd_skinnet.py line 47
Fix it and explain what was wrong."
```

---

## 🔁 MID-SESSION: When Claude Code gets lost or confused

### Reset prompt:
```
Stop. Read CLAUDE.md again, specifically the section [NAME].
We are building [specific module]. The constraint is [constraint].
Ignore everything from the last 5 messages. Start fresh from: [specific point].
```

### When Claude drifts toward wrong tech:
```
REMINDER: We use Streamlit (not FastAPI/React for the UI).
We use faiss-cpu (not Pinecone/ChromaDB).
We use google-generativeai for Gemini (not LangChain).
Redo the last step with the correct stack.
```

---

## 📊 SESSION END (Last 5 minutes — MANDATORY)

### Step 1: Commit everything
```bash
git add -A
git status  # verify what's being committed
git commit -m "[w1/d3] GradCAM++ implementation + coverage tests — all passing"
git push origin main
```

### Step 2: Prompt Claude Code to update PROGRESS.md
```
Update PROGRESS.md with:
- What we completed today
- Any blockers or TODOs
- The exact line/function to start from next session
- Check off completed modules in the checklist
```

### Step 3: Prompt Claude Code to write next TASK.md
```
Write tomorrow's TASK.md based on PLAN.md Day [N+1].
Be specific about file paths and function names.
```

### Step 4: Verify HF Spaces (every 3 days minimum)
```bash
curl -I https://huggingface.co/spaces/[username]/skinai-bangladesh
# Should return 200 OK
```

---

## 🚨 EMERGENCY PROTOCOLS

### "HF Space is sleeping":
1. Visit the URL in browser — click anywhere to wake it
2. Long-term: GitHub Actions keepalive (see scripts/keepalive.py)

### "Claude Code is writing something completely wrong":
1. Stop it immediately (Ctrl+C)
2. Type: "Stop. Read CLAUDE.md constraint [NUMBER] again. This violates it."
3. Restate the constraint explicitly
4. Ask it to start over for that function only

### "I broke something that was working":
```bash
git log --oneline -10  # find last good commit
git stash              # save current broken work
git checkout [hash]    # test old version
git stash pop          # bring back current work
```

### "Running out of context / Claude Code getting confused":
1. Start a NEW Claude Code session
2. Open with: "Read CLAUDE.md, PROGRESS.md, and TASK.md."
3. Fresh context = fresh performance

---

## 📅 WEEKLY RHYTHM

| Day | Focus |
|-----|-------|
| Monday | Heavy coding — most important module of the week |
| Tuesday | Continue heavy coding |
| Wednesday | Integration — connect this week's module to existing code |
| Thursday | Testing + bug fixing |
| Friday | Deploy to HF Spaces + document |
| Saturday | Review + write next week's PLAN |
| Sunday | Light — only documentation or README updates |

---

## 🎯 TOKEN OPTIMIZATION RULES

These rules keep Claude Code efficient and avoid wasted context:

1. **CLAUDE.md is always loaded first** — no re-explaining the project
2. **TASK.md is specific** — one module at a time, not "build everything"
3. **One file per task** — "write severity/engine.py" not "write all the backend"
4. **Always paste errors** — don't describe errors, paste the full traceback
5. **Use function signatures** — tell Claude the exact function signature you want
6. **Never ask for architecture decisions** in Claude Code — those are in DECISIONS.md already
7. **Reference CLAUDE.md sections** — "per the severity engine spec in CLAUDE.md" is faster than repeating the spec

---

## 📁 FILES CLAUDE CODE MUST KNOW ABOUT

```
Every session: CLAUDE.md + PROGRESS.md + TASK.md
When working on model: model/bd_skinnet.py + model/disease_labels.py
When working on severity: severity/engine.py + tests/test_severity.py
When working on RAG: rag/retriever.py + rag/build_index.py
When working on UI: app.py + ui/components.py
When working on PDF: pdf_gen/referral.py
When working on voice: voice/pipeline.py
```

---
*This protocol is how you ship a championship-grade product in 40 days.*
*Read it. Follow it. Win.*
