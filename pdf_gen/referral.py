"""
pdf_gen/referral.py — fpdf2 + uharfbuzz (replaces ReportLab)

fpdf2 pre-shapes Bengali text via HarfBuzz (GSUB/GPOS) before embedding
glyph IDs in the PDF. This means every PDF viewer — including Adobe Acrobat —
renders Bengali correctly. ReportLab skipped shaping entirely, so Acrobat
received raw codepoints and displayed broken characters (though copy-paste
still worked because the Unicode data itself was correct).

Requires: fpdf2>=2.7.6  uharfbuzz>=0.30.0
"""
import logging
import os
import unicodedata
from datetime import datetime

from fpdf import FPDF
from fpdf.enums import Align, XPos, YPos

logger = logging.getLogger(__name__)

# --- Font ---
_FONT_DIR  = os.path.join(os.path.dirname(__file__), "fonts")
_FONT_PATH = os.path.join(_FONT_DIR, "NotoSansBengali-Regular.ttf")
_FONT_URL  = (
    "https://fonts.gstatic.com/s/notosansbengali/v33/"
    "Cn-SJsCGWQxOjaGwMQ6fIiMywrNJIky6nvd8BjzVMvJx2mcSPVFpVEqE-6KmsolLudA.ttf"
)

# --- Palette ---
_BLUE       = (26,  82,  118)
_LIGHT_BLUE = (234, 244, 251)
_BORDER_BL  = (174, 214, 241)
_GREEN      = (30,  132, 73)
_ORANGE     = (214, 137, 16)
_RED        = (146, 43,  33)
_GREY       = (150, 150, 150)
_TIER_COLOR = {1: _GREEN, 2: _ORANGE, 3: _RED}


def _norm(text: str) -> str:
    """NFC-normalize so Bengali vowel signs form correct precomposed code-points."""
    return unicodedata.normalize("NFC", text) if isinstance(text, str) else ""


def _ensure_font() -> bool:
    if os.path.exists(_FONT_PATH):
        return True
    try:
        import urllib.request
        os.makedirs(_FONT_DIR, exist_ok=True)
        urllib.request.urlretrieve(_FONT_URL, _FONT_PATH)
        return True
    except Exception as e:
        logger.warning("Bengali font download failed: %s — falling back to Helvetica", e)
        return False


