"""
SkinAI Bangladesh — main Streamlit app.
"সঠিক রোগী → সঠিক ডাক্তার → সঠিক সময়"
"""

import io
import logging

import streamlit as st
from PIL import Image

from ui.styles import inject_css
from ui.components import (
    render_triage_badge,
    render_gradcam_overlay,
    render_patient_history_table,
    render_disease_card,
    render_rag_answer,
    render_referral_download_button,
)
from severity.engine import compute_tier
from pdf_gen.referral import generate_referral_pdf
from rag.retriever import load_index, answer_question

logger = logging.getLogger(__name__)

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="SkinAI Bangladesh",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inject CSS immediately after page config ──────────────────────────────────
inject_css()


# ── Cached resource loaders ───────────────────────────────────────────────────

@st.cache_resource(show_spinner="Loading RAG knowledge base…")
def _load_rag_index():
    ok = load_index()
    return ok


@st.cache_resource(show_spinner="Loading voice model…")
def _load_whisper():
    try:
        from faster_whisper import WhisperModel
        return WhisperModel("base", device="cpu", compute_type="int8")
    except Exception as e:
        logger.warning("Whisper load failed: %s", e)
        return None


# ── Model inference placeholder ───────────────────────────────────────────────
# ⚠️  CHECKPOINT NOT YET PROVIDED — plug in real inference here when ready.
# Replace _run_model() body with real BD-SkinNet forward pass + GradCAM.

def _run_model(pil_img: Image.Image) -> dict:
    """
    Placeholder until checkpoint is provided (ETA ~3 days).
    Returns the same structure that the real model will return.
    Drop-in replacement: same keys, same types.
    """
    return {
        "disease":      "Tinea",
        "confidence":   0.82,
        "top2": [
            {"disease": "Tinea",             "confidence": 0.82},
            {"disease": "Contact_Dermatitis","confidence": 0.11},
        ],
        "heatmap":      None,   # np.ndarray once GradCAM is live
        "coverage_pct": 22.5,
    }

# ── Transcription helper ──────────────────────────────────────────────────────

def _transcribe(audio_bytes: bytes, fmt: str = "wav") -> str:
    try:
        from voice.pipeline import transcribe_audio
        return transcribe_audio(audio_bytes, fmt)
    except Exception as e:
        logger.warning("Transcription failed: %s", e)
        return ""


def _extract_history(transcript: str) -> dict:
    try:
        from voice.pipeline import extract_patient_history
        return extract_patient_history(transcript)
    except Exception as e:
        logger.warning("History extraction failed: %s", e)
        return {}


# ── Session state defaults ────────────────────────────────────────────────────
_DEFAULTS = {
    "transcript":   "",
    "history":      {},
    "prediction":   None,   # dict from _run_model()
    "tier_result":  None,   # dict from compute_tier()
    "pdf_bytes":    None,
    "rag_answer":   "",
    "rag_lang":     "en",
}
for _k, _v in _DEFAULTS.items():
    st.session_state.setdefault(_k, _v)

_rag_ready = _load_rag_index()


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-logo">🩺 SkinAI Bangladesh</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="sidebar-tagline">ত্বকের রোগ নির্ণয় · AI-চালিত</div>',
                unsafe_allow_html=True)
    st.markdown("---")

    st.markdown(
        '<div class="sidebar-stat">🏆 <strong>SciBlitz AI 2026</strong> — IEEE SB CUET</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sidebar-stat">🔬 <strong>7</strong> skin diseases · F1 = 92.46%</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sidebar-stat">🎙️ Bengali voice · GradCAM++ · RAG</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sidebar-stat">📚 <strong>Sources:</strong> CDC · NIH · WHO · DGHS</div>',
        unsafe_allow_html=True,
    )

    if st.session_state.prediction:
        p = st.session_state.prediction
        t = st.session_state.tier_result
        st.markdown("---")
        st.markdown(
            f'<div class="sidebar-stat">🩺 <strong>{p["disease"].replace("_"," ")}</strong>'
            f'<br>{p["confidence"]*100:.0f}% confidence</div>',
            unsafe_allow_html=True,
        )
        if t:
            tier_icons = {1: "🟢", 2: "🟡", 3: "🔴"}
            st.markdown(
                f'<div class="sidebar-stat">{tier_icons.get(t["tier"],"🔵")} '
                f'<strong>Tier {t["tier"]}</strong> — {t["urgency_label"]}</div>',
                unsafe_allow_html=True,
            )

    st.markdown("---")
    st.markdown(
        '<div class="sk-disclaimer">⚠️ এটি একটি চিকিৎসা যন্ত্র নয়।<br>'
        'সর্বদা একজন লাইসেন্সপ্রাপ্ত চিকিৎসকের পরামর্শ নিন।</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sk-disclaimer">Not a medical device.<br>'
        'Always consult a licensed physician.</div>',
        unsafe_allow_html=True,
    )


