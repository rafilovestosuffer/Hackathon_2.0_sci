# UI OVERHAUL — 2026-05-20
"""
ui/components.py — Championship-grade reusable widgets for SkinAI Bangladesh.
All functions are standalone; call from app.py after inject_css().
"""

import re
import streamlit as st

from model.disease_labels import get_bengali
from severity.engine import CONF_TIER2, CONF_TIER3  # single source of truth
from ui.styles import (
    PRIMARY, TEAL,
    TIER1_BG, TIER1_BORDER, TIER1_TEXT,
    TIER2_BG, TIER2_BORDER, TIER2_TEXT,
    TIER3_BG, TIER3_BORDER, TIER3_TEXT,
    TEXT_DARK, TEXT_MID, TEXT_LIGHT,
    BORDER_COLOR,
)

# ── Tier config ───────────────────────────────────────────────────────────────
_TIER_CONFIG = {
    1: {"badge_class": "badge-tier1", "icon": "🟢", "label": "NON-URGENT",  "label_bn": "জরুরি নয়"},
    2: {"badge_class": "badge-tier2", "icon": "🟡", "label": "ROUTINE",     "label_bn": "নিয়মিত"},
    3: {"badge_class": "badge-tier3", "icon": "🔴", "label": "URGENT",      "label_bn": "জরুরি"},
}
_TIER_ICONS = {1: "✅", 2: "⚠️", 3: "🚨"}

def bn_en(bengali: str, english: str) -> str:
    """Return a bilingual message: Bengali line then italic English line."""
    return f"{bengali}\n\n_{english}_"


_HISTORY_LABELS = {
    "chief_complaint":      ("Chief Complaint",      "প্রধান অভিযোগ"),
    "symptoms":             ("Symptoms",             "উপসর্গ"),
    "affected_area":        ("Affected Area",        "আক্রান্ত স্থান"),
    "duration":             ("Duration",             "স্থায়িত্ব"),
    "progression":          ("Progression",          "অগ্রগতি"),
    "previous_treatment":   ("Previous Treatment",   "পূর্ববর্তী চিকিৎসা"),
    "associated_symptoms":  ("Associated Symptoms",  "সহগামী উপসর্গ"),
    "patient_name":         ("Patient Name",         "রোগীর নাম"),
    "patient_age":          ("Patient Age",          "রোগীর বয়স"),
}


# ══════════════════════════════════════════════════════════════════════════════
# NEW COMPONENTS
# ══════════════════════════════════════════════════════════════════════════════

def render_sidebar_pipeline(
    voice_done: bool,
    image_done: bool,
    diagnosis_done: bool,
    referral_done: bool,
) -> None:
    """Render the 4-step visual pipeline tracker inside the sidebar."""
    steps = [
        ("🎙️", "Voice recorded",   "ভয়েস রেকর্ড",   voice_done),
        ("📷", "Image analysed",   "ছবি বিশ্লেষণ",   image_done),
        ("🧠", "Diagnosis ready",  "রোগ নির্ণয়",     diagnosis_done),
        ("📄", "Referral ready",   "রেফারেল প্রস্তুত", referral_done),
    ]
    first_pending = None
    for i, (_, _, _, done) in enumerate(steps):
        if not done and first_pending is None:
            first_pending = i

    for i, (icon, label_en, label_bn, done) in enumerate(steps):
        if done:
            state_cls = "done"
            dot_cls   = "done"
            dot_inner = "✓"
        elif i == first_pending:
            state_cls = "active"
            dot_cls   = "active"
            dot_inner = str(i + 1)
        else:
            state_cls = "pending"
            dot_cls   = "pending"
            dot_inner = str(i + 1)

        st.markdown(
            f'<div class="pipeline-step {state_cls}">'
            f'  <div class="pipeline-dot {dot_cls}">{dot_inner}</div>'
            f'  <div>'
            f'    <div style="font-size:0.76rem;font-weight:600;">{icon} {label_en}</div>'
            f'    <div style="font-size:0.68rem;font-family:\'Noto Sans Bengali\',sans-serif;">{label_bn}</div>'
            f'  </div>'
            f'</div>',
            unsafe_allow_html=True,
        )


