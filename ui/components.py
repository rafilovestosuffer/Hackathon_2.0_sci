"""
ui/components.py — Reusable Streamlit widgets for SkinAI Bangladesh.
Each function is standalone; call from app.py after inject_css().
"""

import numpy as np
import streamlit as st

from model.disease_labels import get_bengali
from ui.styles import (
    PRIMARY, TEAL,
    TIER1_BG, TIER1_BORDER, TIER1_TEXT,
    TIER2_BG, TIER2_BORDER, TIER2_TEXT,
    TIER3_BG, TIER3_BORDER, TIER3_TEXT,
    TEXT_DARK, TEXT_MID, TEXT_LIGHT,
    BORDER_COLOR,
)

# ── Tier display config ────────────────────────────────────────────────────────
_TIER_CONFIG = {
    1: {
        "badge_class": "badge-tier1",
        "icon": "🟢",
        "label": "NON-URGENT",
        "label_bn": "জরুরি নয়",
    },
    2: {
        "badge_class": "badge-tier2",
        "icon": "🟡",
        "label": "ROUTINE",
        "label_bn": "নিয়মিত",
    },
    3: {
        "badge_class": "badge-tier3",
        "icon": "🔴",
        "label": "URGENT",
        "label_bn": "জরুরি",
    },
}

# Human-readable history field labels
_HISTORY_LABELS = {
    "chief_complaint":      ("Chief Complaint", "প্রধান অভিযোগ"),
    "symptoms":             ("Symptoms", "উপসর্গ"),
    "affected_area":        ("Affected Area", "আক্রান্ত স্থান"),
    "duration":             ("Duration", "স্থায়িত্ব"),
    "progression":          ("Progression", "অগ্রগতি"),
    "previous_treatment":   ("Previous Treatment", "পূর্ববর্তী চিকিৎসা"),
    "associated_symptoms":  ("Associated Symptoms", "সহগামী উপসর্গ"),
    "patient_name":         ("Patient Name", "রোগীর নাম"),
    "patient_age":          ("Patient Age", "রোগীর বয়স"),
}


# ── 1. Triage badge ───────────────────────────────────────────────────────────