# ── Main header ───────────────────────────────────────────────────────────────
st.markdown(
    '<h1 style="font-size:2rem;font-weight:800;margin-bottom:0.1rem;">'
    '🩺 SkinAI Bangladesh</h1>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p style="font-size:1.15rem;font-weight:600;color:#475569;margin-top:0;">'
    'সঠিক রোগী → সঠিক ডাক্তার → সঠিক সময়</p>',
    unsafe_allow_html=True,
)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "🔬 রোগ নির্ণয়",
    "💬 প্রশ্ন করুন",
    "📄 রেফারেল পত্র",
])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Diagnosis & Triage
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown(
        '<div class="sk-section-head">রোগ নির্ণয় ও ট্রিয়াজ</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        "AI ব্যবহার করে ত্বকের রোগ সনাক্ত করুন এবং সঠিক চিকিৎসা স্তর নির্ধারণ করুন।",
    )

    col_left, col_right = st.columns([1, 1], gap="large")

    # ── LEFT: Voice input ─────────────────────────────────────────────────────
    with col_left:
        st.markdown(
            '<div class="sk-section-head">🎙️ ভয়েস ইনপুট (Bengali)</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div style="font-size:0.82rem;color:#94a3b8;margin-bottom:0.4rem;">'
            '🎙️ Click the mic button below to record in Bengali</div>',
            unsafe_allow_html=True,
        )
        audio_data = st.audio_input(
            "বাংলায় বলুন",
            key="audio_record",
            label_visibility="collapsed",
        )

        if audio_data is not None:
            st.audio(audio_data)
            with st.spinner("🔄 Transcribing Bengali audio…"):
                audio_bytes = audio_data.read()
                transcript = _transcribe(audio_bytes, "wav")
                st.session_state.transcript = transcript

            if transcript:
                with st.expander("📝 Transcript", expanded=False):
                    st.write(transcript)
                with st.spinner("🧠 Extracting patient history…"):
                    history = _extract_history(transcript)
                    st.session_state.history = history
            else:
                st.warning("Could not transcribe audio. Please try again in a quiet environment.")

        if st.session_state.history:
            st.markdown("")
            render_patient_history_table(st.session_state.history)
        else:
            st.markdown(
                f'<div style="background:#f8fafc;border:1px dashed #cbd5e1;'
                f'border-radius:10px;padding:1.25rem;text-align:center;'
                f'color:#94a3b8;font-size:0.88rem;margin-top:0.5rem;">'
                f'🎙️ Upload a Bengali voice recording to extract patient history.'
                f'</div>',
                unsafe_allow_html=True,
            )

    # ── RIGHT: Image upload + results ─────────────────────────────────────────
    with col_right:
        st.markdown(
            '<div class="sk-section-head">📷 ছবি আপলোড করুন</div>',
            unsafe_allow_html=True,
        )

        image_file = st.file_uploader(
            "ত্বকের ছবি আপলোড করুন (JPG / PNG)",
            type=["jpg", "jpeg", "png", "webp"],
            key="image_upload",
            label_visibility="collapsed",
        )

        if image_file is not None:
            pil_img = Image.open(image_file).convert("RGB")
            st.image(pil_img, use_container_width=True,
                     caption="Uploaded skin image")

            with st.spinner("🔬 Analysing image…"):
                pred = _run_model(pil_img)
                st.session_state.prediction = pred

            # Disease card
            render_disease_card(
                pred["disease"],
                pred["confidence"],
                pred["top2"],
            )

            # Triage
            tier_result = compute_tier(
                disease_class=pred["disease"],
                confidence=pred["confidence"],
                coverage_pct=pred["coverage_pct"],
                transcript=st.session_state.transcript,
            )
            st.session_state.tier_result = tier_result
            st.session_state.pdf_bytes = None  # reset so PDF regenerates

            render_triage_badge(tier_result)

            # GradCAM
            render_gradcam_overlay(pred["heatmap"], pred["coverage_pct"])

        else:
            st.markdown(
                f'<div style="background:#f8fafc;border:1px dashed #cbd5e1;'
                f'border-radius:10px;padding:2rem;text-align:center;'
                f'color:#94a3b8;font-size:0.88rem;">'
                f'📷 Upload a clear photo of the affected skin area.'
                f'</div>',
                unsafe_allow_html=True,
            )

            # Show cached results if already computed
            if st.session_state.prediction:
                pred = st.session_state.prediction
                render_disease_card(pred["disease"], pred["confidence"], pred["top2"])
                if st.session_state.tier_result:
                    render_triage_badge(st.session_state.tier_result)
                render_gradcam_overlay(pred["heatmap"], pred["coverage_pct"])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — RAG Chatbot
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown(
        '<div class="sk-section-head">💬 প্রশ্ন করুন — Ask a Question</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        "ত্বকের রোগ সম্পর্কে বাংলা বা ইংরেজিতে প্রশ্ন করুন।  "
        "Ask about skin conditions in Bengali or English."
    )

    if not _rag_ready:
        st.warning(
            "⚠️ Knowledge base is loading or unavailable. "
            "RAG answers will be limited. Check that build_index.py has been run."
        )

    st.info(
        "📚 Answers grounded in: **CDC · NIH · WHO · DGHS Bangladesh** only.  "
        "ওষুধের পরামর্শ দেওয়া হয় না — শুধুমাত্র শিক্ষামূলক তথ্য।",
        icon="ℹ️",
    )

    with st.form(key="rag_form", clear_on_submit=False):
        question = st.text_input(
            "আপনার প্রশ্ন লিখুন / Type your question:",
            placeholder="e.g. দাদ রোগের কারণ কী? / What causes ringworm?",
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("🔍 উত্তর খুঁজুন / Search", use_container_width=True)

    if submitted and question.strip():
        with st.spinner("🔍 Searching knowledge base…"):
            answer = answer_question(question.strip())
            # detect language from question
            lang = "bn" if any("ঀ" <= ch <= "৿" for ch in question) else "en"
            st.session_state.rag_answer = answer
            st.session_state.rag_lang = lang

    if st.session_state.rag_answer:
        st.markdown("")
        render_rag_answer(st.session_state.rag_answer, st.session_state.rag_lang)

    st.markdown(
        '<div class="sk-disclaimer">AI-generated educational content only. '
        'Not a substitute for professional medical advice.</div>',
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Referral Letter PDF
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown(
        '<div class="sk-section-head">📄 রেফারেল পত্র — Referral Letter</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        "রোগ নির্ণয়ের পর একটি সম্পূর্ণ AI রেফারেল পত্র তৈরি করুন।  "
        "Generate a complete referral letter after diagnosis."
    )

    pred = st.session_state.prediction
    tier = st.session_state.tier_result
    history = st.session_state.history

    if pred and tier:
        # Summary card before generating PDF
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(
                f'<div class="sk-card"><div class="sk-card-title">Disease</div>'
                f'<div class="sk-card-value">{pred["disease"].replace("_"," ")}</div></div>',
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f'<div class="sk-card"><div class="sk-card-title">Confidence</div>'
                f'<div class="sk-card-value">{pred["confidence"]*100:.0f}%</div></div>',
                unsafe_allow_html=True,
            )
        with c3:
            tier_colors = {1: "#059669", 2: "#d97706", 3: "#dc2626"}
            color = tier_colors.get(tier["tier"], "#475569")
            st.markdown(
                f'<div class="sk-card"><div class="sk-card-title">Triage Tier</div>'
                f'<div class="sk-card-value" style="color:{color};">'
                f'Tier {tier["tier"]} — {tier["urgency_label"]}</div></div>',
                unsafe_allow_html=True,
            )

        st.markdown("")

        if st.button("📄 Generate Referral Letter", use_container_width=True, type="primary"):
            with st.spinner("Generating PDF referral letter…"):
                from model.disease_labels import get_bengali
                session_data = {
                    # Patient history (Section 1)
                    **history,
                    # GradCAM (Section 2)
                    "heatmap":       pred.get("heatmap"),
                    "coverage_pct":  pred.get("coverage_pct", 0.0),
                    # Diagnosis (Section 3)
                    "disease_class":   pred["disease"],
                    "disease_bengali": get_bengali(pred["disease"]),
                    "confidence":      pred["confidence"],
                    "top2":            pred.get("top2", []),
                    # Triage (Section 4)
                    "tier":            tier["tier"],
                    "urgency_label":   tier["urgency_label"],
                    "action":          tier["action"],
                    "facility":        tier["facility"],
                    "bengali_text":    tier["bengali_text"],
                    "transcript":      st.session_state.transcript,
                }
                try:
                    pdf_bytes = generate_referral_pdf(session_data)
                    st.session_state.pdf_bytes = pdf_bytes
                    st.success("✅ Referral letter generated!")
                except Exception as e:
                    st.error(f"PDF generation failed: {e}")
                    st.session_state.pdf_bytes = None

        render_referral_download_button(st.session_state.pdf_bytes)

    else:
        st.markdown(
            f'<div style="background:#f8fafc;border:1px dashed #cbd5e1;'
            f'border-radius:12px;padding:2rem 1.5rem;text-align:center;">'
            f'<div style="font-size:2.5rem;margin-bottom:0.75rem;">📷</div>'
            f'<div style="font-weight:600;color:#475569;margin-bottom:0.4rem;">'
            f'Complete Tab 1 first</div>'
            f'<div style="font-size:0.85rem;color:#94a3b8;">'
            f'Upload a skin image in the রোগ নির্ণয় tab to enable the referral letter.'
            f'</div></div>',
            unsafe_allow_html=True,
        )
        render_referral_download_button(None)

    st.markdown(
        '<div class="sk-disclaimer">This referral letter is AI-generated for informational '
        'purposes only. It does not replace a clinical diagnosis by a licensed physician. '
        '| SkinAI Bangladesh — SciBlitz AI Challenge 2026</div>',
        unsafe_allow_html=True,
    )
