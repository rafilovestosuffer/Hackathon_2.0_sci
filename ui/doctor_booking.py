"""
ui/doctor_booking.py — Doctor consultation booking module.

No external APIs. No database. Session state only.
Full care loop: Screen → Diagnose → Triage → Book → Video Call → PDF
6 demo dermatologists across Bangladesh (Dhaka, Chittagong, Rajshahi,
Sylhet, Mymensingh) — each with unique availability, fees, and specialisations.
"""

import random
from datetime import date, timedelta

import streamlit as st

# ══════════════════════════════════════════════════════════════════════════════
# DOCTOR ROSTER (6 hardcoded — no DB)
# ══════════════════════════════════════════════════════════════════════════════

DEMO_DOCTORS = [
    # ── 1. Dr. Nusrat Jahan ── CMCH, Chittagong ──────────────────────────────
    {
        "id": "dr_nusrat_001",
        "name": "Dr. Nusrat Jahan",
        "name_bn": "ডা. নুসরাত জাহান",
        "credentials": "MBBS, DDV (Dermatology & Venereology)",
        "credentials_bn": "এমবিবিএস, ডিডিভি (চর্মরোগ বিশেষজ্ঞ)",
        "hospital": "Chittagong Medical College Hospital",
        "hospital_bn": "চট্টগ্রাম মেডিকেল কলেজ হাসপাতাল",
        "hospital_short": "CMCH · Chittagong",
        "department": "Department of Dermatology",
        "department_bn": "চর্মরোগ বিভাগ",
        "experience_years": 12,
        "languages": ["Bengali", "English"],
        "specializations": [
            "Skin Infections", "Eczema & Psoriasis",
            "Pigmentation Disorders", "Tropical Dermatology",
        ],
        "available_days": {"Sunday": True, "Tuesday": True, "Thursday": True},
        "morning_slots": ["10:00 AM", "10:30 AM", "11:00 AM", "11:30 AM"],
        "evening_slots": ["06:00 PM", "06:30 PM", "07:00 PM", "07:30 PM"],
        "consultation_duration_min": 20,
        "fee_bdt": 500,
        "rating": 4.8,
        "total_consultations": 1240,
        "avatar_emoji": "👩‍⚕️",
        "meet_link": "https://meet.google.com/abc-defg-hij",
        "verified": True,
        "location": "Chittagong",
    },

    # ── 2. Dr. Farhan Ahmed ── DMCH, Dhaka ────────────────────────────────────
    {
        "id": "dr_farhan_002",
        "name": "Dr. Farhan Ahmed",
        "name_bn": "ডা. ফারহান আহমেদ",
        "credentials": "MBBS, MD (Dermatology), MCPS",
        "credentials_bn": "এমবিবিএস, এমডি (চর্মরোগ), এমসিপিএস",
        "hospital": "Dhaka Medical College Hospital",
        "hospital_bn": "ঢাকা মেডিকেল কলেজ হাসপাতাল",
        "hospital_short": "DMCH · Dhaka",
        "department": "Department of Dermatology & STD",
        "department_bn": "চর্মরোগ ও যৌনরোগ বিভাগ",
        "experience_years": 15,
        "languages": ["Bengali", "English"],
        "specializations": [
            "Psoriasis & Immunobullous Disorders", "Skin Cancer Screening",
            "Cosmetic Dermatology", "Autoimmune Skin Disorders",
        ],
        "available_days": {"Monday": True, "Wednesday": True, "Saturday": True},
        "morning_slots": ["09:00 AM", "09:30 AM", "10:00 AM", "10:30 AM"],
        "evening_slots": ["05:00 PM", "05:30 PM", "06:00 PM", "06:30 PM"],
        "consultation_duration_min": 20,
        "fee_bdt": 800,
        "rating": 4.9,
        "total_consultations": 2150,
        "avatar_emoji": "👨‍⚕️",
        "meet_link": "https://meet.google.com/bcd-efgh-ijk",
        "verified": True,
        "location": "Dhaka",
    },

    # ── 3. Dr. Sadia Islam ── BSMMU, Dhaka ───────────────────────────────────
    {
        "id": "dr_sadia_003",
        "name": "Dr. Sadia Islam",
        "name_bn": "ডা. সাদিয়া ইসলাম",
        "credentials": "MBBS, FCPS (Dermatology & Venereology)",
        "credentials_bn": "এমবিবিএস, এফসিপিএস (চর্মরোগ বিশেষজ্ঞ)",
        "hospital": "Bangabandhu Sheikh Mujib Medical University",
        "hospital_bn": "বঙ্গবন্ধু শেখ মুজিব মেডিকেল বিশ্ববিদ্যালয়",
        "hospital_short": "BSMMU · Dhaka",
        "department": "Department of Dermatology",
        "department_bn": "চর্মরোগ বিভাগ",
        "experience_years": 9,
        "languages": ["Bengali", "English"],
        "specializations": [
            "Paediatric Dermatology", "Atopic Dermatitis",
            "Allergic & Contact Dermatitis", "Hair & Nail Disorders",
        ],
        "available_days": {"Sunday": True, "Wednesday": True, "Friday": True},
        "morning_slots": ["10:00 AM", "10:30 AM", "11:00 AM", "11:30 AM"],
        "evening_slots": ["05:00 PM", "05:30 PM", "06:00 PM", "06:30 PM"],
        "consultation_duration_min": 25,
        "fee_bdt": 700,
        "rating": 4.7,
        "total_consultations": 890,
        "avatar_emoji": "👩‍⚕️",
        "meet_link": "https://meet.google.com/cde-fghi-jkl",
        "verified": True,
        "location": "Dhaka",
    },

    # ── 4. Dr. Kamal Hossain ── RMCH, Rajshahi ───────────────────────────────
    {
        "id": "dr_kamal_004",
        "name": "Dr. Kamal Hossain",
        "name_bn": "ডা. কামাল হোসেন",
        "credentials": "MBBS, MD (Skin & VD) — DU Gold Medalist",
        "credentials_bn": "এমবিবিএস, এমডি (ত্বক ও যৌনরোগ) — স্বর্ণপদকপ্রাপ্ত",
        "hospital": "Rajshahi Medical College Hospital",
        "hospital_bn": "রাজশাহী মেডিকেল কলেজ হাসপাতাল",
        "hospital_short": "RMCH · Rajshahi",
        "department": "Department of Dermatology",
        "department_bn": "চর্মরোগ বিভাগ",
        "experience_years": 20,
        "languages": ["Bengali", "English", "Hindi"],
        "specializations": [
            "Tropical & Infectious Dermatology", "Scabies & Fungal Infections",
            "Vitiligo Management", "Neglected Tropical Skin Diseases",
        ],
        "available_days": {"Tuesday": True, "Thursday": True, "Saturday": True},
        "morning_slots": ["09:30 AM", "10:00 AM", "10:30 AM", "11:00 AM"],
        "evening_slots": ["05:30 PM", "06:00 PM", "06:30 PM", "07:00 PM"],
        "consultation_duration_min": 20,
        "fee_bdt": 600,
        "rating": 4.9,
        "total_consultations": 3280,
        "avatar_emoji": "👨‍⚕️",
        "meet_link": "https://meet.google.com/def-ghij-klm",
        "verified": True,
        "location": "Rajshahi",
    },

    # ── 5. Dr. Anika Rahman ── SOMCH, Sylhet ─────────────────────────────────
    {
        "id": "dr_anika_005",
        "name": "Dr. Anika Rahman",
        "name_bn": "ডা. আনিকা রহমান",
        "credentials": "MBBS, DDV, CCD (Cosmetic Dermatology)",
        "credentials_bn": "এমবিবিএস, ডিডিভি, সিসিডি (সৌন্দর্য চর্মরোগ)",
        "hospital": "Sylhet MAG Osmani Medical College Hospital",
        "hospital_bn": "সিলেট এমএজি ওসমানী মেডিকেল কলেজ হাসপাতাল",
        "hospital_short": "SOMCH · Sylhet",
        "department": "Department of Skin & VD",
        "department_bn": "চর্ম ও যৌনরোগ বিভাগ",
        "experience_years": 7,
        "languages": ["Bengali", "English", "Sylheti"],
        "specializations": [
            "Acne & Rosacea", "Hyperpigmentation & Melasma",
            "Eczema & Seborrhoeic Dermatitis", "Dermoscopy",
        ],
        "available_days": {"Monday": True, "Thursday": True, "Sunday": True},
        "morning_slots": ["10:00 AM", "10:30 AM", "11:00 AM", "11:30 AM"],
        "evening_slots": ["06:00 PM", "06:30 PM", "07:00 PM", "07:30 PM"],
        "consultation_duration_min": 20,
        "fee_bdt": 450,
        "rating": 4.6,
        "total_consultations": 540,
        "avatar_emoji": "👩‍⚕️",
        "meet_link": "https://meet.google.com/efg-hijk-lmn",
        "verified": True,
        "location": "Sylhet",
    },

    # ── 6. Dr. Tanvir Chowdhury ── MMCH, Mymensingh ──────────────────────────
    {
        "id": "dr_tanvir_006",
        "name": "Dr. Tanvir Chowdhury",
        "name_bn": "ডা. তানভির চৌধুরী",
        "credentials": "MBBS, MS (Dermatology), MRCP (UK)",
        "credentials_bn": "এমবিবিএস, এমএস (চর্মরোগ), এমআরসিপি (যুক্তরাজ্য)",
        "hospital": "Mymensingh Medical College Hospital",
        "hospital_bn": "ময়মনসিংহ মেডিকেল কলেজ হাসপাতাল",
        "hospital_short": "MMCH · Mymensingh",
        "department": "Department of Dermatology",
        "department_bn": "চর্মরোগ বিভাগ",
        "experience_years": 11,
        "languages": ["Bengali", "English"],
        "specializations": [
            "Rural & Community Dermatology", "Skin Infections & Parasitology",
            "Teledermatology", "Chronic Wound & Ulcer Care",
        ],
        "available_days": {"Wednesday": True, "Friday": True, "Saturday": True},
        "morning_slots": ["09:00 AM", "09:30 AM", "10:00 AM", "10:30 AM"],
        "evening_slots": ["05:00 PM", "05:30 PM", "06:00 PM", "06:30 PM"],
        "consultation_duration_min": 20,
        "fee_bdt": 400,
        "rating": 4.7,
        "total_consultations": 1560,
        "avatar_emoji": "👨‍⚕️",
        "meet_link": "https://meet.google.com/fgh-ijkl-mno",
        "verified": True,
        "location": "Mymensingh",
    },
]

