# TASK — May 31, 2026 | Week 2 / Day 14

## TODAY'S GOAL
W2 integration test — full E2E smoke test on HF Space.
Fix any bugs found. Day 14 is validation + polish, not new features.

## CONTEXT
- Day 13 complete: app.py fully wired — 3 tabs, all components, RAG, PDF
- 133/133 tests passing
- BD-SkinNet checkpoint NOT yet received (ETA ~Jun 2)
  _run_model() in app.py is a clean placeholder — real inference drops in when checkpoint arrives
- Do NOT touch today: any module except app.py bug fixes

---

## CHECKPOINT INTEGRATION NOTE (when bd_skinnet_best.pth arrives)
File to edit: app.py — function _run_model(pil_img)
Replace the body with real BD-SkinNet + GradCAM forward pass:
- Load model via BDSkinNet(num_classes=7) + torch.load(CKPT, map_location="cpu")
- Apply INT8 quantization: torch.quantization.quantize_dynamic(model, {torch.nn.Linear})
- Run compute_gradcam(model, tensor) for heatmap + coverage_pct
- Return same dict: {disease, confidence, top2, heatmap, coverage_pct}

---

## TASKS (in order)

### TASK 1 — Deploy to HF Space and smoke test
- Push Day 13 code to HF Space (clean branch strategy)
- Open HF Space public URL: https://huggingface.co/spaces/rafilovestosuffer/skinai-bangladesh
- Check: sidebar loads with dark theme and Bengali text
- Check: all 3 tabs render without error
- Check: Tab 2 RAG question returns an answer (needs GEMINI_API_KEY in HF secrets)
- Check: Tab 3 shows "complete Tab 1 first" message correctly

### TASK 2 — Fix any bugs found
- List bugs, fix them, re-test

### TASK 3 — W2 sign-off
- All modules done: voice, RAG, severity, PDF, UI, app.py
- Remaining: model checkpoint (external, ~Jun 2), hospital map (Week 3)
- Update PROGRESS.md for W2 completion

### TASK 4 — Commit and push
```
git add app.py PROGRESS.md TASK.md PLAN.md
git commit -m "[w2/d14] W2 integration test + HF Space verified"
git push origin main
```

---

## DEFINITION OF DONE
- [ ] HF Space loads without error at public URL
- [ ] Sidebar: dark theme, Bengali text visible
- [ ] Tab 1: image upload shows disease card + triage badge (placeholder model)
- [ ] Tab 2: RAG question returns styled answer
- [ ] Tab 3: "complete Tab 1 first" message before diagnosis
- [ ] W2 marked complete in PROGRESS.md
- [ ] Committed and pushed

---

## NEXT SESSION (Day 15 — Jun 1)
- Write map/hospital_finder.py — Overpass API, top 5 nearest hospitals, Folium map
- Wire into Tab 1: show map only when tier == 3
- Inject hospital[0] into PDF Section 4
- Commit: [w3/d15] emergency hospital map
