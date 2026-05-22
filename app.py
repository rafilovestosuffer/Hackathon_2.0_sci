# UI OVERHAUL — 2026-05-20
"""
SkinAI Bangladesh — main Streamlit app.
"সঠিক রোগী → সঠিক ডাক্তার → সঠিক সময়"
"""

import hashlib
import io
import logging

import numpy as np
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
    render_cost_estimate,
    render_impact_comparison,
    render_audio_triage,
    enhance_skin_image,
    render_symptom_timeline,
    render_chw_result,
    # existing components
    render_gradcam_overlay,
    render_patient_history_table,
    render_disease_card,
    render_referral_download_button,
    check_image_quality,
    bn_en,
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


def _transcribe(
    audio_bytes: bytes,
    language: str | None = "bn",
) -> tuple[str, str, float, str, float]:
    """
    Transcribe audio bytes → (transcript, error_reason, rms_energy,
                              detected_lang, lang_prob).

    - Passes bytes directly; pipeline detects format from magic bytes via PyAV.
    - language=None → auto-detect (Whisper picks the language); "bn"/"en" force.
    - Returns ("", reason, rms, "", 0.0) on failure.
    """
    if not audio_bytes or len(audio_bytes) < 500:
        return "", "no_audio", 0.0, "", 0.0

    # Measure RMS so we can tell user if mic is silent
    try:
        from faster_whisper.audio import decode_audio
        import io as _io
        _arr = decode_audio(_io.BytesIO(audio_bytes))
        rms = float(np.sqrt(np.mean(_arr.astype(np.float64) ** 2))) if len(_arr) else 0.0
    except Exception:
        rms = -1.0   # unknown

    try:
        from voice.pipeline import transcribe_audio_detailed
        text, detected, prob = transcribe_audio_detailed(audio_bytes, language=language)
        if text and text.strip():
            return text.strip(), "", rms, detected, prob
        return "", "silence", rms, detected, prob
    except ImportError:
        return "", "not_installed", rms, "", 0.0
    except Exception as e:
        logger.warning("Transcription failed: %s", e)
        return "", str(e), rms, "", 0.0


def _extract_history(transcript: str) -> dict:
    try:
        from voice.pipeline import extract_patient_history
        return extract_patient_history(transcript)
    except Exception as e:
        logger.warning("History extraction failed: %s", e)
        return {}


def _push_history_to_form(h: dict) -> None:
    """Push extracted history into form widget session_state keys so they auto-fill."""
    syms = h.get("symptoms", [])
    st.session_state["form_patient_name"]    = h.get("patient_name", "")
    st.session_state["form_patient_age"]     = h.get("patient_age", "")
    st.session_state["form_chief_complaint"] = h.get("chief_complaint", "")
    st.session_state["form_affected_area"]   = h.get("affected_area", "")
    st.session_state["form_duration"]        = h.get("duration", "")
    st.session_state["form_progression"]     = h.get("progression", "")
    st.session_state["form_prev_treatment"]  = h.get("previous_treatment", "")
    st.session_state["form_symptoms"]        = ", ".join(syms) if isinstance(syms, list) else str(syms)


# ── Session state defaults ────────────────────────────────────────────────────
_DEFAULTS = {
    "transcript":        "",
    "history":           {},
    "prediction":        None,
    "tier_result":       None,
    "nearest_hospital":  None,
    "pdf_bytes":         None,
    "chw_pdf_bytes":     None,
    "rag_answer":        "",
    "rag_lang":          "en",
    "chat_history":      [],
    "chw_mode":          False,
    "_last_audio_hash":  "",   # prevents re-processing same audio on rerun
}
for _k, _v in _DEFAULTS.items():
    st.session_state.setdefault(_k, _v)

@st.cache_resource(show_spinner="Loading knowledge base…")
def _warm_rag() -> bool:
    return _load_rag_index()