# Backward-compat alias — existing tests import DEMO_DOCTOR directly
DEMO_DOCTOR = DEMO_DOCTORS[0]

# Fast lookup
_DOCTOR_BY_ID: dict = {d["id"]: d for d in DEMO_DOCTORS}


def get_doctor(doctor_id: str) -> dict:
    """Return doctor dict by ID, falling back to first doctor."""
    return _DOCTOR_BY_ID.get(doctor_id, DEMO_DOCTORS[0])


# ══════════════════════════════════════════════════════════════════════════════
# BENGALI HELPERS
# ══════════════════════════════════════════════════════════════════════════════

_BN_NUM = {
    "0": "০", "1": "১", "2": "২", "3": "৩", "4": "৪",
    "5": "৫", "6": "৬", "7": "৭", "8": "৮", "9": "৯",
}

_BN_DAYS = {
    "Sunday":    "রবিবার",   "Monday":    "সোমবার",
    "Tuesday":   "মঙ্গলবার", "Wednesday": "বুধবার",
    "Thursday":  "বৃহস্পতিবার", "Friday": "শুক্রবার",
    "Saturday":  "শনিবার",
}

_BN_DAY_SHORT = {
    "Sunday": "রবি", "Monday": "সোম", "Tuesday": "মঙ্গল",
    "Wednesday": "বুধ", "Thursday": "বৃহ", "Friday": "শুক্র",
    "Saturday": "শনি",
}

