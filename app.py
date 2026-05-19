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
    check_image_quality,
)
from severity.engine import compute_tier
from pdf_gen.referral import generate_referral_pdf
from rag.retriever import load_index, answer_question
from map.hospital_finder import find_nearest_hospitals, render_hospital_map, get_district_coords, _DEFAULT_LAT, _DEFAULT_LON

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
    if not ok:
        # Index not built yet (Docker build may have failed silently) — build now
        try:
            from rag.build_index import build as _build_index
            logger.info("FAISS index missing — building at startup…")
            _build_index()
            ok = load_index()
        except Exception as exc:
            logger.error("RAG index build failed at startup: %s", exc)
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
    "transcript":        "",
    "history":           {},
    "prediction":        None,   # dict from _run_model()
    "tier_result":       None,   # dict from compute_tier()
    "nearest_hospital":  None,   # dict from find_nearest_hospitals()[0], Tier 3 only
    "pdf_bytes":         None,
    "rag_answer":        "",
    "rag_lang":          "en",
    "chat_history":      [],     # list of {role, content, lang} for Tab 2 chat UI
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

    # ── Pipeline progress tracker ─────────────────────────────────────────────
    st.markdown("---")
    st.markdown(
        '<div class="sidebar-stat"><strong>📊 Pipeline Progress</strong></div>',
        unsafe_allow_html=True,
    )
    _progress_steps = [
        ("🎙️ Voice recorded",  bool(st.session_state.transcript)),
        ("📷 Image analysed",   st.session_state.prediction is not None),
        ("🧠 Diagnosis ready",  st.session_state.tier_result is not None),
        ("📄 Referral ready",   st.session_state.pdf_bytes is not None),
    ]
    for _label, _done in _progress_steps:
        _tick  = "✅" if _done else "⬜"
        _color = "#60a5fa" if _done else "#64748b"
        st.markdown(
            f'<div class="sidebar-stat" style="color:{_color} !important;">'
            f'{_tick} {_label}</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ── Demo mode ─────────────────────────────────────────────────────────────
    st.markdown(
        '<div class="sidebar-stat">🎬 <strong>Demo Mode</strong></div>',
        unsafe_allow_html=True,
    )
    if st.button(
        "🎬 Load Demo (Scabies — Tier 3)",
        use_container_width=True,
        help="Pre-loads a Scabies Tier 3 case so all tabs are populated instantly.",
        key="demo_btn",
    ):
        _demo_transcript = "জ্বর আছে, চুলকানি ছড়িয়ে পড়ছে, ব্যথা হচ্ছে"
        _demo_pred = {
            "disease":      "Scabies",
            "confidence":   0.38,   # < 0.40 → Signal 2 → Tier 3
            "top2": [
                {"disease": "Scabies", "confidence": 0.38},
                {"disease": "Eczema",  "confidence": 0.22},
            ],
            "heatmap":      None,
            "coverage_pct": 45.0,   # > 40 % → Signal 3 escalates further
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

        # ── Option A: in-browser mic recorder ────────────────────────────
        st.markdown(
            '<div style="font-size:0.82rem;color:#94a3b8;margin-bottom:0.25rem;">'
            '⏺ Option 1 — Record directly (click mic, speak, click stop)</div>',
            unsafe_allow_html=True,
        )
        audio_data = st.audio_input(
            "বাংলায় বলুন",
            key="audio_record",
            label_visibility="collapsed",
        )

        # ── Option B: file upload fallback ────────────────────────────────
        st.markdown(
            '<div style="font-size:0.82rem;color:#94a3b8;margin:0.5rem 0 0.25rem 0;">'
            '📁 Option 2 — Upload a voice file (WAV / MP3 / OGG)</div>',
            unsafe_allow_html=True,
        )
        audio_file = st.file_uploader(
            "Upload audio",
            type=["wav", "mp3", "ogg", "webm", "m4a"],
            key="audio_file",
            label_visibility="collapsed",
        )

        # ── Process whichever source provided audio ───────────────────────
        audio_bytes = None
        audio_fmt = "wav"

        if audio_data is not None:
            audio_bytes = audio_data.read()
            audio_fmt = "wav"
            st.audio(audio_data)
        elif audio_file is not None:
            audio_bytes = audio_file.read()
            audio_fmt = audio_file.name.rsplit(".", 1)[-1].lower()
            st.audio(audio_file)

        if audio_bytes:
            with st.spinner("🔄 Transcribing Bengali audio…"):
                transcript = _transcribe(audio_bytes, audio_fmt)
                st.session_state.transcript = transcript

            if transcript:
                with st.expander("📝 Transcript", expanded=False):
                    st.write(transcript)
                with st.spinner("🧠 Extracting patient history…"):
                    history = _extract_history(transcript)
                    st.session_state.history = history
            else:
                st.warning("Could not transcribe. Please speak clearly, or try uploading a WAV file.")

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
            try:
                pil_img = Image.open(image_file).convert("RGB")
            except Exception:
                st.error(
                    "⚠️ Could not read this image file. "
                    "Please upload a valid JPG or PNG.\n\n"
                    "ছবিটি পড়া যাচ্ছে না। "
                    "অনুগ্রহ করে একটি বৈধ JPG বা PNG ফাইল আপলোড করুন।"
                )
                st.stop()

            st.image(pil_img, use_container_width=True,
                     caption="Uploaded skin image")

            # ── Image quality check ───────────────────────────────────────
            is_blurry, blur_var = check_image_quality(pil_img)
            if is_blurry:
                st.markdown(
                    f'<div class="blur-warning">'
                    f'⚠️ <strong>Image may be blurry</strong> (sharpness score: {blur_var:.0f}). '
                    f'ছবিটি অস্পষ্ট হতে পারে — ভালো ফলাফলের জন্য স্পষ্ট আলোকিত ছবি ব্যবহার করুন। '
                    f'Processing anyway…'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            st.session_state.pdf_bytes = None   # reset before new inference
            st.session_state.chat_history = []  # clear stale chat on new diagnosis

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

            render_triage_badge(tier_result)

            # ── Tier 3 only: Emergency hospital map ───────────────────────
            if tier_result["tier"] == 3:
                st.markdown(
                    '<div class="sk-section-head" style="color:#dc2626;">'
                    '🏥 Nearest Emergency Hospitals — নিকটতম হাসপাতাল</div>',
                    unsafe_allow_html=True,
                )
                district = st.text_input(
                    "Enter your district (e.g. Rangpur, Dhaka, Chittagong):",
                    key="district_input",
                    placeholder="Type district name…",
                )
                if district:
                    coords = get_district_coords(district)
                    user_lat = coords[0] if coords else _DEFAULT_LAT
                    user_lon = coords[1] if coords else _DEFAULT_LON
                    # Cache per district so repeated lookups don't hammer Overpass API
                    _hcache = st.session_state.setdefault("hospital_cache", {})
                    _dk = district.strip().lower()
                    if _dk not in _hcache:
                        with st.spinner("🔍 Finding nearest hospitals…"):
                            _hcache[_dk] = find_nearest_hospitals(user_lat, user_lon, n=5)
                    hospitals = _hcache[_dk]
                    if hospitals:
                        # Store top hospital for PDF Section 4
                        st.session_state.nearest_hospital = hospitals[0]
                        # Table
                        st.markdown("**Top 5 nearest hospitals:**")
                        for i, h in enumerate(hospitals):
                            st.markdown(
                                f'<div class="sk-card" style="margin-bottom:0.5rem;">'
                                f'<span style="font-weight:700;color:#dc2626;">#{i+1}</span> '
                                f'<strong>{h["name"]}</strong><br>'
                                f'<span style="font-size:0.82rem;color:#475569;">'
                                f'📍 {h["address"]} &nbsp;|&nbsp; 🚗 {h["dist_km"]} km'
                                + (f' &nbsp;|&nbsp; 📞 {h["phone"]}' if h.get("phone") else "")
                                + '</span></div>',
                                unsafe_allow_html=True,
                            )
                        # Folium map
                        try:
                            from streamlit_folium import st_folium
                            with st.spinner("🗺️ Rendering hospital map…"):
                                fmap = render_hospital_map(hospitals, user_lat, user_lon)
                            if fmap:
                                st_folium(fmap, use_container_width=True, height=380)
                        except Exception:
                            pass
                    else:
                        st.warning(
                            "🏥 No hospitals found nearby. "
                            "Try a different or more specific district name.\n\n"
                            "নিকটে কোনো হাসপাতাল পাওয়া যায়নি। "
                            "অন্য জেলার নাম দিয়ে আবার চেষ্টা করুন।"
                        )

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
# TAB 2 — RAG Chatbot (context-aware, with chat history)
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

    # ── Disease context banner ────────────────────────────────────────────────
    _disease_context_str: str | None = None
    if st.session_state.prediction:
        _p = st.session_state.prediction
        _disease_display = _p["disease"].replace("_", " ")
        _conf_pct = int(_p["confidence"] * 100)
        _disease_context_str = f"{_disease_display} ({_conf_pct}% confidence)"
        st.success(
            f"💊 **Current diagnosis: {_disease_display}** ({_conf_pct}%) — "
            "answering questions in this context.",
            icon="🩺",
        )

    # ── Clear chat button ─────────────────────────────────────────────────────
    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat", key="clear_chat_btn"):
            st.session_state.chat_history = []
            st.session_state.rag_answer = ""
            st.rerun()

    # ── Chat history display ──────────────────────────────────────────────────
    for _msg in st.session_state.chat_history:
        with st.chat_message(_msg["role"]):
            if _msg["role"] == "assistant":
                render_rag_answer(_msg["content"], _msg.get("lang", "en"))
            else:
                st.write(_msg["content"])

    # ── Chat input (always at bottom) ─────────────────────────────────────────
    _question = st.chat_input(
        "আপনার প্রশ্ন লিখুন / Type your question… (Bengali or English)",
        key="chat_input",
    )
    if _question and _question.strip():
        _q = _question.strip()
        # Append user turn
        st.session_state.chat_history.append({"role": "user", "content": _q})

        # Detect language
        _lang = "bn" if any("ঀ" <= ch <= "৿" for ch in _q) else "en"

        # Get answer with disease context injected into system prompt
        with st.spinner("🔍 Searching knowledge base…"):
            _answer = answer_question(
                _q,
                lang=_lang,
                disease_context=_disease_context_str,
            )

        # Append assistant turn
        st.session_state.chat_history.append({
            "role":    "assistant",
            "content": _answer,
            "lang":    _lang,
        })

        # Keep backward-compat fields (used in PDF flow)
        st.session_state.rag_answer = _answer
        st.session_state.rag_lang   = _lang

        st.rerun()

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
            with st.spinner("📄 Generating PDF referral letter…"):
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
                    # Hospital (Tier 3 only — injected into Section 4)
                    "hospital_name":    (st.session_state.nearest_hospital or {}).get("name", ""),
                    "hospital_address": (st.session_state.nearest_hospital or {}).get("address", ""),
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
