"""
pages/doctor.py — Doctor Queue (clinician in the loop)
Accessible at: {hf_spaces_url}/doctor

A licensed clinician reviews consented cases from the web app, Telegram and
the offline /lite page: confirm or override the AI's class and tier, add a
note. Every decision goes to the audit log; Telegram patients get the
decision pushed to them. Urgent (tier 3) patients were already told to go
today, so review never delays urgent care.
"""

import datetime
import hmac
import os

import streamlit as st

from cases import store
from cases.notify import notify_patient
from model.disease_labels import CLASS_NAMES, get_bengali, get_tier

st.set_page_config(
    page_title="SkinAI — Doctor Queue",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

_TIER_LABEL = {0: "Tier 0 · Healthy", 1: "Tier 1 · Non-urgent",
               2: "Tier 2 · Routine", 3: "Tier 3 · Urgent"}
_TIER_ICON = {0: "💚", 1: "🟢", 2: "🟡", 3: "🔴"}

st.title("🩺 Doctor Queue · ডাক্তারের পর্যালোচনা")
st.caption("Clinician review of consented SkinAI cases — confirm or override the AI. "
           "Cases hold no name or phone and are deleted after 7 days.")

# --- PIN gate ---
_pin = os.environ.get("DOCTOR_PIN", "")
if not _pin:
    st.error("Doctor access is not configured on this server (DOCTOR_PIN is not set).")
    st.stop()
if not st.session_state.get("doctor_ok"):
    with st.form("pin_form"):
        entered = st.text_input("Doctor PIN", type="password")
        if st.form_submit_button("Enter"):
            if hmac.compare_digest(entered.strip(), _pin):
                st.session_state.doctor_ok = True
                st.rerun()
            else:
                st.error("Wrong PIN.")
    st.stop()

st.warning("🔴 Tier-3 patients have already been told to go to a facility today — "
           "review audits and corrects; it never delays urgent care.  ·  "
           "জরুরি রোগীদের আগেই আজ যেতে বলা হয়েছে।")

# --- Live KPIs ---
stats = store.get_stats()
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Pending", stats["pending"])
c2.metric("Reviewed", stats["reviewed"])
c3.metric("Tier agreement",
          "—" if stats["tier_agreement"] is None else f"{stats['tier_agreement']:.0%}")
c4.metric("Overrides", stats["overrides"])
c5.metric("Under-triage caught", stats["under_triage"],
          help="Cases where the doctor raised the AI's tier.")

view = st.radio("Show", ["Pending", "Reviewed", "All"], horizontal=True)
status = {"Pending": "pending", "All": None}.get(view)
cases = store.list_cases(status)
if view == "Reviewed":
    cases = [c for c in cases if c["status"] != "pending"]

if not cases:
    st.info("No cases here yet." if view != "Pending" else "No cases waiting for review.")


def _age(ts: str) -> str:
    try:
        delta = datetime.datetime.utcnow() - datetime.datetime.fromisoformat(ts)
    except ValueError:
        return ts
    mins = int(delta.total_seconds() // 60)
    if mins < 60:
        return f"{mins} min ago"
    if mins < 60 * 48:
        return f"{mins // 60} h ago"
    return f"{mins // 1440} days ago"


for case in cases:
    tier = case["ai_tier"]
    title = (f"{_TIER_ICON[tier]} {_TIER_LABEL[tier]} — {case['ai_disease'].replace('_', ' ')} "
             f"({case['ai_conf']:.0%}) · {case['source']} · {case['district'] or '—'} · "
             f"{_age(case['created_ts'])}")
    if case["status"] != "pending":
        title += f"  ✓ {case['status']} → Tier {case['dr_tier']}"
    with st.expander(title, expanded=(case["status"] == "pending" and tier == 3)):
        left, right = st.columns([1, 2], gap="large")
        with left:
            if case["thumb_jpeg"]:
                st.image(case["thumb_jpeg"], caption="Lesion photo (downscaled)",
                         use_container_width=True)
            else:
                st.caption("No photo stored.")
        with right:
            st.markdown(f"**AI:** {case['ai_disease'].replace('_', ' ')} · "
                        f"{get_bengali(case['ai_disease'])} — {case['ai_conf']:.0%} confidence")
            if case["reasons"]:
                st.markdown("**Why this tier:**")
                for r in case["reasons"]:
                    st.markdown(f"- {r.get('en', '')}")
            if case["red_flags"]:
                st.markdown("**Red flags reported:** " + ", ".join(case["red_flags"]))

            if case["status"] != "pending":
                st.success(f"Decision: {case['status']} — "
                           f"{case['dr_disease'].replace('_', ' ')}, Tier {case['dr_tier']}"
                           + (f" · Note: {case['dr_note']}" if case["dr_note"] else ""))
            else:
                with st.form(f"decide_{case['id']}"):
                    choice = st.radio("Decision", ["✓ Confirm AI", "✎ Override"],
                                      horizontal=True, key=f"ch_{case['id']}")
                    idx = CLASS_NAMES.index(case["ai_disease"]) if case["ai_disease"] in CLASS_NAMES else 0
                    disease = st.selectbox(
                        "Condition (used if overriding)", CLASS_NAMES, index=idx,
                        format_func=lambda c: f"{c.replace('_', ' ')} · {get_bengali(c)}",
                        key=f"dz_{case['id']}")
                    new_tier = st.selectbox(
                        "Tier (used if overriding)", [0, 1, 2, 3], index=tier,
                        format_func=lambda t: _TIER_LABEL[t], key=f"tr_{case['id']}",
                        help=f"Base tier for the chosen class: {get_tier(disease)}")
                    note = st.text_input("Note to patient (optional, no medicine names)",
                                         key=f"nt_{case['id']}", max_chars=300)
                    if st.form_submit_button("Save decision", type="primary"):
                        if choice.startswith("✓"):
                            updated = store.decide(case["id"], action="confirmed",
                                                   disease=case["ai_disease"], tier=tier,
                                                   note=note)
                        else:
                            updated = store.decide(case["id"], action="overridden",
                                                   disease=disease, tier=int(new_tier),
                                                   note=note)
                        sent = notify_patient(updated) if updated else False
                        st.session_state["_doctor_toast"] = (
                            "Saved · patient notified on Telegram" if sent else "Saved")
                        st.rerun()

_toast = st.session_state.pop("_doctor_toast", None)
if _toast:
    st.toast(_toast, icon="✅")

st.divider()
col_a, col_b = st.columns(2)
with col_a:
    st.download_button("⬇ Export anonymised CSV", store.export_csv(),
                       file_name="skinai_cases.csv", mime="text/csv",
                       help="No photos, chat ids or notes.")
with col_b:
    with st.expander("Audit log (latest 50)"):
        log = store.get_audit()[-50:]
        if log:
            st.dataframe(
                [{"time (UTC)": r["ts"], "case": r["case_id"][:8], "action": r["action"],
                  "from tier": r["from_tier"], "to tier": r["to_tier"], "by": r["actor"]}
                 for r in reversed(log)],
                use_container_width=True, hide_index=True)
        else:
            st.caption("No entries yet.")