_BN_MONTHS = [
    "জানুয়ারি", "ফেব্রুয়ারি", "মার্চ", "এপ্রিল", "মে", "জুন",
    "জুলাই", "আগস্ট", "সেপ্টেম্বর", "অক্টোবর", "নভেম্বর", "ডিসেম্বর",
]


def _to_bn_num(s: str) -> str:
    return "".join(_BN_NUM.get(c, c) for c in s)


def _time_to_bn(time_en: str) -> str:
    """
    '06:30 PM' → 'সন্ধ্যা ৬:৩০'   '10:00 AM' → 'সকাল ১০:০০'
    AM → সকাল | PM hour <5 → বিকেল | PM hour ≥5 → সন্ধ্যা  (12-hr clock)
    """
    try:
        parts = time_en.strip().split()
        h_str, m_str = parts[0].split(":")
        meridiem = parts[1].upper()
        hour = int(h_str)
        if meridiem == "AM":
            prefix = "সকাল"
        elif hour < 5:
            prefix = "বিকেল"
        else:
            prefix = "সন্ধ্যা"
        return f"{prefix} {_to_bn_num(str(hour))}:{_to_bn_num(m_str)}"
    except Exception:
        return time_en


def _format_consult_bn(n: int) -> str:
    """1240 → '১,২৪০+'   890 → '৮৯০+'"""
    s = str(n)
    if len(s) <= 3:
        return _to_bn_num(s) + "+"
    return _to_bn_num(s[:-3]) + "," + _to_bn_num(s[-3:]) + "+"


