"""
scripts/verify_numbers.py — print every number the pitch is allowed to use.

Reads results/*.json (written by scripts — never typed by hand) and prints a
claim sheet. Anything without a results file prints as [TBD] and must not
appear in the video, README or submission.

    python scripts/verify_numbers.py
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")


def _load(name: str) -> dict | None:
    path = os.path.join(RES, name)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _fmt(v, suffix="") -> str:
    return "[TBD]" if v is None else f"{v}{suffix}"


def main() -> int:
    tbd = 0

    def line(label, value, source):
        nonlocal tbd
        if value == "[TBD]":
            tbd += 1
        print(f"  {label:<44} {value:<14} {source}")

    print("Model (live checkpoint)")
    s = _load("triage_safety.json") or {}
    src = "results/triage_safety.json" if s else "missing - run scripts/eval_triage_safety.py"
    line("Test images (n)", _fmt(s.get("n_images")), src)
    line("Accuracy", _fmt(s.get("accuracy")), src)
    line("Macro-F1", _fmt(s.get("macro_f1")), src)
    line("Misclassified images escalated (%)", _fmt(s.get("errors_escalated_pct"), "%"), src)
    line("Under-triage (%)", _fmt(s.get("under_triage_pct"), "%"), src)
    line("Median inference latency (ms)", _fmt(s.get("latency_ms_median")), src)
    if s.get("split_note"):
        print(f"  split: {s['split_note']}")

    print("\nField test")
    f = _load("field_test_summary.json") or {}
    src = "results/field_test_summary.json" if f else "missing"
    line("Participants (n)", _fmt(f.get("n_participants")), src)
    line("Completion rate (%)", _fmt(f.get("completion_pct"), "%"), src)
    line("Median time to referral decision (s)", _fmt(f.get("median_seconds_to_decision")), src)
    line("Used offline /lite path (n)", _fmt(f.get("n_offline")), src)
    line("Mean ease rating (1-5)", _fmt(f.get("mean_ease_1to5")), src)

    print("\nDoctor review")
    d = _load("doctor_review_summary.json") or {}
    src = "results/doctor_review_summary.json" if d else "missing - export /doctor stats"
    line("Doctors (n)", _fmt(d.get("n_doctors")), src)
    line("Cases reviewed (n)", _fmt(d.get("n_cases")), src)
    line("Tier agreement with AI (%)", _fmt(d.get("tier_agreement_pct"), "%"), src)
    line("Under-triage overrides (n)", _fmt(d.get("under_triage_overrides")), src)

    print("\nLow-bandwidth (/lite)")
    b = _load("lite_bandwidth.json") or {}
    src = "results/lite_bandwidth.json" if b else "missing"
    line("Median upload size (KB)", _fmt(b.get("median_upload_kb")), src)
    line("Upload time on Slow 3G profile (s)", _fmt(b.get("slow3g_upload_seconds")), src)

    print(f"\n{tbd} number(s) still [TBD] - keep them out of the pitch.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
