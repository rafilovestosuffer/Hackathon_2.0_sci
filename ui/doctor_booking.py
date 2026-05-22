"""
ui/doctor_booking.py — Doctor consultation booking module.

No external APIs. No database. Session state only.
Full care loop: Screen → Diagnose → Triage → Book → Video Call → PDF
"""

import random
from datetime import date, timedelta

import streamlit as st

# ── Demo doctor (hardcoded — no DB) ──────────────────────────────────────────

DEMO_DOCTOR = {
    "id": "dr_nusrat_001",
    "name": "Dr. Nusrat Jahan",
    "name_bn": "ডা. নুসরাত জাহান",
    "credentials": "MBBS, DDV (Dermatology & Venereology)",
    "credentials_bn": "এমবিবিএস, ডিডিভি (চর্মরোগ বিশেষজ্ঞ)",
    "hospital": "Chittagong Medical College Hospital",
    "hospital_bn": "চট্টগ্রাম মেডিকেল কলেজ হাসপাতাল",
    "department": "Department of Dermatology",
    "department_bn": "চর্মরোগ বিভাগ",
    "experience_years": 12,
    "languages": ["Bengali", "English"],
    "specializations": [
        "Skin Infections", "Eczema & Psoriasis",
        "Pigmentation Disorders", "Tropical Dermatology",
    ],
    "available_days": {
        "Sunday": True,
        "Tuesday": True,
        "Thursday": True,
    },
    "morning_slots": ["10:00 AM", "10:30 AM", "11:00 AM", "11:30 AM"],
    "evening_slots": ["06:00 PM", "06:30 PM", "07:00 PM", "07:30 PM"],
    "consultation_duration_min": 20,
    "fee_bdt": 500,
    "rating": 4.8,
    "total_consultations": 1240,
    "avatar_emoji": "👩‍⚕️",
    "meet_link": "https://meet.google.com/abc-defg-hij",
    "verified": True,
}

# ── Bengali helpers ───────────────────────────────────────────────────────────

_BN_NUM = {
    "0": "০", "1": "১", "2": "২", "3": "৩", "4": "৪",
    "5": "৫", "6": "৬", "7": "৭", "8": "৮", "9": "৯",
}

_BN_DAYS = {
    "Sunday":    "রবিবার",
    "Monday":    "সোমবার",
    "Tuesday":   "মঙ্গলবার",
    "Wednesday": "বুধবার",
    "Thursday":  "বৃহস্পতিবার",
    "Friday":    "শুক্রবার",
    "Saturday":  "শনিবার",
}

_BN_MONTHS = [
    "জানুয়ারি", "ফেব্রুয়ারি", "মার্চ", "এপ্রিল", "মে", "জুন",
    "জুলাই", "আগস্ট", "সেপ্টেম্বর", "অক্টোবর", "নভেম্বর", "ডিসেম্বর",
]


def _to_bn_num(s: str) -> str:
    """Convert ASCII digit string to Bengali numeral string."""
    return "".join(_BN_NUM.get(c, c) for c in s)


def _time_to_bn(time_en: str) -> str:
    """
    Convert English time to Bengali.
    '06:30 PM' → 'সন্ধ্যা ৬:৩০'
    '10:00 AM' → 'সকাল ১০:০০'
    AM → সকাল | PM <5pm → বিকেল | PM 5pm+ → সন্ধ্যা
    """
    try:
        parts = time_en.strip().split()
        h_str, m_str = parts[0].split(":")
        meridiem = parts[1].upper()
        hour = int(h_str)
        if meridiem == "AM":
            prefix = "সকাল"
        elif hour < 5:   # 12–4 PM → বিকেল; 5–11 PM → সন্ধ্যা (12-hr clock)
            prefix = "বিকেল"
        else:
            prefix = "সন্ধ্যা"
        return f"{prefix} {_to_bn_num(str(hour))}:{_to_bn_num(m_str)}"
    except Exception:
        return time_en


# ── Slot generation ───────────────────────────────────────────────────────────