# ══════════════════════════════════════════════════════════════════════════════
# SLOT GENERATION
# ══════════════════════════════════════════════════════════════════════════════

def get_available_slots(days_ahead: int = 7, doctor: dict = None) -> list:
    """
    Return available appointment days for the next `days_ahead` days for the
    given doctor (defaults to DEMO_DOCTOR / first in roster).
    Each entry: {date, date_display, date_display_bn, day_name, day_name_bn, slots}
    """
    if doctor is None:
        doctor = DEMO_DOCTORS[0]
    today = date.today()
    result = []
    for i in range(1, days_ahead + 1):
        d = today + timedelta(days=i)
        day_name = d.strftime("%A")
        if not doctor["available_days"].get(day_name):
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
            for t in doctor["morning_slots"] + doctor["evening_slots"]
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


# ══════════════════════════════════════════════════════════════════════════════
# SECTION RENDERERS (private)
# ══════════════════════════════════════════════════════════════════════════════

def _render_tier_context_banner(tier) -> None:
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


def _render_emergency_block() -> None:
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


def _render_doctor_selection_grid(selected_id: str) -> None:
    """Doctor roster — 3-per-row selection cards."""
    st.markdown(
        '<div class="card-section-header" style="margin-bottom:0.5rem;">'
        '<span style="font-size:1.1rem;">🩺</span>'
        '<div>'
        '<div class="card-section-title">ডাক্তার বেছে নিন · Choose a Dermatologist</div>'
        '<div class="card-section-sub">'
        '৬ জন বিশেষজ্ঞ · Chittagong · Dhaka · Rajshahi · Sylhet · Mymensingh</div>'
        '</div></div>',
        unsafe_allow_html=True,
    )

    for row_start in range(0, len(DEMO_DOCTORS), 3):
        row_docs = DEMO_DOCTORS[row_start:row_start + 3]
        cols = st.columns(3)
        for col, doc in zip(cols, row_docs):
            with col:
                is_sel = selected_id == doc["id"]
                border = "#0D9E75" if is_sel else "#E2E8F0"
                bg     = "#F0FFF8" if is_sel else "#FFFFFF"
                shadow = "0 0 0 2px #0D9E75" if is_sel else "0 1px 3px rgba(0,0,0,0.07)"

                filled = int(doc["rating"])
                stars = "★" * filled + "☆" * (5 - filled)

                avail_html = "".join(
                    f'<span style="background:#E6FFFA;color:#0D9E75;padding:0.1rem 0.35rem;'
                    f'border-radius:4px;font-size:0.63rem;font-weight:700;margin:0.1rem 0.1rem 0 0;">'
                    f'{_BN_DAY_SHORT[d]}</span>'
                    for d, v in doc["available_days"].items() if v
                )
                consult_bn  = _format_consult_bn(doc["total_consultations"])
                verified_tag = (
                    '<span style="background:#D4EDDA;color:#155724;padding:0.1rem 0.4rem;'
                    'border-radius:4px;font-size:0.6rem;font-weight:700;">✅ DGHS</span>'
                    if doc.get("verified") else ""
                )
                lang_str = " + ".join(doc["languages"][:2])
                sel_indicator = (
                    '<div style="position:absolute;top:0.5rem;right:0.5rem;background:#0D9E75;'
                    'color:white;border-radius:99px;width:1.25rem;height:1.25rem;'
                    'display:flex;align-items:center;justify-content:center;'
                    'font-size:0.7rem;font-weight:700;">✓</div>'
                    if is_sel else ""
                )

                st.markdown(
                    f'<div style="position:relative;background:{bg};border:2px solid {border};'
                    f'border-radius:12px;padding:0.85rem 0.85rem 0.65rem;'
                    f'box-shadow:{shadow};min-height:210px;">'
                    f'{sel_indicator}'
                    # Avatar + rating row
                    f'<div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.45rem;">'
                    f'<span style="font-size:2rem;">{doc["avatar_emoji"]}</span>'
                    f'<div>'
                    f'<div style="color:#F4C842;font-size:0.85rem;line-height:1;">{stars}</div>'
                    f'<div style="font-size:0.63rem;color:#718096;margin-top:0.1rem;">'
                    f'{doc["rating"]}/5 &nbsp;{verified_tag}</div>'
                    f'</div>'
                    f'</div>'
                    # Name
                    f'<div style="font-size:0.88rem;font-weight:800;color:#1A202C;line-height:1.2;">'
                    f'{doc["name_bn"]}</div>'
                    f'<div style="font-size:0.78rem;font-weight:600;color:#1A6FA8;">'
                    f'{doc["name"]}</div>'
                    f'<div style="font-size:0.65rem;color:#4A5568;margin-top:0.15rem;'
                    f'white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">'
                    f'{doc["credentials"]}</div>'
                    # Hospital + location
                    f'<div style="font-size:0.7rem;color:#2D3748;margin-top:0.25rem;">'
                    f'🏥 {doc["hospital_short"]}</div>'
                    # Stats row
                    f'<div style="font-size:0.65rem;color:#718096;margin-top:0.15rem;">'
                    f'⏱️ {doc["experience_years"]} yrs &nbsp;·&nbsp; 💬 {lang_str} &nbsp;·&nbsp; '
                    f'{consult_bn} পরামর্শ</div>'
                    # Available days
                    f'<div style="margin-top:0.3rem;display:flex;flex-wrap:wrap;">{avail_html}</div>'
                    # Fee
                    f'<div style="font-size:0.82rem;font-weight:700;color:#0D9E75;margin-top:0.3rem;">'
                    f'৳{doc["fee_bdt"]} &nbsp;·&nbsp; {doc["consultation_duration_min"]} min</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                btn_label = "✓ নির্বাচিত" if is_sel else "বেছে নিন"
                if st.button(
                    btn_label,
                    key=f"sel_doc_{doc['id']}",
                    use_container_width=True,
                    type="primary" if is_sel else "secondary",
                ):
                    if not is_sel:
                        # Reset date/slot when switching doctors
                        st.session_state.selected_date_idx = None
                        st.session_state.selected_slot     = None
                    st.session_state.selected_doctor_id = doc["id"]
                    st.rerun()

        st.markdown('<div style="margin-bottom:0.5rem;"></div>', unsafe_allow_html=True)


def _render_doctor_profile(doc: dict) -> None:
    """Selected doctor — expanded profile card."""
    filled = int(doc["rating"])
    stars = "★" * filled + "☆" * (5 - filled)
    spec_tags = "".join(
        f'<span style="background:#E6FFFA;color:#0D9E75;padding:0.15rem 0.5rem;'
        f'border-radius:99px;font-size:0.72rem;font-weight:600;margin:0.15rem 0.15rem 0 0;">'
        f'{s}</span>'
        for s in doc["specializations"]
    )
    verified_html = (
        '<span style="background:#D4EDDA;color:#155724;padding:0.15rem 0.55rem;'
        'border-radius:99px;font-size:0.72rem;font-weight:700;display:inline-block;'
        'margin-top:0.3rem;">✅ DGHS Verified</span>'
        if doc.get("verified") else ""
    )
    consult_bn = _format_consult_bn(doc["total_consultations"])
    lang_str   = " + ".join(doc["languages"])
    avail_days = ", ".join(
        _BN_DAYS[d] for d, v in doc["available_days"].items() if v
    )

    st.markdown(
        f'<div style="background:#f0f4f8;border-radius:12px;padding:1.25rem;'
        f'box-shadow:0 2px 6px rgba(0,0,0,0.07);margin-bottom:1rem;">'
        f'<div style="display:flex;gap:1.25rem;align-items:flex-start;">'
        f'<div style="text-align:center;min-width:82px;">'
        f'<div style="font-size:3.4rem;">{doc["avatar_emoji"]}</div>'
        f'<div style="color:#F4C842;font-size:1rem;letter-spacing:0.05em;">{stars}</div>'
        f'<div style="font-size:0.7rem;color:#718096;">{doc["rating"]}/5</div>'
        f'{verified_html}'
        f'</div>'
        f'<div style="flex:1;">'
        f'<div style="font-size:1.15rem;font-weight:800;color:#1A202C;">{doc["name_bn"]}</div>'
        f'<div style="font-size:0.95rem;font-weight:600;color:#1A6FA8;">{doc["name"]}</div>'
        f'<div style="font-size:0.8rem;color:#4A5568;margin-top:0.15rem;">{doc["credentials_bn"]}</div>'
        f'<div style="font-size:0.78rem;color:#718096;">{doc["credentials"]}</div>'
        f'<div style="font-size:0.82rem;color:#2D3748;margin-top:0.35rem;">'
        f'🏥 {doc["hospital_bn"]}</div>'
        f'<div style="font-size:0.75rem;color:#718096;">{doc["hospital"]}</div>'
        f'<div style="margin-top:0.4rem;display:flex;gap:0.75rem;flex-wrap:wrap;font-size:0.78rem;color:#4A5568;">'
        f'<span>⏱️ {doc["experience_years"]} yrs exp.</span>'
        f'<span>💬 {lang_str}</span>'
        f'<span style="color:#0D9E75;font-weight:600;">{consult_bn} পরামর্শ সম্পন্ন</span>'
        f'</div>'
        f'<div style="font-size:0.75rem;color:#4A5568;margin-top:0.2rem;">📅 {avail_days}</div>'
        f'<div style="margin-top:0.5rem;display:flex;flex-wrap:wrap;">{spec_tags}</div>'
        f'</div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )


def _render_calendar_strip(available_slots: list, doc: dict) -> None:
    """7-day horizontal calendar, highlighting the selected doctor's available days."""
    today    = date.today()
    slot_map = {s["date"]: (i, s) for i, s in enumerate(available_slots)}
    avail_days_bn = " / ".join(
        _BN_DAY_SHORT[d] for d, v in doc["available_days"].items() if v
    )

    st.markdown(
        f'<div class="card-section-header" style="margin-top:0.5rem;">'
        f'<span style="font-size:1.0rem;">📅</span>'
        f'<div>'
        f'<div class="card-section-title">তারিখ বেছে নিন · Select Date</div>'
        f'<div class="card-section-sub">উপলব্ধ দিন: {avail_days_bn}</div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    cols = st.columns(7)
    for offset in range(7):
        d = today + timedelta(days=offset + 1)
        day_name = d.strftime("%A")
        with cols[offset]:
            if d in slot_map:
                slot_idx, slot_data = slot_map[d]
                is_sel = st.session_state.get("selected_date_idx") == slot_idx
                border = "#0D9E75" if is_sel else "#CBD5E1"
                bg     = "#E6FFFA" if is_sel else "#FFFFFF"
                tick   = "✓ " if is_sel else ""
                st.markdown(
                    f'<div style="background:{bg};border:2px solid {border};'
                    f'border-radius:10px;padding:0.45rem 0.2rem;text-align:center;'
                    f'margin-bottom:0.3rem;">'
                    f'<div style="font-size:0.62rem;font-weight:700;color:#0D9E75;">'
                    f'{slot_data["day_name_bn"]}</div>'
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
                    st.session_state.selected_slot     = None
                    st.rerun()
            else:
                st.markdown(
                    f'<div style="background:#F1F5F9;border:1px solid #E2E8F0;'
                    f'border-radius:10px;padding:0.45rem 0.2rem;text-align:center;'
                    f'margin-bottom:0.3rem;opacity:0.5;">'
                    f'<div style="font-size:0.62rem;font-weight:600;color:#A0AEC0;">'
                    f'{_BN_DAYS.get(day_name, day_name)}</div>'
                    f'<div style="font-size:1.25rem;font-weight:800;color:#CBD5E1;">'
                    f'{_to_bn_num(str(d.day))}</div>'
                    f'<div style="font-size:0.62rem;color:#CBD5E1;">অনুপলব্ধ</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )


def _render_time_slots(day_data: dict) -> None:
    """Morning + evening slot grid (2 × 4)."""
    slots   = day_data["slots"]
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

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            '<div style="font-size:0.82rem;font-weight:700;color:#1A6FA8;'
            'margin-bottom:0.4rem;">☀️ সকাল · Morning</div>',
            unsafe_allow_html=True,
        )
        m1, m2 = st.columns(2)
        for i, slot in enumerate(morning):
            with (m1 if i % 2 == 0 else m2):
                is_sel = st.session_state.get("selected_slot") == slot["time_en"]
                if st.button(slot["time_bn"], key=f"slot_{slot['time_en']}",
                             type="primary" if is_sel else "secondary",
                             use_container_width=True):
                    st.session_state.selected_slot = slot["time_en"]
                    st.rerun()

    with c2:
        st.markdown(
            '<div style="font-size:0.82rem;font-weight:700;color:#0D9E75;'
            'margin-bottom:0.4rem;">🌆 সন্ধ্যা · Evening</div>',
            unsafe_allow_html=True,
        )
        e1, e2 = st.columns(2)
        for i, slot in enumerate(evening):
            with (e1 if i % 2 == 0 else e2):
                is_sel = st.session_state.get("selected_slot") == slot["time_en"]
                if st.button(slot["time_bn"], key=f"slot_{slot['time_en']}",
                             type="primary" if is_sel else "secondary",
                             use_container_width=True):
                    st.session_state.selected_slot = slot["time_en"]
                    st.rerun()

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
    c1, c2 = st.columns(2)
    with c1:
        st.text_input("আপনার নাম · Your Name", value=default_name,
                      key="patient_name_input", placeholder="যেমন: রহিম / Rahim")
    with c2:
        st.text_input("মোবাইল নম্বর · Mobile Number", key="patient_phone",
                      placeholder="01XXXXXXXXX", max_chars=11)


def _render_confirm_button(tier, available_slots: list, doc: dict) -> None:
    clicked = st.button(
        "📅 অ্যাপয়েন্টমেন্ট নিশ্চিত করুন | Confirm Appointment",
        type="primary", use_container_width=True,
        key="confirm_booking_btn",
    )
    if not clicked:
        return

    errors      = []
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

    day_data = available_slots[sel_date_idx]
    disease  = (st.session_state.get("prediction") or {}).get("disease", "")
    try:
        from model.disease_labels import get_bengali as _get_bn
        disease_bn = _get_bn(disease)
    except Exception:
        disease_bn = ""

    booking_id = f"SKN-{day_data['date'].strftime('%d%m')}-{random.randint(1000, 9999)}"
    st.session_state.booking_details = {
        "doctor_name":         doc["name"],
        "doctor_name_bn":      doc["name_bn"],
        "doctor_credentials":  doc["credentials"],
        "hospital":            doc["hospital"],
        "hospital_bn":         doc["hospital_bn"],
        "appointment_date":    day_data["date_display"],
        "appointment_date_bn": day_data["date_display_bn"],
        "appointment_time":    sel_slot,
        "appointment_time_bn": _time_to_bn(sel_slot),
        "consultation_fee":    doc["fee_bdt"],
        "meet_link":           doc["meet_link"],
        "patient_name":        name,
        "disease_diagnosed":   disease,
        "disease_diagnosed_bn": disease_bn,
        "tier":                tier or 0,
        "booking_id":          booking_id,
    }
    st.session_state.booking_confirmed = True
    st.rerun()


def _render_confirmed_booking_card() -> None:
    bd = st.session_state.booking_details

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

    disease_line = (
        f'<div><div style="font-size:0.72rem;color:#718096;">রোগ · Condition</div>'
        f'<div style="font-weight:600;">{bd["disease_diagnosed"]}</div></div>'
        if bd.get("disease_diagnosed") else ""
    )

    st.markdown(
        f'<div style="background:#FFFFFF;border-left:4px solid #00C896;border-radius:10px;'
        f'padding:1.25rem;box-shadow:0 2px 8px rgba(0,0,0,0.08);margin-bottom:1rem;">'
        f'<div style="font-family:monospace;font-size:0.75rem;color:#718096;'
        f'margin-bottom:0.75rem;font-weight:600;">বুকিং আইডি: {bd["booking_id"]}</div>'
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

    st.link_button(
        "🎥 ভিডিও কলে যোগ দিন | Join Video Call",
        bd["meet_link"], type="primary", use_container_width=True,
    )
    st.markdown(
        '<div style="font-size:0.78rem;color:#718096;text-align:center;margin:0.5rem 0 1rem 0;">'
        'ডাক্তার অ্যাপয়েন্টমেন্টের ৫ মিনিট আগে একই লিংকে যোগ দেবেন।<br>'
        '<em>Doctor will join at the same link 5 minutes before your appointment.</em>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="background:#EFF6FF;border:1px solid #93C5FD;border-radius:8px;'
        'padding:0.6rem 0.9rem;font-size:0.78rem;color:#1E40AF;margin-bottom:0.75rem;">'
        '📄 অ্যাপয়েন্টমেন্ট বিবরণ রেফারেল পত্রে অন্তর্ভুক্ত হবে। '
        'Tab 3 থেকে PDF ডাউনলোড করুন।<br>'
        '<em>Appointment details are embedded in your referral PDF (Tab 3).</em>'
        '</div>',
        unsafe_allow_html=True,
    )

    if st.button("❌ বুকিং বাতিল | Cancel Booking",
                 key="cancel_booking_btn", type="secondary"):
        st.session_state.booking_confirmed   = False
        st.session_state.booking_details     = None
        st.session_state.selected_date_idx   = None
        st.session_state.selected_slot       = None
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PUBLIC API
# ══════════════════════════════════════════════════════════════════════════════

def render_doctor_booking_tab() -> None:
    """
    Render the full doctor booking tab.
    Reads all state from st.session_state. No parameters needed.
    """
    for key, default in [
        ("booking_confirmed",   False),
        ("booking_details",     None),
        ("selected_date_idx",   None),
        ("selected_slot",       None),
        ("patient_name_input",  ""),
        ("patient_phone",       ""),
        ("selected_doctor_id",  DEMO_DOCTORS[0]["id"]),
    ]:
        st.session_state.setdefault(key, default)

    tier_result     = st.session_state.get("tier_result")
    tier            = tier_result.get("tier") if tier_result else None
    patient_history = st.session_state.get("history") or {}
    selected_doc    = get_doctor(st.session_state.get("selected_doctor_id",
                                                       DEMO_DOCTORS[0]["id"]))

    # ── Tab header ─────────────────────────────────────────────────────────
    fee_range = f"৳{min(d['fee_bdt'] for d in DEMO_DOCTORS)}–{max(d['fee_bdt'] for d in DEMO_DOCTORS)}"
    st.markdown(
        f'<div class="card-section-header">'
        f'<span style="font-size:1.1rem;">📅</span>'
        f'<div>'
        f'<div class="card-section-title">ডাক্তার বুকিং · Doctor Booking</div>'
        f'<div class="card-section-sub">'
        f'সঠিক রোগী → সঠিক ডাক্তার → সঠিক সময় · '
        f'৬ বিশেষজ্ঞ · Video consultation · {fee_range}</div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    _render_tier_context_banner(tier)

    if tier == 3:
        _render_emergency_block()
        return

    # ── Doctor selection grid ──────────────────────────────────────────────
    _render_doctor_selection_grid(selected_doc["id"])

    st.markdown("---")

    # ── Selected doctor expanded profile ──────────────────────────────────
    _render_doctor_profile(selected_doc)

    if st.session_state.booking_confirmed and st.session_state.booking_details:
        _render_confirmed_booking_card()
        return

    # ── Calendar strip ─────────────────────────────────────────────────────
    available_slots = get_available_slots(7, doctor=selected_doc)
    if not available_slots:
        st.warning("কোনো উপলব্ধ স্লট নেই। · No available slots in the next 7 days.")
        return

    _render_calendar_strip(available_slots, selected_doc)

    # ── Time slots ─────────────────────────────────────────────────────────
    sel_idx = st.session_state.get("selected_date_idx")
    if sel_idx is not None and sel_idx < len(available_slots):
        _render_time_slots(available_slots[sel_idx])

    # ── Patient info ───────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown(
        '<div class="card-section-header">'
        '<span style="font-size:1.0rem;">👤</span>'
        '<div>'
        '<div class="card-section-title">রোগীর তথ্য · Patient Info</div>'
        '<div class="card-section-sub">'
        'শুধুমাত্র অ্যাপয়েন্টমেন্টের জন্য · For appointment only</div>'
        '</div></div>',
        unsafe_allow_html=True,
    )
    _render_patient_info_fields(patient_history)

    st.markdown('<div style="margin-top:0.75rem;"></div>', unsafe_allow_html=True)
    _render_confirm_button(tier, available_slots, selected_doc)

    st.markdown(
        '<div class="sk-disclaimer" style="margin-top:0.75rem;">'
        'ডেমো উদ্দেশ্যে। এটি একটি বাস্তব অ্যাপয়েন্টমেন্ট সিস্টেম নয়। '
        'For demonstration purposes only. Not a real appointment system.'
        '</div>',
        unsafe_allow_html=True,
    )
