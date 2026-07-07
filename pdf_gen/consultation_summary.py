"""
pdf_gen/consultation_summary.py — Post-Consultation AI Care Summary PDF

fpdf2 + uharfbuzz (same stack as referral.py — Bengali renders correctly in
Adobe Acrobat because fpdf2 pre-shapes text via HarfBuzz before embedding).

Gemini 2.5 Flash-Lite extracts structured data from the consultation transcript;
fpdf2 renders a 6-section bilingual Bengali+English PDF the patient takes home.
"""
import json
import logging
import os
import unicodedata
from datetime import datetime

from fpdf import FPDF
from fpdf.enums import Align, XPos, YPos

logger = logging.getLogger(__name__)

# --- Font (identical paths to referral.py — shares the cached .ttf) ---
_FONT_DIR  = os.path.join(os.path.dirname(__file__), "fonts")
_FONT_PATH = os.path.join(_FONT_DIR, "NotoSansBengali-Regular.ttf")
_FONT_URL  = (
    "https://fonts.gstatic.com/s/notosansbengali/v33/"
    "Cn-SJsCGWQxOjaGwMQ6fIiMywrNJIky6nvd8BjzVMvJx2mcSPVFpVEqE-6KmsolLudA.ttf"
)

# --- Palette ---
_TEAL      = (46,  134, 171)   # #2E86AB — header logo
_BLUE      = (26,   82, 118)   # section headings
_LT_BLUE   = (235, 245, 251)   # #EBF5FB — diagnosis box fill
_BD_BLUE   = (174, 214, 241)   # box border blue
_GREEN_BG  = (234, 250, 241)   # #EAFAF1 — dos column
_RED_BG    = (253, 237, 236)   # #FDEDEC — donts column
_GREEN     = (30,  132,  73)
_RED       = (146,  43,  33)
_GREY      = (150, 150, 150)
_BLACK     = (0,     0,   0)

# --- Gemini prompts ---
_SYS_PROMPT = (
    "You are a medical documentation assistant for SkinAI Bangladesh, a rural "
    "dermatology triage system. You are given a transcript of a completed "
    "doctor-patient consultation. Your job is to extract ONLY what the doctor "
    "explicitly said or instructed.\n\n"
    "STRICT RULES:\n"
    "* Extract ONLY information explicitly stated in the transcript.\n"
    "* If a field has no information in the transcript, set it to null.\n"
    "* NEVER invent, infer, or hallucinate any medical instruction.\n"
    "* NEVER add medicine names not mentioned by the doctor.\n"
    "* Output ONLY valid JSON. No preamble. No markdown. No explanation."
)

# --- Default warning signs (shown when transcript has none) ---
_DEFAULT_WARNINGS_BN = [
    "জ্বর ১০২°F এর উপরে",
    "দ্রুত ছড়িয়ে পড়া লালভাব",
    "শ্বাস নিতে কষ্ট",
    "মুখ বা গলা ফুলে যাওয়া",
]
_DEFAULT_WARNINGS_EN = [
    "Fever above 102°F",
    "Rapidly spreading redness",
    "Difficulty breathing",
    "Swelling of face or throat",
]

# --- Singleton Gemini client ---
_gemini_client = None


def _get_gemini_client():
    global _gemini_client
    if _gemini_client is None:
        from google import genai
        _gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY", ""))
    return _gemini_client


def _strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        parts = text.split("```")
        text = parts[1] if len(parts) > 1 else text
        if text.startswith("json"):
            text = text[4:]
    return text.strip()


# --- Font bootstrap ---

def _ensure_font() -> bool:
    if os.path.exists(_FONT_PATH):
        return True
    try:
        import urllib.request
        os.makedirs(_FONT_DIR, exist_ok=True)
        urllib.request.urlretrieve(_FONT_URL, _FONT_PATH)
        return True
    except Exception as exc:
        logger.warning("Bengali font download failed: %s — falling back to Helvetica", exc)
        return False


def _norm(text) -> str:
    if not isinstance(text, str):
        text = str(text) if text is not None else ""
    return unicodedata.normalize("NFC", text)


# --- PDF base class (mirrors referral.py _PDF exactly) ---