_rag_ready = _warm_rag()


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
        'margin-bottom:0.2rem;">🎬 Demo Mode</div>'
        '<div style="font-size:0.68rem;color:#718096;margin-bottom:0.4rem;">'
        'Shows full triage range — no image/audio needed</div>',
        unsafe_allow_html=True,
    )

    _DEMO_CASES = {
        "demo_tier1": {
            "label": "🟢 Demo — Tinea Tier 1",
            "help":  "Non-urgent pharmacist case",
            "transcript": "সামান্য চুলকানি আছে, তেমন সমস্যা নেই",
            "pred": {
                "disease": "Tinea", "confidence": 0.85,
                "top2": [{"disease": "Tinea", "confidence": 0.85},
                         {"disease": "Contact_Dermatitis", "confidence": 0.09}],
                "heatmap": None, "coverage_pct": 18.0,
            },
            "history": {
                "patient_name": "করিম (Demo)", "patient_age": "২৮",
                "chief_complaint": "হাতে গোলাকার ফুসকুড়ি",
                "symptoms": ["ringworm", "mild itching"],
                "affected_area": "বাম হাত",
                "duration": "৩ দিন",
                "progression": "স্থির আছে",
                "previous_treatment": "কিছু নেওয়া হয়নি",
                "associated_symptoms": [],
            },
        },
        "demo_tier2": {
            "label": "🟡 Demo — Eczema Tier 2",
            "help":  "Routine Upazila Health Complex case",
            "transcript": "সারা বাহুতে চুলকানি ও লালচে দাগ, তিন সপ্তাহ ধরে",
            "pred": {
                "disease": "Eczema", "confidence": 0.72,
                "top2": [{"disease": "Eczema", "confidence": 0.72},
                         {"disease": "Atopic_Dermatitis", "confidence": 0.18}],
                "heatmap": None, "coverage_pct": 32.0,
            },
            "history": {
                "patient_name": "সুমাইয়া (Demo)", "patient_age": "২২",
                "chief_complaint": "বাহুতে ও হাঁটুর পেছনে চুলকানি ও শুষ্ক ত্বক",
                "symptoms": ["itching", "redness", "dry patches"],
                "affected_area": "বাহু, হাঁটু",
                "duration": "৩ সপ্তাহ",
                "progression": "ধীরে ধীরে বাড়ছে",
                "previous_treatment": "সাধারণ লোশন ব্যবহার করেছেন",
                "associated_symptoms": [],
            },
        },
        "demo_tier3": {
            "label": "🔴 Demo — Scabies Tier 3",
            "help":  "Urgent — full pipeline with hospital map",
            "transcript": "জ্বর আছে, চুলকানি ছড়িয়ে পড়ছে, ব্যথা হচ্ছে",
            "pred": {
                "disease": "Scabies", "confidence": 0.38,
                "top2": [{"disease": "Scabies", "confidence": 0.38},
                         {"disease": "Eczema",  "confidence": 0.22}],
                "heatmap": None, "coverage_pct": 45.0,
            },
            "history": {
                "patient_name": "রহিম (Demo)", "patient_age": "৩৫",
                "chief_complaint": "সারা শরীরে তীব্র চুলকানি ও ফুসকুড়ি",
                "symptoms": ["intense itching", "spreading rash", "skin thickening"],
                "affected_area": "বাহু, পেট, উরু",
                "duration": "১০ দিন",
                "progression": "দ্রুত ছড়িয়ে পড়ছে",
                "previous_treatment": "কোনো চিকিৎসা নেওয়া হয়নি",
                "associated_symptoms": ["জ্বর", "ব্যথা"],
            },
        },
    }

    for _dk, _dc in _DEMO_CASES.items():
        if st.button(_dc["label"], use_container_width=True, help=_dc["help"], key=_dk):
            _dp = _dc["pred"]
            st.session_state.prediction = _dp
            st.session_state.tier_result = compute_tier(
                disease_class=_dp["disease"],
                confidence=_dp["confidence"],
                coverage_pct=_dp["coverage_pct"],
                transcript=_dc["transcript"],
            )
            st.session_state.history          = _dc["history"]
            st.session_state.transcript       = _dc["transcript"]
            st.session_state.nearest_hospital = None
            st.session_state.pdf_bytes        = None
            st.session_state.chat_history     = []
            st.rerun()

    st.markdown("---")

    # ── CHW Mode toggle ───────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown(
        '<div class="sidebar-stat" style="font-size:0.72rem;font-weight:700;'
        'margin-bottom:0.2rem;">👩‍⚕️ CHW / সেবিকা মোড</div>'
        '<div style="font-size:0.65rem;color:#718096;margin-bottom:0.3rem;">'
        'Simplified view for community health workers</div>',
        unsafe_allow_html=True,
    )
    st.session_state.setdefault("chw_mode", False)
    _chw = st.toggle(
        "Enable CHW Mode",
        key="chw_mode_toggle",
        value=st.session_state.get("chw_mode", False),
    )
    st.session_state["chw_mode"] = _chw

    # ── Impact comparison ─────────────────────────────────────────────────────
    st.markdown("---")
    render_impact_comparison()
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
    '<div class="hero-banner">'
    '  <div class="hero-glow"></div>'
    '  <div class="hero-glow-2"></div>'
    '  <div class="hero-title">🩺 SkinAI Bangladesh</div>'
    '  <div class="hero-tagline">'
    '    সঠিক রোগী &nbsp;→&nbsp; সঠিক ডাক্তার &nbsp;→&nbsp; সঠিক সময়'
    '  </div>'
    '  <div class="stat-bar">'
    '    <span class="stat-chip stat-chip-blue">🔬 7 Disease Classes</span>'
    '    <span class="stat-chip stat-chip-green">📊 F1 = 92.46%</span>'
    '    <span class="stat-chip stat-chip-teal">🏥 BD Clinical Data</span>'
    '    <span class="stat-chip stat-chip-dark">🔒 No Login Required</span>'
    '  </div>'
    '</div>',
    unsafe_allow_html=True,
)


# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🔬 রোগ নির্ণয়",
    "💬 প্রশ্ন করুন",
    "📄 রেফারেল পত্র",
    "📊 Disease Insights",
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Diagnosis & Triage
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    # ── Quick Demo Bar ────────────────────────────────────────────────────────
    st.markdown(
        '<div style="background:#F0F9FF;border:1px solid #BAE6FD;border-radius:8px;'
        'padding:0.5rem 0.75rem;margin-bottom:0.75rem;font-size:0.82rem;color:#0369A1;">'
        '🎬 <strong>No image?</strong> Try instant demo cases below:'
        '</div>',
        unsafe_allow_html=True,
    )
    _dcol1, _dcol2, _dcol3 = st.columns(3)
    with _dcol1:
        if st.button("🟢 Demo — Tinea (Tier 1)", use_container_width=True, key="tab_demo_t1"):
            _dp = _DEMO_CASES["demo_tier1"]["pred"]
            st.session_state.prediction  = _dp
            st.session_state.tier_result = compute_tier(_dp["disease"], _dp["confidence"], _dp["coverage_pct"], _DEMO_CASES["demo_tier1"]["transcript"])
            st.session_state.history     = _DEMO_CASES["demo_tier1"]["history"]
            st.session_state.transcript  = _DEMO_CASES["demo_tier1"]["transcript"]
            st.session_state.pdf_bytes   = None
            st.rerun()
    with _dcol2:
        if st.button("🟡 Demo — Eczema (Tier 2)", use_container_width=True, key="tab_demo_t2"):
            _dp = _DEMO_CASES["demo_tier2"]["pred"]
            st.session_state.prediction  = _dp
            st.session_state.tier_result = compute_tier(_dp["disease"], _dp["confidence"], _dp["coverage_pct"], _DEMO_CASES["demo_tier2"]["transcript"])
            st.session_state.history     = _DEMO_CASES["demo_tier2"]["history"]
            st.session_state.transcript  = _DEMO_CASES["demo_tier2"]["transcript"]
            st.session_state.pdf_bytes   = None
            st.rerun()
    with _dcol3:
        if st.button("🔴 Demo — Scabies (Tier 3 URGENT)", use_container_width=True, key="tab_demo_t3"):
            _dp = _DEMO_CASES["demo_tier3"]["pred"]
            st.session_state.prediction  = _dp
            st.session_state.tier_result = compute_tier(_dp["disease"], _dp["confidence"], _dp["coverage_pct"], _DEMO_CASES["demo_tier3"]["transcript"])
            st.session_state.history     = _DEMO_CASES["demo_tier3"]["history"]
            st.session_state.transcript  = _DEMO_CASES["demo_tier3"]["transcript"]
            st.session_state.pdf_bytes   = None
            st.rerun()

    st.markdown("---")
    col_left, col_right = st.columns([1, 1], gap="large")

    # ── LEFT COLUMN: Voice Input + Patient Data ────────────────────────────────
    with col_left:
        st.markdown(
            '<div class="card-section-header">'
            '<span style="font-size:1.1rem;">🎙️</span>'
            '<div>'
            '<div class="card-section-title">ভয়েস ইনপুট · Voice Input</div>'
            '<div class="card-section-sub">(ঐচ্ছিক — optional)</div>'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="info-box">'
            '🤖 Speak in <strong>Bengali or English</strong> — AI auto-extracts patient history'
            '</div>',
            unsafe_allow_html=True,
        )

        # ── Language selector ─────────────────────────────────────────────────
        _lang_col1, _lang_col2 = st.columns([1, 2])
        with _lang_col1:
            st.markdown(
                '<div style="font-size:0.78rem;font-weight:600;color:#4A5568;'
                'padding-top:0.4rem;">🌐 Language:</div>',
                unsafe_allow_html=True,
            )
        with _lang_col2:
            # Default to Bengali — single-pass, fastest, and matches the BD
            # rural-clinic use case. Auto-detect is one click away for the
            # bilingual showcase.
            _audio_lang_choice = st.selectbox(
                "Audio language",
                options=["Bengali (বাংলা)", "English", "Auto-detect"],
                index=0,
                key="audio_lang_select",
                label_visibility="collapsed",
            )
        _lang_map = {
            "Auto-detect":        None,
            "Bengali (বাংলা)":    "bn",
            "English":            "en",
        }
        _selected_lang = _lang_map[_audio_lang_choice]

        # ── Voice tabs: Live Mic (primary) | Upload (backup) | Text ──────────
        _vtab_mic, _vtab_upload, _vtab_text = st.tabs([
            "🎙️ Record Voice", "📁 Upload Audio", "✏️ Type Text",
        ])

        audio_bytes = None
        audio_fmt   = "wav"

        with _vtab_mic:
            st.markdown(
                '<div style="font-size:0.82rem;color:#4A5568;margin-bottom:0.5rem;">'
                '🎙️ Click <strong>Start recording</strong>, speak in Bengali or English '
                'for <strong>at least 3 seconds</strong>, then click <strong>Stop</strong>.</div>'
                '<div style="font-size:0.72rem;color:#A0AEC0;margin-bottom:0.5rem;">'
                '🔒 First use: your browser will ask for microphone permission — click <strong>Allow</strong>.<br>'
                '💡 Tip: speak a full sentence (name, age, symptoms, duration) — '
                'very short clips are hard to transcribe.</div>',
                unsafe_allow_html=True,
            )

            _mic_available = True
            try:
                from streamlit_mic_recorder import mic_recorder
            except ImportError:
                _mic_available = False
                st.warning(
                    "🎙️ Recorder component not installed. "
                    "Use **Upload Audio** or **Type Text**, or try the demo clip below."
                )

            if _mic_available:
                _mic = mic_recorder(
                    start_prompt="🔴 Start recording",
                    stop_prompt="⏹️ Stop recording",
                    just_once=False,
                    use_container_width=True,
                    format="wav",
                    key="mic_recorder_v2",
                )
                if _mic and _mic.get("bytes"):
                    _mic_bytes = _mic["bytes"]
                    # 16 kHz mono 16-bit PCM ≈ 32 kB/s; ~50 kB ≈ 1.5 s of speech.
                    # Shorter than that almost always fails Whisper + VAD.
                    if len(_mic_bytes) >= 48_000:
                        audio_bytes = _mic_bytes
                        audio_fmt   = "wav"
                        st.audio(audio_bytes, format="audio/wav")
                        st.success("✅ রেকর্ডিং সম্পন্ন — Transcribing…")
                    elif len(_mic_bytes) > 500:
                        st.warning(
                            "⚠️ Recording too short (<1.5s). Please speak for at "
                            "least 3 seconds — say your name, age, and symptoms.\n\n"
                            "রেকর্ডিং খুব ছোট — অন্তত ৩ সেকেন্ড বলুন: নাম, বয়স, লক্ষণ।"
                        )

            # Champion-mode: sample clip for judges with no mic / silent room
            with st.expander("🎧 No mic? Try a sample Bengali clip"):
                from pathlib import Path as _Path
                _demo_path = _Path(__file__).parent / "assets" / "demo_bn_sample.wav"
                if _demo_path.exists():
                    if st.button(
                        "▶️ Use demo clip (Rahim, 35, itchy rash for 5 days)",
                        key="demo_clip_btn",
                        use_container_width=True,
                    ):
                        audio_bytes = _demo_path.read_bytes()
                        audio_fmt   = "wav"
                        st.audio(audio_bytes, format="audio/wav")
                        st.success("✅ Demo clip loaded — Transcribing…")
                else:
                    st.caption(
                        "Demo clip not bundled in this build. Use Upload Audio with any "
                        "Bengali or English WAV/MP3 file instead."
                    )

        with _vtab_upload:
            st.markdown(
                '<div style="font-size:0.78rem;color:#718096;margin:0.3rem 0 0.4rem 0;">'
                'Upload a voice recording (WAV / MP3 / OGG / M4A / WEBM)</div>',
                unsafe_allow_html=True,
            )
            audio_file = st.file_uploader(
                "Upload audio",
                type=["wav", "mp3", "ogg", "webm", "m4a"],
                key="audio_file",
                label_visibility="collapsed",
            )
            if audio_file is not None:
                audio_bytes = audio_file.read()
                audio_fmt   = audio_file.name.rsplit(".", 1)[-1].lower()
                if audio_bytes:
                    st.audio(audio_bytes, format=f"audio/{audio_fmt}")
                    st.success("✅ অডিও আপলোড সম্পন্ন — Audio received, transcribing…")

        with _vtab_text:
            st.markdown(
                '<div style="font-size:0.78rem;color:#718096;margin:0.3rem 0 0.4rem 0;">'
                'বাংলায় বা ইংরেজিতে লিখুন · Type in Bengali or English</div>',
                unsafe_allow_html=True,
            )
            _manual = st.text_area(
                "Patient history",
                value=st.session_state.get("manual_transcript_val", ""),
                placeholder=(
                    "Bengali: যেমন — আমার নাম রহিম, বয়স ৩৫। সারা শরীলে চুলকানি হচ্ছে, জ্বর আছে, ৫ দিন ধরে...\n"
                    "English: My name is Rahim, age 35. I have itching all over, fever, for 5 days..."
                ),
                key="manual_transcript",
                label_visibility="collapsed",
                height=110,
            )
            if st.button("✅ Extract history from text", key="use_manual_btn", use_container_width=True):
                if _manual.strip():
                    st.session_state["manual_transcript_val"] = _manual.strip()
                    st.session_state.transcript = _manual.strip()
                    with st.spinner("🧠 Extracting patient history…"):
                        _history = _extract_history(_manual.strip())
                        st.session_state.history = _history
                        _push_history_to_form(_history)
                    st.rerun()
                else:
                    st.warning("Please enter some text first.")

        # ── Process audio if captured (hash-guarded to prevent infinite rerun) ──
        if audio_bytes:
            _audio_hash = hashlib.md5(audio_bytes).hexdigest()
            _already_processed = (_audio_hash == st.session_state.get("_last_audio_hash", ""))

            if not _already_processed:
                st.session_state["_last_audio_hash"] = _audio_hash

                _spinner_msg = (
                    "🔄 Transcribing audio (auto-detect)…" if _selected_lang is None
                    else f"🔄 Transcribing {_audio_lang_choice} audio…"
                )
                with st.spinner(_spinner_msg):
                    _transcript, _err, _rms, _detected, _det_prob = _transcribe(
                        audio_bytes, language=_selected_lang
                    )
                    st.session_state.transcript = _transcript

                # Show RMS energy level — helps diagnose silent mic issues
                if _rms >= 0:
                    _rms_pct = min(int(_rms * 5000), 100)
                    _rms_color = "#27AE60" if _rms_pct > 5 else "#E74C3C"
                    st.markdown(
                        f'<div style="font-size:0.72rem;color:#718096;margin-bottom:0.3rem;">'
                        f'🎚️ Mic level: <span style="color:{_rms_color};font-weight:600;">'
                        f'{_rms_pct}%</span>'
                        f'{"&nbsp;✅ sound detected" if _rms_pct > 5 else "&nbsp;⚠️ too quiet — speak louder"}'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

                # Detected-language pill (only when Whisper actually ran)
                if _detected:
                    _lang_flags = {"bn": "🇧🇩 Bengali", "en": "🇬🇧 English"}
                    _lang_label = _lang_flags.get(_detected, _detected.upper())
                    _pill_bg = "#E6FFFA" if _det_prob >= 0.6 else "#FFF5E6"
                    _pill_fg = "#0F766E" if _det_prob >= 0.6 else "#9A3412"
                    st.markdown(
                        f'<div style="display:inline-block;background:{_pill_bg};'
                        f'color:{_pill_fg};padding:0.15rem 0.55rem;border-radius:999px;'
                        f'font-size:0.72rem;font-weight:600;margin-bottom:0.4rem;">'
                        f'🔍 Detected: {_lang_label} · {_det_prob * 100:.0f}%'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

                if _transcript:
                    st.markdown(
                        f'<div class="transcript-box">📝 {_transcript}</div>',
                        unsafe_allow_html=True,
                    )
                    with st.spinner("🧠 Extracting patient history from voice…"):
                        _history = _extract_history(_transcript)
                        _has_data = any(
                            bool(v) for v in _history.values() if v not in ([], "")
                        )
                        if _has_data:
                            st.session_state.history = _history
                            _push_history_to_form(_history)
                            st.success("✅ Patient history extracted — form auto-filled below.")
                        else:
                            st.info(
                                "ℹ️ Transcript captured but no patient details found. "
                                "Try speaking: **name · age · symptoms · duration**. "
                                "Or fill the form below manually."
                            )
                else:
                    _err_map_bn = {
                        "no_audio":      "রেকর্ডিং খালি — আবার চেষ্টা করুন।",
                        "silence":       "কোনো কণ্ঠস্বর পাওয়া যায়নি — মাইক্রোফোনের কাছে জোরে বলুন।",
                        "not_installed": "faster-whisper এই পরিবেশে ইনস্টল নেই।",
                    }
                    _err_map_en = {
                        "no_audio":      "Recording was empty — please try again.",
                        "silence":       "We couldn't hear anything (mic too quiet) — move closer and speak louder.",
                        "not_installed": "Voice engine missing — contact admin.",
                    }
                    st.warning(bn_en(
                        "⚠️ " + _err_map_bn.get(_err, f"ট্রান্সক্রিপশন ব্যর্থ: {_err}"),
                        "Transcription failed — " + _err_map_en.get(_err, _err),
                    ))

            # Always show transcript if we have one
            elif st.session_state.transcript:
                st.markdown(
                    f'<div class="transcript-box">📝 {st.session_state.transcript}</div>',
                    unsafe_allow_html=True,
                )

        # Show persisted transcript even when no audio in this render
        if not audio_bytes and st.session_state.transcript:
            st.markdown(
                f'<div class="transcript-box">📝 {st.session_state.transcript}</div>',
                unsafe_allow_html=True,
            )

        st.markdown("---")

        # ── Patient Data Form — always visible, editable ──────────────────────
        st.markdown(
            '<div class="card-section-header">'
            '<span style="font-size:1rem;">👤</span>'
            '<div>'
            '<div class="card-section-title" style="font-size:0.95rem;">Patient Data</div>'
            '<div class="card-section-sub">Auto-filled from voice · Edit as needed</div>'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        _h = st.session_state.history or {}
        _form_col1, _form_col2 = st.columns(2)
        with _form_col1:
            _f_name = st.text_input(
                "Patient Name · রোগীর নাম",
                key="form_patient_name",
                placeholder="e.g. রহিম / Rahim",
            )
            _f_complaint = st.text_input(
                "Chief Complaint · প্রধান সমস্যা",
                key="form_chief_complaint",
                placeholder="e.g. চুলকানি / Itching rash",
            )
            _f_area = st.text_input(
                "Affected Area · আক্রান্ত স্থান",
                key="form_affected_area",
                placeholder="e.g. বাহু, পেট / Arm, abdomen",
            )
            _f_duration = st.text_input(
                "Duration · কতদিন ধরে",
                key="form_duration",
                placeholder="e.g. ৫ দিন / 5 days",
            )
        with _form_col2:
            _f_age = st.text_input(
                "Patient Age · বয়স",
                key="form_patient_age",
                placeholder="e.g. ৩৫ / 35",
            )
            _f_symptoms = st.text_input(
                "Symptoms (comma-separated)",
                key="form_symptoms",
                placeholder="e.g. itching, redness, fever",
            )
            _f_progression = st.text_input(
                "Progression · অবস্থার পরিবর্তন",
                key="form_progression",
                placeholder="e.g. ছড়িয়ে পড়ছে / spreading",
            )
            _f_prev = st.text_input(
                "Previous Treatment · পূর্ববর্তী চিকিৎসা",
                key="form_prev_treatment",
                placeholder="e.g. কোনো চিকিৎসা নেই / None",
            )

        if st.button("💾 Save Patient Data", key="save_patient_btn", use_container_width=True):
            _syms_raw = st.session_state.get("form_symptoms", "")
            _syms = [s.strip() for s in _syms_raw.split(",") if s.strip()]
            st.session_state.history = {
                **_h,
                "patient_name":        st.session_state.get("form_patient_name", ""),
                "patient_age":         st.session_state.get("form_patient_age", ""),
                "chief_complaint":     st.session_state.get("form_chief_complaint", ""),
                "affected_area":       st.session_state.get("form_affected_area", ""),
                "duration":            st.session_state.get("form_duration", ""),
                "progression":         st.session_state.get("form_progression", ""),
                "previous_treatment":  st.session_state.get("form_prev_treatment", ""),
                "symptoms":            _syms,
                "associated_symptoms": _h.get("associated_symptoms", []),
            }
            # st.toast survives the implicit rerun that follows the button
            # click; st.success + st.rerun() killed the feedback before it
            # could render, so the user thought nothing happened.
            st.toast("✅ Patient data saved!", icon="💾")

        if st.session_state.history and st.session_state.history.get("patient_name"):
            st.markdown("")
            render_patient_history_table(st.session_state.history)

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
                st.error(bn_en(
                    "ছবিটি পড়া যাচ্ছে না। বৈধ JPG বা PNG ফাইল আপলোড করুন।",
                    "Could not read this image. Please upload a valid JPG or PNG.",
                ))
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

            # F5 — Auto-enhance low-light / blurry images before inference
            enhanced_img, was_enhanced = enhance_skin_image(pil_img)
            if was_enhanced:
                _ecol1, _ecol2 = st.columns(2)
                with _ecol1:
                    st.image(pil_img, use_container_width=True, caption="Original")
                with _ecol2:
                    st.image(enhanced_img, use_container_width=True, caption="✨ Enhanced")
                st.markdown(
                    '<div class="info-box" style="font-size:0.78rem;">'
                    '✨ <strong>Auto-enhanced</strong> for better analysis '
                    '(CLAHE + unsharp mask) · ছবি স্বয়ংক্রিয়ভাবে উন্নত করা হয়েছে'
                    '</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.image(pil_img, use_container_width=True, caption="Uploaded skin image")

            st.session_state.pdf_bytes    = None
            st.session_state.chat_history = []

            with st.spinner("🔬 Analysing skin image…"):
                pred = _run_model(enhanced_img if was_enhanced else pil_img)
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

    # ── FULL-WIDTH: Severity Tier Banner + enhancements ───────────────────────
    if st.session_state.tier_result:
        _tr = st.session_state.tier_result
        st.markdown('<div style="margin-top:0.25rem;"></div>', unsafe_allow_html=True)

        # F3 — CHW mode: simplified big card instead of standard banner
        if st.session_state.get("chw_mode") and st.session_state.prediction:
            render_chw_result(st.session_state.prediction, _tr)
        else:
            render_tier_banner(
                tier          = _tr["tier"],
                urgency_label = _tr["urgency_label"],
                action_text   = _tr["action"],
                bn_text       = _tr["bengali_text"],
                facility      = _tr["facility"],
            )

        # F1 — Bengali TTS readout
        render_audio_triage(_tr.get("bengali_text", ""))

        # F2 — Cost estimate card
        render_cost_estimate(_tr["tier"])

        # F6 — Symptom timeline (only when history has duration)
        _dur = (st.session_state.history or {}).get("duration", "")
        if _dur:
            render_symptom_timeline(_dur, _tr["tier"])

        # ── All tiers: Nearest healthcare facility map ────────────────────────
        _map_config = {
            1: ("🏪", "#27AE60", "Nearest Pharmacies · নিকটতম ফার্মেসি"),
            2: ("🏥", "#D68910", "Nearest Upazila Health Complexes · নিকটতম উপজেলা স্বাস্থ্য কমপ্লেক্স"),
            3: ("🚨", "#C0392B", "Nearest Emergency Hospitals · নিকটতম জরুরি হাসপাতাল"),
        }
        _icon, _color, _title = _map_config.get(_tr["tier"], _map_config[1])
        st.markdown(
            f'<div class="card-section-header" style="margin-top:0.25rem;">'
            f'<span style="font-size:1.1rem;color:{_color};">{_icon}</span>'
            f'<div>'
            f'<div class="card-section-title" style="color:{_color};">{_title}</div>'
            f'</div>'
            f'</div>',
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
                with st.spinner("🔍 Finding nearest healthcare facilities…"):
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
                st.warning(bn_en(
                    "নিকটে কোনো স্বাস্থ্যসেবা পাওয়া যায়নি। অন্য জেলার নাম দিয়ে চেষ্টা করুন।",
                    "No facilities found nearby. Try a different district name.",
                ))


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — RAG Chatbot
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    # ── Source info bar ───────────────────────────────────────────────────────
    if not _rag_ready:
        st.warning(bn_en(
            "⚠️ জ্ঞানভান্ডার লোড হচ্ছে না। build_index.py চালানো হয়েছে কিনা যাচাই করুন।",
            "Knowledge base unavailable — check that build_index.py has been run.",
        ))

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

    # ── Chat history (native st.chat_message — auto-scroll, accessible) ─────────
    for _msg in st.session_state.chat_history:
        with st.chat_message(_msg["role"]):
            st.markdown(_msg["content"])
            if _msg["role"] == "assistant":
                st.caption("📚 CDC · NIH · WHO · DGHS Bangladesh")

    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat", key="clear_chat_btn"):
            st.session_state.chat_history = []
            st.session_state.rag_answer   = ""
            st.rerun()
    else:
        # Empty state
        st.markdown(
            '<div class="chat-empty" style="text-align:center;padding:1.5rem 0;">'
            '<div style="font-size:2rem;margin-bottom:0.4rem;">💬</div>'
            '<div style="font-weight:600;color:#4A5568;">ত্বকের রোগ সম্পর্কে প্রশ্ন করুন</div>'
            '<div style="font-size:0.78rem;color:#A0AEC0;">'
            'Ask about skin conditions in Bengali or English</div>'
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

        # ── Generate buttons ───────────────────────────────────────────────────
        from model.disease_labels import get_bengali as _get_bn
        _session_data = {
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

        _pdf_col1, _pdf_col2 = st.columns(2)
        with _pdf_col1:
            if st.button(
                "📋 Full Referral Letter",
                use_container_width=True,
                type="primary",
                key="gen_pdf_btn",
            ):
                with st.spinner("📄 Generating PDF…"):
                    try:
                        st.session_state.pdf_bytes     = generate_referral_pdf(_session_data)
                        st.session_state.chw_pdf_bytes = None
                        st.toast("✅ Referral letter ready!", icon="📄")
                    except Exception as e:
                        st.error(f"PDF generation failed: {e}")

        with _pdf_col2:
            if st.button(
                "👩‍⚕️ CHW Referral Slip",
                use_container_width=True,
                key="gen_chw_pdf_btn",
                help="Simple 1-page slip for community health workers",
            ):
                with st.spinner("📄 Generating CHW slip…"):
                    try:
                        from pdf_gen.referral import generate_chw_referral_slip
                        st.session_state.chw_pdf_bytes = generate_chw_referral_slip(_session_data)
                        st.session_state.pdf_bytes     = None
                        st.toast("✅ CHW slip ready!", icon="👩‍⚕️")
                    except Exception as e:
                        st.error(f"CHW slip generation failed: {e}")

        # ── Download buttons ───────────────────────────────────────────────────
        render_referral_download_button(st.session_state.pdf_bytes)

        _chw_pdf = st.session_state.get("chw_pdf_bytes")
        if _chw_pdf is not None:
            import base64 as _b64
            _chw_b64 = _b64.b64encode(_chw_pdf).decode()
            st.markdown(
                f'<a href="data:application/pdf;base64,{_chw_b64}" '
                f'download="skinai_chw_slip.pdf" '
                f'style="display:block;width:100%;padding:0.75rem 1rem;background:#805AD5;'
                f'color:white;text-align:center;border-radius:8px;font-size:0.95rem;'
                f'font-weight:700;text-decoration:none;box-sizing:border-box;margin-top:0.5rem;">'
                f'📥 CHW Referral Slip ডাউনলোড করুন · Download CHW Slip (PDF)'
                f'</a>',
                unsafe_allow_html=True,
            )

    else:
        # ── Empty state with progress indicator ───────────────────────────────
        _voice_done     = bool(st.session_state.transcript)
        _image_done     = st.session_state.prediction is not None
        _diagnosis_done = st.session_state.tier_result is not None

        def _prog_dot(done: bool, is_next: bool = False, step_num: int = 1) -> tuple:
            if done:
                return '<div class="prog-dot prog-dot-done">✓</div>', 'done-row'
            elif is_next:
                return f'<div class="prog-dot prog-dot-next">{step_num}</div>', 'next-row'
            return f'<div class="prog-dot">{step_num}</div>', ''

        _d1, _c1 = _prog_dot(_voice_done,     False,                  1)
        _d2, _c2 = _prog_dot(_image_done,     not _image_done,        2)
        _d3, _c3 = _prog_dot(_diagnosis_done, _image_done and not _diagnosis_done, 3)
        _d4, _c4 = _prog_dot(False,           False,                  4)

        st.markdown(
            f'<div class="referral-empty">'
            f'<div style="font-size:3rem;margin-bottom:0.75rem;">📋</div>'
            f'<div style="font-weight:700;font-size:1.1rem;color:#1A202C;margin-bottom:0.3rem;">'
            f'রেফারেল পত্র পেতে রোগ নির্ণয় সম্পন্ন করুন</div>'
            f'<div style="font-size:0.84rem;color:#718096;margin-bottom:1.2rem;">'
            f'Complete the steps below to generate your referral letter</div>'
            f'<div class="referral-progress-row {_c1}">'
            f'{_d1} 🎙️ Voice input <span style="font-size:0.78rem;color:#A0AEC0;">(optional)</span></div>'
            f'<div class="referral-progress-row {_c2}">'
            f'{_d2} 📷 Upload skin image &nbsp;<strong style="color:#1A6FA8;">← Start here</strong></div>'
            f'<div class="referral-progress-row {_c3}">'
            f'{_d3} 🧠 AI analysis runs automatically</div>'
            f'<div class="referral-progress-row {_c4}">'
            f'{_d4} 📄 Generate referral letter</div>'
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
# TAB 4 — Epidemiology / Disease Prevalence Heatmap
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown(
        '<div class="card-section-header">'
        '<span style="font-size:1.1rem;">📊</span>'
        '<div>'
        '<div class="card-section-title">Bangladesh Skin Disease Prevalence · Epidemiological Overview</div>'
        '<div class="card-section-sub">Division-level data · DGHS Annual Report 2023 · WHO South-East Asia</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    from map.bd_heatmap import (
        get_all_diseases, get_division_stats, render_prevalence_map,
        DISEASE_LABELS_BN, DISEASE_COLORS,
    )

    _diseases = get_all_diseases()
    _disease_options = {d.replace("_", " "): d for d in _diseases}

    _sel_display = st.selectbox(
        "Select disease · রোগ বেছে নিন",
        options=list(_disease_options.keys()),
        index=0,
        key="epi_disease_select",
    )
    _sel_disease = _disease_options[_sel_display]
    _sel_bn      = DISEASE_LABELS_BN.get(_sel_disease, _sel_display)
    _sel_color   = DISEASE_COLORS.get(_sel_disease, "#1A6FA8")

    st.markdown(
        f'<div class="info-box" style="font-family:\'Noto Sans Bengali\',sans-serif;">'
        f'রোগ: <strong>{_sel_display}</strong> · {_sel_bn}'
        f'</div>',
        unsafe_allow_html=True,
    )

    _epi_col1, _epi_col2 = st.columns([3, 2], gap="large")

    with _epi_col1:
        st.markdown(
            '<div style="font-size:0.78rem;font-weight:600;color:#4A5568;margin-bottom:0.4rem;">'
            '🗺️ Geographic Distribution · ভৌগোলিক বিতরণ</div>',
            unsafe_allow_html=True,
        )
        try:
            from streamlit_folium import st_folium
            _epi_map = render_prevalence_map(_sel_disease)
            st_folium(_epi_map, use_container_width=True, height=420)
        except Exception as _e:
            st.warning(f"Map rendering failed: {_e}")

    with _epi_col2:
        st.markdown(
            '<div style="font-size:0.78rem;font-weight:600;color:#4A5568;margin-bottom:0.4rem;">'
            '📊 Prevalence by Division · বিভাগ অনুযায়ী প্রকোপ</div>',
            unsafe_allow_html=True,
        )
        _stats = get_division_stats(_sel_disease)
        _max_pct = _stats[0]["prevalence"] if _stats else 1
        for _row in _stats:
            _div  = _row["division"]
            _pct  = _row["prevalence"]
            _bar_w = int((_pct / _max_pct) * 100)
            st.markdown(
                f'<div style="margin-bottom:0.45rem;">'
                f'  <div style="display:flex;justify-content:space-between;'
                f'font-size:0.78rem;font-weight:600;margin-bottom:0.15rem;">'
                f'    <span>{_div}</span>'
                f'    <span style="color:{_sel_color};">{_pct}%</span>'
                f'  </div>'
                f'  <div style="background:#E2E8F0;border-radius:99px;height:8px;overflow:hidden;">'
                f'    <div style="width:{_bar_w}%;height:8px;background:{_sel_color};'
                f'border-radius:99px;transition:width 0.3s;"></div>'
                f'  </div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown(
        '<div class="sk-disclaimer" style="margin-top:1rem;">'
        '📋 Data: DGHS Annual Dermatology OPD Report 2023 + WHO South-East Asia Skin Disease Surveillance. '
        'Figures are estimates for educational purposes only.'
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
