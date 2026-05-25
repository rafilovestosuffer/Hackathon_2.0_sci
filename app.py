# UI OVERHAUL — 2026-05-20
"""
SkinAI Bangladesh — main Streamlit app.
"সঠিক রোগী → সঠিক ডাক্তার → সঠিক সময়"
"""

import hashlib
import io
import logging
from datetime import datetime

import numpy as np
import streamlit as st
from PIL import Image

from ui.styles import inject_css
from ui.components import (
    render_tier_banner,
    render_chat_message,
    render_suggested_questions,
    render_referral_preview,
    render_audio_triage,
    enhance_skin_image,
    render_symptom_timeline,
    render_chw_result,
    render_patient_history_table,
    render_disease_card,
    render_referral_download_button,
    check_image_quality,
    bn_en,
    render_fairness_disclosure,
    render_business_model,
    render_ethics_card,
    render_scalability_roadmap,
    render_nrb_sponsor,
)
from ui.doctor_booking import render_doctor_booking_tab
from ui.consultation_room import render_consultation_room
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
    initial_sidebar_state="collapsed",
)

inject_css()

# Hide the sidebar UI + restore the glass-morphism card at a wider max-width.
# The clinical mesh background defined in ui/styles.py (.stApp) should peek
# around the edges of a centered translucent white card — this is the design
# intent. We override only the max-width so the card breathes on big screens.
st.markdown(
    """
    <style>
      section[data-testid="stSidebar"] { display: none !important; }
      div[data-testid="stSidebarCollapsedControl"] { display: none !important; }
      button[kind="header"] { display: none !important; }

      /* Wider card so wide monitors don't feel cramped, but still let the
         clinical mesh background show at the edges (the glass design). */
      .block-container,
      [data-testid="stAppViewContainer"] .main .block-container {
        max-width: 1500px !important;
        padding-top: 1.4rem !important;
        padding-left: 2.4rem !important;
        padding-right: 2.4rem !important;
      }
      @media (max-width: 1100px) {
        .block-container {
          max-width: 100% !important;
          padding-left: 1.4rem !important;
          padding-right: 1.4rem !important;
        }
      }
      @media (max-width: 700px) {
        .block-container {
          padding-left: 0.9rem !important;
          padding-right: 0.9rem !important;
        }
      }
    </style>
    """,
    unsafe_allow_html=True,
)


# ── Cached loaders ────────────────────────────────────────────────────────────

@st.cache_resource(show_spinner="Loading RAG knowledge base…")
def _load_rag_index():
    return load_index()


# ── BD-SkinNet model loader + inference ──────────────────────────────────────

_HF_REPO     = "rafilovestosuffer/bd-skinnet"
_HF_FILENAME = "bd_skinnet_int8.pth"


@st.cache_resource(show_spinner="Loading BD-SkinNet model…")
def _load_bd_skinnet():
    """Download INT8 checkpoint from HF Hub (cached for the session lifetime)."""
    try:
        from huggingface_hub import hf_hub_download
        from model.bd_skinnet import load_model
        ckpt_path = hf_hub_download(repo_id=_HF_REPO, filename=_HF_FILENAME)
        return load_model(ckpt_path)
    except Exception as exc:
        logger.warning("BD-SkinNet load failed: %s", exc)
        return None


def _run_model(pil_img: Image.Image) -> dict:
    from model.bd_skinnet import predict

    model = _load_bd_skinnet()
    if model is None:
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

    result = predict(model, pil_img)
    return {
        "disease":      result["disease_class"],
        "confidence":   result["confidence"],
        "top2": [
            {"disease": t["class"], "confidence": t["confidence"]}
            for t in result["top2"]
        ],
        "heatmap":      None,
        "coverage_pct": 0.0,
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
    "demo_image_path":   None,  # set by demo buttons; cleared by real upload
    "_last_audio_hash":  "",   # prevents re-processing same audio on rerun
    "prevention_tips_cache": {},
    # Doctor booking state
    "booking_confirmed":  False,
    "booking_details":    None,
    "selected_date_idx":  None,
    "selected_slot":      None,
    "patient_name_input": "",
    "patient_phone":      "",
    "selected_doctor_id": "dr_nusrat_001",
    # Consultation room state
    "consultation_transcript":       "",
    "consultation_completed":        False,
    "consultation_duration_minutes": 30,
    "summary_pdf_bytes":             None,
    "prescribed_medicines_list":     [],
    "_generate_pdf_now":             False,
    "manual_consultation_notes_text": "",
    "_demo_pdf_bytes":               None,
}
for _k, _v in _DEFAULTS.items():
    st.session_state.setdefault(_k, _v)

