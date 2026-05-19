# TASK — Jun 1, 2026 | Week 3 / Day 16

## TODAY'S GOAL
1. RAG chatbot — context-aware (pass current diagnosis into system prompt)
2. scripts/keepalive.py — ping HF Space every 20 min (CONSTRAINT 7)
3. Demo mode — pre-loaded Scabies Tier 3 sample for judges

## CONTEXT
- Day 15 complete: map/hospital_finder.py + 17 tests, wired into app.py Tier 3
- Full suite: 150/150 passing
- BD-SkinNet checkpoint still pending (~Jun 2) — _run_model() placeholder active
- Do NOT touch today: model/, severity/, voice/, rag/retriever.py, pdf_gen/, ui/

---

## CHECKPOINT INTEGRATION (when bd_skinnet_best.pth arrives ~Jun 2)
File: app.py — replace body of _run_model(pil_img)
```python
# 1. Load model (cached)
from model.bd_skinnet import BDSkinNet
from model.gradcam import compute_gradcam
import torch, torchvision.transforms as T

CKPT = "model/checkpoints/bd_skinnet_best.pth"

@st.cache_resource
def _load_bd_skinnet():
    model = BDSkinNet(num_classes=7)
    model.load_state_dict(torch.load(CKPT, map_location="cpu"))
    model.eval()
    return torch.quantization.quantize_dynamic(model, {torch.nn.Linear}, dtype=torch.qint8)

# 2. In _run_model():
model = _load_bd_skinnet()
tfm = T.Compose([T.Resize((224,224)), T.ToTensor(),
                 T.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])])
tensor = tfm(pil_img).unsqueeze(0)
with torch.no_grad():
    probs = torch.softmax(model(tensor), dim=1)[0].tolist()
from model.disease_labels import CLASS_NAMES
indexed = sorted(enumerate(probs), key=lambda x: -x[1])
top2 = [{"disease": CLASS_NAMES[i], "confidence": p} for i, p in indexed[:2]]
gc = compute_gradcam(model, tensor)
return {"disease": top2[0]["disease"], "confidence": top2[0]["confidence"],
        "top2": top2, "heatmap": gc["overlay"], "coverage_pct": gc["coverage_pct"]}
```

---

## TASKS (in order)

### TASK 1 — RAG context awareness
In app.py Tab 2, pass the current diagnosis as context to the RAG answer:
- If st.session_state.prediction exists, prepend disease context to the question
- Show banner: "💊 Current diagnosis: Tinea — asking in this context"
- Update answer_question() call: include disease in the question string if known

### TASK 2 — scripts/keepalive.py
Write scripts/keepalive.py:
```python
# Ping HF Space every 20 min to prevent sleeping (CONSTRAINT 7 — app live until Jul 12)
# Usage: python scripts/keepalive.py
# Or via GitHub Actions cron (add .github/workflows/keepalive.yml)
import time, requests, os
HF_SPACE_URL = "https://rafilovestosuffer-skinai-bangladesh.hf.space"
INTERVAL = 20 * 60  # 20 minutes
def ping():
    try:
        r = requests.get(HF_SPACE_URL, timeout=15)
        print(f"Ping OK — {r.status_code}")
    except Exception as e:
        print(f"Ping failed: {e}")
if __name__ == "__main__":
    while True:
        ping()
        time.sleep(INTERVAL)
```
Also write .github/workflows/keepalive.yml — cron every 20 min.

### TASK 3 — Demo mode
Add a "🎬 Load Demo Case" button in Tab 1 sidebar section:
- Loads: Scabies, 0.38 confidence (→ Tier 3 via Signal 2), coverage_pct=45.0
- Pre-fills session_state so all 3 tabs show demo data without real image/voice
- Label: "🎬 Load Demo (Scabies — Tier 3)"

### TASK 4 — Commit and push
```
git add map/hospital_finder.py tests/test_hospital.py app.py scripts/keepalive.py \
        .github/workflows/keepalive.yml PROGRESS.md TASK.md PLAN.md DECISIONS.md
git commit -m "[w3/d15+16] hospital map + keepalive + demo mode"
git push origin main
```
Push to HF Space via clean branch strategy.

---

## DEFINITION OF DONE
- [ ] Hospital map: Tier 3 → district input → hospital table + Folium map (already done Day 15)
- [ ] RAG chatbot shows current disease context banner
- [ ] scripts/keepalive.py written and works (python scripts/keepalive.py — single ping)
- [ ] GitHub Actions keepalive.yml with cron schedule
- [ ] Demo mode button loads Scabies Tier 3 case instantly
- [ ] All tests still passing
- [ ] Committed and pushed to GitHub + HF Space

---

## NEXT SESSION (Day 17 — Jun 2)
- Checkpoint arrives (~Jun 2) — plug in real BD-SkinNet inference
- Polish UI: loading spinners, error messages, edge cases
- Commit: [w3/d13b] real model inference connected
