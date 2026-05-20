# UI OVERHAUL — 2026-05-20
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
    # new components
    render_sidebar_pipeline,
    render_stat_card,
    render_tier_banner,
    render_chat_message,
    render_suggested_questions,
    render_referral_preview,
    # existing components
    render_gradcam_overlay,
    render_patient_history_table,
    render_disease_card,
    render_referral_download_button,
    check_image_quality,
)
from severity.engine import compute_tier
from pdf_gen.referral import generate_referral_pdf
from rag.retriever import load_index, answer_question
from map.hospital_finder import (
    find_nearest_hospitals,
    render_hospital_map,
    get_district_coords,
    _DEFAULT_LAT,
    _DEFAULT_LON,
)

logger = logging.getLogger(__name__)

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="SkinAI Bangladesh",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()


# ── Cached loaders ────────────────────────────────────────────────────────────

@st.cache_resource(show_spinner="Loading RAG knowledge base…")
def _load_rag_index():
    return load_index()


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

def _run_model(pil_img: Image.Image) -> dict:
    return {
        "disease":      "Tinea",
        "confidence":   0.82,
        "top2": [
            {"disease": "Tinea",              "confidence": 0.82},
            {"disease": "Contact_Dermatitis", "confidence": 0.11},
        ],
        "heatmap":      None,
        "coverage_pct": 22.5,
    }


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
    "transcript":       "",
    "history":          {},
    "prediction":       None,
    "tier_result":      None,
    "nearest_hospital": None,
    "pdf_bytes":        None,
    "rag_answer":       "",
    "rag_lang":         "en",
    "chat_history":     [],
}
for _k, _v in _DEFAULTS.items():
    st.session_state.setdefault(_k, _v)

