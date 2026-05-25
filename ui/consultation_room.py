"""
ui/consultation_room.py — Post-Booking Consultation Room

Three-mode interface after a doctor appointment is confirmed:
  Tab 1 — Demo Video:   embed a YouTube/local video + one-click demo transcript
  Tab 2 — Live Audio:   record/upload consultation audio → Whisper → transcript
  Tab 3 — Manual Notes: typed notes fallback

Any mode that produces a transcript shows the same transcript editor and
PDF generation button beneath.
"""

import logging
import urllib.parse

import streamlit as st

logger = logging.getLogger(__name__)


# ── Pharmacy helpers ─────────────────────────────────────────────────────────

def _medeasy_search_url(medicine_name: str) -> str:
    query = urllib.parse.quote_plus(medicine_name.strip())
    return f"https://medeasy.health/search?q={query}"


def _epharma_search_url(medicine_name: str) -> str:
    query = urllib.parse.quote_plus(medicine_name.strip())
    return f"https://epharma.com.bd/en/medicines?search={query}"


def _render_medeasy_section(medicines: list) -> None:
    if not medicines:
        return

    st.markdown("---")
    st.markdown(
        '<div style="background:#EBF5FB;border:2px solid #AED6F1;border-radius:14px;'
        'padding:1.2rem 1.4rem 1rem 1.4rem;margin-bottom:0.8rem;">'
        '<div style="font-weight:800;font-size:1.1rem;color:#1A5276;">'
        '💊 ওষুধ অর্ডার করুন · Order Medicines Online</div>'
        '<div style="font-size:0.92rem;color:#1F618D;margin-top:0.25rem;">'
        'আপনার পছন্দের ফার্মেসি বেছে নিন · Choose your pharmacy and order instantly</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    with st.expander("ওষুধের তালিকা ও অর্ডার · View Medicines & Order", expanded=True):
        for med in medicines:
            name    = med.get("name", "")
            name_bn = med.get("name_bn", "")
            dose    = med.get("dose", "")
            freq    = med.get("frequency", "")
            dur     = med.get("duration", "")
            url_me  = _medeasy_search_url(name)
            url_ep  = _epharma_search_url(name)

            st.markdown(
                f'<div style="border:1.5px solid #AED6F1;border-radius:12px;'
                f'padding:1.1rem 1.3rem;margin-bottom:1rem;background:#FDFEFE;'
                f'box-shadow:0 1px 4px rgba(0,0,0,0.06);">'
                f'<div style="font-weight:700;font-size:1.08rem;margin-bottom:0.2rem;">{name}</div>'
                f'<div style="font-family:\'Noto Sans Bengali\',sans-serif;font-size:0.95rem;color:#4A5568;margin-bottom:0.15rem;">{name_bn}</div>'
                f'<div style="font-size:0.85rem;color:#718096;margin-bottom:0.9rem;">'
                f'মাত্রা: {dose} &nbsp;·&nbsp; {freq} &nbsp;·&nbsp; {dur}</div>'
                f'<div style="display:flex;gap:1rem;flex-wrap:wrap;">'
                f'<a href="{url_me}" target="_blank" rel="noopener noreferrer" '
                f'style="flex:1;min-width:160px;display:block;text-align:center;background:#1A6FA8;color:white;'
                f'font-size:0.95rem;font-weight:700;padding:0.65rem 1rem;border-radius:8px;'
                f'text-decoration:none;letter-spacing:0.01em;">🔵 MedEasy-তে অর্ডার করুন</a>'
                f'<a href="{url_ep}" target="_blank" rel="noopener noreferrer" '
                f'style="flex:1;min-width:160px;display:block;text-align:center;background:#27AE60;color:white;'
                f'font-size:0.95rem;font-weight:700;padding:0.65rem 1rem;border-radius:8px;'
                f'text-decoration:none;letter-spacing:0.01em;">🟢 ePharma-তে অর্ডার করুন</a>'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.caption(
            "SkinAI কোনো ওষুধ সুপারিশ করে না — শুধু ডাক্তারের পরামর্শকৃত ওষুধ কিনুন।\n"
            "SkinAI does not recommend medicines. Only purchase what your doctor prescribed."
        )

# ── Demo consultation transcript (Rahim — Tinea Corporis) ─────────────────────
# Matches the demo_consultation_summary.pdf exactly so judges see end-to-end.

DEMO_TRANSCRIPT = """ডাক্তার: আসুন রহিম ভাই, বসুন। আজকের SkinAI রিপোর্ট দেখলাম — বাম হাতে টিনিয়া কর্পোরিস, ৮২% নিশ্চিত। আপনার সমস্যা কতদিন ধরে?

রহিম: ডাক্তার সাহেব, তিন সপ্তাহ হয়ে গেছে। গোলাকার লাল দাগ, চুলকানি অনেক। বাড়িতে নারকেল তেল দিয়েছিলাম কিন্তু কোনো কাজ হয়নি।

ডাক্তার: হ্যাঁ, নারকেল তেল এই রোগে কাজ করে না। এটা একটা ছত্রাক সংক্রমণ — Tinea Corporis, যাকে আমরা দাদ বলি। চিন্তা নেই, সম্পূর্ণ সারানো যায়।

আমি দুটো ওষুধ দিচ্ছি:

প্রথম — ক্লোট্রিমাজল ১% ক্রিম। প্রতিদিন সকালে এবং রাতে — দুইবার — পাতলা করে লাগাবেন। আগে এলাকাটা সাবান দিয়ে ধুয়ে ভালো করে শুকাবেন, তারপর লাগাবেন। ১৪ দিন করতে হবে — মাঝে বন্ধ করবেন না।

দ্বিতীয় — সেটিরিজিন ১০ মিলিগ্রাম ট্যাবলেট। রাতে ঘুমানোর আগে একটা, ৭ দিন। এটা চুলকানি কমাবে।

রহিম: বুঝেছি। আর কী করতে হবে?

ডাক্তার: কয়েকটা গুরুত্বপূর্ণ কথা শুনুন:

করণীয় — এলাকাটা সবসময় পরিষ্কার ও শুকনো রাখবেন। সব কাপড়, বিছানার চাদর গরম পানিতে ধুবেন। ঢিলা সুতির পোশাক পরবেন। ১৪ দিনের কোর্স শেষ করবেন।

বর্জনীয় — পরিবারের সাথে তোয়ালে বা কাপড় শেয়ার করবেন না। দাগে হাত দিয়ে আঁচড়াবেন না — ছড়িয়ে যাবে। নিজে নিজে ওষুধ বন্ধ করবেন না। কোনো ঘরোয়া প্রলেপ দেবেন না।

খাবার — চিনি কম খাবেন, টক দই খেতে পারেন, প্রচুর পানি পান করুন।

রহিম: কতদিনে ভালো হবে?

ডাক্তার: ৭ দিনে উন্নতি দেখবেন, ১৪ দিনে সম্পূর্ণ ভালো হয়ে যাবে। তবে মনে রাখবেন — যদি ৭ দিনে কোনো উন্নতি না হয়, দাগ মুখে বা হাতে ছড়িয়ে পড়ে, ফোসকা দেখা দেয়, বা জ্বর আসে — সঙ্গে সঙ্গে জেলা হাসপাতালে যাবেন।

১৪ দিন পর — ৬ই জুন — আমার কাছে আবার আসবেন।

রহিম: ধন্যবাদ অনেক ডাক্তার সাহেব।

ডাক্তার: ভালো থাকবেন রহিম ভাই। SkinAI সিস্টেম সঠিকভাবেই ধরেছে রোগটা — ভালো করেছেন দেরি না করে আসার জন্য।

---
[Consultation duration: 30 minutes | Date: 2026-05-23 | Dr. Nusrat Jahan — CMCH]"""


# ── YouTube / video helpers ───────────────────────────────────────────────────

def _extract_youtube_id(url: str) -> str | None:
    """Return YouTube video ID from a watch or short URL, or None."""
    import re
    patterns = [
        r"(?:youtube\.com/watch\?v=|youtu\.be/)([A-Za-z0-9_-]{11})",
        r"youtube\.com/embed/([A-Za-z0-9_-]{11})",
    ]
    for pat in patterns:
        m = re.search(pat, url)
        if m:
            return m.group(1)
    return None


def _embed_video(url: str) -> None:
    """Embed video — YouTube via iframe, everything else via st.video."""
    yt_id = _extract_youtube_id(url)
    if yt_id:
        st.markdown(
            f'<div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;">'
            f'<iframe style="position:absolute;top:0;left:0;width:100%;height:100%;" '
            f'src="https://www.youtube.com/embed/{yt_id}?rel=0" '
            f'frameborder="0" allow="autoplay; encrypted-media" allowfullscreen>'
            f'</iframe></div>',
            unsafe_allow_html=True,
        )
    else:
        try:
            st.video(url)
        except Exception:
            st.info("Video could not be loaded. Paste a valid YouTube URL above.")


# ── Tab 1 — Demo Video ────────────────────────────────────────────────────────

def _tab_demo_video() -> str | None:
    """
    Show video embed + one-click demo transcript loader.
    Returns transcript string if demo loaded, else None.
    """
    st.markdown(
        "#### 🎬 Demo Consultation Video\n"
        "Paste your consultation demo video URL below (YouTube link or direct .mp4). "
        "Then click **Load Demo Transcript** to see the AI-generated PDF instantly."
    )

    video_url = st.text_input(
        "Video URL",
        value=st.session_state.get("demo_video_url", ""),
        placeholder="https://www.youtube.com/watch?v=YOUR_VIDEO_ID",
        key="demo_video_url_input",
        label_visibility="collapsed",
    )

    if video_url and video_url.strip():
        st.session_state["demo_video_url"] = video_url.strip()
        _embed_video(video_url.strip())
    else:
        # Placeholder art when no URL set
        st.markdown(
            '<div style="background:#f0f4f8;border:2px dashed #aec6cf;border-radius:8px;'
            'height:220px;display:flex;align-items:center;justify-content:center;'
            'flex-direction:column;color:#666;font-size:14px;text-align:center;padding:20px;">'
            '<span style="font-size:40px;">🎥</span><br>'
            '<b>Paste your YouTube demo video URL above</b><br>'
            '<span style="font-size:12px;margin-top:6px;">Once you record the Rahim story demo, '
            'paste the YouTube link here</span>'
            '</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ── Demo transcript loader + instant PDF download ─────────────────────────
    st.markdown(
        '<div style="background:#EBF5FB;border:1.5px solid #AED6F1;border-radius:10px;'
        'padding:0.8rem 1rem 0.6rem 1rem;margin-bottom:0.7rem;">'
        '<div style="font-weight:700;font-size:0.88rem;color:#1A5276;margin-bottom:0.15rem;">'
        '📋 Demo: AI Post-Consultation Care Summary</div>'
        '<div style="font-size:0.77rem;color:#1F618D;">'
        'Download a real AI-generated care summary extracted from a doctor–patient '
        'conversation — medicines, dos &amp; don\'ts, warning signs, follow-up date. '
        'No recording needed.</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    col_a, col_b, col_c = st.columns([2, 1, 1])
    with col_a:
        st.markdown(
            "**Try the demo instantly** — load Rahim's pre-built consultation "
            "transcript and generate a real PDF without recording."
        )
        st.caption(
            "Rahim Uddin · 35 · Tinea Corporis · Dr. Nusrat Jahan — CMCH · 2026-05-23"
        )
    with col_b:
        if st.button(
            "▶ Load Demo Transcript",
            use_container_width=True,
            type="primary",
            key="load_demo_transcript",
        ):
            st.session_state["consultation_transcript"] = DEMO_TRANSCRIPT
            st.session_state["consultation_completed"]  = True
            st.session_state["consultation_duration_minutes"] = 30
            st.rerun()

    with col_c:
        # Always-visible demo summary PDF download — no pipeline run needed
        if "_demo_summary_pdf" not in st.session_state or not st.session_state.get("prescribed_medicines_list"):
            try:
                from pdf_gen.consultation_summary import generate_demo_summary_pdf
                _demo_pdf, _demo_meds = generate_demo_summary_pdf()
                st.session_state["_demo_summary_pdf"] = _demo_pdf
                st.session_state["prescribed_medicines_list"] = _demo_meds
            except Exception as _e:
                logger.warning("Demo summary PDF pre-gen failed: %s", _e)
                st.session_state["_demo_summary_pdf"] = None

        _dsb = st.session_state.get("_demo_summary_pdf")
        if _dsb:
            st.download_button(
                label="📥 Demo Care Summary PDF",
                data=_dsb,
                file_name="skinai_rahim_care_summary.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="primary",
                key="dl_demo_summary_always",
            )
        else:
            st.button(
                "📥 Demo Care Summary PDF",
                use_container_width=True,
                disabled=True,
                key="dl_demo_summary_disabled",
            )
    if st.session_state.get("consultation_transcript") == DEMO_TRANSCRIPT:
        with st.expander("📄 View demo transcript", expanded=False):
            st.text(DEMO_TRANSCRIPT)

    _render_medeasy_section(st.session_state.get("prescribed_medicines_list", []))

    return None


# ── Tab 2 — Live Audio Recording ──────────────────────────────────────────────

def _tab_live_recording() -> str | None:
    """
    Record or upload consultation audio → Whisper transcript.
    Returns transcript string on success, else None.
    """
    st.markdown(
        "#### 🎙️ Record or Upload Consultation Audio\n"
        "Record the patient-doctor conversation, or upload an existing audio file. "
        "The Bengali voice AI (Whisper) will transcribe it automatically."
    )

    transcript_out = None

    # ── Option A: microphone recording ───────────────────────────────────────
    st.markdown("**Option A — Record directly (microphone)**")
    try:
        audio_val = st.audio_input(
            "Click the mic to start recording",
            key="consultation_audio_recorder",
        )
        if audio_val is not None:
            audio_bytes = audio_val.read()
            if st.button("🔄 Transcribe Recording", key="transcribe_mic", type="primary"):
                with st.spinner("Whisper AI সক্রিয় — বাংলা ট্রান্সক্রিপ্ট তৈরি হচ্ছে..."):
                    from voice.pipeline import transcribe_audio
                    transcript_out = transcribe_audio(audio_bytes, language="bn")
                    if not transcript_out:
                        st.warning(
                            "Transcript is empty — audio may be too short or silent. "
                            "Try speaking closer to the microphone."
                        )
    except AttributeError:
        st.info(
            "Live microphone recording requires Streamlit ≥ 1.33. "
            "Please use Option B (file upload) below."
        )

    st.markdown("---")

    # ── Option B: file upload ─────────────────────────────────────────────────
    st.markdown("**Option B — Upload audio file (.wav · .mp3 · .m4a · .ogg · .webm)**")
    audio_file = st.file_uploader(
        "Upload consultation recording",
        type=["wav", "mp3", "m4a", "ogg", "webm"],
        key="consultation_audio_upload",
        label_visibility="collapsed",
    )
    if audio_file is not None:
        st.audio(audio_file)
        if st.button("🔄 Transcribe Uploaded Audio", key="transcribe_upload", type="primary"):
            audio_bytes = audio_file.read()
            with st.spinner("Whisper AI সক্রিয় — ট্রান্সক্রিপ্ট তৈরি হচ্ছে..."):
                from voice.pipeline import transcribe_audio
                transcript_out = transcribe_audio(audio_bytes, language="bn")
                if not transcript_out:
                    st.warning(
                        "No speech detected. Check that the file contains audible Bengali speech."
                    )

    return transcript_out


# ── Tab 3 — Manual Notes ─────────────────────────────────────────────────────

def _tab_manual_notes() -> str | None:
    """Type/paste consultation notes. Returns transcript string or None."""
    st.markdown(
        "#### 📝 Type or Paste Consultation Notes\n"
        "If you don't have a recording, type what the doctor said. "
        "Include medicines, instructions, and follow-up date."
    )
    notes = st.text_area(
        "Consultation notes",
        value=st.session_state.get("manual_consultation_notes_text", ""),
        placeholder=(
            "ডাক্তার বললেন: ক্লোট্রিমাজল ক্রিম দিনে দুইবার লাগাবেন...\n"
            "Doctor said: Apply Clotrimazole cream twice daily for 14 days. "
            "Return on June 6th or if rash spreads."
        ),
        height=220,
        key="manual_consultation_text_area",
    )
    if notes and notes.strip():
        st.session_state["manual_consultation_notes_text"] = notes
        return notes.strip()
    return None


# ── Transcript editor + PDF generation ───────────────────────────────────────

def _render_transcript_and_pdf(transcript: str) -> None:
    """Show editable transcript and PDF generation button."""
    st.markdown("---")
    st.markdown("### 📋 পরামর্শ ট্রান্সক্রিপ্ট | Consultation Transcript")

    edited = st.text_area(
        "Review and edit transcript before generating PDF",
        value=transcript,
        height=180,
        key="final_transcript_editor",
        label_visibility="collapsed",
    )
    if edited and edited.strip():
        transcript = edited.strip()

    # Store confirmed transcript
    st.session_state["consultation_transcript"]       = transcript
    st.session_state["consultation_completed"]        = True
    st.session_state["consultation_duration_minutes"] = st.session_state.get(
        "consultation_duration_minutes", 30
    )

    st.markdown("---")
    st.markdown("### 📥 পরামর্শ সারসংক্ষেপ PDF | Care Summary PDF")

    info_col, btn_col = st.columns([3, 1])
    with info_col:
        st.success(
            "পরামর্শ রেকর্ড করা হয়েছে। AI এখন ডাক্তারের নির্দেশনা বিশ্লেষণ করে "
            "একটি দ্বিভাষিক (বাংলা + ইংরেজি) সারসংক্ষেপ তৈরি করবে।\n\n"
            "Consultation captured. AI will now extract the doctor's instructions "
            "and generate a bilingual Bengali+English care summary PDF."
        )
    with btn_col:
        duration = st.session_state.get("consultation_duration_minutes", 30)
        if st.button(
            "⚙ Generate PDF",
            use_container_width=True,
            type="secondary",
            key="generate_pdf_trigger",
        ):
            st.session_state["_generate_pdf_now"] = True

    if st.session_state.get("_generate_pdf_now"):
        with st.spinner(
            "Gemini AI ডাক্তারের নির্দেশনা বিশ্লেষণ করছে... | "
            "Gemini extracting doctor instructions..."
        ):
            try:
                from pdf_gen.consultation_summary import generate_consultation_summary_pdf
                from datetime import datetime

                pdf_bytes, medicines = generate_consultation_summary_pdf(
                    consultation_transcript=transcript,
                    session_state=dict(st.session_state),
                    consultation_duration_minutes=duration,
                )
                st.session_state["summary_pdf_bytes"] = pdf_bytes
                st.session_state["prescribed_medicines_list"] = medicines
                st.session_state["_generate_pdf_now"] = False
            except Exception as exc:
                st.error(f"PDF generation failed: {exc}")
                st.session_state["_generate_pdf_now"] = False

    if st.session_state.get("summary_pdf_bytes"):
        from datetime import datetime

        pdf_bytes = st.session_state["summary_pdf_bytes"]
        size_kb   = len(pdf_bytes) / 1024

        st.download_button(
            label="📥 সারসংক্ষেপ ডাউনলোড করুন  |  Download Care Summary PDF",
            data=pdf_bytes,
            file_name=f"skinai_care_summary_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary",
            key="final_pdf_download",
        )
        st.caption(f"PDF size: {size_kb:.1f} KB  ·  Bilingual Bengali + English")

        # Preview metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Sections", "6")
        m2.metric("Language", "Bengali + English")
        m3.metric("Duration", f"{duration} min")
        m4.metric("Size", f"{size_kb:.0f} KB")

        _render_medeasy_section(st.session_state.get("prescribed_medicines_list", []))


# ── Public entry point ────────────────────────────────────────────────────────

def render_consultation_room() -> None:
    """Render the full Consultation Room UI. Call this from app.py Tab 5."""
    st.markdown("---")
    st.markdown("## 🏥 পরামর্শ কক্ষ  |  Consultation Room")
    st.markdown(
        "Your appointment is confirmed. Choose how to capture your consultation — "
        "watch the demo video, record live audio, or type notes. "
        "The AI will extract your doctor's instructions and generate a take-home PDF."
    )

    # Three input modes
    tab_video, tab_audio, tab_manual = st.tabs([
        "🎬 Demo Video",
        "🎙️ Live Recording",
        "📝 Manual Notes",
    ])

    new_transcript = None

    with tab_video:
        _tab_demo_video()

    with tab_audio:
        result = _tab_live_recording()
        if result:
            new_transcript = result

    with tab_manual:
        result = _tab_manual_notes()
        if result:
            new_transcript = result

    # If a tab just produced a new transcript, store it
    if new_transcript:
        st.session_state["consultation_transcript"]       = new_transcript
        st.session_state["consultation_completed"]        = True
        st.session_state["consultation_duration_minutes"] = 30

    # Show transcript editor + PDF button whenever a transcript is ready
    final_transcript = st.session_state.get("consultation_transcript", "")
    if final_transcript and st.session_state.get("consultation_completed"):
        _render_transcript_and_pdf(final_transcript)