def get_available_slots(days_ahead: int = 7) -> list:
    """
    Generate available appointment slots for the next `days_ahead` days.
    Only returns days matching DEMO_DOCTOR['available_days'] (Sun/Tue/Thu).
    Returns list of dicts: {date, date_display, date_display_bn, day_name,
                            day_name_bn, slots}
    """
    today = date.today()
    result = []
    for i in range(1, days_ahead + 1):
        d = today + timedelta(days=i)
        day_name = d.strftime("%A")
        if not DEMO_DOCTOR["available_days"].get(day_name):
            continue
        month_idx = d.month - 1
        date_display = f"{day_name}, {d.day} {d.strftime('%B %Y')}"
        date_display_bn = (
            f"{_BN_DAYS[day_name]}, "
            f"{_to_bn_num(str(d.day))} "
            f"{_BN_MONTHS[month_idx]} "
            f"{_to_bn_num(str(d.year))}"
        )
        time_slots = [
            {"time_en": t, "time_bn": _time_to_bn(t), "available": True}
            for t in DEMO_DOCTOR["morning_slots"] + DEMO_DOCTOR["evening_slots"]
        ]
        result.append({
            "date":            d,
            "date_display":    date_display,
            "date_display_bn": date_display_bn,
            "day_name":        day_name,
            "day_name_bn":     _BN_DAYS[day_name],
            "slots":           time_slots,
        })
    return result


# ── Section renderers (private) ───────────────────────────────────────────────

def _render_tier_context_banner(tier) -> None:
    """Show tier-specific context message above the booking flow."""
    if tier == 1:
        st.info(
            "💊 **আপনার অবস্থা মৃদু।** ফার্মাসিস্টের পরামর্শ যথেষ্ট।\n\n"
            "Your condition is mild — pharmacist advice is sufficient. "
            "Specialist booking is **optional** for a professional second opinion.",
            icon="ℹ️",
        )
    elif tier == 2:
        st.markdown(
            '<div style="background:#FFF3CD;border:2px solid #E67E22;border-radius:10px;'
            'padding:0.75rem 1rem;margin-bottom:0.75rem;">'
            '<div style="font-size:1rem;font-weight:700;color:#7D3C00;">'
            '🏥 বিশেষজ্ঞ ডাক্তারের পরামর্শ প্রয়োজন — এখনই বুক করুন</div>'
            '<div style="font-size:0.82rem;color:#A04000;margin-top:0.2rem;">'
            'Dermatologist consultation recommended. Book your video appointment below.'
            '</div></div>',
            unsafe_allow_html=True,
        )
    elif tier is None:
        st.info(
            "🩺 রোগ নির্ণয়ের পর অ্যাপয়েন্টমেন্ট নিশ্চিত করা যাবে। "
            "আপাতত ডাক্তার ও উপলব্ধ স্লট দেখুন।\n\n"
            "Preview the doctor and available slots. **Complete diagnosis in Tab 1** "
            "to unlock appointment confirmation.",
            icon="💡",
        )


def _render_emergency_block() -> None:
    """Tier 3: show emergency block, block booking form entirely."""
    st.markdown(
        '<div style="background:#FADBD8;border:2px solid #C0392B;border-radius:12px;'
        'padding:1.25rem;text-align:center;margin-bottom:1rem;">'
        '<div style="font-size:1.4rem;font-weight:800;color:#922B21;">🚨 এই অবস্থা জরুরি।</div>'
        '<div style="font-size:1rem;font-weight:700;color:#922B21;margin-top:0.4rem;">'
        'ভিডিও কলের জন্য অপেক্ষা করবেন না।</div>'
        '<div style="font-size:0.88rem;color:#7B241C;margin-top:0.4rem;">'
        'This condition is URGENT. Do NOT wait for a video call.</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="background:#FFFFFF;border:1.5px solid #E2E8F0;border-radius:10px;'
        'padding:1rem 1.25rem;text-align:center;margin-bottom:0.75rem;">'
        '<div style="font-size:1rem;font-weight:700;color:#C0392B;">'
        '🏥 এখনই নিকটতম হাসপাতালে যান</div>'
        '<div style="font-size:0.88rem;color:#4A5568;margin-top:0.35rem;">'
        'Go to the nearest District Hospital immediately.</div>'
        '<div style="background:#C0392B;color:#FFFFFF;border-radius:8px;'
        'padding:0.6rem 1.4rem;display:inline-block;margin-top:0.7rem;'
        'font-size:1rem;font-weight:700;">'
        '📞 জাতীয় স্বাস্থ্য বাতায়ন: 16789</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.caption(
        "🗺️ Hospital map with 5 nearest locations is available in Tab 1 "
        "(রোগ নির্ণয়) after entering your district."
    )