# --- PDF base class ---
class _PDF(FPDF):
    """FPDF subclass with Bengali font helpers and layout primitives."""

    _has_bn: bool = False   # set to True after add_font succeeds

    def bootstrap(self) -> "_PDF":
        self.set_margins(15, 15, 15)
        self.set_auto_page_break(True, margin=15)
        if _ensure_font():
            try:
                self.add_font("Bengali", fname=_FONT_PATH)
                self._has_bn = True
            except Exception as e:
                logger.warning("Bengali font registration failed: %s", e)
        return self

    # Font selectors
    # Both methods use the Bengali TTF when loaded.  NotoSansBengali carries
    # high-quality Latin glyphs AND covers the full Unicode range (no latin-1
    # limit), so em-dashes, ©, etc. never raise FPDFUnicodeEncodingException.
    # Helvetica is only the fallback when the font file is unavailable.

    def lat(self, size: int = 10, bold: bool = False):
        if self._has_bn:
            self.set_font("Bengali", size=size)
        else:
            self.set_font("Helvetica", "B" if bold else "", size)
        try:
            self.set_text_shaping(False)
        except Exception:
            pass

    def bn(self, size: int = 10):
        if self._has_bn:
            self.set_font("Bengali", size=size)
        else:
            self.set_font("Helvetica", size=size)
        try:
            self.set_text_shaping(True, script="Beng", language="BEN")
        except Exception:
            pass

    # Section heading

    def section_heading(self, en: str, bn_text: str):
        self.ln(5)
        self.set_text_color(*_BLUE)

        # Latin title — measure width, then place Bengali on same line
        self.lat(12, bold=True)
        en_str = en + "  |  "
        en_w = self.get_string_width(en_str)
        self.cell(en_w, 7, en_str, new_x=XPos.END, new_y=YPos.TOP)

        self.bn(12)
        self.cell(0, 7, _norm(bn_text), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # Underline rule
        self.set_draw_color(*_BLUE)
        self.set_line_width(0.5)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(3)
        self.set_text_color(0, 0, 0)
        self.set_line_width(0.2)

    # Patient-history KV table

    def kv_table(self, rows: list, col_l: int = 52):
        """Two-column label|value table.  rows = [(en, bn, value), ...]"""
        col_v = self.w - self.l_margin - self.r_margin - col_l
        self.set_draw_color(*_BORDER_BL)
        self.set_line_width(0.3)

        for label_en, label_bn_str, value in rows:
            val_str = _norm(str(value)) if value else "—"

            if self.will_page_break(14):
                self.add_page()

            y0 = self.get_y()
            x0 = self.l_margin

            # Pass 1 — draw value text (determines row height via wrapping)
            self.set_xy(x0 + col_l + 2, y0 + 2)
            self.bn(9)
            self.multi_cell(col_v - 4, 5, val_str,
                            new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            row_h = max(12, self.get_y() - y0 + 2)

            # Pass 2 — draw label fill + borders (on top; text already drawn)
            self.set_fill_color(*_LIGHT_BLUE)
            self.rect(x0, y0, col_l, row_h, style="FD")           # label: fill+border
            self.rect(x0 + col_l, y0, col_v, row_h, style="D")    # value: border only

            # Pass 3 — label text on top of blue fill
            self.lat(9, bold=True)
            self.set_xy(x0 + 2, y0 + 2)
            self.cell(col_l - 4, 5, label_en)
            self.bn(8)
            self.set_xy(x0 + 2, y0 + 7)
            self.cell(col_l - 4, 4, _norm(label_bn_str))

            self.set_y(y0 + row_h)

    # Urgency badge

    def urgency_badge(self, label: str, color: tuple):
        bw = self.w - self.l_margin - self.r_margin
        y  = self.get_y()
        self.set_fill_color(*color)
        self.rect(self.l_margin, y, bw, 14, style="F")
        self.set_text_color(255, 255, 255)
        self.lat(14, bold=True)
        self.set_xy(self.l_margin, y + 2)
        self.cell(bw, 10, label, align=Align.C, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2)
        self.set_text_color(0, 0, 0)

    # Inline Latin + Bengali line

    def mixed_line(self, prefix: str, bn_word: str, suffix: str, size: int = 10, bold: bool = False):
        """Render one line: [Latin prefix][Bengali word][Latin suffix]."""
        self.lat(size, bold=bold)
        pw = self.get_string_width(prefix)
        self.cell(pw, 6, prefix, new_x=XPos.END, new_y=YPos.TOP)

        if bn_word:
            self.bn(size)
            bw = self.get_string_width(_norm(bn_word))
            self.cell(bw, 6, _norm(bn_word), new_x=XPos.END, new_y=YPos.TOP)

        self.lat(size, bold=bold)
        self.cell(0, 6, suffix, new_x=XPos.LMARGIN, new_y=YPos.NEXT)


# --- Public API ---

def generate_referral_pdf(session_data: dict) -> bytes:
    """Generate 4-section AI referral letter. Returns raw PDF bytes."""
    pdf = _PDF(unit="mm", format="A4")
    pdf.bootstrap()
    pdf.add_page()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Header
    pdf.set_text_color(*_BLUE)
    pdf.lat(17, bold=True)
    pdf.cell(0, 10, "SkinAI Bangladesh — AI Referral Letter",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(*_GREY)
    pdf.lat(8)
    pdf.cell(0, 5, f"Generated: {now}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 5, "AI-powered dermatological screening & triage",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(2)

    # Section 1 — Patient History
    pdf.section_heading("Section 1 — Patient History", "রোগীর ইতিহাস")

    symptoms_val = _norm(", ".join(session_data.get("symptoms") or []) or "—")
    assoc_val    = _norm(", ".join(session_data.get("associated_symptoms") or []) or "—")
    pdf.kv_table([
        ("Name",               "নাম",
         _norm(session_data.get("patient_name") or "")),
        ("Age",                "বয়স",
         _norm(session_data.get("patient_age") or "")),
        ("Chief Complaint",    "প্রধান অভিযোগ",
         _norm(session_data.get("chief_complaint") or "")),
        ("Symptoms",           "লক্ষণসমূহ",
         symptoms_val),
        ("Affected Area",      "আক্রান্ত স্থান",
         _norm(session_data.get("affected_area") or "")),
        ("Duration",           "সময়কাল",
         _norm(session_data.get("duration") or "")),
        ("Progression",        "অগ্রগতি",
         _norm(session_data.get("progression") or "")),
        ("Previous Treatment", "পূর্ববর্তী চিকিৎসা",
         _norm(session_data.get("previous_treatment") or "")),
        ("Associated Symptoms","সহগামী উপসর্গ",
         assoc_val),
    ])

    # Section 2 — Clinical Observation
    pdf.section_heading("Section 2 — Clinical Observation",
                        "ক্লিনিক্যাল পর্যবক্ষণ")

    pdf.lat(9)
    pdf.multi_cell(0, 5,
        "Skin image analysed by BD-SkinNet (Swin+CBAM). "
        "Patient was instructed to consult the recommended facility "
        "for in-person clinical examination.",
        new_x=XPos.LMARGIN, new_y=YPos.NEXT,
    )
    pdf.set_text_color(*_GREY)
    pdf.lat(8)
    pdf.cell(0, 5, f"Assessment datetime: {now}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(0, 0, 0)

    # Section 3 — AI Diagnostic Assessment
    pdf.section_heading("Section 3 — AI Diagnostic Assessment", "AI রোগ নির্ণয়")

    disease_class   = session_data.get("disease_class", "Unknown")
    disease_bengali = _norm(session_data.get("disease_bengali", ""))
    confidence      = session_data.get("confidence", 0.0)
    top2            = session_data.get("top2") or []

    # Mixed-script line: Latin disease name + Bengali name in parens
    pdf.mixed_line(
        f"Primary Diagnosis: {disease_class} (",
        disease_bengali,
        f") — {confidence:.1%} confidence",
        size=10, bold=False,
    )

    if len(top2) > 1 and top2[1].get("confidence", 0.0) > 0.15:
        diff_cls  = top2[1].get("disease", top2[1].get("class", ""))
        diff_conf = top2[1].get("confidence", 0.0)
        pdf.lat(9)
        pdf.cell(0, 5, f"Differential Diagnosis: {diff_cls} ({diff_conf:.1%})",
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_text_color(*_GREY)
    pdf.lat(8)
    pdf.multi_cell(0, 5,
        "Model: BD-SkinNet (Swin-B + CBAM, INT8) | F1 = 92.46% | "
        "Trained on Faridpur MCH + Rangpur MCH clinical data")
    pdf.set_text_color(*_RED)
    pdf.cell(0, 5, "This is an AI-assisted screening tool, not a medical diagnosis.",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(0, 0, 0)

    # Section 4 — Triage Recommendation
    pdf.section_heading("Section 4 — Triage Recommendation",
                        "ট্রিয়াজ সুপারিশ")

    tier          = session_data.get("tier", 1)
    urgency_label = session_data.get("urgency_label", "NON-URGENT")
    action        = session_data.get("action", "")
    facility      = session_data.get("facility", "")
    bengali_text  = _norm(session_data.get("bengali_text", ""))
    hospital_name = session_data.get("hospital_name") or ""
    hospital_addr = session_data.get("hospital_address") or ""

    pdf.urgency_badge(urgency_label, _TIER_COLOR.get(tier, _GREY))
    pdf.ln(2)

    pdf.lat(10, bold=True)
    pdf.cell(0, 5, f"Action: {action}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 5, f"Facility: {facility}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    if bengali_text:
        pdf.bn(10)
        pdf.multi_cell(0, 6, bengali_text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    if tier == 3 and hospital_name:
        pdf.lat(9)
        pdf.cell(0, 5, f"Nearest Hospital: {hospital_name} — {hospital_addr}",
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Scheduled Appointment (if booked via doctor booking tab)
    booking_confirmed = session_data.get("booking_confirmed", False)
    booking_details   = session_data.get("booking_details") or {}
    if booking_confirmed and booking_details:
        pdf.ln(5)
        pdf.section_heading(
            "Scheduled Appointment",
            "নির্ধারিত অ্যাপয়েন্টমেন্ট",
        )
        appt_rows = [
            ("Doctor",    _norm("ডাক্তার"),
             f"{booking_details.get('doctor_name', '')} | "
             f"{booking_details.get('doctor_credentials', '')}"),
            ("Hospital",  _norm("হাসপাতাল"),
             booking_details.get("hospital", "")),
            ("Date",      _norm("তারিখ"),
             f"{booking_details.get('appointment_date', '')} "
             f"({_norm(booking_details.get('appointment_date_bn', ''))})"),
            ("Time",      _norm("সময়"),
             f"{booking_details.get('appointment_time', '')} "
             f"({_norm(booking_details.get('appointment_time_bn', ''))})"),
            ("Mode",      _norm("মাধ্যম"),
             _norm("Video Consultation (ভিডিও পরামর্শ)")),
            ("Booking ID",_norm("বুকিং আইডি"),
             booking_details.get("booking_id", "")),
            ("Join Link", _norm("লিংক"),
             booking_details.get("meet_link", "")),
            ("Fee",       _norm("ফি"),
             f"BDT {booking_details.get('consultation_fee', 500)} "
             f"(payable at consultation)"),
        ]
        pdf.kv_table(appt_rows)
        pdf.ln(3)
        pdf.set_text_color(*_BLUE)
        pdf.bn(9)
        pdf.multi_cell(0, 5.5, _norm(
            "অ্যাপয়েন্টমেন্টের সময় উপরের লিংকে প্রবেশ করুন। "
            "ডাক্তার একই লিংকে যোগ দেবেন।"
        ), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_text_color(0, 0, 0)

    # Footer
    pdf.ln(5)
    pdf.set_text_color(*_RED)
    pdf.lat(8)
    pdf.multi_cell(0, 5,
        "[!] Not a medical device. Always consult a licensed physician. | "
        "SkinAI Bangladesh © 2026")

    return bytes(pdf.output())


def generate_demo_consultation_pdf() -> bytes:
    """
    Generate a fully-populated demo consultation PDF (Rahim, Tier 3 Scabies case).
    Used for the always-visible demo download button — no pipeline run required.
    """
    demo_data = {
        # Patient history
        "patient_name":        "রহিম মিয়া (Rahim Mia)",
        "patient_age":         "৩৫ বছর (35 years)",
        "chief_complaint":     "সারা শরীলে তীব্র চুলকানি ও ফুসকুড়ি · Intense itching and spreading rash all over body",
        "symptoms":            ["intense itching", "spreading rash", "skin thickening", "redness"],
        "affected_area":       "বাহু, পেট, উরু · Arms, abdomen, thighs",
        "duration":            "১০ দিন (10 days)",
        "progression":         "দ্রুত ছড়িয়ে পড়ছে · Spreading rapidly",
        "previous_treatment":  "কোনো চিকিৎসা নেওয়া হয়নি · No prior treatment",
        "associated_symptoms": ["জ্বর (fever)", "ব্যথা (pain)", "রাতে বেশি চুলকানি (worse at night)"],
        # AI diagnosis
        "disease_class":   "Scabies",
        "disease_bengali": "খুজলি (স্ক্যাবিস)",
        "confidence":      0.38,
        "top2": [
            {"disease": "Scabies", "confidence": 0.38},
            {"disease": "Eczema",  "confidence": 0.22},
        ],
        # Triage
        "tier":          3,
        "urgency_label": "URGENT",
        "action":        "Seek emergency care TODAY at District Hospital",
        "facility":      "District Hospital",
        "bengali_text":  "আজই জেলা হাসপাতালে জরুরি চিকিৎসা নিন — জরুরি চিকিৎসা প্রয়োজন",
        "hospital_name":    "Rangpur Medical College Hospital",
        "hospital_address": "Rangpur Sadar, Rangpur District",
        # Doctor booking (post-consultation)
        "booking_confirmed": True,
        "booking_details": {
            "doctor_name":        "Dr. Nusrat Jahan",
            "doctor_credentials": "MBBS, DDV (Dermatology) — BCPS Fellow",
            "hospital":           "Rangpur Medical College Hospital",
            "appointment_date":   "2026-05-26",
            "appointment_date_bn":"মঙ্গলবার, ২৬ মে ২০২৬",
            "appointment_time":   "10:00 AM",
            "appointment_time_bn":"সকাল ১০:০০ টা",
            "booking_id":         "DEMO-RXS-2026-001",
            "meet_link":          "https://meet.skinai.bd/demo-consultation-001",
            "consultation_fee":   500,
        },
    }
    return generate_referral_pdf(demo_data)


def generate_chw_referral_slip(session_data: dict) -> bytes:
    """Generate simplified 1-page CHW referral slip. Returns raw PDF bytes."""
    pdf = _PDF(unit="mm", format="A4")
    pdf.bootstrap()
    pdf.add_page()
    now  = datetime.now().strftime("%Y-%m-%d %H:%M")
    tier = session_data.get("tier", 1)
    tc   = _TIER_COLOR.get(tier, _GREY)

    # Header
    pdf.set_text_color(*_BLUE)
    pdf.lat(18, bold=True)
    pdf.cell(0, 12, "SkinAI Bangladesh — CHW Referral Slip",
             align=Align.C, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.bn(10)
    pdf.cell(0, 6,
             _norm("সেবিকা রেফারেল স্লিপ · Community Health Worker Copy"),
             align=Align.C, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(*_GREY)
    pdf.lat(8)
    pdf.cell(0, 5, f"Date: {now}", align=Align.C, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)

    # Urgency badge
    tier_labels = {
        1: "NON-URGENT",
        2: "ROUTINE — REFER",
        3: "URGENT — SEND NOW!",
    }
    pdf.urgency_badge(tier_labels.get(tier, "ROUTINE"), tc)

    # Bengali urgency line
    bn_labels = {
        1: _norm("জরুরি নয়"),
        2: _norm("রেফার করুন"),
        3: _norm("এখনই পাঠান!"),
    }
    pdf.set_text_color(*tc)
    pdf.bn(14)
    pdf.cell(0, 8, bn_labels.get(tier, ""), align=Align.C,
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(4)

    # Patient info table
    name       = _norm(session_data.get("patient_name") or "—")
    age        = _norm(session_data.get("patient_age") or "—")
    disease    = session_data.get("disease_class", "—")
    disease_bn = _norm(session_data.get("disease_bengali", ""))
    facility   = session_data.get("facility", "")
    action_bn  = _norm(session_data.get("bengali_text", ""))

    try:
        from severity.engine import COST_ESTIMATE
        cost = COST_ESTIMATE.get(tier, COST_ESTIMATE.get(2, {}))
        cost_str = f"{cost.get('range', '')} — {_norm(cost.get('note_bn', ''))}"
    except Exception:
        cost_str = "—"

    pdf.kv_table([
        ("Patient",  _norm("রোগী"),     f"{name} · Age {age}"),
        ("Condition",_norm("রোগ"),            f"{disease} ({disease_bn})"),
        ("Go To",    _norm("কোথায় যাবেন"), facility),
        ("Est. Cost",_norm("আনুমানিক খরচ"), cost_str),
    ])
    pdf.ln(5)

    # Bengali instruction
    if action_bn:
        pdf.set_text_color(*tc)
        pdf.bn(13)
        pdf.multi_cell(0, 7, action_bn, align=Align.C)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(4)

    # Nearest hospital (Tier 3)
    if tier == 3:
        hosp_name = session_data.get("hospital_name", "")
        hosp_addr = session_data.get("hospital_address", "")
        if hosp_name:
            pdf.lat(10, bold=True)
            pdf.cell(0, 5, f"Nearest Hospital: {hosp_name} — {hosp_addr}",
                     new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(3)

    # Footer
    pdf.set_text_color(*_RED)
    pdf.lat(8)
    pdf.multi_cell(0, 5,
        "AI-assisted screening. Not a substitute for clinical diagnosis. | "
        "SkinAI Bangladesh © 2026")

    return bytes(pdf.output())