class _PDF(FPDF):
    _has_bn: bool = False

    def bootstrap(self) -> "_PDF":
        self.set_margins(15, 15, 15)
        self.set_auto_page_break(True, margin=15)
        if _ensure_font():
            try:
                self.add_font("Bengali", fname=_FONT_PATH)
                self._has_bn = True
            except Exception as exc:
                logger.warning("Bengali font registration failed: %s", exc)
        return self

    def lat(self, size: int = 10, bold: bool = False):
        if self._has_bn:
            self.set_font("Bengali", size=size)
        else:
            self.set_font("Helvetica", "B" if bold else "", size)
        # Disable shaping for Latin — no conjuncts needed
        try:
            self.set_text_shaping(False)
        except Exception:
            pass

    def bn(self, size: int = 10):
        if self._has_bn:
            self.set_font("Bengali", size=size)
        else:
            self.set_font("Helvetica", size=size)
        # Enable HarfBuzz shaping for Bengali conjuncts
        try:
            self.set_text_shaping(True, script="Beng", language="BEN")
        except Exception:
            pass

    def section_heading(self, en: str, bn_text: str):
        self.ln(5)
        self.set_text_color(*_BLUE)
        self.lat(12, bold=True)
        en_str = en + "  |  "
        en_w = self.get_string_width(en_str)
        self.cell(en_w, 7, en_str, new_x=XPos.END, new_y=YPos.TOP)
        self.bn(12)
        self.cell(0, 7, _norm(bn_text), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(*_BLUE)
        self.set_line_width(0.5)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(3)
        self.set_text_color(*_BLACK)
        self.set_line_width(0.2)

    def bullet(self, text: str, x_offset: float = 3, line_h: float = 6):
        self.set_x(self.l_margin + x_offset)
        self.bn(9)
        self.multi_cell(
            self.w - self.l_margin - self.r_margin - x_offset,
            line_h,
            _norm(f"• {text}"),
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )


# --- Gemini extraction ---

def _extract_via_gemini(transcript: str, duration: int) -> dict | None:
    """
    Call Gemini 2.5 Flash-Lite to extract structured consultation data.
    Returns parsed dict on success, None on all-retry failure.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    prompt = (
        f"{_SYS_PROMPT}\n\n"
        f"Consultation transcript:\n{transcript}\n\n"
        "Extract and return ONLY this JSON structure:\n"
        "{\n"
        '  "diagnosis_confirmed": "string or null",\n'
        '  "prescribed_medicines": [\n'
        '    {\n'
        '      "name": "string",\n'
        '      "name_bn": "string",\n'
        '      "dose": "string",\n'
        '      "frequency": "string",\n'
        '      "duration": "string",\n'
        '      "instructions": "string or null"\n'
        '    }\n'
        '  ],\n'
        '  "dos": ["string"],\n'
        '  "donts": ["string"],\n'
        '  "diet_instructions": ["string"],\n'
        '  "activity_restrictions": ["string"],\n'
        '  "follow_up_date": "string or null",\n'
        '  "follow_up_condition": "string or null",\n'
        '  "warning_signs": ["string"],\n'
        '  "warning_signs_bn": ["string"],\n'
        '  "doctor_notes": "string or null",\n'
        f'  "consultation_date": "{today}",\n'
        f'  "consultation_duration": "{duration} minutes"\n'
        "}"
    )
    for attempt in range(3):
        try:
            client = _get_gemini_client()
            response = client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=prompt,
            )
            data = json.loads(_strip_fences(response.text))
            return data
        except Exception as exc:
            logger.warning("Gemini attempt %d failed: %s", attempt + 1, exc)
    return None


def _safe_list(data: dict, key: str) -> list:
    val = data.get(key) or []
    return val if isinstance(val, list) else []


def _safe_str(data: dict, key: str) -> str:
    val = data.get(key)
    return str(val).strip() if val else ""


# --- Fallback PDF (Gemini unavailable) ---

def _fallback_pdf(session_state: dict, duration: int) -> bytes:
    prediction = session_state.get("prediction") or {}
    disease    = prediction.get("disease", "Unknown")
    confidence = prediction.get("confidence", 0.0)
    tier_result = session_state.get("tier_result") or {}
    tier        = tier_result.get("tier", 1)
    now_str     = datetime.now().strftime("%Y-%m-%d %H:%M")

    pdf = _PDF(unit="mm", format="A4")
    pdf.bootstrap()
    pdf.add_page()

    pdf.set_text_color(*_TEAL)
    pdf.lat(16, bold=True)
    pdf.cell(0, 10, "SkinAI Bangladesh — Consultation Summary",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(*_GREY)
    pdf.lat(9)
    pdf.cell(0, 5, f"Generated: {now_str}  |  Duration: {duration} minutes",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(5)

    pdf.set_text_color(*_RED)
    pdf.lat(10, bold=True)
    pdf.multi_cell(0, 6,
        "Consultation summary unavailable — please contact your doctor.\n"
        "পরামর্শ সারসংক্ষেপ পাওয়া যায়নি — আপনার চিকিৎসকের সাথে যোগাযোগ করুন।"
    )
    pdf.ln(4)
    pdf.set_text_color(*_BLACK)
    pdf.lat(9)
    pdf.cell(0, 5, f"AI Diagnosis: {disease} ({confidence:.1%} confidence)",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 5, f"Triage Tier: {tier}",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(8)
    pdf.set_text_color(*_GREY)
    pdf.lat(8)
    pdf.multi_cell(0, 5,
        "This document summarizes your doctor's verbal instructions. "
        "It is NOT a prescription. Always follow your doctor's direct advice.")
    return bytes(pdf.output())


# --- Section renderers ---

def _render_header(pdf: _PDF, data: dict, session_state: dict, duration: int):
    pw = pdf.w - pdf.l_margin - pdf.r_margin
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Logo rectangle
    pdf.set_fill_color(*_TEAL)
    pdf.rect(pdf.l_margin, pdf.get_y(), 12, 12, style="F")
    logo_y = pdf.get_y()

    # Title block beside logo
    pdf.set_xy(pdf.l_margin + 14, logo_y)
    pdf.set_text_color(*_TEAL)
    pdf.lat(15, bold=True)
    pdf.cell(pw - 14, 7, "SkinAI Bangladesh — Post-Consultation Care Summary",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_xy(pdf.l_margin + 14, logo_y + 7)
    pdf.bn(11)
    pdf.cell(pw - 14, 6, _norm("পরামর্শ সারসংক্ষেপ"),
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_y(max(pdf.get_y(), logo_y + 14))
    pdf.ln(2)

    # Patient info row
    prediction  = session_state.get("prediction") or {}
    history     = session_state.get("history") or {}
    disease     = prediction.get("disease", "Unknown")
    try:
        from model.disease_labels import get_bengali
        disease_bn = get_bengali(disease)
    except Exception:
        disease_bn = ""

    patient_name = _norm(history.get("patient_name") or _safe_str(data, "patient_name") or "রোগী")
    cons_date    = _safe_str(data, "consultation_date") or now_str[:10]
    cons_dur     = _safe_str(data, "consultation_duration") or f"{duration} minutes"

    pdf.set_text_color(*_GREY)
    pdf.lat(9)
    pdf.cell(pw / 2, 5, f"Patient: {patient_name}  |  Date: {cons_date}  |  {cons_dur}",
             new_x=XPos.END, new_y=YPos.TOP)
    pdf.cell(pw / 2, 5, f"AI Diagnosis: {disease}",
             align=Align.R, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    if disease_bn:
        pdf.bn(8)
        pdf.cell(0, 5, _norm(f"রোগ নির্ণয়: {disease_bn}"),
                 align=Align.R, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_text_color(*_BLACK)
    pdf.ln(2)
    # Divider
    pdf.set_draw_color(*_BLUE)
    pdf.set_line_width(0.8)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.set_line_width(0.2)
    pdf.ln(2)


def _render_diagnosis(pdf: _PDF, data: dict, session_state: dict):
    pdf.section_heading("Section 1 — Confirmed Diagnosis", "চিকিৎসকের রোগ নির্ণয়")

    prediction = session_state.get("prediction") or {}
    disease    = prediction.get("disease", "Unknown")
    confidence = prediction.get("confidence", 0.0)
    diagnosis  = _safe_str(data, "diagnosis_confirmed") or disease

    pw = pdf.w - pdf.l_margin - pdf.r_margin
    box_y = pdf.get_y()
    box_h = 22

    # Colored background box
    pdf.set_fill_color(*_LT_BLUE)
    pdf.set_draw_color(*_BD_BLUE)
    pdf.set_line_width(0.5)
    pdf.rect(pdf.l_margin, box_y, pw, box_h, style="FD")

    pdf.set_xy(pdf.l_margin + 3, box_y + 3)
    pdf.set_text_color(*_BLUE)
    pdf.lat(11, bold=True)
    pdf.cell(pw - 6, 7, f"Diagnosis: {diagnosis}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_x(pdf.l_margin + 3)
    pdf.set_text_color(*_GREY)
    pdf.lat(9)
    pdf.cell(pw / 2 - 6, 5,
             f"AI Confidence: {confidence:.1%}  |  Model: BD-SkinNet",
             new_x=XPos.END, new_y=YPos.TOP)
    pdf.bn(9)
    pdf.set_text_color(*_BLUE)
    pdf.cell(pw / 2, 5, _norm("AI আত্মবিশ্বাস: ") + f"{confidence:.1%}",
             align=Align.R, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_y(box_y + box_h + 2)
    pdf.set_text_color(*_BLACK)
    pdf.set_line_width(0.2)


def _render_medicines(pdf: _PDF, data: dict):
    pdf.section_heading("Section 2 — Prescribed Medicines", "ওষুধের তালিকা")

    medicines = _safe_list(data, "prescribed_medicines")
    pw = pdf.w - pdf.l_margin - pdf.r_margin

    if not medicines:
        pdf.set_text_color(*_GREY)
        pdf.bn(10)
        pdf.set_x(pdf.l_margin)
        pdf.cell(pw, 7, _norm("চিকিৎসক কোনো ওষুধ নির্ধারণ করেননি"),
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_text_color(*_BLACK)
        pdf.ln(2)
    else:
        # Column widths — must sum to pw (180mm for A4 with 15mm margins)
        cols = [46, 22, 32, 22, 58]
        headers_en = ["Medicine Name", "Dose", "Frequency", "Duration", "Special Notes"]
        headers_bn = ["ওষুধের নাম",   "মাত্রা", "কতবার",  "কতদিন",  "বিশেষ নির্দেশ"]
        row_h = 8

        # Header — draw filled rect first, then text on top
        hdr_y = pdf.get_y()
        pdf.set_fill_color(*_BLUE)
        pdf.set_draw_color(*_BLUE)
        pdf.set_line_width(0.3)
        pdf.rect(pdf.l_margin, hdr_y, pw, row_h, style="F")

        pdf.set_text_color(255, 255, 255)
        x = pdf.l_margin
        for cw, h_en, h_bn in zip(cols, headers_en, headers_bn):
            pdf.set_xy(x + 1, hdr_y + 1)
            pdf.lat(8, bold=True)
            pdf.cell(cw - 2, 3.5, h_en, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_xy(x + 1, hdr_y + 4.5)
            pdf.bn(7)
            pdf.cell(cw - 2, 3, _norm(h_bn), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            x += cw
        pdf.set_y(hdr_y + row_h)
        pdf.set_text_color(*_BLACK)

        # Medicine rows — draw border rect first, then text on top
        pdf.set_draw_color(*_BD_BLUE)
        for i, med in enumerate(medicines):
            if not isinstance(med, dict):
                continue

            name        = _safe_str(med, "name") or "—"
            name_bn     = _safe_str(med, "name_bn") or ""
            dose        = _safe_str(med, "dose") or "—"
            frequency   = _safe_str(med, "frequency") or "—"
            duration    = _safe_str(med, "duration") or "—"
            instruction = _safe_str(med, "instructions") or "—"

            actual_h = row_h + (4 if name_bn else 0)
            row_y    = pdf.get_y()
            fill     = (i % 2 == 1)

            # Draw cell boxes
            if fill:
                pdf.set_fill_color(*_LT_BLUE)
            xc = pdf.l_margin
            for cw in cols:
                pdf.rect(xc, row_y, cw, actual_h, style="FD" if fill else "D")
                xc += cw

            # Draw cell text
            vals = [
                (cols[0], name[:32], name_bn),   # no char-count cut — Bengali conjuncts break mid-slice
                (cols[1], dose[:18],         ""),
                (cols[2], frequency[:24],    ""),
                (cols[3], duration[:18],     ""),
                (cols[4], instruction[:44],  ""),
            ]
            x = pdf.l_margin
            for cw, en_val, bn_val in vals:
                pdf.set_xy(x + 1, row_y + 1)
                pdf.lat(8)
                pdf.cell(cw - 2, 4, en_val, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                if bn_val:
                    pdf.set_xy(x + 1, row_y + 5)
                    pdf.bn(6)   # size 6 so full Bengali name fits within 44mm column
                    pdf.cell(cw - 2, 3.5, _norm(bn_val),
                             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                x += cw

            pdf.set_y(row_y + actual_h)

        pdf.ln(2)

    # Disclaimer — always reset x before multi_cell to avoid width-0 errors
    pdf.set_x(pdf.l_margin)
    pdf.set_text_color(*_RED)
    pdf.lat(8)
    pdf.multi_cell(pw, 5,
        "[!] Take these medicines ONLY as directed by your doctor. "
        "Do not change dose without consulting your doctor.")
    pdf.set_x(pdf.l_margin)
    pdf.bn(8)
    pdf.multi_cell(pw, 5, _norm(
        "[!] এই ওষুধগুলি শুধুমাত্র আপনার চিকিৎসকের নির্দেশে গ্রহণ করুন। "
        "নিজে নিজে ওষুধ পরিবর্তন করবেন না।"))
    pdf.set_text_color(*_BLACK)
    pdf.set_line_width(0.2)


def _render_dos_donts(pdf: _PDF, data: dict):
    pdf.section_heading("Section 3 — Care Instructions", "করণীয় ও বর্জনীয়")

    dos   = (_safe_list(data, "dos") + _safe_list(data, "diet_instructions"))
    donts = (_safe_list(data, "donts") + _safe_list(data, "activity_restrictions"))

    pw    = pdf.w - pdf.l_margin - pdf.r_margin
    col_w = (pw - 4) / 2   # 2mm gap each side
    x_l   = pdf.l_margin
    x_r   = pdf.l_margin + col_w + 4
    item_h = 7              # mm per bullet line

    # Estimate column heights (min 28mm to hold header + 1 item)
    h_l = max(28, 20 + len(dos) * item_h)
    h_r = max(28, 20 + len(donts) * item_h)
    start_y = pdf.get_y()

    # Check if columns fit on current page; if not, start new page
    if start_y + max(h_l, h_r) > pdf.h - pdf.b_margin - 10:
        pdf.add_page()
        start_y = pdf.get_y()

    # Draw background rectangles
    pdf.set_fill_color(*_GREEN_BG)
    pdf.set_draw_color(*_GREEN)
    pdf.set_line_width(0.6)
    pdf.rect(x_l, start_y, col_w, h_l, style="FD")

    pdf.set_fill_color(*_RED_BG)
    pdf.set_draw_color(*_RED)
    pdf.rect(x_r, start_y, col_w, h_r, style="FD")

    # Left column — DOS
    cy = start_y + 2
    pdf.set_xy(x_l + 2, cy)
    pdf.set_text_color(*_GREEN)
    pdf.lat(9, bold=True)
    pdf.cell(col_w - 4, 6, "(+) What to DO", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    cy += 6
    pdf.set_xy(x_l + 2, cy)
    pdf.bn(8)
    pdf.cell(col_w - 4, 5, _norm("করণীয়"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    cy += 5

    pdf.set_text_color(*_BLACK)
    items_l = dos or [_norm("আপনার চিকিৎসক কোনো বিশেষ নির্দেশনা দেননি")]
    for item in items_l:
        pdf.set_xy(x_l + 3, cy)
        pdf.bn(8)
        # Truncate to fit single line; multi-line in a side column needs set_x each time
        display = _norm(f"• {item}")
        pdf.cell(col_w - 5, 6, display, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        cy += item_h

    # Right column — DONTS
    cy = start_y + 2
    pdf.set_xy(x_r + 2, cy)
    pdf.set_text_color(*_RED)
    pdf.lat(9, bold=True)
    pdf.cell(col_w - 4, 6, "(-) What NOT to DO", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    cy += 6
    pdf.set_xy(x_r + 2, cy)
    pdf.bn(8)
    pdf.cell(col_w - 4, 5, _norm("বর্জনীয়"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    cy += 5

    pdf.set_text_color(*_BLACK)
    items_r = donts or [_norm("আপনার চিকিৎসক কোনো বিশেষ নিষেধাজ্ঞা দেননি")]
    for item in items_r:
        pdf.set_xy(x_r + 3, cy)
        pdf.bn(8)
        display = _norm(f"• {item}")
        pdf.cell(col_w - 5, 6, display, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        cy += item_h

    pdf.set_y(start_y + max(h_l, h_r) + 3)
    pdf.set_text_color(*_BLACK)
    pdf.set_line_width(0.2)


def _render_warning_signs(pdf: _PDF, data: dict):
    pdf.section_heading("Section 4 — Danger Signs", "জরুরি সতর্কতা")

    signs_bn = _safe_list(data, "warning_signs_bn") or _DEFAULT_WARNINGS_BN
    signs_en = _safe_list(data, "warning_signs") or _DEFAULT_WARNINGS_EN

    pw    = pdf.w - pdf.l_margin - pdf.r_margin
    n     = max(len(signs_bn), len(signs_en))
    box_h = max(40, 28 + n * 8)
    box_y = pdf.get_y()

    if box_y + box_h > pdf.h - pdf.b_margin - 10:
        pdf.add_page()
        box_y = pdf.get_y()

    # Red-bordered alert box
    pdf.set_fill_color(255, 245, 245)
    pdf.set_draw_color(*_RED)
    pdf.set_line_width(1.2)
    pdf.rect(pdf.l_margin, box_y, pw, box_h, style="FD")
    pdf.set_line_width(0.2)

    # Header
    cy = box_y + 3
    pdf.set_xy(pdf.l_margin + 3, cy)
    pdf.set_text_color(*_RED)
    pdf.lat(10, bold=True)
    pdf.cell(pw - 6, 6,
             "[!] DANGER SIGNS — Go to hospital IMMEDIATELY if you have:",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    cy += 6
    pdf.set_xy(pdf.l_margin + 3, cy)
    pdf.bn(9)
    pdf.cell(pw - 6, 5,
             _norm("[!] এই লক্ষণ দেখলে এখনই হাসপাতালে যান:"),
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    cy += 6

    # Signs (Bengali + English paired) — multi_cell so long lines wrap instead of clip
    pdf.set_text_color(*_BLACK)
    item_w = pw - 10
    for bn_sign, en_sign in zip(
        signs_bn + [""] * max(0, len(signs_en) - len(signs_bn)),
        signs_en + [""] * max(0, len(signs_bn) - len(signs_en)),
    ):
        line = ""
        if bn_sign and en_sign:
            line = f"• {_norm(bn_sign)}  /  {en_sign}"
        elif bn_sign:
            line = f"• {_norm(bn_sign)}"
        elif en_sign:
            line = f"• {en_sign}"
        if line:
            pdf.set_xy(pdf.l_margin + 5, cy)
            pdf.bn(9)
            pdf.multi_cell(item_w, 6.5, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            cy = pdf.get_y() + 1   # track actual y after potential wrap

    # Extend box to actual content if it grew beyond the estimate
    actual_bottom = max(box_y + box_h, cy + 3)
    if actual_bottom > box_y + box_h:
        pdf.set_fill_color(255, 245, 245)
        pdf.set_draw_color(*_RED)
        pdf.set_line_width(1.2)
        pdf.rect(pdf.l_margin, box_y, pw, actual_bottom - box_y, style="FD")
        pdf.set_line_width(0.2)

    pdf.set_y(actual_bottom + 3)
    pdf.set_text_color(*_BLACK)


def _render_followup(pdf: _PDF, data: dict):
    pdf.section_heading("Section 5 — Follow-Up", "পুনরায় ডাক্তার দেখানো")

    follow_date = _safe_str(data, "follow_up_date")
    follow_cond = _safe_str(data, "follow_up_condition")
    doctor_notes = _safe_str(data, "doctor_notes")

    pw = pdf.w - pdf.l_margin - pdf.r_margin
    if follow_date:
        pdf.set_x(pdf.l_margin)
        pdf.lat(10)
        pdf.cell(pw, 6, f"Follow-up date: {follow_date}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    if follow_cond:
        pdf.ln(2)
        pdf.set_x(pdf.l_margin)
        pdf.bn(10)
        # Single bilingual block — avoids repeating English after "যদি:"
        pdf.multi_cell(pw, 6, _norm(follow_cond), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    if not follow_date and not follow_cond:
        pdf.set_text_color(*_GREY)
        pdf.set_x(pdf.l_margin)
        pdf.bn(10)
        pdf.cell(pw, 6, _norm("আপনার চিকিৎসকের পরামর্শ অনুযায়ী ফলো-আপ করুন"),
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_x(pdf.l_margin)
        pdf.lat(9)
        pdf.cell(pw, 5, "Follow up as advised by your doctor.",
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_text_color(*_BLACK)

    if doctor_notes:
        pdf.ln(3)
        pdf.set_text_color(*_BLUE)
        pdf.set_x(pdf.l_margin)
        pdf.lat(9, bold=True)
        pdf.cell(pw, 5, "Doctor's Notes:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_text_color(*_BLACK)
        pdf.set_x(pdf.l_margin)
        pdf.lat(9)
        pdf.multi_cell(pw, 5, doctor_notes, new_x=XPos.LMARGIN, new_y=YPos.NEXT)


def _render_footer(pdf: _PDF):
    pdf.ln(6)
    pw = pdf.w - pdf.l_margin - pdf.r_margin
    pdf.set_draw_color(*_GREY)
    pdf.set_line_width(0.4)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.ln(3)

    pdf.set_text_color(*_GREY)
    pdf.lat(8)
    pdf.cell(0, 5,
             "Generated by SkinAI Bangladesh — AI-Powered Dermatology Triage",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_text_color(*_RED)
    pdf.lat(8)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(pw, 5,
        "[!] This document summarizes your doctor's verbal instructions. "
        "It is NOT a prescription. Always follow your doctor's direct advice.")
    pdf.set_x(pdf.l_margin)
    pdf.bn(8)
    pdf.multi_cell(pw, 5, _norm(
        "এই নথি আপনার চিকিৎসকের মৌখিক নির্দেশনার সারসংক্ষেপ। "
        "এটি কোনো প্রেসক্রিপশন নয়।"))

    pdf.set_text_color(*_GREY)
    pdf.lat(8)
    pdf.cell(0, 5, f"Page 1", align=Align.R,
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(*_BLACK)
    pdf.set_line_width(0.2)


# --- Public API ---

def generate_consultation_summary_pdf(
    consultation_transcript: str,
    session_state: dict,
    consultation_duration_minutes: int,
) -> tuple[bytes, list]:
    """
    Generate a bilingual Bengali+English post-consultation care summary PDF.

    Args:
        consultation_transcript: Full text of the doctor-patient conversation.
        session_state: Copy of st.session_state (prediction, history, tier_result).
        consultation_duration_minutes: 30 or 60.

    Returns:
        Tuple of (raw PDF bytes, list of prescribed medicine dicts).
    """
    # Step 1: Gemini extraction
    data = None
    if consultation_transcript and consultation_transcript.strip():
        data = _extract_via_gemini(consultation_transcript, consultation_duration_minutes)

    if data is None:
        logger.warning("Gemini extraction failed — returning fallback PDF")
        return _fallback_pdf(session_state, consultation_duration_minutes), []

    # Step 2: Build PDF
    pdf = _PDF(unit="mm", format="A4")
    pdf.bootstrap()
    pdf.add_page()

    _render_header(pdf, data, session_state, consultation_duration_minutes)
    _render_diagnosis(pdf, data, session_state)
    _render_medicines(pdf, data)
    _render_dos_donts(pdf, data)
    _render_warning_signs(pdf, data)
    _render_followup(pdf, data)
    _render_footer(pdf)

    return bytes(pdf.output()), _safe_list(data, "prescribed_medicines")


# --- Demo PDF (no Gemini, no session_state required) ---

def generate_demo_summary_pdf() -> tuple[bytes, list]:
    """
    Hardcoded post-consultation care summary for Rahim Uddin — Tinea Corporis.
    Mirrors the DEMO_TRANSCRIPT in ui/consultation_room.py exactly.
    No Gemini API call. Safe to call at app startup or on any deployment.
    """
    _DEMO_DATA = {
        "diagnosis_confirmed": "Tinea Corporis (দাদ)",
        "prescribed_medicines": [
            {
                "name": "Clotrimazole 1% Cream",
                "name_bn": "ক্লোট্রিমাজল ১% ক্রিম",
                "dose": "Thin layer",
                "frequency": "2x daily (AM & PM)",
                "duration": "14 days",
                "instructions": "Wash & dry area first. Do NOT stop early.",
            },
            {
                "name": "Cetirizine 10 mg Tablet",
                "name_bn": "সেটিরিজিন ১০ মিগ্রা ট্যাবলেট",
                "dose": "1 tablet",
                "frequency": "1x daily (bedtime)",
                "duration": "7 days",
                "instructions": "Reduces itching. May cause drowsiness.",
            },
        ],
        "dos": [
            "Keep the affected area clean and dry at all times",
            "Wash all clothes and bedsheets in hot water",
            "Wear loose, breathable cotton clothing",
            "Complete the full 14-day cream course without stopping",
            "Eat yogurt and drink plenty of water daily",
        ],
        "donts": [
            "Do NOT share towels, clothing, or bedsheets with family members",
            "Do NOT scratch the rash — it will spread",
            "Do NOT stop the medicine on your own before 14 days",
            "Do NOT apply any home remedy (coconut oil, turmeric, etc.)",
            "Avoid excessive sugar in diet during treatment",
        ],
        "diet_instructions": [],
        "activity_restrictions": [],
        "follow_up_date": "৬ জুন, ২০২৬  (June 6, 2026)",
        "follow_up_condition": (
            "৭ দিনে উন্নতি না হলে, দাগ ছড়িয়ে পড়লে, ফোসকা বা জ্বর হলে — "
            "সঙ্গে সঙ্গে জেলা হাসপাতালে যান।\n"
            "(Return immediately if: no improvement in 7 days, rash spreads, "
            "blisters appear, or fever develops.)"
        ),
        "warning_signs": [
            "No improvement after 7 days of treatment",
            "Rash spreading to face, hands, or other body parts",
            "Blisters or open sores appearing",
            "Fever or chills",
        ],
        "warning_signs_bn": [
            "৭ দিনেও কোনো উন্নতি না হলে",
            "দাগ মুখে, হাতে বা অন্য স্থানে ছড়িয়ে পড়লে",
            "ফোসকা বা ঘা দেখা দিলে",
            "জ্বর বা ঠাণ্ডা লাগলে",
        ],
        "doctor_notes": (
            "Dr. Nusrat Jahan — Chittagong Medical College Hospital (CMCH)\n"
            "Consultation Date: 2026-05-23 | Duration: 30 minutes\n"
            "SkinAI Bangladesh AI diagnosis confirmed by treating physician."
        ),
        "consultation_date": "2026-05-23",
        "consultation_duration": "30 minutes",
    }

    _DEMO_SESSION = {
        "prediction": {
            "disease": "Tinea",
            "confidence": 0.82,
        },
        "history": {
            "patient_name": "রহিম উদ্দিন (Rahim Uddin)",
            "patient_age": "৩৫",
        },
        "tier_result": {"tier": 1},
    }

    pdf = _PDF(unit="mm", format="A4")
    pdf.bootstrap()
    pdf.add_page()

    _render_header(pdf, _DEMO_DATA, _DEMO_SESSION, 30)
    _render_diagnosis(pdf, _DEMO_DATA, _DEMO_SESSION)
    _render_medicines(pdf, _DEMO_DATA)
    _render_dos_donts(pdf, _DEMO_DATA)
    _render_warning_signs(pdf, _DEMO_DATA)
    _render_followup(pdf, _DEMO_DATA)
    _render_footer(pdf)

    return bytes(pdf.output()), _DEMO_DATA["prescribed_medicines"]
