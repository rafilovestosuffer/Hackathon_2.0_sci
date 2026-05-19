# TASK — May 22, 2026 | Week 1 / Day 5

## TODAY'S GOAL
Deploy SkinAI Bangladesh to Hugging Face Spaces as a live, publicly accessible
skeleton — zero login, instant load, Bengali UI visible — and record the public URL.

## CONTEXT
- Day 4 complete: severity/engine.py + tests/test_severity.py (29/29 passing)
- packages.txt already has: libsndfile1, ffmpeg ✓
- app.py is a minimal 3-line placeholder — needs a real skeleton today
- HF Space does NOT exist yet — you must create it manually (Step 0 below)
- Do NOT touch today: model/, severity/, voice/, rag/

---

## TASKS (in order)

### STEP 0 — Create HF Space manually (you do this, not Claude)
1. Go to https://huggingface.co/spaces → click "Create new Space"
2. Settings:
   - Space name: `skinai-bangladesh`
   - SDK: **Streamlit**
   - Python version: **3.10**
   - Hardware: **CPU Basic (free)**
   - Visibility: **Public**
3. Click "Create Space" — it will show an empty repo
4. Copy the git remote URL shown on the Space page
   (format: `https://huggingface.co/spaces/<your-username>/skinai-bangladesh`)
5. Add the remote locally:
   ```
   git remote add hf https://huggingface.co/spaces/<your-username>/skinai-bangladesh
   ```

---

### STEP 1 — Upgrade app.py to proper skeleton
- [ ] Replace current placeholder app.py with a full Bengali-tabbed skeleton:
  - `st.set_page_config` — title, icon, wide layout
  - Sidebar: project name, team, competition name, disclaimer (Bengali)
  - 3 tabs in Bengali:
    - Tab 1 "রোগ নির্ণয়" — voice + image placeholders (st.info coming soon)
    - Tab 2 "প্রশ্ন করুন" — RAG chatbot placeholder
    - Tab 3 "রেফারেল পত্র" — PDF download placeholder
  - st.info banner: "পরীক্ষামূলক সংস্করণ — সম্পূর্ণ সিস্টেম শীঘ্রই আসছে"
  - Footer: "Not a medical device. Always consult a licensed physician."

### STEP 2 — Verify requirements.txt is HF-compatible
- [ ] Check requirements.txt — confirm no GPU-only packages
- [ ] Confirm `torch` line does NOT have `+cu118` or CUDA suffix
  (HF CPU Spaces need CPU-only torch — use torch>=2.0.0 with no CUDA suffix)
- [ ] If needed, add this line at the top of requirements.txt:
  `--extra-index-url https://download.pytorch.org/whl/cpu`

### STEP 3 — Push to HF Space
- [ ] Push GitHub repo to HF Space remote:
  ```
  git push hf main
  ```
- [ ] Watch build logs on the HF Space page
- [ ] Wait for "Running" green badge (usually 3–8 minutes for first build)

### STEP 4 — Verify public URL
- [ ] Open the Space URL in an incognito window (no HF login)
- [ ] Confirm: page loads, Bengali tabs visible, no errors
- [ ] Confirm: no login prompt, instant access
- [ ] Screenshot or note the exact public URL

### STEP 5 — Record URL and commit
- [ ] Add public URL to PROGRESS.md:
  `HF Spaces URL: https://huggingface.co/spaces/<username>/skinai-bangladesh`
- [ ] Commit to GitHub:
  ```
  git commit -m "[w1/d5] HF Spaces deployed — public URL live"
  git push origin main
  ```
- [ ] Also push updated code to HF Space:
  ```
  git push hf main
  ```

---

## DEFINITION OF DONE
- [ ] HF Space shows "Running" (green) — not "Building" or "Error"
- [ ] Public URL opens with zero login in incognito browser
- [ ] Bengali tabs visible: রোগ নির্ণয় | প্রশ্ন করুন | রেফারেল পত্র
- [ ] No Python errors or import crashes in build logs
- [ ] Public URL recorded in PROGRESS.md
- [ ] Committed and pushed to both GitHub AND HF Space remote

---

## KNOWN RISK: Build failures on HF Spaces
If the build fails, most likely causes (check logs):
1. **torch CUDA suffix** → remove `+cu118`, use `--extra-index-url` for CPU wheel
2. **faster-whisper** → needs ffmpeg (already in packages.txt) ✓
3. **sentence-transformers** → may try to download model on import → add
   `@st.cache_resource` wrapping or defer imports to inside functions
4. **Memory limit** → CPU Basic = 16GB RAM — fine for skeleton, avoid loading
   model or FAISS index at startup today

For the skeleton today, none of these heavy imports should be triggered.
app.py should import ONLY streamlit. Do NOT import model/, voice/, rag/ in app.py yet.

---

## NEXT SESSION (Day 6 — May 23)
- Write pdf_gen/referral.py — 4-section reportlab PDF
- Write tests/test_pdf.py — smoke test
- Test Bengali font rendering (Noto Sans Bengali via reportlab)
