"""
scripts/eval_triage_safety.py — test metrics + triage safety for the LIVE checkpoint.

Runs the served INT8 checkpoint (model/service.py → HF Hub) over a labelled
test set and writes results/triage_safety.json. No thresholds are tuned:
compute_tier() runs exactly as deployed (no voice transcript).

Input: a CSV with columns `filepath,label`, where label uses the app's class
names (Atopic_Dermatitis, Contact_Dermatitis, Eczema, Scabies,
Seborrheic_Dermatitis, Tinea, ...). The images MUST be ones this checkpoint
never saw in training or validation — state where the CSV came from with
--split-note, it is copied into the results file.

Rows whose label the live model cannot output (e.g. Vitiligo) are counted
separately as out-of-scope, and their triage outcome is still reported.

Usage (Kaggle T4 or CPU):
    python scripts/eval_triage_safety.py --csv test.csv --root /kaggle/input/... \
        --split-note "test.csv from <kernel/notebook>, seed 42, real images only"

Metrics written:
  accuracy, macro-F1, per-class precision/recall/F1 (in-scope rows)
  errors_escalated_pct : of misclassified images, % that the triage engine sent
                         to tier >= 2 because confidence was below 0.60
  under_triage_pct     : % of images whose final tier is below the base tier
                         of their TRUE class (the patient would be sent to a
                         lower level of care than their condition needs)
  latency_ms_median    : CPU/GPU inference time per image on the machine used
"""
from __future__ import annotations

import argparse
import csv
import datetime
import json
import os
import statistics
import sys
import time
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model import service                                   # noqa: E402
from model.disease_labels import get_tier                   # noqa: E402
from severity.engine import CONF_TIER2, compute_tier        # noqa: E402


def _f1(p: float, r: float) -> float:
    return 2 * p * r / (p + r) if (p + r) else 0.0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True, help="filepath,label CSV of held-out images")
    ap.add_argument("--root", default="", help="prefix joined to relative filepaths")
    ap.add_argument("--split-note", required=True,
                    help="where the test list came from and why it is unseen by this checkpoint")
    ap.add_argument("--out", default=os.path.join("results", "triage_safety.json"))
    args = ap.parse_args()

    model = service.get_model()
    if model is None:
        print("model failed to load:", service.load_error())
        return 1
    classes = list(model.class_names)

    with open(args.csv, newline="", encoding="utf-8") as f:
        rows = [(os.path.join(args.root, r["filepath"]), r["label"]) for r in csv.DictReader(f)]

    preds, latencies = [], []
    for path, label in rows:
        with open(path, "rb") as fh:
            data = fh.read()
        t0 = time.perf_counter()
        out = service.run_inference(data)
        latencies.append((time.perf_counter() - t0) * 1000)
        if not out["available"]:
            print("inference failed on", path)
            return 1
        tier = compute_tier(out["disease"], out["confidence"], "")["tier"]
        preds.append({"path": path, "label": label, "pred": out["disease"],
                      "conf": out["confidence"], "tier": tier})

    in_scope = [p for p in preds if p["label"] in classes]
    out_scope = [p for p in preds if p["label"] not in classes]

    per_class = {}
    for c in classes:
        tp = sum(1 for p in in_scope if p["pred"] == c and p["label"] == c)
        fp = sum(1 for p in in_scope if p["pred"] == c and p["label"] != c)
        fn = sum(1 for p in in_scope if p["pred"] != c and p["label"] == c)
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec = tp / (tp + fn) if tp + fn else 0.0
        per_class[c] = {"precision": round(prec, 4), "recall": round(rec, 4),
                        "f1": round(_f1(prec, rec), 4), "support": tp + fn}

    errors = [p for p in in_scope if p["pred"] != p["label"]]
    escalated = [p for p in errors if p["conf"] < CONF_TIER2 and p["tier"] >= 2]
    under = [p for p in preds if p["tier"] < get_tier(p["label"])]

    result = {
        "generated_utc": datetime.datetime.utcnow().isoformat(timespec="seconds"),
        "checkpoint": f"{service.HF_REPO}/{service.HF_FILENAME}",
        "checkpoint_meta": getattr(model, "checkpoint_meta", {}),
        "model_classes": classes,
        "test_csv": os.path.basename(args.csv),
        "split_note": args.split_note,
        "n_images": len(preds),
        "n_in_scope": len(in_scope),
        "n_out_of_scope": len(out_scope),
        "out_of_scope_labels": dict(Counter(p["label"] for p in out_scope)),
        "accuracy": round(sum(1 for p in in_scope if p["pred"] == p["label"]) / len(in_scope), 4)
                    if in_scope else None,
        "macro_f1": round(statistics.mean(v["f1"] for v in per_class.values() if v["support"]), 4)
                    if in_scope else None,
        "per_class": per_class,
        "n_errors": len(errors),
        "errors_escalated_pct": round(100 * len(escalated) / len(errors), 1) if errors else None,
        "under_triage_n": len(under),
        "under_triage_pct": round(100 * len(under) / len(preds), 1) if preds else None,
        "out_of_scope_tier_counts": dict(Counter(p["tier"] for p in out_scope)),
        "latency_ms_median": round(statistics.median(latencies), 1) if latencies else None,
        "thresholds": {"CONF_TIER2": CONF_TIER2},
        "notes": "Triage run without voice transcript (photo-only). No thresholds tuned on this set.",
    }
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(json.dumps({k: result[k] for k in ("n_images", "accuracy", "macro_f1",
                                             "errors_escalated_pct", "under_triage_pct",
                                             "latency_ms_median")}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