def render_stat_card(label: str, value: str, color: str = "#1A6FA8") -> None:
    """Render a metric stat card (used inside the sidebar expander)."""
    st.markdown(
        f'<div class="stat-card-sb">'
        f'  <div class="stat-card-sb-label">{label}</div>'
        f'  <div class="stat-card-sb-value" style="color:{color} !important;">{value}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_tier_banner(
    tier: int,
    urgency_label: str,
    action_text: str,
    bn_text: str,
    facility: str,
) -> None:
    """Render the full-width colored severity tier banner."""
    icons   = {1: "✅", 2: "⚠️", 3: "🚨"}
    labels  = {1: "NON-URGENT",  2: "ROUTINE",  3: "URGENT · জরুরি"}
    t       = tier if tier in (1, 2, 3) else 2
    icon    = icons[t]
    badge   = labels[t]

    st.markdown(
        f'<div class="tier-banner tier-banner-{t}">'
        f'  <div class="tier-banner-icon">{icon}</div>'
        f'  <div style="flex:1">'
        f'    <div><span class="tier-badge-pill tier-badge-{t}">{badge}</span></div>'
        f'    <div class="tier-urgency tier-urgency-{t}">{urgency_label}</div>'
        f'    <div class="tier-action">{action_text}</div>'
        f'    <div class="tier-action-bn tier-action-bn-{t}">{bn_text}</div>'
        f'    <div class="tier-facility">🏥 {facility}</div>'
        f'  </div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_confidence_bar(
    confidence_float: float,
    label_en: str,
    label_bn: str,
) -> None:
    """Render a styled HTML confidence progress bar with bilingual label."""
    pct = max(0.0, min(100.0, confidence_float * 100))

    if confidence_float >= 0.80:
        bar_color = "#27AE60"
        cap_cls   = "conf-high"
        cap_text  = f"✓ {label_bn} &nbsp;·&nbsp; {label_en}"
    elif confidence_float >= 0.60:
        bar_color = "#E67E22"
        cap_cls   = "conf-mid"
        cap_text  = f"~ {label_bn} &nbsp;·&nbsp; {label_en}"
    else:
        bar_color = "#C0392B"
        cap_cls   = "conf-low"
        cap_text  = f"⚠ {label_bn} &nbsp;·&nbsp; {label_en}"

    st.markdown(
        f'<div class="conf-label-v2">'
        f'  <span>Confidence · আত্মবিশ্বাস</span>'
        f'  <span class="conf-value-mono" style="color:{bar_color};">{pct:.1f}%</span>'
        f'</div>'
        f'<div class="conf-bar-wrap-v2">'
        f'  <div class="conf-bar-fill-v2" style="width:{pct}%;background:{bar_color};"></div>'
        f'</div>'
        f'<div><span class="conf-caption {cap_cls}">{cap_text}</span></div>',
        unsafe_allow_html=True,
    )


def _md_to_html(text: str) -> str:
    """Minimal markdown → HTML for chat bubble rendering."""
    # Bold then italic
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*',     r'<em>\1</em>',         text)
    # Bullet lines → • prefix
    lines = text.split('\n')
    out = []
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith('- ') or stripped.startswith('• '):
            out.append('• ' + stripped[2:])
        else:
            out.append(line)
    return '<br>'.join(out)