def render_triage_badge(tier_result: dict) -> None:
    """Render colour-coded urgency badge + bilingual action text."""
    tier = tier_result.get("tier", 2)
    cfg = _TIER_CONFIG.get(tier, _TIER_CONFIG[2])

    urgency = tier_result.get("urgency_label", cfg["label"])
    action_en = tier_result.get("action", "")
    action_bn = tier_result.get("bengali_text", tier_result.get("bn", ""))
    facility = tier_result.get("facility", tier_result.get("facility_type", ""))

    st.markdown(
        f"""
        <div class="{cfg['badge_class']}">
            <div class="badge-label">{cfg['icon']} TRIAGE RESULT · ট্রাইয়েজ ফলাফল</div>
            <div class="badge-urgency">{urgency}</div>
            <div class="badge-action">{action_en}</div>
            {'<div class="badge-action-bn">' + action_bn + '</div>' if action_bn else ''}
            {'<div style="margin-top:0.4rem;font-size:0.78rem;opacity:0.75;">Facility: ' + facility + '</div>' if facility else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── 2. GradCAM overlay ────────────────────────────────────────────────────────

def render_gradcam_overlay(heatmap_img, coverage_pct: float) -> None:
    """Render GradCAM heatmap image + coverage progress bar."""
    st.markdown('<div class="sk-section-head">🔬 AI Attention Map — GradCAM++</div>',
                unsafe_allow_html=True)

    if heatmap_img is not None:
        st.image(heatmap_img, use_container_width=True,
                 caption="Highlighted region shows where the AI focused")
    else:
        st.markdown(
            f"""<div style="background:{TIER1_BG};border:1px dashed {BORDER_COLOR};
            border-radius:10px;padding:1.5rem;text-align:center;color:{TEXT_LIGHT};
            font-size:0.88rem;">No heatmap available for this prediction.</div>""",
            unsafe_allow_html=True,
        )

    # Coverage bar
    cov = max(0.0, min(100.0, coverage_pct))
    bar_color = "#6366f1" if cov <= 40 else "#dc2626"
    st.markdown(
        f"""
        <div style="margin-top:0.5rem;">
            <div style="display:flex;justify-content:space-between;
                        font-size:0.8rem;color:{TEXT_MID};margin-bottom:0.25rem;">
                <span>Affected Region Coverage</span>
                <span style="font-weight:700;color:{bar_color};">{cov:.1f}%</span>
            </div>
            <div class="coverage-wrap">
                <div class="coverage-fill" style="width:{cov}%;background:{bar_color};"></div>
            </div>
            <div style="font-size:0.73rem;color:{TEXT_LIGHT};margin-top:0.2rem;">
                {'⚠️ High coverage — escalates severity' if cov > 40 else '✓ Within normal range'}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── 3. Patient history table ──────────────────────────────────────────────────

def render_patient_history_table(history: dict) -> None:
    """Render voice-extracted patient history as a bilingual clean table."""
    st.markdown('<div class="sk-section-head">🎙️ Patient History — রোগীর ইতিহাস</div>',
                unsafe_allow_html=True)

    rows_html = ""
    for key, (en_label, bn_label) in _HISTORY_LABELS.items():
        value = history.get(key, "")
        if isinstance(value, list):
            value = ", ".join(str(v) for v in value if v)
        value = str(value).strip()
        if not value or value.lower() in ("none", "n/a", "unknown", "not mentioned"):
            continue
        rows_html += f"""
        <tr>
            <td>{en_label}<br><span style="font-size:0.75rem;color:{TEXT_LIGHT};">{bn_label}</span></td>
            <td>{value}</td>
        </tr>"""

    if not rows_html:
        st.markdown(
            f'<div style="color:{TEXT_LIGHT};font-size:0.85rem;font-style:italic;">'
            'No history recorded from voice input.</div>',
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        f'<table class="history-table"><tbody>{rows_html}</tbody></table>',
        unsafe_allow_html=True,
    )


# ── 4. Disease card ───────────────────────────────────────────────────────────

def render_disease_card(disease: str, confidence: float, top2: list) -> None:
    """Render disease name (EN+BN), confidence bar, differential if top2[1] > 0.15."""
    bengali_name = get_bengali(disease)
    display_en = disease.replace("_", " ")
    conf_pct = max(0.0, min(100.0, confidence * 100))

    # Colour the bar: green ≥ 60%, amber 40-60%, red < 40%
    if confidence >= 0.60:
        bar_color = TIER1_BORDER
    elif confidence >= 0.40:
        bar_color = TIER2_BORDER
    else:
        bar_color = TIER3_BORDER

    # Confidence-level caption (Bengali + English)
    if confidence >= 0.80:
        conf_caption = (
            '<div class="conf-caption conf-high">'
            '✓ মডেল নিশ্চিত &nbsp;·&nbsp; Model is confident'
            '</div>'
        )
    elif confidence >= 0.60:
        conf_caption = (
            '<div class="conf-caption conf-mid">'
            '~ মোটামুটি নিশ্চিত &nbsp;·&nbsp; Moderately confident'
            '</div>'
        )
    else:
        conf_caption = (
            '<div class="conf-caption conf-low">'
            '⚠ অনিশ্চিত — ডাক্তার দেখান &nbsp;·&nbsp; Uncertain — see a doctor'
            '</div>'
        )

    # Differential diagnosis pill
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
        f"""
        <div class="sk-card">
            <div class="sk-card-title">AI Diagnosis — এআই রোগ নির্ণয়</div>
            <div class="disease-name-en">{display_en}</div>
            <div class="disease-name-bn">{bengali_name}</div>
            <div class="conf-label">
                <span>Confidence</span>
                <span style="font-weight:700;color:{bar_color};">{conf_pct:.1f}%</span>
            </div>
            <div class="conf-bar-wrap">
                <div class="conf-bar-fill" style="width:{conf_pct}%;background:{bar_color};"></div>
            </div>
            {conf_caption}
            {diff_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── 5. RAG answer ─────────────────────────────────────────────────────────────

def render_rag_answer(answer: str, lang: str = "en") -> None:
    """Render RAG chatbot answer in a styled teal-bordered box with source tag."""
    source_tag = (
        '<span class="rag-source-tag">CDC · NIH · WHO · DGHS</span>'
    )
    lang_tag = (
        '<span class="rag-source-tag">Bengali · বাংলা</span>'
        if lang == "bn"
        else '<span class="rag-source-tag">English</span>'
    )

    st.markdown(
        f"""
        <div class="rag-answer-box">
            {answer}
        </div>
        <div style="margin-top:0.4rem;">
            {source_tag}
            {lang_tag}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── 6. Image quality check ────────────────────────────────────────────────────

def check_image_quality(pil_img) -> tuple[bool, float]:
    """
    Laplacian variance blur detection.
    Returns (is_blurry, variance).
    is_blurry = True when variance < 80 (likely too blurry for reliable inference).
    Never raises — returns (False, -1.0) on any error so it never blocks processing.
    """
    try:
        import cv2
        import numpy as np
        img_np = np.array(pil_img.convert("L"))  # grayscale
        lap_var = float(cv2.Laplacian(img_np, cv2.CV_64F).var())
        return lap_var < 80.0, lap_var
    except Exception:
        return False, -1.0


# ── 7. Referral download button ───────────────────────────────────────────────

def render_referral_download_button(pdf_bytes) -> None:
    """Render PDF download button when bytes provided; disabled placeholder otherwise."""
    if pdf_bytes is not None:
        st.download_button(
            label="⬇️ Download Referral Letter (PDF) — রেফারেল পত্র ডাউনলোড",
            data=pdf_bytes,
            file_name="skinai_referral.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    else:
        st.markdown(
            f"""
            <div style="background:{BORDER_COLOR};border-radius:8px;padding:0.65rem 1rem;
                        text-align:center;color:{TEXT_LIGHT};font-size:0.88rem;
                        border:1px solid #cbd5e1;">
                📄 Complete diagnosis to generate referral letter
                <br><span style="font-size:0.78rem;">রেফারেল পত্র পেতে রোগ নির্ণয় সম্পন্ন করুন</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