_rag_ready = _load_rag_index()


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    # ── Logo + tagline ────────────────────────────────────────────────────────
    st.markdown(
        '<div class="sidebar-logo">🩺 SkinAI Bangladesh</div>'
        '<div class="sidebar-tagline">ত্বকের রোগ নির্ণয় · AI-চালিত ট্রাইয়েজ</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # ── Pipeline progress tracker ─────────────────────────────────────────────
    st.markdown(
        '<div class="sidebar-stat" style="font-size:0.72rem;font-weight:700;'
        'letter-spacing:0.06em;text-transform:uppercase;margin-bottom:0.25rem;">'
        '📊 Patient Journey</div>',
        unsafe_allow_html=True,
    )
    render_sidebar_pipeline(
        voice_done    = bool(st.session_state.transcript),
        image_done    = st.session_state.prediction is not None,
        diagnosis_done= st.session_state.tier_result is not None,
        referral_done = st.session_state.pdf_bytes is not None,
    )

    st.markdown("---")

    # ── Knowledge sources ─────────────────────────────────────────────────────
    st.markdown(
        '<div style="font-size:0.68rem;color:#4A6080 !important;'
        'text-transform:uppercase;letter-spacing:0.06em;margin-bottom:0.3rem;">'
        'Knowledge Sources</div>'
        '<div>'
        '<span class="source-pill">CDC</span>'
        '<span class="source-pill">NIH</span>'
        '<span class="source-pill">WHO</span>'
        '<span class="source-pill">DGHS</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # ── About BD-SkinNet (collapsed by default) ────────────────────────────────
    with st.expander("ℹ️ About BD-SkinNet", expanded=False):
        render_stat_card("Clinical Accuracy", "92.46%",  color="#27AE60")
        render_stat_card("Conditions Covered", "7",      color="#1A6FA8")
        render_stat_card("Data Source",  "BD Hospitals", color="#0D9E75")
        st.markdown(
            '<div style="font-size:0.68rem;color:#4A6080 !important;margin-top:0.5rem;'
            'text-align:center;">Faridpur MCH · Rangpur MCH<br>Swin Transformer + CBAM</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ── Demo mode ─────────────────────────────────────────────────────────────
    st.markdown(
        '<div class="sidebar-stat" style="font-size:0.72rem;font-weight:700;'
        'margin-bottom:0.2rem;">🎬 Demo Mode</div>',
        unsafe_allow_html=True,
    )
    if st.button(
        "🎬 Load Demo — Scabies Tier 3",
        use_container_width=True,
        help="Pre-loads a Scabies Tier 3 case so all tabs are populated instantly.",
        key="demo_btn",
    ):
        _demo_transcript = "জ্বর আছে, চুলকানি ছড়িয়ে পড়ছে, ব্যথা হচ্ছে"
        _demo_pred = {
            "disease":      "Scabies",
            "confidence":   0.38,
            "top2": [
                {"disease": "Scabies", "confidence": 0.38},
                {"disease": "Eczema",  "confidence": 0.22},
            ],
            "heatmap":      None,
            "coverage_pct": 45.0,
        }
        _demo_tier = compute_tier(
            disease_class=_demo_pred["disease"],
            confidence=_demo_pred["confidence"],
            coverage_pct=_demo_pred["coverage_pct"],
            transcript=_demo_transcript,
        )
        _demo_history = {
            "patient_name":       "রহিম (Demo)",
            "patient_age":        "৩৫",
            "chief_complaint":    "সারা শরীরে তীব্র চুলকানি ও ফুসকুড়ি",
            "symptoms":           ["intense itching", "spreading rash", "skin thickening"],
            "affected_area":      "বাহু, পেট, উরু",
            "duration":           "১০ দিন",
            "progression":        "দ্রুত ছড়িয়ে পড়ছে",
            "previous_treatment": "কোনো চিকিৎসা নেওয়া হয়নি",
            "associated_symptoms": ["জ্বর", "ব্যথা"],
        }
        st.session_state.prediction       = _demo_pred
        st.session_state.tier_result      = _demo_tier
        st.session_state.history          = _demo_history
        st.session_state.transcript       = _demo_transcript
        st.session_state.nearest_hospital = None
        st.session_state.pdf_bytes        = None
        st.session_state.chat_history     = []
        st.rerun()

    st.markdown("---")

    # ── Disclaimer ────────────────────────────────────────────────────────────
    st.markdown(
        '<div class="sk-disclaimer">'
        'এটি একটি চিকিৎসা যন্ত্র নয়।<br>'
        'সর্বদা একজন লাইসেন্সপ্রাপ্ত চিকিৎসকের পরামর্শ নিন।<br>'
        '<span style="margin-top:0.25rem;display:block;">'
        'Not a medical device. Consult a licensed physician.</span>'
        '</div>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# HERO HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="hero-title">🩺 SkinAI Bangladesh</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="hero-tagline">সঠিক রোগী → সঠিক ডাক্তার → সঠিক সময়</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="stat-bar">'
    '<span class="stat-chip">🔬 7 Disease Classes</span>'
    '<span class="stat-chip">📊 F1 = 92.46%</span>'
    '<span class="stat-chip">🏥 BD Clinical Data</span>'
    '<span class="stat-chip">🔒 No Login Required</span>'
    '</div>',
    unsafe_allow_html=True,
)


# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "🔬 রোগ নির্ণয়",
    "💬 প্রশ্ন করুন",
    "📄 রেফারেল পত্র",
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Diagnosis & Triage
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    col_left, col_right = st.columns([1, 1], gap="large")

    # ── LEFT COLUMN: Voice Input ───────────────────────────────────────────────
    with col_left:
        st.markdown(
            '<div class="card-section-header">'
            '<span style="font-size:1.1rem;">🎙️</span>'
            '<div>'
            '<div class="card-section-title">ভয়েস ইনপুট (Bengali)</div>'
            '<div class="card-section-sub">(ঐচ্ছিক — optional)</div>'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="info-box">'
            '🤖 Bengali voice recording allows AI to extract patient history automatically'
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div style="font-size:0.78rem;color:#718096;margin-bottom:0.2rem;">'
            '⏺ Option 1 — Record directly</div>',
            unsafe_allow_html=True,
        )
        audio_data = st.audio_input(
            "বাংলায় বলুন",
            key="audio_record",
            label_visibility="collapsed",
        )

        st.markdown(
            '<div style="font-size:0.78rem;color:#718096;margin:0.45rem 0 0.2rem 0;">'
            '📁 Option 2 — Upload voice file (WAV / MP3 / OGG)</div>',
            unsafe_allow_html=True,
        )
        audio_file = st.file_uploader(
            "Upload audio",
            type=["wav", "mp3", "ogg", "webm", "m4a"],
            key="audio_file",
            label_visibility="collapsed",
        )

        # Process audio
        audio_bytes = None
        audio_fmt   = "wav"
        if audio_data is not None:
            audio_bytes = audio_data.read()
            audio_fmt   = "wav"
            st.audio(audio_data)
        elif audio_file is not None:
            audio_bytes = audio_file.read()
            audio_fmt   = audio_file.name.rsplit(".", 1)[-1].lower()
            st.audio(audio_file)

        if audio_bytes:
            with st.spinner("🔄 Transcribing Bengali audio…"):
                _transcript = _transcribe(audio_bytes, audio_fmt)
                st.session_state.transcript = _transcript

            if _transcript:
                st.markdown(
                    f'<div class="transcript-box">📝 {_transcript}</div>',
                    unsafe_allow_html=True,
                )
                with st.spinner("🧠 Extracting patient history from voice…"):
                    _history = _extract_history(_transcript)
                    st.session_state.history = _history
            else:
                st.warning(
                    "Could not transcribe. Please speak clearly or upload a WAV file.\n\n"
                    "ট্রান্সক্রিপ্ট করা যাচ্ছে না — স্পষ্টভাবে বলুন বা WAV ফাইল আপলোড করুন।"
                )

        # Patient history display
        if st.session_state.history:
            st.markdown("")
            render_patient_history_table(st.session_state.history)
        else:
            st.markdown(
                '<div style="background:#F8FAFC;border:1.5px dashed #E2E8F0;border-radius:10px;'
                'padding:1.5rem;text-align:center;color:#718096;font-size:0.85rem;margin-top:0.5rem;">'
                '🎙️ বাংলায় রোগীর ইতিহাস রেকর্ড করুন<br>'
                '<span style="font-size:0.75rem;">Record patient history in Bengali to auto-extract details</span>'
                '</div>',
                unsafe_allow_html=True,
            )

    # ── RIGHT COLUMN: Image Upload + Results ───────────────────────────────────
    with col_right:
        st.markdown(
            '<div class="card-section-header">'
            '<span style="font-size:1.1rem;">📷</span>'
            '<div>'
            '<div class="card-section-title">ছবি আপলোড করুন</div>'
            '<div class="card-section-sub" style="color:#E67E22;font-weight:600;">(প্রয়োজনীয় — required)</div>'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        image_file = st.file_uploader(
            "ত্বকের ছবি আপলোড করুন (JPG / PNG)",
            type=["jpg", "jpeg", "png", "webp"],
            key="image_upload",
            label_visibility="collapsed",
        )

        if image_file is not None:
            try:
                pil_img = Image.open(image_file).convert("RGB")
            except Exception:
                st.error(
                    "⚠️ Could not read this image. Please upload a valid JPG or PNG.\n\n"
                    "ছবিটি পড়া যাচ্ছে না। বৈধ JPG বা PNG ফাইল আপলোড করুন।"
                )
                st.stop()

            # Image quality check
            is_blurry, blur_var = check_image_quality(pil_img)
            if is_blurry:
                st.markdown(
                    f'<div class="blur-warning">'
                    f'⚠️ <strong>Image may be blurry</strong> (sharpness: {blur_var:.0f}). '
                    f'ছবিটি অস্পষ্ট হতে পারে — ভালো ফলাফলের জন্য স্পষ্ট ছবি ব্যবহার করুন।'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            st.image(pil_img, use_container_width=True, caption="Uploaded skin image")

            st.session_state.pdf_bytes    = None
            st.session_state.chat_history = []

            with st.spinner("🔬 Analysing skin image…"):
                pred = _run_model(pil_img)
                st.session_state.prediction = pred

            # Compute tier (stored → rendered below columns)
            tier_result = compute_tier(
                disease_class=pred["disease"],
                confidence=pred["confidence"],
                coverage_pct=pred["coverage_pct"],
                transcript=st.session_state.transcript,
            )
            st.session_state.tier_result = tier_result

            # Disease result card
            render_disease_card(pred["disease"], pred["confidence"], pred["top2"])

            # GradCAM
            render_gradcam_overlay(pred["heatmap"], pred["coverage_pct"])

        else:
            # No new upload — show cached results if available
            if st.session_state.prediction:
                pred = st.session_state.prediction
                st.markdown(
                    '<div class="info-box-teal" style="margin-bottom:0.75rem;">'
                    '✓ Previous analysis loaded — upload a new image to re-analyse</div>',
                    unsafe_allow_html=True,
                )
                render_disease_card(pred["disease"], pred["confidence"], pred["top2"])
                render_gradcam_overlay(pred["heatmap"], pred["coverage_pct"])
            else:
                st.markdown(
                    '<div style="background:#F8FAFC;border:1.5px dashed #E2E8F0;border-radius:10px;'
                    'padding:2.5rem 1.5rem;text-align:center;color:#718096;font-size:0.88rem;">'
                    '<div style="font-size:2.5rem;margin-bottom:0.6rem;">📷</div>'
                    'আক্রান্ত ত্বকের একটি স্পষ্ট ছবি আপলোড করুন<br>'
                    '<span style="font-size:0.78rem;">Upload a clear photo of the affected skin area</span>'
                    '</div>',
                    unsafe_allow_html=True,
                )

    # ── FULL-WIDTH: Severity Tier Banner (below both columns) ──────────────────
    if st.session_state.tier_result:
        _tr = st.session_state.tier_result
        st.markdown('<div style="margin-top:0.25rem;"></div>', unsafe_allow_html=True)
        render_tier_banner(
            tier          = _tr["tier"],
            urgency_label = _tr["urgency_label"],
            action_text   = _tr["action"],
            bn_text       = _tr["bengali_text"],
            facility      = _tr["facility"],
        )

        # ── Tier 3 only: Emergency hospital map ───────────────────────────────
        if _tr["tier"] == 3:
            st.markdown(
                '<div class="card-section-header" style="margin-top:0.25rem;">'
                '<span style="font-size:1.1rem;color:#C0392B;">🏥</span>'
                '<div>'
                '<div class="card-section-title" style="color:#C0392B;">'
                'Nearest Emergency Hospitals · নিকটতম হাসপাতাল</div>'
                '</div>'
                '</div>',
                unsafe_allow_html=True,
            )
            district = st.text_input(
                "Enter your district (e.g. Rangpur, Dhaka, Chittagong):",
                key="district_input",
                placeholder="Type district name…",
            )
            if district:
                coords   = get_district_coords(district)
                user_lat = coords[0] if coords else _DEFAULT_LAT
                user_lon = coords[1] if coords else _DEFAULT_LON

                _hcache = st.session_state.setdefault("hospital_cache", {})
                _dk     = district.strip().lower()
                if _dk not in _hcache:
                    with st.spinner("🔍 Finding nearest hospitals…"):
                        _hcache[_dk] = find_nearest_hospitals(user_lat, user_lon, n=5)
                hospitals = _hcache[_dk]

                if hospitals:
                    st.session_state.nearest_hospital = hospitals[0]
                    for i, h in enumerate(hospitals):
                        phone_html = (
                            f' &nbsp;·&nbsp; 📞 {h["phone"]}' if h.get("phone") else ""
                        )
                        st.markdown(
                            f'<div class="hospital-card">'
                            f'  <div class="hospital-rank">#{i+1}</div>'
                            f'  <div>'
                            f'    <div class="hospital-name">{h["name"]}</div>'
                            f'    <div class="hospital-meta">'
                            f'      📍 {h["address"]} &nbsp;·&nbsp; 🚗 {h["dist_km"]} km{phone_html}'
                            f'    </div>'
                            f'  </div>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )
                    try:
                        from streamlit_folium import st_folium
                        with st.spinner("🗺️ Rendering map…"):
                            fmap = render_hospital_map(hospitals, user_lat, user_lon)
                        if fmap:
                            st_folium(fmap, use_container_width=True, height=380)
                    except Exception:
                        pass
                else:
                    st.warning(
                        "No hospitals found nearby. Try a different district name.\n\n"
                        "নিকটে কোনো হাসপাতাল পাওয়া যায়নি। অন্য জেলার নাম দিয়ে চেষ্টা করুন।"
                    )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — RAG Chatbot
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    # ── Source info bar ───────────────────────────────────────────────────────
    if not _rag_ready:
        st.warning(
            "⚠️ Knowledge base loading or unavailable. "
            "Check that build_index.py has been run."
        )

    st.markdown(
        '<div class="chat-outer-info">'
        '<span>📚 Answers grounded in:</span>'
        '<span class="info-source-pill">CDC</span>'
        '<span class="info-source-pill">NIH</span>'
        '<span class="info-source-pill">WHO</span>'
        '<span class="info-source-pill">DGHS Bangladesh</span>'
        '<span style="margin-left:auto;font-size:0.75rem;color:#4A5568;">'
        'ওষুধের পরামর্শ দেওয়া হয় না · শুধু শিক্ষামূলক তথ্য</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    # ── Disease context ────────────────────────────────────────────────────────
    _disease_context_str = None
    if st.session_state.prediction:
        _p = st.session_state.prediction
        _disease_display    = _p["disease"].replace("_", " ")
        _conf_pct           = int(_p["confidence"] * 100)
        _disease_context_str = f"{_disease_display} ({_conf_pct}% confidence)"
        st.success(
            f"🩺 **Current diagnosis: {_disease_display}** ({_conf_pct}%) — "
            "answering questions in this clinical context.",
            icon="🩺",
        )

    # ── Chat container ─────────────────────────────────────────────────────────
    if st.session_state.chat_history:
        msgs_html = "".join(
            render_chat_message(
                role    = m["role"],
                content = m["content"],
                sources = ["CDC", "NIH", "WHO", "DGHS"] if m["role"] == "assistant" else [],
            )
            for m in st.session_state.chat_history
        )
        st.markdown(
            f'<div class="chat-container" id="skinai-chat">'
            f'{msgs_html}'
            f'<div id="chat-bottom"></div>'
            f'</div>'
            f'<script>'
            f'(function(){{var b=document.getElementById("chat-bottom");'
            f'if(b)b.scrollIntoView({{behavior:"smooth"}});}})();'
            f'</script>',
            unsafe_allow_html=True,
        )
        if st.button("🗑️ Clear Chat", key="clear_chat_btn"):
            st.session_state.chat_history = []
            st.session_state.rag_answer   = ""
            st.rerun()
    else:
        # Empty state
        st.markdown(
            '<div class="chat-container">'
            '<div class="chat-empty">'
            '<div class="chat-empty-icon">💬</div>'
            '<div class="chat-empty-text">ত্বকের রোগ সম্পর্কে প্রশ্ন করুন</div>'
            '<div style="font-size:0.78rem;color:#A0AEC0;">'
            'Ask about skin conditions in Bengali or English</div>'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div style="font-size:0.82rem;font-weight:600;color:#4A5568;'
            'margin:0.5rem 0 0.35rem 0;">সাজেস্টেড প্রশ্ন · Suggested Questions</div>',
            unsafe_allow_html=True,
        )
        _suggested = render_suggested_questions([
            "টিনিয়া কর্পোরিস কী?",
            "চর্মরোগের লক্ষণ কী?",
            "কখন ডাক্তার দেখাব?",
        ])
        if _suggested:
            st.session_state.chat_history.append({"role": "user", "content": _suggested})
            _lang = "bn" if any("ঀ" <= ch <= "৿" for ch in _suggested) else "en"
            with st.spinner("🔍 Searching knowledge base…"):
                _answer = answer_question(
                    _suggested,
                    lang=_lang,
                    disease_context=_disease_context_str,
                )
            st.session_state.chat_history.append({
                "role": "assistant", "content": _answer, "lang": _lang
            })
            st.session_state.rag_answer = _answer
            st.session_state.rag_lang   = _lang
            st.rerun()

    # ── Chat input ─────────────────────────────────────────────────────────────
    _question = st.chat_input(
        "আপনার প্রশ্ন লিখুন / Type your question… (Bengali or English)",
        key="chat_input",
    )
    if _question and _question.strip():
        _q = _question.strip()
        st.session_state.chat_history.append({"role": "user", "content": _q})
        _lang = "bn" if any("ঀ" <= ch <= "৿" for ch in _q) else "en"
        with st.spinner("🔍 Searching knowledge base…"):
            _answer = answer_question(
                _q,
                lang=_lang,
                disease_context=_disease_context_str,
            )
        st.session_state.chat_history.append({
            "role": "assistant", "content": _answer, "lang": _lang
        })
        st.session_state.rag_answer = _answer
        st.session_state.rag_lang   = _lang
        st.rerun()

    st.markdown(
        '<div class="sk-disclaimer">'
        'AI-generated educational content only. Not a substitute for professional medical advice.'
        '</div>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Referral Letter PDF
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown(
        '<div class="card-section-header">'
        '<span style="font-size:1.1rem;">📄</span>'
        '<div>'
        '<div class="card-section-title">রেফারেল পত্র · Referral Letter</div>'
        '<div class="card-section-sub">AI-generated · Zero manual input required</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    pred    = st.session_state.prediction
    tier    = st.session_state.tier_result
    history = st.session_state.history

    if pred and tier:
        # ── PDF Preview cards ─────────────────────────────────────────────────
        render_referral_preview(pred, tier, history)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Generate button ────────────────────────────────────────────────────
        if not st.session_state.pdf_bytes:
            if st.button(
                "📋 Generate Referral Letter",
                use_container_width=True,
                type="primary",
                key="gen_pdf_btn",
            ):
                with st.spinner("📄 Generating PDF referral letter…"):
                    from model.disease_labels import get_bengali as _get_bn
                    session_data = {
                        **history,
                        "heatmap":         pred.get("heatmap"),
                        "coverage_pct":    pred.get("coverage_pct", 0.0),
                        "disease_class":   pred["disease"],
                        "disease_bengali": _get_bn(pred["disease"]),
                        "confidence":      pred["confidence"],
                        "top2":            pred.get("top2", []),
                        "tier":            tier["tier"],
                        "urgency_label":   tier["urgency_label"],
                        "action":          tier["action"],
                        "facility":        tier["facility"],
                        "bengali_text":    tier["bengali_text"],
                        "transcript":      st.session_state.transcript,
                        "hospital_name":    (st.session_state.nearest_hospital or {}).get("name", ""),
                        "hospital_address": (st.session_state.nearest_hospital or {}).get("address", ""),
                    }
                    try:
                        pdf_bytes = generate_referral_pdf(session_data)
                        st.session_state.pdf_bytes = pdf_bytes
                        st.success("✅ Referral letter generated!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"PDF generation failed: {e}")
                        st.session_state.pdf_bytes = None

        # ── Download button ────────────────────────────────────────────────────
        render_referral_download_button(st.session_state.pdf_bytes)

    else:
        # ── Empty state with progress indicator ───────────────────────────────
        _voice_done     = bool(st.session_state.transcript)
        _image_done     = st.session_state.prediction is not None
        _diagnosis_done = st.session_state.tier_result is not None

        def _prog_dot(done: bool, is_next: bool = False) -> str:
            if done:
                return '<div class="prog-dot prog-dot-done">✓</div>'
            elif is_next:
                return '<div class="prog-dot prog-dot-next"></div>'
            return '<div class="prog-dot"></div>'

        st.markdown(
            f'<div class="referral-empty">'
            f'<div style="font-size:3rem;margin-bottom:0.75rem;">📋</div>'
            f'<div style="font-weight:700;font-size:1.05rem;color:#4A5568;margin-bottom:0.3rem;">'
            f'রেফারেল পত্র পেতে রোগ নির্ণয় সম্পন্ন করুন</div>'
            f'<div style="font-size:0.82rem;color:#718096;margin-bottom:1rem;">'
            f'Complete the diagnosis steps to generate your referral letter</div>'
            f'<div class="referral-progress-row">'
            f'{_prog_dot(_voice_done)} 🎙️ Voice input (optional)</div>'
            f'<div class="referral-progress-row">'
            f'{_prog_dot(_image_done, not _image_done)} 📷 Upload skin image &nbsp;<strong>← Start here</strong></div>'
            f'<div class="referral-progress-row">'
            f'{_prog_dot(_diagnosis_done)} 🧠 Run diagnosis</div>'
            f'<div class="referral-progress-row">'
            f'{_prog_dot(False)} 📄 Generate referral</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        render_referral_download_button(None)

    st.markdown(
        '<div class="sk-disclaimer">'
        'This referral letter is AI-generated for informational purposes only. '
        'It does not replace a clinical diagnosis by a licensed physician.'
        '</div>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# APP FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="app-footer">'
    'SciBlitz AI Challenge 2026 · IEEE SB CUET · Track A: Health &amp; Society'
    '</div>',
    unsafe_allow_html=True,
)