def render_chat_message(role: str, content: str, sources=None) -> str:
    """Return an HTML string for a single chat bubble (does NOT call st.markdown)."""
    if sources is None:
        sources = []

    if role == "user":
        safe = (
            content
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        return (
            f'<div class="chat-bubble-wrap-user">'
            f'  <div class="chat-bubble-user">{safe}</div>'
            f'</div>'
        )

    # AI message
    html_body = _md_to_html(content)
    chips = "".join(
        f'<span class="chat-source-chip">{s}</span>' for s in sources
    )
    src_html = f'<div class="chat-source-chips">{chips}</div>' if chips else ""

    return (
        f'<div class="chat-bubble-wrap-ai">'
        f'  <div class="ai-avatar">AI</div>'
        f'  <div style="flex:1">'
        f'    <div class="chat-bubble-ai">{html_body}</div>'
        f'    {src_html}'
        f'  </div>'
        f'</div>'
    )


def render_suggested_questions(questions_list: list) -> str | None:
    """
    Render clickable pill suggestion buttons in a row.
    Returns the question string that was clicked, or None.
    """
    cols = st.columns(len(questions_list))
    for i, (col, q) in enumerate(zip(cols, questions_list)):
        with col:
            if st.button(q, key=f"sq_{i}", use_container_width=True):
                return q
    return None


def render_referral_preview(pred: dict, tier_result: dict, history: dict) -> None:
    """Render the 4-section PDF preview cards inside Tab 3."""
    from model.disease_labels import get_bengali as _gb

    disease_en = pred.get("disease", "—").replace("_", " ")
    disease_bn = _gb(pred.get("disease", ""))
    conf_pct   = pred.get("confidence", 0.0) * 100
    cov_pct    = pred.get("coverage_pct", 0.0)
    tier       = tier_result.get("tier", 2)
    tier_colors = {1: "#27AE60", 2: "#E67E22", 3: "#C0392B"}
    tier_color  = tier_colors.get(tier, "#4A5568")
    tier_label  = tier_result.get("urgency_label", f"Tier {tier}")

    # Section 1 — Patient History
    complaint   = history.get("chief_complaint", "—")
    symptoms    = history.get("symptoms", [])
    symp_str    = ", ".join(symptoms) if isinstance(symptoms, list) else str(symptoms)
    area        = history.get("affected_area", "—")
    name        = history.get("patient_name", "—")

    symp_chips = ""
    if symp_str and symp_str != "—":
        for s in symp_str.split(", ")[:4]:
            symp_chips += f'<span style="background:#EBF5FB;color:#1A5276;font-size:0.72rem;border-radius:99px;padding:0.1rem 0.55rem;margin:0.1rem;display:inline-block;">{s}</span>'

    st.markdown(
        f'<div class="referral-section-card">'
        f'  <div class="referral-section-num">1</div>'
        f'  <div style="flex:1">'
        f'    <div class="referral-section-title">Patient History · রোগীর ইতিহাস</div>'
        f'    <div class="referral-section-content">'
        f'      <strong>{name}</strong> &nbsp;|&nbsp; {complaint}<br>'
        f'      <span style="font-size:0.78rem;color:#718096;">🗺️ {area}</span><br>'
        f'      <div style="margin-top:0.3rem;">{symp_chips}</div>'
        f'    </div>'
        f'  </div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Section 2 — Clinical Observation (GradCAM)
    cov_bar_color = "#27AE60" if cov_pct <= 40 else "#C0392B"
    cov_note      = "⚠️ High coverage — severity escalated" if cov_pct > 40 else "✓ Within normal range"
    st.markdown(
        f'<div class="referral-section-card">'
        f'  <div class="referral-section-num">2</div>'
        f'  <div style="flex:1">'
        f'    <div class="referral-section-title">Clinical Observation · ক্লিনিক্যাল পর্যবেক্ষণ</div>'
        f'    <div class="referral-section-content">'
        f'      GradCAM++ Heatmap · Affected region coverage: '
        f'      <strong style="color:{cov_bar_color};">{cov_pct:.1f}%</strong><br>'
        f'      <div style="background:#E2E8F0;border-radius:99px;height:8px;margin:0.35rem 0;overflow:hidden;">'
        f'        <div style="width:{min(cov_pct,100):.0f}%;height:8px;background:{cov_bar_color};border-radius:99px;"></div>'
        f'      </div>'
        f'      <span style="font-size:0.75rem;color:#718096;">{cov_note}</span>'
        f'    </div>'
        f'  </div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Section 3 — AI Diagnostic Assessment
    diff_html = ""
    top2 = pred.get("top2", [])
    if len(top2) >= 2 and isinstance(top2[1], dict) and top2[1].get("confidence", 0) > 0.15:
        d2 = top2[1]
        diff_html = (
            f'<br><span class="differential-pill">'
            f'Differential: {d2["disease"].replace("_"," ")} ({d2["confidence"]*100:.0f}%)'
            f'</span>'
        )
    st.markdown(
        f'<div class="referral-section-card">'
        f'  <div class="referral-section-num">3</div>'
        f'  <div style="flex:1">'
        f'    <div class="referral-section-title">AI Diagnostic Assessment · এআই রোগ নির্ণয়</div>'
        f'    <div class="referral-section-content">'
        f'      <strong>{disease_en}</strong> &nbsp;·&nbsp; {disease_bn}<br>'
        f'      <span style="font-family:\'JetBrains Mono\',monospace;font-size:0.85rem;font-weight:600;">Confidence: {conf_pct:.1f}%</span>'
        f'      {diff_html}'
        f'    </div>'
        f'  </div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Section 4 — Triage Recommendation
    action_en   = tier_result.get("action", "")
    action_bn   = tier_result.get("bengali_text", "")
    facility    = tier_result.get("facility", "")
    st.markdown(
        f'<div class="referral-section-card">'
        f'  <div class="referral-section-num" style="background:{tier_color};">4</div>'
        f'  <div style="flex:1">'
        f'    <div class="referral-section-title">Triage Recommendation · ট্রাইয়েজ সুপারিশ</div>'
        f'    <div class="referral-section-content">'
        f'      <span style="background:{tier_color};color:white;font-size:0.7rem;font-weight:700;'
        f'             border-radius:99px;padding:0.15rem 0.65rem;">{tier_label}</span><br>'
        f'      <span style="margin-top:0.3rem;display:block;">{action_en}</span>'
        f'      <span style="font-family:\'Noto Sans Bengali\',sans-serif;color:{tier_color};font-weight:600;">{action_bn}</span><br>'
        f'      <span style="font-size:0.75rem;color:#718096;">🏥 {facility}</span>'
        f'    </div>'
        f'  </div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# EXISTING COMPONENTS (kept + lightly upgraded)
# ══════════════════════════════════════════════════════════════════════════════

def render_triage_badge(tier_result: dict) -> None:
    """Legacy badge — kept for backward compat. Prefer render_tier_banner."""
    tier = tier_result.get("tier", 2)
    cfg  = _TIER_CONFIG.get(tier, _TIER_CONFIG[2])

    urgency   = tier_result.get("urgency_label", cfg["label"])
    action_en = tier_result.get("action", "")
    action_bn = tier_result.get("bengali_text", tier_result.get("bn", ""))
    facility  = tier_result.get("facility", tier_result.get("facility_type", ""))

    st.markdown(
        f'<div class="{cfg["badge_class"]}">'
        f'  <div class="badge-label">{cfg["icon"]} TRIAGE RESULT · ট্রাইয়েজ ফলাফল</div>'
        f'  <div class="badge-urgency">{urgency}</div>'
        f'  <div class="badge-action">{action_en}</div>'
        + (f'  <div class="badge-action-bn">{action_bn}</div>' if action_bn else '')
        + (f'  <div style="margin-top:0.4rem;font-size:0.78rem;opacity:0.75;">Facility: {facility}</div>' if facility else '')
        + f'</div>',
        unsafe_allow_html=True,
    )


def render_gradcam_overlay(heatmap_img, coverage_pct: float) -> None:
    """Render GradCAM heatmap image + coverage bar."""
    st.markdown(
        '<div class="card-section-header">'
        '<span style="font-size:1rem;">🔬</span>'
        '<span class="card-section-title">AI Attention Map — GradCAM++</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    if heatmap_img is not None:
        st.image(heatmap_img, use_container_width=True)
        st.markdown(
            '<div class="gradcam-caption">লাল এলাকা মডেলের মনোযোগের কেন্দ্র · '
            'Red region = model focus area</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div style="background:{TIER1_BG};border:1px dashed {BORDER_COLOR};'
            f'border-radius:10px;padding:1.25rem;text-align:center;color:{TEXT_LIGHT};'
            f'font-size:0.85rem;">GradCAM heatmap will appear here when checkpoint is loaded.</div>',
            unsafe_allow_html=True,
        )

    cov       = max(0.0, min(100.0, coverage_pct))
    bar_color = "#27AE60" if cov <= 40 else "#C0392B"
    note      = "⚠️ High coverage — escalates severity" if cov > 40 else "✓ Within normal range"
    st.markdown(
        f'<div style="margin-top:0.55rem;">'
        f'  <div style="display:flex;justify-content:space-between;font-size:0.78rem;'
        f'              color:{TEXT_MID};margin-bottom:0.22rem;">'
        f'    <span>Affected region coverage</span>'
        f'    <span style="font-weight:700;font-family:\'JetBrains Mono\',monospace;color:{bar_color};">{cov:.1f}%</span>'
        f'  </div>'
        f'  <div class="coverage-wrap">'
        f'    <div class="coverage-fill" style="width:{cov}%;background:{bar_color};"></div>'
        f'  </div>'
        f'  <div style="font-size:0.72rem;color:{TEXT_LIGHT};margin-top:0.18rem;">{note}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_patient_history_table(history: dict) -> None:
    """Render voice-extracted patient history as a bilingual chip grid."""
    st.markdown(
        '<div class="card-section-header">'
        '<span style="font-size:1rem;">🎙️</span>'
        '<span class="card-section-title">Patient History · রোগীর ইতিহাস</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    # Build chip grid for key fields
    chips_html = '<div class="history-chip-grid">'
    rendered = 0
    for key, (en_label, bn_label) in _HISTORY_LABELS.items():
        value = history.get(key, "")
        if isinstance(value, list):
            value = ", ".join(str(v) for v in value if v)
        value = str(value).strip()
        if not value or value.lower() in ("none", "n/a", "unknown", "not mentioned", ""):
            continue
        chips_html += (
            f'<div class="history-chip">'
            f'  <div class="history-chip-label">{en_label} · {bn_label}</div>'
            f'  <div class="history-chip-value">{value}</div>'
            f'</div>'
        )
        rendered += 1

    chips_html += '</div>'

    if rendered == 0:
        st.markdown(
            f'<div style="color:{TEXT_LIGHT};font-size:0.84rem;font-style:italic;">'
            'No history recorded from voice input.</div>',
            unsafe_allow_html=True,
        )
        return

    st.markdown(chips_html, unsafe_allow_html=True)


def render_disease_card(disease: str, confidence: float, top2: list) -> None:
    """Render disease name (EN+BN), confidence bar, differential if top2[1] > 0.15."""
    bengali_name = get_bengali(disease)
    display_en   = disease.replace("_", " ")
    conf_pct     = max(0.0, min(100.0, confidence * 100))

    # Bar colour: green ≥ CONF_TIER2, amber CONF_TIER3–CONF_TIER2, red < CONF_TIER3
    if confidence >= CONF_TIER2:
        bar_color = TIER1_BORDER
    elif confidence >= CONF_TIER3:
        bar_color = TIER2_BORDER
    else:
        bar_color = TIER3_BORDER

    # Caption label
    if confidence >= 0.80:
        cap_cls  = "conf-high"
        cap_text = "✓ মডেল নিশ্চিত &nbsp;·&nbsp; Model is confident"
    elif confidence >= CONF_TIER2:
        cap_cls  = "conf-mid"
        cap_text = "~ মোটামুটি নিশ্চিত &nbsp;·&nbsp; Moderately confident"
    else:
        cap_cls  = "conf-low"
        cap_text = "⚠ অনিশ্চিত — ডাক্তার দেখান &nbsp;·&nbsp; Uncertain — see a doctor"

    diff_html = ""
    if (
        isinstance(top2, (list, tuple))
        and len(top2) >= 2
        and isinstance(top2[1], dict)
        and top2[1].get("confidence", 0.0) > 0.15
    ):
        d2 = top2[1]
        d2_name = d2.get("disease", "").replace("_", " ")
        d2_conf = d2.get("confidence", 0.0) * 100
        diff_html = (
            f'<div class="differential-pill">'
            f'Differential: {d2_name} ({d2_conf:.0f}%)'
            f'</div>'
        )

    st.markdown(
        f'<div class="sk-card">'
        f'  <div class="sk-card-title">AI Diagnosis — এআই রোগ নির্ণয়</div>'
        f'  <div class="disease-name-en">{display_en}</div>'
        f'  <div class="disease-name-bn">{bengali_name}</div>'
        f'  <div class="conf-label">'
        f'    <span>Confidence</span>'
        f'    <span class="conf-value-mono" style="color:{bar_color};">{conf_pct:.1f}%</span>'
        f'  </div>'
        f'  <div class="conf-bar-wrap">'
        f'    <div class="conf-bar-fill" style="width:{conf_pct}%;background:{bar_color};"></div>'
        f'  </div>'
        f'  <span class="conf-caption {cap_cls}">{cap_text}</span>'
        f'  {diff_html}'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_rag_answer(answer: str, lang: str = "en") -> None:
    """Render RAG answer in styled teal-bordered box with source tags."""
    src_tag  = '<span class="rag-source-tag">CDC · NIH · WHO · DGHS</span>'
    lang_tag = (
        '<span class="rag-source-tag">Bengali · বাংলা</span>'
        if lang == "bn"
        else '<span class="rag-source-tag">English</span>'
    )
    st.markdown(
        f'<div class="rag-answer-box">{answer}</div>'
        f'<div style="margin-top:0.35rem;">{src_tag}{lang_tag}</div>',
        unsafe_allow_html=True,
    )


def check_image_quality(pil_img) -> tuple[bool, float]:
    """
    Laplacian variance blur detection.
    Returns (is_blurry, variance). Never raises.
    """
    try:
        import cv2
        import numpy as np
        img_np  = np.array(pil_img.convert("L"))
        lap_var = float(cv2.Laplacian(img_np, cv2.CV_64F).var())
        return lap_var < 80.0, lap_var
    except Exception:
        return False, -1.0


def render_referral_download_button(pdf_bytes) -> None:
    """Native Streamlit download button when PDF available; muted placeholder otherwise."""
    if pdf_bytes is not None:
        st.download_button(
            label="📥 রেফারেল পত্র ডাউনলোড করুন · Download Referral Letter (PDF)",
            data=pdf_bytes,
            file_name="skinai_referral.pdf",
            mime="application/pdf",
            use_container_width=True,
            key="dl_referral_btn",
        )
    else:
        st.markdown(
            f'<div style="background:{BORDER_COLOR};border-radius:10px;padding:0.75rem 1rem;'
            f'text-align:center;color:{TEXT_LIGHT};font-size:0.86rem;border:1px solid #CBD5E1;">'
            f'📄 Complete diagnosis in Tab 1 to generate the referral letter<br>'
            f'<span style="font-size:0.76rem;font-family:\'Noto Sans Bengali\',sans-serif;">'
            f'রেফারেল পত্র পেতে প্রথম ট্যাবে রোগ নির্ণয় সম্পন্ন করুন</span>'
            f'</div>',
            unsafe_allow_html=True,
        )


# ══════════════════════════════════════════════════════════════════════════════
# F2 — Treatment Cost Estimate
# ══════════════════════════════════════════════════════════════════════════════

def render_cost_estimate(tier: int) -> None:
    """Teal card showing estimated treatment cost in Taka for the given tier."""
    from severity.engine import COST_ESTIMATE
    info = COST_ESTIMATE.get(tier, COST_ESTIMATE[2])
    tier_colors = {1: "#27AE60", 2: "#E67E22", 3: "#C0392B"}
    color = tier_colors.get(tier, "#1A6FA8")
    st.markdown(
        f'<div style="background:#F0FFF4;border:1.5px solid {color};border-radius:10px;'
        f'padding:0.75rem 1rem;margin-top:0.5rem;">'
        f'  <div style="font-size:0.72rem;font-weight:700;color:{color};'
        f'text-transform:uppercase;letter-spacing:0.06em;margin-bottom:0.3rem;">'
        f'💰 Estimated Cost · আনুমানিক খরচ</div>'
        f'  <div style="font-size:1.4rem;font-weight:800;color:{color};">'
        f'{info["range"]}</div>'
        f'  <div style="font-size:0.8rem;color:#4A5568;margin-top:0.15rem;">'
        f'{info["note"]}</div>'
        f'  <div style="font-family:\'Noto Sans Bengali\',sans-serif;font-size:0.78rem;'
        f'color:#4A5568;margin-top:0.1rem;">{info["note_bn"]}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# F7 — "Without SkinAI vs. With SkinAI" Impact Comparison
# ══════════════════════════════════════════════════════════════════════════════

def render_impact_comparison() -> None:
    """Two-column before/after impact panel — goes in sidebar or Tab 1."""
    st.markdown(
        '<div style="margin-top:0.5rem;">'
        '<div style="font-size:0.68rem;font-weight:700;color:#4A6080;'
        'text-transform:uppercase;letter-spacing:0.06em;margin-bottom:0.4rem;">'
        '⚖️ Impact · পার্থক্য</div>'

        '<div style="display:flex;gap:0.4rem;">'

        # Left — without SkinAI
        '<div style="flex:1;background:#FFF5F5;border:1.5px solid #FC8181;'
        'border-radius:8px;padding:0.55rem 0.6rem;">'
        '<div style="font-size:1rem;margin-bottom:0.15rem;">❌</div>'
        '<div style="font-size:0.62rem;font-weight:700;color:#C53030;margin-bottom:0.2rem;">'
        'Without SkinAI</div>'
        '<div style="font-size:0.6rem;color:#742A2A;line-height:1.4;">'
        'হাতুড়ে ডাক্তার<br>ভুল চিকিৎসা<br>১৪ দিন দেরি<br>অবস্থা খারাপ'
        '</div>'
        '</div>'

        # Right — with SkinAI
        '<div style="flex:1;background:#F0FFF4;border:1.5px solid #68D391;'
        'border-radius:8px;padding:0.55rem 0.6rem;">'
        '<div style="font-size:1rem;margin-bottom:0.15rem;">✅</div>'
        '<div style="font-size:0.62rem;font-weight:700;color:#22543D;margin-bottom:0.2rem;">'
        'With SkinAI</div>'
        '<div style="font-size:0.6rem;color:#276749;line-height:1.4;">'
        'AI নির্ণয়<br>সঠিক রেফারেল<br>&lt;১ ঘণ্টায়<br>সুস্থতার পথ'
        '</div>'
        '</div>'

        '</div>'  # flex container
        '</div>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# F1 — Bengali TTS (gTTS) for triage result readout
# ══════════════════════════════════════════════════════════════════════════════

def render_audio_triage(tier_action_bn: str) -> None:
    """
    Synthesise triage text → Bengali MP3 via gTTS, play inline.
    Silently skips on network failure — never raises.
    """
    if not tier_action_bn:
        return
    try:
        import io as _io
        from gtts import gTTS
        buf = _io.BytesIO()
        tts = gTTS(text=tier_action_bn, lang="bn", slow=False)
        tts.write_to_fp(buf)
        buf.seek(0)
        st.markdown(
            '<div style="font-size:0.72rem;color:#4A5568;margin-top:0.4rem;margin-bottom:0.15rem;">'
            '🔊 বাংলায় শুনুন · Listen in Bengali</div>',
            unsafe_allow_html=True,
        )
        st.audio(buf.read(), format="audio/mp3")
    except Exception:
        pass  # TTS is enhancement-only; silent failure is fine


# ══════════════════════════════════════════════════════════════════════════════
# F5 — Automatic Image Enhancement (CLAHE + unsharp mask)
# ══════════════════════════════════════════════════════════════════════════════

def enhance_skin_image(pil_img):
    """
    Auto-enhance a skin photo for low light or mild blur.
    Returns (enhanced_PIL_Image, was_enhanced: bool).
    Never raises.
    """
    try:
        import cv2
        import numpy as np
        from PIL import Image as _PILImage

        img_np = np.array(pil_img.convert("RGB"))

        is_blurry, lap_var = check_image_quality(pil_img)
        mean_brightness = float(img_np.mean())
        needs_enhance = is_blurry or mean_brightness < 80

        if not needs_enhance:
            return pil_img, False

        # CLAHE on L channel for low-light correction
        lab = cv2.cvtColor(img_np, cv2.COLOR_RGB2LAB)
        l_ch, a_ch, b_ch = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l_ch = clahe.apply(l_ch)
        enhanced = cv2.merge([l_ch, a_ch, b_ch])
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2RGB)

        # Unsharp mask for mild blur
        if is_blurry:
            blur = cv2.GaussianBlur(enhanced, (0, 0), 3)
            enhanced = cv2.addWeighted(enhanced, 1.5, blur, -0.5, 0)

        return _PILImage.fromarray(enhanced.astype(np.uint8)), True
    except Exception:
        return pil_img, False


# ══════════════════════════════════════════════════════════════════════════════
# F6 — Symptom Duration Timeline
# ══════════════════════════════════════════════════════════════════════════════

_BN_NUMBERS = {
    "এক": 1, "দুই": 2, "তিন": 3, "চার": 4, "পাঁচ": 5,
    "ছয়": 6, "সাত": 7, "আট": 8, "নয়": 9, "দশ": 10,
    "এগারো": 11, "বারো": 12, "তেরো": 13, "চোদ্দ": 14,
    "পনেরো": 15, "ষোল": 16, "সতেরো": 17, "আঠারো": 18,
}
_BN_DIGITS = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")


def _parse_duration_days(duration_str: str) -> int | None:
    """Parse Bengali/English duration string → integer days. Returns None if unparseable."""
    if not duration_str:
        return None
    s = duration_str.strip().lower().translate(_BN_DIGITS)

    # Normalise Bengali unit words
    s = s.replace("সপ্তাহ", "week").replace("মাস", "month").replace("দিন", "day")

    # Try to extract number
    nums = re.findall(r'\d+', s)
    num = int(nums[0]) if nums else None

    # Try Bengali word numbers
    if num is None:
        for word, val in _BN_NUMBERS.items():
            if word in s:
                num = val
                break

    if num is None:
        return None

    if "month" in s:
        return num * 30
    if "week" in s:
        return num * 7
    return num


def render_symptom_timeline(duration_str: str, tier: int) -> None:
    """
    Horizontal 3-node timeline: Onset → Today → Expected Recovery.
    Only renders when duration can be parsed.
    """
    days = _parse_duration_days(duration_str)
    if not days:
        return

    from datetime import date, timedelta
    today = date.today()
    onset = today - timedelta(days=days)

    tier_recovery = {1: 7, 2: 14, 3: None}
    recovery_days = tier_recovery.get(tier)

    if recovery_days:
        recovery_date = today + timedelta(days=recovery_days)
        recovery_label = recovery_date.strftime("%b %d")
        recovery_note  = f"~{recovery_days}d recovery"
        node3_color    = "#27AE60"
    else:
        recovery_label = "জরুরি চিকিৎসা"
        recovery_note  = "Seek care NOW"
        node3_color    = "#C0392B"

    onset_str  = onset.strftime("%b %d")
    today_str  = today.strftime("%b %d")

    st.markdown(
        f'<div style="margin:0.75rem 0 0.25rem 0;">'
        f'  <div style="font-size:0.72rem;font-weight:700;color:#4A5568;'
        f'text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.5rem;">'
        f'  📅 Symptom Timeline · উপসর্গের সময়রেখা</div>'
        f'  <div style="display:flex;align-items:center;gap:0;">'

        # Node 1 — Onset
        f'  <div style="text-align:center;flex:0 0 auto;">'
        f'    <div style="width:36px;height:36px;border-radius:50%;background:#C0392B;'
        f'color:white;display:flex;align-items:center;justify-content:center;'
        f'font-size:1rem;margin:0 auto;">🔴</div>'
        f'    <div style="font-size:0.64rem;font-weight:700;color:#C0392B;margin-top:0.2rem;">{onset_str}</div>'
        f'    <div style="font-size:0.6rem;color:#718096;">Onset</div>'
        f'  </div>'

        # Line
        f'  <div style="flex:1;height:3px;background:linear-gradient(90deg,#C0392B,#E67E22);'
        f'margin:0 4px;"></div>'

        # Node 2 — Today
        f'  <div style="text-align:center;flex:0 0 auto;">'
        f'    <div style="width:36px;height:36px;border-radius:50%;background:#E67E22;'
        f'color:white;display:flex;align-items:center;justify-content:center;'
        f'font-size:1rem;margin:0 auto;">🟡</div>'
        f'    <div style="font-size:0.64rem;font-weight:700;color:#E67E22;margin-top:0.2rem;">{today_str}</div>'
        f'    <div style="font-size:0.6rem;color:#718096;">Today</div>'
        f'  </div>'

        # Line
        f'  <div style="flex:1;height:3px;background:linear-gradient(90deg,#E67E22,{node3_color});'
        f'margin:0 4px;"></div>'

        # Node 3 — Recovery / Care
        f'  <div style="text-align:center;flex:0 0 auto;">'
        f'    <div style="width:36px;height:36px;border-radius:50%;background:{node3_color};'
        f'color:white;display:flex;align-items:center;justify-content:center;'
        f'font-size:1rem;margin:0 auto;">{"🟢" if recovery_days else "🚨"}</div>'
        f'    <div style="font-size:0.64rem;font-weight:700;color:{node3_color};margin-top:0.2rem;">{recovery_label}</div>'
        f'    <div style="font-size:0.6rem;color:#718096;">{recovery_note}</div>'
        f'  </div>'

        f'  </div>'  # flex
        f'</div>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# F3 — CHW (Community Health Worker) Simplified Result Card
# ══════════════════════════════════════════════════════════════════════════════

def render_chw_result(pred: dict, tier_result: dict) -> None:
    """
    Simplified decision card for Shasthya Seboika / ASHA workers.
    Large font, no medical jargon, binary refer/no-refer decision.
    """
    from severity.engine import COST_ESTIMATE
    tier    = tier_result.get("tier", 2)
    disease = pred.get("disease", "Unknown").replace("_", " ")
    disease_bn = get_bengali(pred.get("disease", ""))
    action_bn  = tier_result.get("bengali_text", "")
    facility   = tier_result.get("facility", "")
    cost       = COST_ESTIMATE.get(tier, COST_ESTIMATE[2])

    icons  = {1: "✅", 2: "⚠️", 3: "🚨"}
    labels = {1: "রেফারেল নয়", 2: "রেফারেল করুন", 3: "এখনই পাঠান!"}
    bgs    = {1: "#F0FFF4", 2: "#FFFBEB", 3: "#FFF5F5"}
    colors_map = {1: "#22543D", 2: "#7B341E", 3: "#742A2A"}
    borders = {1: "#68D391", 2: "#F6AD55", 3: "#FC8181"}

    icon     = icons.get(tier, "⚠️")
    label    = labels.get(tier, "রেফারেল করুন")
    bg       = bgs.get(tier, "#FFFBEB")
    fg       = colors_map.get(tier, "#4A5568")
    border   = borders.get(tier, "#F6AD55")

    st.markdown(
        f'<div style="background:{bg};border:3px solid {border};border-radius:16px;'
        f'padding:1.5rem;text-align:center;margin:0.5rem 0;">'

        f'<div style="font-size:3.5rem;line-height:1;">{icon}</div>'
        f'<div style="font-size:1.8rem;font-weight:900;color:{fg};margin:0.4rem 0;">'
        f'{label}</div>'

        f'<div style="font-family:\'Noto Sans Bengali\',sans-serif;font-size:1rem;'
        f'font-weight:700;color:{fg};margin:0.3rem 0;">{disease_bn}</div>'
        f'<div style="font-size:0.85rem;color:#4A5568;margin-bottom:0.5rem;">{disease}</div>'

        f'<div style="background:rgba(0,0,0,0.06);border-radius:8px;padding:0.5rem 0.75rem;'
        f'margin:0.5rem 0;font-family:\'Noto Sans Bengali\',sans-serif;'
        f'font-size:0.95rem;font-weight:600;color:{fg};">{action_bn}</div>'

        f'<div style="font-size:0.78rem;color:#4A5568;">🏥 {facility}</div>'
        f'<div style="font-size:0.85rem;font-weight:700;color:{fg};margin-top:0.35rem;">'
        f'💰 {cost["range"]} &nbsp;·&nbsp; {cost["note_bn"]}</div>'

        f'</div>',
        unsafe_allow_html=True,
    )