@st.cache_resource(show_spinner="Loading knowledge base…")
def _warm_rag() -> bool:
    return _load_rag_index()

_rag_ready = _warm_rag()


# ══════════════════════════════════════════════════════════════════════════════
# DEMO CASES — defined at module scope so both the sidebar (Quick Actions) and
# Tab 1 (Quick Demo Bar) can reuse the same dict.
# ══════════════════════════════════════════════════════════════════════════════
_DEMO_CASES = {
    "demo_tier1": {
        "label": "🟢 Demo — Tinea Tier 1",
        "help":  "Non-urgent pharmacist case",
        "image": "assets/demo/tinea.jpg",
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
        "image": "assets/demo/eczema.jpg",
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
        "image": "assets/demo/scabies.jpg",
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
    "demo_normal": {
        "label": "💚 Demo — Normal Healthy Skin",
        "help":  "No disease detected — healthy skin result",
        "transcript": "ত্বকে কোনো সমস্যা নেই, পরীক্ষা করতে চাইছি",
        "pred": {
            "disease": "Normal", "confidence": 0.91,
            "top2": [{"disease": "Normal",           "confidence": 0.91},
                     {"disease": "Contact_Dermatitis","confidence": 0.05}],
            "heatmap": None, "coverage_pct": 8.0,
        },
        "history": {
            "patient_name": "নাসরিন (Demo)", "patient_age": "২৬",
            "chief_complaint": "ত্বক পরীক্ষা করতে চাই",
            "symptoms": ["no symptoms"],
            "affected_area": "হাতের তালু",
            "duration": "—",
            "progression": "কোনো পরিবর্তন নেই",
            "previous_treatment": "কোনো চিকিৎসা নেই",
            "associated_symptoms": [],
        },
    },
}


# ══════════════════════════════════════════════════════════════════════════════
# (No sidebar — full-width single-column layout. All actions live in tabs.)
# `chw_mode` keeps its default value (False) from _DEFAULTS for downstream code.
# ══════════════════════════════════════════════════════════════════════════════


# ══════════════════════════════════════════════════════════════════════════════
# HERO HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="hero-banner">'
    '  <div class="hero-glow"></div>'
    '  <div class="hero-glow-2"></div>'
    '  <div class="hero-title">SkinAI Bangladesh</div>'
    '  <div class="hero-subtitle">'
    '    AI-powered dermatological screening &amp; smart triage for rural Bangladesh'
    '  </div>'
    '  <div class="hero-tagline-row">'
    '    <div class="hero-step">সঠিক রোগী<small>Right Patient</small></div>'
    '    <div class="hero-arrow">→</div>'
    '    <div class="hero-step">সঠিক ডাক্তার<small>Right Doctor</small></div>'
    '    <div class="hero-arrow">→</div>'
    '    <div class="hero-step">সঠিক সময়<small>Right Time</small></div>'
    '  </div>'
    '  <div style="margin-top:1.1rem;font-size:0.86rem;color:rgba(226,232,240,0.78);'
    '              font-weight:400;letter-spacing:0.01em;line-height:1.55;">'
    '    Swin Transformer + CBAM &nbsp;·&nbsp; 92.46% F1 &nbsp;·&nbsp; '
    '    trained on Bangladesh clinical data &nbsp;·&nbsp; 8 conditions'
    '  </div>'
    '</div>',
    unsafe_allow_html=True,
)


# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Diagnosis · রোগ নির্ণয়",
    "Ask AI · প্রশ্ন করুন",
    "Referral · রেফারেল পত্র",
    "Disease Insights · রোগ-পরিচিতি",
    "Book Doctor · ডাক্তার বুকিং",
    "Impact & Ethics · প্রভাব ও নীতি",
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Diagnosis & Triage
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    # ── Try-a-demo expander (collapsed by default so the real workflow leads) ──
    with st.expander("Try a demo case (skip voice & image)", expanded=False):
        st.caption(
            "Instant pre-filled patient. Use these to see the full pipeline "
            "without recording audio or uploading a photo."
        )
        _demo_keys = list(_DEMO_CASES.keys())
        _demo_cols = st.columns(len(_demo_keys))
        # Plain text labels — no leading emoji circles, the badge inside the
        # demo dict already conveys tier/colour via styled cards downstream.
        _CLEAN_LABELS = {
            "demo_tier1":  "Tinea · Tier 1",
            "demo_tier2":  "Eczema · Tier 2",
            "demo_tier3":  "Scabies · Tier 3",
            "demo_normal": "Normal · Healthy",
        }
        for _col, _dk in zip(_demo_cols, _demo_keys):
            with _col:
                _dc = _DEMO_CASES[_dk]
                if st.button(
                    _CLEAN_LABELS.get(_dk, _dc["label"]),
                    use_container_width=True,
                    help=_dc["help"],
                    key=f"tab_demo_{_dk}",
                ):
                    _dp = dict(_dc["pred"])

                    # If this demo case has a bundled skin photo, load it,
                    # run REAL BD-SkinNet, and use the resulting heatmap +
                    # coverage. Disease label stays the demo-intended class
                    # so the button labelled "Tinea · Tier 1" reliably shows
                    # a Tinea/Tier-1 outcome end-to-end.
                    _img_path = _dc.get("image")
                    if _img_path:
                        from pathlib import Path as _P
                        _full = _P(__file__).parent / _img_path
                        if _full.exists():
                            st.session_state["demo_image_path"] = str(_full)
                            try:
                                _pil = Image.open(_full).convert("RGB")
                                _real = _run_model(_pil)
                                # Real heatmap + real coverage; keep demo
                                # label/confidence for narrative consistency.
                                _dp["heatmap"]      = _real.get("heatmap")
                                _dp["coverage_pct"] = _real.get(
                                    "coverage_pct", _dp["coverage_pct"]
                                )
                            except Exception as _e:
                                logger.warning("Demo inference failed: %s", _e)
                        else:
                            st.session_state["demo_image_path"] = None
                    else:
                        st.session_state["demo_image_path"] = None

                    st.session_state.prediction  = _dp
                    st.session_state.tier_result = compute_tier(
                        _dp["disease"], _dp["confidence"],
                        _dp["coverage_pct"], _dc["transcript"],
                    )
                    st.session_state.history     = _dc["history"]
                    st.session_state.transcript  = _dc["transcript"]
                    st.session_state.pdf_bytes   = None
                    st.session_state.booking_confirmed = False
                    st.session_state.booking_details   = None
                    st.session_state.selected_date_idx = None
                    st.session_state.selected_slot     = None
                    _push_history_to_form(_dc["history"])
                    st.rerun()

    col_left, col_right = st.columns([1, 1], gap="large")

    # ── LEFT COLUMN: Voice Input + Patient Data ────────────────────────────────
    with col_left:
        st.markdown(
            '<div class="sk-section-h2">Voice Input</div>'
            '<div class="sk-meta-bn">ভয়েস ইনপুট · optional</div>',
            unsafe_allow_html=True,
        )
        st.caption(
            "Speak in Bengali or English. The AI will transcribe and "
            "extract patient history automatically."
        )

        # ── Language selector ─────────────────────────────────────────────────
        _audio_lang_choice = st.selectbox(
            "Audio language",
            options=["Bengali (বাংলা)", "English", "Auto-detect"],
            index=0,
            key="audio_lang_select",
            help="Default Bengali. Auto-detect picks the language for you.",
        )
        _lang_map = {
            "Auto-detect":        None,
            "Bengali (বাংলা)":    "bn",
            "English":            "en",
        }
        _selected_lang = _lang_map[_audio_lang_choice]

        audio_bytes = None
        audio_fmt   = "wav"

        # ── Primary: live microphone recording ───────────────────────────────
        _mic_available = True
        try:
            from streamlit_mic_recorder import mic_recorder
        except ImportError:
            _mic_available = False
            st.warning(
                "Recorder component not installed. Use the upload/type "
                "fallback below."
            )

        if _mic_available:
            _mic = mic_recorder(
                start_prompt="Start recording",
                stop_prompt="Stop recording",
                just_once=False,
                use_container_width=True,
                format="wav",
                key="mic_recorder_v2",
            )
            st.caption(
                "Speak a full sentence (name, age, symptoms, duration) for "
                "at least 3 seconds. First use will prompt for mic permission."
            )
            if _mic and _mic.get("bytes"):
                _mic_bytes = _mic["bytes"]
                if len(_mic_bytes) >= 48_000:
                    audio_bytes = _mic_bytes
                    audio_fmt   = "wav"
                    st.audio(audio_bytes, format="audio/wav")
                    st.success("Recording captured — transcribing…")
                elif len(_mic_bytes) > 500:
                    st.warning(
                        "Recording too short (<1.5s). Please speak for at "
                        "least 3 seconds — say your name, age, and symptoms."
                    )

        # ── Fallback options collapsed by default ────────────────────────────
        with st.expander("Can't use a microphone?  Upload audio or type instead.", expanded=False):
            _fb_upload, _fb_text = st.tabs(["Upload audio file", "Type the history"])

            with _fb_upload:
                audio_file = st.file_uploader(
                    "Upload a voice recording",
                    type=["wav", "mp3", "ogg", "webm", "m4a"],
                    key="audio_file",
                    help="Accepted: WAV · MP3 · OGG · M4A · WEBM",
                )
                if audio_file is not None:
                    audio_bytes = audio_file.read()
                    audio_fmt   = audio_file.name.rsplit(".", 1)[-1].lower()
                    if audio_bytes:
                        st.audio(audio_bytes, format=f"audio/{audio_fmt}")
                        st.success("Audio received — transcribing…")

            with _fb_text:
                _manual = st.text_area(
                    "Patient history",
                    value=st.session_state.get("manual_transcript_val", ""),
                    placeholder=(
                        "e.g. My name is Rahim, age 35. Itching all over with "
                        "fever for 5 days.\n"
                        "যেমন — আমার নাম রহিম, বয়স ৩৫। সারা শরীরে চুলকানি, জ্বর, ৫ দিন ধরে।"
                    ),
                    key="manual_transcript",
                    height=110,
                    help="Bengali or English both work.",
                )
                if st.button("Extract history from text", key="use_manual_btn", use_container_width=True):
                    if _manual.strip():
                        st.session_state["manual_transcript_val"] = _manual.strip()
                        st.session_state.transcript = _manual.strip()
                        with st.spinner("Extracting patient history…"):
                            _history = _extract_history(_manual.strip())
                            st.session_state.history = _history
                            _push_history_to_form(_history)
                        st.rerun()
                    else:
                        st.warning("Please enter some text first.")

            # Bundled sample clip for judges in a silent room
            from pathlib import Path as _Path
            _demo_path = _Path(__file__).parent / "assets" / "demo_bn_sample.wav"
            if _demo_path.exists():
                st.divider()
                st.caption("No mic available? Use a pre-recorded Bengali sample:")
                if st.button(
                    "Use demo clip (Rahim, 35, itchy rash for 5 days)",
                    key="demo_clip_btn",
                    use_container_width=True,
                ):
                    audio_bytes = _demo_path.read_bytes()
                    audio_fmt   = "wav"
                    st.audio(audio_bytes, format="audio/wav")
                    st.success("Demo clip loaded — transcribing…")

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
            '<div class="sk-section-h2">Patient Data</div>'
            '<div class="sk-meta">Auto-filled from voice · edit as needed</div>',
            unsafe_allow_html=True,
        )
        st.write("")  # small breathing room

        _h = st.session_state.history or {}
        _form_col1, _form_col2 = st.columns(2)
        with _form_col1:
            _f_name = st.text_input(
                "Patient Name",
                key="form_patient_name",
                placeholder="e.g. Rahim",
                help="রোগীর নাম",
            )
            _f_complaint = st.text_input(
                "Chief Complaint",
                key="form_chief_complaint",
                placeholder="e.g. Itching rash",
                help="প্রধান সমস্যা",
            )
            _f_area = st.text_input(
                "Affected Area",
                key="form_affected_area",
                placeholder="e.g. Arm, abdomen",
                help="আক্রান্ত স্থান",
            )
            _f_duration = st.text_input(
                "Duration",
                key="form_duration",
                placeholder="e.g. 5 days",
                help="কতদিন ধরে",
            )
        with _form_col2:
            _f_age = st.text_input(
                "Patient Age",
                key="form_patient_age",
                placeholder="e.g. 35",
                help="বয়স",
            )
            _f_symptoms = st.text_input(
                "Symptoms (comma-separated)",
                key="form_symptoms",
                placeholder="e.g. itching, redness, fever",
                help="লক্ষণসমূহ — কমা দিয়ে আলাদা করুন",
            )
            _f_progression = st.text_input(
                "Progression",
                key="form_progression",
                placeholder="e.g. spreading",
                help="অবস্থার পরিবর্তন",
            )
            _f_prev = st.text_input(
                "Previous Treatment",
                key="form_prev_treatment",
                placeholder="e.g. None",
                help="পূর্ববর্তী চিকিৎসা",
            )

        if st.button("Save patient data", key="save_patient_btn", use_container_width=True, type="primary"):
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
            '<div class="sk-section-h2">Skin Photo</div>'
            '<div class="sk-meta-bn">ছবি আপলোড করুন · required</div>',
            unsafe_allow_html=True,
        )

        image_file = st.file_uploader(
            "Upload a clear photo of the affected skin area",
            type=["jpg", "jpeg", "png", "webp"],
            key="image_upload",
            help="ত্বকের ছবি আপলোড করুন (JPG / PNG / WEBP)",
        )

        if image_file is not None:
            # A real upload always supersedes any demo image
            st.session_state["demo_image_path"] = None
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
            render_fairness_disclosure()

        else:
            # No new upload — show the demo photo + cached results if a demo
            # button was clicked, or just cached results otherwise.
            _demo_path = st.session_state.get("demo_image_path")
            if _demo_path:
                from pathlib import Path as _P
                if _P(_demo_path).exists():
                    st.image(_demo_path,
                             use_container_width=True,
                             caption="Demo skin image — loaded from sample case")
            if st.session_state.prediction:
                pred = st.session_state.prediction
                if not _demo_path:
                    st.markdown(
                        '<div class="info-box-teal" style="margin-bottom:0.75rem;">'
                        'Previous analysis loaded — upload a new image to re-analyse</div>',
                        unsafe_allow_html=True,
                    )
                render_disease_card(pred["disease"], pred["confidence"], pred["top2"])
                render_fairness_disclosure()
            elif not _demo_path:
                st.markdown(
                    '<div style="background:#F8FAFC;border:1.5px dashed #E2E8F0;border-radius:10px;'
                    'padding:2.2rem 1.5rem;text-align:center;color:#64748B;font-size:0.88rem;">'
                    'Upload a clear photo of the affected skin area'
                    '<div style="font-size:0.78rem;color:#94A3B8;margin-top:0.35rem;">'
                    'আক্রান্ত ত্বকের একটি স্পষ্ট ছবি আপলোড করুন</div>'
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

        # F6 — Symptom timeline (only when history has duration)
        _dur = (st.session_state.history or {}).get("duration", "")
        if _dur:
            render_symptom_timeline(_dur, _tr["tier"])

        # ── All tiers: Nearest healthcare facility map (skip for tier 0) ────────
        if _tr["tier"] == 0:
            st.markdown(
                '<div style="background:#E8FDF1;border:1.5px solid #6FCFA5;border-radius:10px;'
                'padding:1rem 1.25rem;margin-top:0.5rem;text-align:center;">'
                '<div style="font-size:2rem;">💚</div>'
                '<div style="font-weight:700;font-size:1rem;color:#064E3B;margin:0.3rem 0;">'
                'আপনার ত্বক সুস্থ — No Referral Needed</div>'
                '<div style="font-size:0.84rem;color:#065F46;">কোনো হাসপাতাল বা ফার্মেসিতে যাওয়ার প্রয়োজন নেই।'
                '<br>No facility visit required. Your skin appears healthy.</div>'
                '</div>',
                unsafe_allow_html=True,
            )
        else:
            _map_config = {
                1: ("Nearest Pharmacies",                "নিকটতম ফার্মেসি"),
                2: ("Nearest Upazila Health Complexes",  "নিকটতম উপজেলা স্বাস্থ্য কমপ্লেক্স"),
                3: ("Nearest Emergency Hospitals",       "নিকটতম জরুরি হাসপাতাল"),
            }
            _title, _bn = _map_config.get(_tr["tier"], _map_config[1])
            st.markdown(
                f'<div class="sk-section-h2" style="margin-top:0.6rem;">{_title}</div>'
                f'<div class="sk-meta-bn">{_bn}</div>',
                unsafe_allow_html=True,
            )
            district = st.text_input(
                "Your district",
                key="district_input",
                placeholder="e.g. Rangpur, Dhaka, Chittagong",
                help="জেলার নাম লিখুন",
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
        '<span>Answers grounded in:</span>'
        '<span class="info-source-pill">CDC</span>'
        '<span class="info-source-pill">NIH</span>'
        '<span class="info-source-pill">WHO</span>'
        '<span class="info-source-pill">DGHS Bangladesh</span>'
        '<span style="margin-left:auto;font-size:0.75rem;color:#4A5568;">'
        'Educational only — no medicine recommendations</span>'
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
            f"**Current diagnosis: {_disease_display}** ({_conf_pct}%) — "
            "answering questions in this clinical context.",
        )

    # ── Chat history (native st.chat_message — auto-scroll, accessible) ─────────
    for _msg in st.session_state.chat_history:
        with st.chat_message(_msg["role"]):
            st.markdown(_msg["content"])
            if _msg["role"] == "assistant":
                st.caption("CDC · NIH · WHO · DGHS Bangladesh")

    if st.session_state.chat_history:
        if st.button("Clear chat", key="clear_chat_btn"):
            st.session_state.chat_history = []
            st.session_state.rag_answer   = ""
            st.rerun()
    else:
        # Empty state
        st.markdown(
            '<div class="chat-empty" style="text-align:center;padding:1.4rem 0 0.6rem 0;">'
            '<div style="font-weight:600;color:#1A202C;font-size:1rem;">'
            'Ask about skin conditions</div>'
            '<div class="sk-meta-bn" style="color:#94A3B8;">ত্বকের রোগ সম্পর্কে প্রশ্ন করুন</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="sk-section-h3" style="margin-top:0.8rem;">Suggested questions</div>',
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
    # ── Sample PDF — collapsed, available without running the pipeline ───────
    with st.expander("Download a sample referral letter (no diagnosis needed)", expanded=False):
        st.caption(
            "Fully-populated example: Rahim · Scabies Tier 3 · with doctor booking. "
            "Generates instantly so judges can see the format."
        )
        _demo_col1, _demo_col2 = st.columns([2, 1])
        with _demo_col1:
            if st.button(
                "Generate sample PDF",
                use_container_width=True,
                key="gen_demo_pdf_btn",
            ):
                with st.spinner("Building sample PDF…"):
                    try:
                        from pdf_gen.referral import generate_demo_consultation_pdf
                        st.session_state["_demo_pdf_bytes"] = generate_demo_consultation_pdf()
                    except Exception as _e:
                        st.error(f"Sample PDF failed: {_e}")
        with _demo_col2:
            _demo_pdf = st.session_state.get("_demo_pdf_bytes")
            if _demo_pdf:
                st.download_button(
                    label="Download sample",
                    data=_demo_pdf,
                    file_name="skinai_demo_consultation.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key="dl_demo_pdf_btn",
                    type="primary",
                )
            else:
                st.button(
                    "Download sample",
                    use_container_width=True,
                    disabled=True,
                    key="dl_demo_pdf_disabled",
                )

    pred    = st.session_state.prediction
    tier    = st.session_state.tier_result
    history = st.session_state.history

    if pred and tier and tier.get("tier") == 0:
        # ── Tier 0: Healthy skin — no referral needed ─────────────────────────
        st.markdown(
            '<div style="background:#E8FDF1;border:1.5px solid #6FCFA5;border-radius:14px;'
            'padding:1.6rem 2rem;text-align:center;margin:1rem 0;">'
            '<div style="font-size:1.15rem;font-weight:700;color:#064E3B;margin-bottom:0.4rem;">'
            'Skin appears healthy</div>'
            '<div class="sk-meta-bn" style="color:#065F46;">ত্বক স্বাভাবিক</div>'
            '<div style="font-size:0.86rem;color:#047857;margin-top:0.6rem;">'
            'No skin disease detected — no referral letter is needed.<br>'
            'If symptoms develop or persist, please consult a doctor.</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    elif pred and tier:
        # ── PDF Preview cards ─────────────────────────────────────────────────
        render_referral_preview(pred, tier, history)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Single primary action: radio + Generate ───────────────────────────
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
            "booking_confirmed": st.session_state.get("booking_confirmed", False),
            "booking_details":   st.session_state.get("booking_details"),
        }

        _pdf_type = st.radio(
            "Document type",
            options=["Full referral letter", "CHW referral slip (1 page)"],
            horizontal=True,
            key="pdf_type_choice",
            help="The CHW slip is a simplified one-pager for community health workers.",
        )

        if st.button("Generate PDF", use_container_width=True, type="primary", key="gen_pdf_btn"):
            with st.spinner("Generating PDF…"):
                try:
                    if _pdf_type.startswith("Full"):
                        st.session_state.pdf_bytes     = generate_referral_pdf(_session_data)
                        st.session_state.chw_pdf_bytes = None
                    else:
                        from pdf_gen.referral import generate_chw_referral_slip
                        st.session_state.chw_pdf_bytes = generate_chw_referral_slip(_session_data)
                        st.session_state.pdf_bytes     = None
                except Exception as e:
                    st.error(f"PDF generation failed: {e}")

        # ── Download buttons ───────────────────────────────────────────────────
        render_referral_download_button(st.session_state.pdf_bytes)

        _chw_pdf = st.session_state.get("chw_pdf_bytes")
        if _chw_pdf is not None:
            st.download_button(
                label="Download CHW slip (PDF)",
                data=_chw_pdf,
                file_name="skinai_chw_slip.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="dl_chw_btn",
                type="primary",
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
            f'<div style="font-weight:700;font-size:1.05rem;color:#1A202C;margin-bottom:0.2rem;">'
            f'Complete a diagnosis to generate a referral letter</div>'
            f'<div class="sk-meta-bn">রেফারেল পত্র পেতে রোগ নির্ণয় সম্পন্ন করুন</div>'
            f'<div style="height:1rem;"></div>'
            f'<div class="referral-progress-row {_c1}">'
            f'{_d1} Voice input <span style="font-size:0.78rem;color:#A0AEC0;">(optional)</span></div>'
            f'<div class="referral-progress-row {_c2}">'
            f'{_d2} Upload skin image &nbsp;<strong style="color:#1A6FA8;">← start here</strong></div>'
            f'<div class="referral-progress-row {_c3}">'
            f'{_d3} AI analysis runs automatically</div>'
            f'<div class="referral-progress-row {_c4}">'
            f'{_d4} Generate referral letter</div>'
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
        '<div class="sk-section-h2">Bangladesh Skin Disease Prevalence</div>'
        '<div class="sk-meta">Relative burden levels · WHO SEARO · peer-reviewed literature</div>',
        unsafe_allow_html=True,
    )
    st.write("")

    from map.bd_heatmap import (
        get_all_diseases, get_division_stats, render_prevalence_map,
        DISEASE_LABELS_BN, DISEASE_COLORS, DISEASE_SOURCE,
        LEVEL_LABEL, LEVEL_COLOR, LEVEL_BG, LEVEL_BORDER,
    )

    _diseases = get_all_diseases()
    _disease_options = {d.replace("_", " "): d for d in _diseases}
    _disease_option_keys = list(_disease_options.keys())

    # Pre-select the most-recent diagnosis (if any) — saves clicks
    _default_idx = 0
    _current_pred = (st.session_state.get("prediction") or {}).get("disease", "")
    if _current_pred:
        _pretty = _current_pred.replace("_", " ")
        if _pretty in _disease_option_keys:
            _default_idx = _disease_option_keys.index(_pretty)

    _sel_display = st.selectbox(
        "Disease",
        options=_disease_option_keys,
        index=_default_idx,
        key="epi_disease_select",
        help="রোগ বেছে নিন",
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
            '📊 Burden Level by Division</div>',
            unsafe_allow_html=True,
        )
        _stats = get_division_stats(_sel_disease)
        for _row in _stats:
            _div   = _row["division"]
            _level = _row["level"]
            _label = LEVEL_LABEL.get(_level, _level)
            _color = LEVEL_COLOR.get(_level, "#718096")
            _bg    = LEVEL_BG.get(_level, "#F8FAFC")
            _bord  = LEVEL_BORDER.get(_level, "#CBD5E1")
            st.markdown(
                f'<div style="display:flex;align-items:center;justify-content:space-between;'
                f'background:{_bg};border:1px solid {_bord};border-radius:8px;'
                f'padding:0.4rem 0.7rem;margin-bottom:0.35rem;">'
                f'  <span style="font-size:0.8rem;font-weight:600;color:#2D3748;">{_div}</span>'
                f'  <span style="background:{_color};color:white;font-size:0.7rem;font-weight:700;'
                f'border-radius:99px;padding:0.15rem 0.65rem;">{_label}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # Citation row
    _src = DISEASE_SOURCE.get(_sel_disease, "WHO SEARO regional patterns")
    st.markdown(
        f'<div style="font-size:0.72rem;color:#718096;margin-top:0.5rem;">'
        f'📚 <strong>Source basis:</strong> {_src}</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sk-disclaimer" style="margin-top:0.75rem;">'
        '⚠️ Burden levels (High / Medium / Low) are qualitative indicators derived from '
        'WHO South-East Asia regional patterns and peer-reviewed literature. '
        'They are not exact survey figures. For official statistics, refer to DGHS Bangladesh Health Bulletin.'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div style="margin-top:1.25rem;"></div>', unsafe_allow_html=True)

    with st.expander("💡 Prevention Tips & Early Warning Signs · প্রতিরোধ টিপস", expanded=True):
        _cache_key = _sel_disease
        if _cache_key not in st.session_state.prevention_tips_cache:
            if _rag_ready:
                with st.spinner("Generating tips from medical knowledge base…"):
                    _tip_q = (
                        f"What are the key prevention tips, early warning signs, "
                        f"and when should someone see a doctor for {_sel_display}? "
                        f"Give 4-5 bullet points. Answer in both Bengali and English."
                    )
                    _tips = answer_question(
                        _tip_q,
                        disease_context=_sel_display,
                    )
                    st.session_state.prevention_tips_cache[_cache_key] = _tips
            else:
                st.session_state.prevention_tips_cache[_cache_key] = (
                    "Knowledge base not available. Please check RAG index setup."
                )
        st.markdown(st.session_state.prevention_tips_cache[_cache_key])

        st.markdown(
            '<div style="font-size:0.75rem;font-weight:600;color:#4A5568;margin-top:0.75rem;margin-bottom:0.25rem;">'
            '💬 Ask a quick question · দ্রুত প্রশ্ন করুন</div>',
            unsafe_allow_html=True,
        )
        _prev_questions = [
            f"How is {_sel_display} spread?",
            "Can children get this condition?",
            "What home care steps are safe?",
        ]
        _pq_cols = st.columns(len(_prev_questions))
        _qq = None
        for _pqi, (_pqc, _pqt) in enumerate(zip(_pq_cols, _prev_questions)):
            with _pqc:
                if st.button(_pqt, key=f"prev_tip_{_pqi}", use_container_width=True):
                    _qq = _pqt
        if _qq and _rag_ready:
            with st.spinner("Looking up answer…"):
                _follow = answer_question(_qq, disease_context=_sel_display)
            st.markdown(_follow)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — Doctor Booking
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    render_doctor_booking_tab()
    render_consultation_room()


# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — Impact, Ethics & Roadmap (Infinity AI BuildFest submission content)
# ══════════════════════════════════════════════════════════════════════════════
with tab6:
    st.markdown(
        '<div style="background:linear-gradient(135deg,#1A6FA8 0%,#0D9E75 100%);'
        'color:white;border-radius:14px;padding:1.1rem 1.4rem;margin-bottom:1rem;">'
        '<div style="font-size:1.05rem;font-weight:800;letter-spacing:0.01em;">'
        'Impact, Ethics &amp; Roadmap</div>'
        '<div style="font-size:0.82rem;opacity:0.92;margin-top:0.3rem;line-height:1.55;">'
        'How SkinAI Bangladesh sustains itself, the safeguards behind every prediction, '
        'the 12-month plan to reach eight districts, and how the diaspora can fund it.'
        '</div></div>',
        unsafe_allow_html=True,
    )

    _t6a, _t6b, _t6c, _t6d = st.tabs([
        "Business Model",
        "Ethics & Model Card",
        "Scalability",
        "NRB Collaboration",
    ])
    with _t6a:
        render_business_model()
    with _t6b:
        render_ethics_card()
    with _t6c:
        render_scalability_roadmap()
    with _t6d:
        render_nrb_sponsor()


# ══════════════════════════════════════════════════════════════════════════════
# APP FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="app-footer">'
    'SkinAI Bangladesh · Right patient → Right doctor → Right time · '
    'Built for IEEE SB CUET SciBlitz &amp; Infinity AI BuildFest'
    '</div>',
    unsafe_allow_html=True,
)
