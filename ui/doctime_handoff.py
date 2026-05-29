"""Tab 5 — DocTime telemedicine handoff (Phase 1).

Honest co-branded handoff: deep-link + QR + WhatsApp + referral PDF.
No fake API calls, no fake booking IDs. See plan file for rationale.
"""

from __future__ import annotations

import io

import qrcode
import streamlit as st

from telemedicine import get_provider, payload_from_session
from telemedicine.providers import REGISTRY
from ui.components import (
    render_tier_banner,
    render_disease_card,
    render_referral_download_button,
)
from ui.styles import (
    PRIMARY, TEAL, TEXT_DARK, TEXT_MID, TEXT_LIGHT, BORDER_COLOR,
    TIER3_BORDER,
)


_DOCTIME_NAVY = "#0B2A52"   # DocTime brand navy (visual reference only)
_DOCTIME_TEAL = "#00B4B4"   # DocTime brand teal accent
_WHATSAPP     = "#25D366"


def _qr_png_bytes(payload: str) -> bytes:
    """Build a small QR PNG for the handoff URL."""
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=2,
    )
    qr.add_data(payload)
    qr.make(fit=True)
    img = qr.make_image(fill_color=_DOCTIME_NAVY, back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _render_empty_state() -> None:
    st.markdown(
        f"""
        <div style="background:#F8FAFC;border:1px dashed {BORDER_COLOR};
                    border-radius:14px;padding:2.2rem 1.6rem;text-align:center;
                    color:{TEXT_LIGHT};">
          <div style="font-size:2rem;margin-bottom:0.6rem;">🩺</div>
          <div style="font-size:1.05rem;font-weight:700;color:{TEXT_DARK};
                      margin-bottom:0.4rem;">
            Complete diagnosis first
          </div>
          <div style="font-size:0.86rem;font-family:'Noto Sans Bengali',sans-serif;
                      color:{TEXT_MID};margin-bottom:0.8rem;">
            প্রথমে Tab 1-এ রোগ নির্ণয় সম্পন্ন করুন
          </div>
          <div style="font-size:0.82rem;color:{TEXT_MID};line-height:1.55;">
            Run a voice + image diagnosis in <b>Tab 1 · Diagnosis</b>, then
            return here to hand the case off to a DocTime BMDC-registered
            dermatologist.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_doctime_card(provider, urgent: bool) -> None:
    border = TIER3_BORDER if urgent else _DOCTIME_NAVY
    border_w = "2px" if urgent else "1px"
    urgent_pill = (
        f'<span style="background:{TIER3_BORDER};color:white;font-size:0.7rem;'
        f'font-weight:800;padding:3px 10px;border-radius:999px;'
        f'letter-spacing:0.04em;margin-left:0.4rem;">TIER 3 · URGENT</span>'
        if urgent else ""
    )
    st.markdown(
        f"""
        <div style="background:white;border:{border_w} solid {border};
                    border-radius:16px;padding:1.4rem 1.5rem;
                    box-shadow:0 4px 14px rgba(11,42,82,0.06);
                    margin-bottom:1.1rem;">
          <div style="display:flex;justify-content:space-between;align-items:center;
                      flex-wrap:wrap;gap:0.6rem;">
            <div style="display:flex;align-items:center;gap:0.8rem;">
              <div style="background:linear-gradient(135deg,{_DOCTIME_NAVY} 0%,
                          {_DOCTIME_TEAL} 100%);color:white;font-weight:900;
                          font-size:1.15rem;letter-spacing:0.02em;
                          padding:0.55rem 0.95rem;border-radius:10px;">
                DocTime
              </div>
              <div>
                <div style="font-size:1.05rem;font-weight:800;color:{TEXT_DARK};">
                  {provider.bn_name} · BMDC-verified dermatologists
                </div>
                <div style="font-size:0.82rem;color:{TEXT_MID};margin-top:2px;
                            font-family:'Noto Sans Bengali',sans-serif;">
                  {provider.tagline_bn}
                </div>
              </div>
            </div>
            <div>
              <span style="background:{PRIMARY};color:white;font-size:0.72rem;
                           font-weight:800;padding:4px 11px;border-radius:999px;
                           letter-spacing:0.04em;">
                PHASE 1 · LAUNCH PARTNER
              </span>
              {urgent_pill}
            </div>
          </div>

          <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:0.6rem;
                      margin-top:1.1rem;">
            <div style="background:#F0F9FF;border-radius:8px;padding:0.6rem;
                        text-align:center;">
              <div style="font-size:1.05rem;">⏱️</div>
              <div style="font-size:0.74rem;color:{TEXT_MID};font-weight:600;">24/7</div>
              <div style="font-size:0.7rem;color:{TEXT_LIGHT};">video</div>
            </div>
            <div style="background:#F0F9FF;border-radius:8px;padding:0.6rem;
                        text-align:center;">
              <div style="font-size:1.05rem;">🏥</div>
              <div style="font-size:0.74rem;color:{TEXT_MID};font-weight:600;">BMDC</div>
              <div style="font-size:0.7rem;color:{TEXT_LIGHT};">licensed</div>
            </div>
            <div style="background:#F0F9FF;border-radius:8px;padding:0.6rem;
                        text-align:center;">
              <div style="font-size:1.05rem;">💵</div>
              <div style="font-size:0.74rem;color:{TEXT_MID};font-weight:600;">
                {provider.fee_range_bdt}
              </div>
              <div style="font-size:0.7rem;color:{TEXT_LIGHT};">per consult</div>
            </div>
            <div style="background:#F0F9FF;border-radius:8px;padding:0.6rem;
                        text-align:center;">
              <div style="font-size:1.05rem;">📝</div>
              <div style="font-size:0.74rem;color:{TEXT_MID};font-weight:600;">e-Rx</div>
              <div style="font-size:0.7rem;color:{TEXT_LIGHT};">prescription</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_handoff_grid(provider, payload) -> None:
    deep = provider.deep_link(payload)
    wa = provider.whatsapp_url(payload)
    qr_bytes = _qr_png_bytes(provider.qr_payload(payload))

    col_app, col_qr, col_wa = st.columns(3, gap="medium")

    with col_app:
        st.markdown(
            f"""
            <div style="background:white;border:1px solid {BORDER_COLOR};
                        border-radius:14px;padding:1.1rem 1rem;height:100%;
                        text-align:center;">
              <div style="font-size:1.7rem;">📱</div>
              <div style="font-weight:800;color:{TEXT_DARK};margin-top:0.3rem;">
                Open DocTime
              </div>
              <div style="font-size:0.78rem;color:{TEXT_MID};margin:0.35rem 0 0.8rem;
                          font-family:'Noto Sans Bengali',sans-serif;">
                DocTime অ্যাপে যান
              </div>
              <a href="{deep}" target="_blank" rel="noopener"
                 style="display:inline-block;background:{_DOCTIME_NAVY};color:white;
                        text-decoration:none;font-weight:700;font-size:0.86rem;
                        padding:0.55rem 1.1rem;border-radius:8px;
                        width:100%;box-sizing:border-box;">
                Continue on DocTime →
              </a>
              <div style="font-size:0.72rem;color:{TEXT_LIGHT};margin-top:0.55rem;
                          line-height:1.45;">
                Opens app on Android · web on desktop
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_qr:
        st.markdown(
            f"""
            <div style="background:white;border:1px solid {BORDER_COLOR};
                        border-radius:14px;padding:1.1rem 1rem 0.6rem;height:100%;
                        text-align:center;">
              <div style="font-size:1.7rem;">📷</div>
              <div style="font-weight:800;color:{TEXT_DARK};margin-top:0.3rem;">
                Scan with phone
              </div>
              <div style="font-size:0.78rem;color:{TEXT_MID};margin:0.35rem 0 0.7rem;
                          font-family:'Noto Sans Bengali',sans-serif;">
                ফোনে স্ক্যান করুন
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.image(qr_bytes, width=180)
        st.caption("Hand patient the screen — they scan, DocTime opens on their device.")

    with col_wa:
        st.markdown(
            f"""
            <div style="background:white;border:1px solid {BORDER_COLOR};
                        border-radius:14px;padding:1.1rem 1rem;height:100%;
                        text-align:center;">
              <div style="font-size:1.7rem;">💬</div>
              <div style="font-weight:800;color:{TEXT_DARK};margin-top:0.3rem;">
                WhatsApp hotline
              </div>
              <div style="font-size:0.78rem;color:{TEXT_MID};margin:0.35rem 0 0.8rem;
                          font-family:'Noto Sans Bengali',sans-serif;">
                হোয়াটসঅ্যাপে যোগাযোগ
              </div>
              <a href="{wa}" target="_blank" rel="noopener"
                 style="display:inline-block;background:{_WHATSAPP};color:white;
                        text-decoration:none;font-weight:700;font-size:0.86rem;
                        padding:0.55rem 1.1rem;border-radius:8px;
                        width:100%;box-sizing:border-box;">
                Open prefilled chat →
              </a>
              <div style="font-size:0.72rem;color:{TEXT_LIGHT};margin-top:0.55rem;
                          line-height:1.45;">
                Bengali message ready · {provider.hotline}
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.expander("Preview the Bengali message sent to DocTime", expanded=False):
        st.code(provider.prefilled_message(payload, lang="bn"), language=None)


def _render_phase_strip() -> None:
    """Footer: 'integration layer' narrative with greyed Phase-3 partners."""
    stubs = [REGISTRY[k] for k in ("praava health", "medical", "maya")]
    pills = "".join(
        f'<span style="background:#F1F5F9;color:{TEXT_LIGHT};font-size:0.72rem;'
        f'font-weight:600;padding:3px 10px;border-radius:999px;margin-right:0.4rem;'
        f'border:1px dashed {BORDER_COLOR};">{s.name}</span>'
        for s in stubs
    )
    st.markdown(
        f"""
        <div style="margin-top:1.2rem;padding-top:1rem;border-top:1px solid {BORDER_COLOR};
                    font-size:0.78rem;color:{TEXT_LIGHT};line-height:1.6;">
          <b style="color:{TEXT_MID};">SkinAI Bangladesh × DocTime</b> —
          telemedicine integration layer · MOU in discussion · Phase 1 of 3.
          <div style="margin-top:0.6rem;">
            Coming in Phase 3: {pills}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_doctime_handoff_tab() -> None:
    """Entry point — called from app.py inside `with tab5:`."""
    payload = payload_from_session(st.session_state)

    st.markdown(
        f"""
        <div style="background:linear-gradient(135deg,{_DOCTIME_NAVY} 0%,
                    {PRIMARY} 100%);color:white;border-radius:14px;
                    padding:1.1rem 1.4rem;margin-bottom:1.1rem;">
          <div style="font-size:1.05rem;font-weight:800;letter-spacing:0.01em;">
            Hand off to a real doctor — via DocTime
          </div>
          <div style="font-size:0.82rem;opacity:0.92;margin-top:0.3rem;line-height:1.55;">
            Phase 1 launch partner. The AI referral PDF travels with the patient
            so the DocTime dermatologist sees your tier + diagnosis upfront.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if payload is None:
        _render_empty_state()
        return

    # 1. Patient context — reuse existing components.
    tr = st.session_state.tier_result
    render_tier_banner(
        tr.get("tier", 0),
        tr.get("urgency_label", ""),
        tr.get("action", ""),
        tr.get("bengali_text", tr.get("bn", "")),
        tr.get("facility", ""),
    )
    pred = st.session_state.prediction
    render_disease_card(
        pred.get("disease", ""),
        float(pred.get("confidence", 0.0)),
        pred.get("top2") or [],
    )

    # 2. DocTime provider card.
    provider = get_provider("DocTime")
    _render_doctime_card(provider, urgent=(payload.tier >= 3))

    # 3. Three-column handoff actions.
    _render_handoff_grid(provider, payload)

    # 4. PDF attach reminder.
    st.markdown(
        f"""
        <div style="background:#FFFBEB;border:1px solid #FCD34D;border-radius:12px;
                    padding:0.95rem 1.1rem;margin-top:1.2rem;display:flex;
                    align-items:center;gap:0.8rem;">
          <div style="font-size:1.4rem;">📎</div>
          <div style="flex:1;">
            <div style="font-weight:700;color:{TEXT_DARK};font-size:0.92rem;">
              Show this PDF to your DocTime doctor
            </div>
            <div style="font-size:0.8rem;color:{TEXT_MID};margin-top:2px;
                        font-family:'Noto Sans Bengali',sans-serif;">
              এই PDF DocTime ডাক্তারকে দেখান — পুরো AI বিশ্লেষণ সংযুক্ত
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_referral_download_button(st.session_state.get("pdf_bytes"), key="dl_referral_btn_doctime")

    # 5. Phase strip.
    _render_phase_strip()
