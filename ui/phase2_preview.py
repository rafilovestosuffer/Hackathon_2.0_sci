"""Tab 6 — Phase 2 Preview: our own dermatologist network.

Wraps the existing mock booking flow in `ui/doctor_booking.py` with a
"Phase 2 — Preview" banner so judges understand it is the future state,
not the live Phase-1 path. Phase 1 (DocTime) lives on Tab 5.
"""

from __future__ import annotations

import streamlit as st

from ui.doctor_booking import render_doctor_booking_tab
from ui.consultation_room import render_consultation_room


_PHASE2_NAVY = "#1E293B"
_PHASE2_AMBER = "#D97706"


def render_phase2_preview_tab() -> None:
    st.markdown(
        f"""
        <div style="background:linear-gradient(135deg,{_PHASE2_NAVY} 0%,#334155 100%);
                    color:white;border-radius:14px;padding:1.1rem 1.4rem;
                    margin-bottom:0.9rem;">
          <div style="display:flex;align-items:center;gap:0.6rem;flex-wrap:wrap;">
            <span style="background:{_PHASE2_AMBER};color:white;font-size:0.7rem;
                         font-weight:800;padding:3px 10px;border-radius:999px;
                         letter-spacing:0.04em;">PHASE 2 · PREVIEW</span>
            <span style="font-size:1.02rem;font-weight:800;">
              Our own dermatologist network
            </span>
          </div>
          <div style="font-size:0.82rem;opacity:0.92;margin-top:0.5rem;line-height:1.55;">
            Private beta with Faridpur Medical College Hospital &amp;
            Rangpur Medical College Hospital. For live consultations today, use
            <b>Tab 5 · DocTime</b> (Phase 1 launch partner).
            <span style="font-family:'Noto Sans Bengali',sans-serif;">
              আজকের জন্য Tab 5-এ DocTime ব্যবহার করুন।
            </span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_doctor_booking_tab()
    render_consultation_room()