def _render_doctor_profile() -> None:
    """Section A — Doctor profile card."""
    doc = DEMO_DOCTOR
    filled = int(doc["rating"])
    stars = "★" * filled + "☆" * (5 - filled)
    spec_tags = "".join(
        f'<span style="background:#E6FFFA;color:#0D9E75;padding:0.15rem 0.5rem;'
        f'border-radius:99px;font-size:0.72rem;font-weight:600;margin:0.15rem '
        f'0.15rem 0.15rem 0;">{s}</span>'
        for s in doc["specializations"]
    )
    verified_html = (
        '<span style="background:#D4EDDA;color:#155724;padding:0.15rem 0.55rem;'
        'border-radius:99px;font-size:0.72rem;font-weight:700;display:inline-block;'
        'margin-top:0.3rem;">✅ DGHS Verified</span>'
        if doc["verified"] else ""
    )
    total_bn = "১,২৪০+"

    st.markdown(
        f'<div style="background:#f0f4f8;border-radius:12px;padding:1.25rem;'
        f'box-shadow:0 2px 6px rgba(0,0,0,0.07);margin-bottom:1rem;">'
        f'<div style="display:flex;gap:1.25rem;align-items:flex-start;">'
        # Avatar column
        f'<div style="text-align:center;min-width:82px;">'
        f'<div style="font-size:3.4rem;">{doc["avatar_emoji"]}</div>'
        f'<div style="color:#F4C842;font-size:1rem;letter-spacing:0.05em;">{stars}</div>'
        f'<div style="font-size:0.7rem;color:#718096;">{doc["rating"]}/5</div>'
        f'{verified_html}'
        f'</div>'
        # Info column
        f'<div style="flex:1;">'
        f'<div style="font-size:1.15rem;font-weight:800;color:#1A202C;">{doc["name_bn"]}</div>'
        f'<div style="font-size:0.95rem;font-weight:600;color:#1A6FA8;">{doc["name"]}</div>'
        f'<div style="font-size:0.8rem;color:#4A5568;margin-top:0.15rem;">{doc["credentials_bn"]}</div>'
        f'<div style="font-size:0.78rem;color:#718096;">{doc["credentials"]}</div>'
        f'<div style="font-size:0.82rem;color:#2D3748;margin-top:0.35rem;">🏥 {doc["hospital_bn"]}</div>'
        f'<div style="font-size:0.75rem;color:#718096;">{doc["hospital"]}</div>'
        f'<div style="margin-top:0.4rem;display:flex;gap:0.75rem;flex-wrap:wrap;'
        f'font-size:0.78rem;color:#4A5568;">'
        f'<span>⏱️ {doc["experience_years"]} yrs exp.</span>'
        f'<span>💬 {" + ".join(doc["languages"])}</span>'
        f'<span style="color:#0D9E75;font-weight:600;">{total_bn} পরামর্শ সম্পন্ন</span>'
        f'</div>'
        f'<div style="margin-top:0.5rem;display:flex;flex-wrap:wrap;">{spec_tags}</div>'
        f'</div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )


def _render_calendar_strip(available_slots: list) -> None:
    """Section B — 7-day horizontal calendar, highlights Sun/Tue/Thu."""
    today = date.today()
    slot_map = {s["date"]: (i, s) for i, s in enumerate(available_slots)}
    cols = st.columns(7)

    for offset in range(7):
        d = today + timedelta(days=offset + 1)
        day_name = d.strftime("%A")
        with cols[offset]:
            if d in slot_map:
                slot_idx, slot_data = slot_map[d]
                is_sel = st.session_state.get("selected_date_idx") == slot_idx
                border = "#0D9E75" if is_sel else "#CBD5E1"
                bg = "#E6FFFA" if is_sel else "#FFFFFF"
                tick = "✓ " if is_sel else ""
                st.markdown(
                    f'<div style="background:{bg};border:2px solid {border};'
                    f'border-radius:10px;padding:0.45rem 0.2rem;text-align:center;'
                    f'margin-bottom:0.3rem;cursor:pointer;">'
                    f'<div style="font-size:0.62rem;font-weight:700;color:#0D9E75;'
                    f'line-height:1.2;">{slot_data["day_name_bn"]}</div>'
                    f'<div style="font-size:1.25rem;font-weight:800;color:#1A202C;">'
                    f'{_to_bn_num(str(d.day))}</div>'
                    f'<div style="font-size:0.62rem;color:#718096;">'
                    f'{_BN_MONTHS[d.month - 1]}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                label = f"{tick}বেছেছেন" if is_sel else "বেছে নিন"
                if st.button(label, key=f"date_sel_{slot_idx}",
                             use_container_width=True):
                    st.session_state.selected_date_idx = slot_idx
                    st.session_state.selected_slot = None
                    st.rerun()
            else:
                # Unavailable day
                st.markdown(
                    f'<div style="background:#F1F5F9;border:1px solid #E2E8F0;'
                    f'border-radius:10px;padding:0.45rem 0.2rem;text-align:center;'
                    f'margin-bottom:0.3rem;opacity:0.55;">'
                    f'<div style="font-size:0.62rem;font-weight:600;color:#A0AEC0;">'
                    f'{_BN_DAYS.get(day_name, day_name)}</div>'
                    f'<div style="font-size:1.25rem;font-weight:800;color:#CBD5E1;">'
                    f'{_to_bn_num(str(d.day))}</div>'
                    f'<div style="font-size:0.62rem;color:#CBD5E1;">অনুপলব্ধ</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )


def _render_time_slots(day_data: dict) -> None:
    """Section C — Morning + evening slot grid (2×4 layout)."""
    slots = day_data["slots"]
    morning = [s for s in slots if "AM" in s["time_en"]]
    evening = [s for s in slots if "PM" in s["time_en"]]

    st.markdown(
        f'<div class="card-section-header" style="margin-top:0.75rem;">'
        f'<span style="font-size:1.0rem;">🕐</span>'
        f'<div>'
        f'<div class="card-section-title">সময় বেছে নিন · Select Time</div>'
        f'<div class="card-section-sub">{day_data["date_display_bn"]} · '
        f'{day_data["date_display"]}</div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    slot_col1, slot_col2 = st.columns(2)

    with slot_col1:
        st.markdown(
            '<div style="font-size:0.82rem;font-weight:700;color:#1A6FA8;'
            'margin-bottom:0.4rem;">☀️ সকাল · Morning</div>',
            unsafe_allow_html=True,
        )
        m1, m2 = st.columns(2)
        for i, slot in enumerate(morning):
            col = m1 if i % 2 == 0 else m2
            with col:
                is_sel = st.session_state.get("selected_slot") == slot["time_en"]
                btn_type = "primary" if is_sel else "secondary"
                if st.button(
                    slot["time_bn"],
                    key=f"slot_{slot['time_en']}",
                    type=btn_type,
                    use_container_width=True,
                ):
                    st.session_state.selected_slot = slot["time_en"]
                    st.rerun()

    with slot_col2:
        st.markdown(
            '<div style="font-size:0.82rem;font-weight:700;color:#0D9E75;'
            'margin-bottom:0.4rem;">🌆 সন্ধ্যা · Evening</div>',
            unsafe_allow_html=True,
        )
        e1, e2 = st.columns(2)
        for i, slot in enumerate(evening):
            col = e1 if i % 2 == 0 else e2
            with col:
                is_sel = st.session_state.get("selected_slot") == slot["time_en"]
                btn_type = "primary" if is_sel else "secondary"
                if st.button(
                    slot["time_bn"],
                    key=f"slot_{slot['time_en']}",
                    type=btn_type,
                    use_container_width=True,
                ):
                    st.session_state.selected_slot = slot["time_en"]
                    st.rerun()

    # Show selection summary
    sel_slot = st.session_state.get("selected_slot")
    if sel_slot:
        st.markdown(
            f'<div style="background:#E6FFFA;border:1px solid #0D9E75;border-radius:8px;'
            f'padding:0.4rem 0.75rem;font-size:0.82rem;color:#065F46;margin-top:0.4rem;">'
            f'✓ বেছেছেন: <strong>{_time_to_bn(sel_slot)}</strong> · {sel_slot}'
            f'</div>',
            unsafe_allow_html=True,
        )


def _render_patient_info_fields(patient_history: dict) -> None:
    """Section D — Minimal patient info (name + phone only)."""
    st.markdown(
        '<div style="font-size:0.78rem;color:#718096;margin-bottom:0.5rem;">'
        '🔒 এই তথ্য শুধুমাত্র অ্যাপয়েন্টমেন্টের জন্য ব্যবহৃত হবে। · '
        'This information will only be used for your appointment.'
        '</div>',
        unsafe_allow_html=True,
    )
    default_name = (
        patient_history.get("patient_name")
        or st.session_state.get("form_patient_name", "")
        or ""
    )
    pi_col1, pi_col2 = st.columns(2)
    with pi_col1:
        st.text_input(
            "আপনার নাম · Your Name",
            value=default_name,
            key="patient_name_input",
            placeholder="যেমন: রহিম / Rahim",
        )
    with pi_col2:
        st.text_input(
            "মোবাইল নম্বর · Mobile Number",
            key="patient_phone",
            placeholder="01XXXXXXXXX",
            max_chars=11,
        )


def _render_confirm_button(tier, available_slots: list) -> None:
    """Section E — Confirm button with validation."""
    is_disabled = (tier is None)

    if is_disabled:
        st.markdown(
            '<div class="info-box" style="margin-bottom:0.5rem;">'
            '🩺 রোগ নির্ণয়ের পর অ্যাপয়েন্টমেন্ট নিশ্চিত করা যাবে।<br>'
            '<span style="font-size:0.78rem;color:#718096;">'
            'Complete diagnosis in Tab 1 to enable booking.</span>'
            '</div>',
            unsafe_allow_html=True,
        )

    clicked = st.button(
        "📅 অ্যাপয়েন্টমেন্ট নিশ্চিত করুন | Confirm Appointment",
        type="primary",
        use_container_width=True,
        key="confirm_booking_btn",
        disabled=is_disabled,
    )

    if not clicked:
        return

    # Validation
    errors = []
    sel_date_idx = st.session_state.get("selected_date_idx")
    sel_slot     = st.session_state.get("selected_slot")
    name         = st.session_state.get("patient_name_input", "").strip()
    phone        = st.session_state.get("patient_phone", "").strip()

    if sel_date_idx is None:
        errors.append("❌ তারিখ বেছে নিন। · Please select a date.")
    if sel_slot is None:
        errors.append("❌ সময় বেছে নিন। · Please select a time slot.")
    if not name or len(name) < 2:
        errors.append("❌ সঠিক নাম দিন (ন্যূনতম ২ অক্ষর)। · Enter a valid name (min 2 chars).")
    if not (phone.startswith("01") and len(phone) == 11 and phone.isdigit()):
        errors.append("❌ সঠিক মোবাইল নম্বর দিন (01XXXXXXXXX)। · Enter valid mobile (01XXXXXXXXX).")

    if errors:
        for err in errors:
            st.error(err)
        return

    # Build booking details
    day_data = available_slots[sel_date_idx]
    disease = (st.session_state.get("prediction") or {}).get("disease", "")
    try:
        from model.disease_labels import get_bengali as _get_bn
        disease_bn = _get_bn(disease)
    except Exception:
        disease_bn = ""

    booking_id = (
        f"SKN-{day_data['date'].strftime('%d%m')}-{random.randint(1000, 9999)}"
    )
    st.session_state.booking_details = {
        "doctor_name":         DEMO_DOCTOR["name"],
        "doctor_name_bn":      DEMO_DOCTOR["name_bn"],
        "doctor_credentials":  DEMO_DOCTOR["credentials"],
        "hospital":            DEMO_DOCTOR["hospital"],
        "hospital_bn":         DEMO_DOCTOR["hospital_bn"],
        "appointment_date":    day_data["date_display"],
        "appointment_date_bn": day_data["date_display_bn"],
        "appointment_time":    sel_slot,
        "appointment_time_bn": _time_to_bn(sel_slot),
        "consultation_fee":    DEMO_DOCTOR["fee_bdt"],
        "meet_link":           DEMO_DOCTOR["meet_link"],
        "patient_name":        name,
        "disease_diagnosed":   disease,
        "disease_diagnosed_bn": disease_bn,
        "tier":                tier or 0,
        "booking_id":          booking_id,
    }
    st.session_state.booking_confirmed = True
    st.rerun()


def _render_confirmed_booking_card() -> None:
    """Section F — Confirmed booking card with video call button."""
    bd = st.session_state.booking_details

    # Success banner
    st.markdown(
        '<div style="background:#D4EDDA;border:2px solid #28A745;border-radius:12px;'
        'padding:1rem;margin-bottom:1rem;text-align:center;">'
        '<div style="font-size:1.2rem;font-weight:800;color:#155724;">'
        '✅ অ্যাপয়েন্টমেন্ট সফলভাবে নিশ্চিত হয়েছে!</div>'
        '<div style="font-size:0.85rem;color:#155724;margin-top:0.2rem;">'
        'Appointment Successfully Confirmed!</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    # Booking summary card
    disease_line = ""
    if bd.get("disease_diagnosed"):
        disease_line = (
            f'<div><div style="font-size:0.75rem;color:#718096;">রোগ · Condition</div>'
            f'<div style="font-weight:600;">{bd["disease_diagnosed"]}</div></div>'
        )

    st.markdown(
        f'<div style="background:#FFFFFF;border-left:4px solid #00C896;border-radius:10px;'
        f'padding:1.25rem;box-shadow:0 2px 8px rgba(0,0,0,0.08);margin-bottom:1rem;">'
        f'<div style="font-family:monospace;font-size:0.75rem;color:#718096;'
        f'margin-bottom:0.75rem;font-weight:600;">'
        f'বুকিং আইডি: {bd["booking_id"]}</div>'
        f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:0.6rem;">'
        f'<div><div style="font-size:0.72rem;color:#718096;">ডাক্তার · Doctor</div>'
        f'<div style="font-weight:700;font-size:0.9rem;">{bd["doctor_name_bn"]}</div>'
        f'<div style="font-size:0.75rem;color:#4A5568;">{bd["doctor_name"]}</div>'
        f'<div style="font-size:0.72rem;color:#718096;">{bd["doctor_credentials"]}</div></div>'
        f'<div><div style="font-size:0.72rem;color:#718096;">হাসপাতাল · Hospital</div>'
        f'<div style="font-weight:700;font-size:0.85rem;">{bd["hospital_bn"]}</div>'
        f'<div style="font-size:0.75rem;color:#4A5568;">{bd["hospital"]}</div></div>'
        f'<div><div style="font-size:0.72rem;color:#718096;">তারিখ · Date</div>'
        f'<div style="font-weight:700;">{bd["appointment_date_bn"]}</div>'
        f'<div style="font-size:0.75rem;color:#4A5568;">{bd["appointment_date"]}</div></div>'
        f'<div><div style="font-size:0.72rem;color:#718096;">সময় · Time</div>'
        f'<div style="font-weight:700;font-size:1rem;">{bd["appointment_time_bn"]}</div>'
        f'<div style="font-size:0.75rem;color:#4A5568;">{bd["appointment_time"]}</div></div>'
        f'<div><div style="font-size:0.72rem;color:#718096;">রোগী · Patient</div>'
        f'<div style="font-weight:700;">{bd["patient_name"]}</div></div>'
        f'<div><div style="font-size:0.72rem;color:#718096;">পরামর্শ ফি · Fee</div>'
        f'<div style="font-weight:700;font-size:1rem;">৳{bd["consultation_fee"]}</div>'
        f'<div style="font-size:0.72rem;color:#718096;">Payable at consultation</div></div>'
        f'{disease_line}'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    # Video call button
    st.link_button(
        "🎥 ভিডিও কলে যোগ দিন | Join Video Call",
        bd["meet_link"],
        type="primary",
        use_container_width=True,
    )

    st.markdown(
        '<div style="font-size:0.78rem;color:#718096;text-align:center;'
        'margin:0.5rem 0 1rem 0;">'
        'ডাক্তার অ্যাপয়েন্টমেন্টের ৫ মিনিট আগে একই লিংকে যোগ দেবেন।<br>'
        '<em>Doctor will join at the same link 5 minutes before your appointment.</em>'
        '</div>',
        unsafe_allow_html=True,
    )

    # PDF nudge when booking is confirmed
    st.markdown(
        '<div style="background:#EFF6FF;border:1px solid #93C5FD;border-radius:8px;'
        'padding:0.6rem 0.9rem;font-size:0.78rem;color:#1E40AF;margin-bottom:0.75rem;">'
        '📄 অ্যাপয়েন্টমেন্ট বিবরণ রেফারেল পত্রে অন্তর্ভুক্ত হবে। '
        'Tab 3 থেকে PDF ডাউনলোড করুন।<br>'
        '<em>Appointment details are embedded in your referral PDF (Tab 3).</em>'
        '</div>',
        unsafe_allow_html=True,
    )

    # Cancel button
    if st.button("❌ বুকিং বাতিল | Cancel Booking",
                 key="cancel_booking_btn", type="secondary"):
        st.session_state.booking_confirmed   = False
        st.session_state.booking_details     = None
        st.session_state.selected_date_idx   = None
        st.session_state.selected_slot       = None
        st.rerun()


# ── Public API ────────────────────────────────────────────────────────────────

def render_doctor_booking_tab() -> None:
    """
    Render the full doctor booking tab.
    Reads all state from st.session_state. No parameters required.
    Tier-aware: tier 1 = optional, tier 2 = recommended, tier 3 = emergency only,
    tier None = preview only (confirm disabled).
    """
    # Init booking state if missing
    for key, default in [
        ("booking_confirmed",  False),
        ("booking_details",    None),
        ("selected_date_idx",  None),
        ("selected_slot",      None),
        ("patient_name_input", ""),
        ("patient_phone",      ""),
    ]:
        st.session_state.setdefault(key, default)

    tier_result = st.session_state.get("tier_result")
    tier = tier_result.get("tier") if tier_result else None
    patient_history = st.session_state.get("history") or {}

    # ── Tab header ────────────────────────────────────────────────────────────
    st.markdown(
        '<div class="card-section-header">'
        '<span style="font-size:1.1rem;">📅</span>'
        '<div>'
        '<div class="card-section-title">ডাক্তার বুকিং · Doctor Booking</div>'
        '<div class="card-section-sub">'
        'সঠিক রোগী → সঠিক ডাক্তার → সঠিক সময় · Video consultation · ৳500</div>'
        '</div></div>',
        unsafe_allow_html=True,
    )

    # ── Tier-aware context banner ─────────────────────────────────────────────
    _render_tier_context_banner(tier)

    # ── Tier 3: show emergency block, abort booking flow ─────────────────────
    if tier == 3:
        _render_emergency_block()
        return

    # ── Section A: Doctor profile ─────────────────────────────────────────────
    _render_doctor_profile()

    # ── Section F: if already confirmed, show confirmation and stop ───────────
    if st.session_state.booking_confirmed and st.session_state.booking_details:
        _render_confirmed_booking_card()
        return

    # ── Section B: Calendar strip ─────────────────────────────────────────────
    st.markdown(
        '<div class="card-section-header" style="margin-top:0.5rem;">'
        '<span style="font-size:1.0rem;">📅</span>'
        '<div>'
        '<div class="card-section-title">তারিখ বেছে নিন · Select Date</div>'
        '<div class="card-section-sub">পরবর্তী ৭ দিনের উপলব্ধ দিনগুলো (রবি/মঙ্গল/বৃহস্পতি)</div>'
        '</div></div>',
        unsafe_allow_html=True,
    )

    available_slots = get_available_slots(7)

    if not available_slots:
        st.warning("কোনো উপলব্ধ স্লট নেই। · No available slots in the next 7 days.")
        return

    _render_calendar_strip(available_slots)

    # ── Section C: Time slots ─────────────────────────────────────────────────
    sel_idx = st.session_state.get("selected_date_idx")
    if sel_idx is not None and sel_idx < len(available_slots):
        _render_time_slots(available_slots[sel_idx])

    # ── Section D: Patient info ───────────────────────────────────────────────
    st.markdown("---")
    st.markdown(
        '<div class="card-section-header">'
        '<span style="font-size:1.0rem;">👤</span>'
        '<div>'
        '<div class="card-section-title">রোগীর তথ্য · Patient Info</div>'
        '<div class="card-section-sub">শুধুমাত্র অ্যাপয়েন্টমেন্টের জন্য · For appointment only</div>'
        '</div></div>',
        unsafe_allow_html=True,
    )
    _render_patient_info_fields(patient_history)

    # ── Section E: Confirm button ─────────────────────────────────────────────
    st.markdown('<div style="margin-top:0.75rem;"></div>', unsafe_allow_html=True)
    _render_confirm_button(tier, available_slots)

    st.markdown(
        '<div class="sk-disclaimer" style="margin-top:0.75rem;">'
        'ডেমো উদ্দেশ্যে। এটি একটি বাস্তব অ্যাপয়েন্টমেন্ট সিস্টেম নয়। '
        'For demonstration purposes only. Not a real appointment system.'
        '</div>',
        unsafe_allow_html=True,
    )
