import io
import os
import tempfile
from datetime import datetime

import numpy as np
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ── Font registration ─────────────────────────────────────────────────────────
_FONT_DIR = os.path.join(os.path.dirname(__file__), "fonts")
_FONT_PATH = os.path.join(_FONT_DIR, "NotoSansBengali-Regular.ttf")
_BENGALI_FONT = "NotoSansBengali"
_FONT_REGISTERED = False


_FONT_URL = (
    "https://fonts.gstatic.com/s/notosansbengali/v33/"
    "Cn-SJsCGWQxOjaGwMQ6fIiMywrNJIky6nvd8BjzVMvJx2mcSPVFpVEqE-6KmsolLudA.ttf"
)


def _register_font():
    global _FONT_REGISTERED, _BENGALI_FONT
    if _FONT_REGISTERED:
        return
    if not os.path.exists(_FONT_PATH):
        try:
            import urllib.request
            os.makedirs(_FONT_DIR, exist_ok=True)
            urllib.request.urlretrieve(_FONT_URL, _FONT_PATH)
        except Exception:
            pass
    if os.path.exists(_FONT_PATH):
        pdfmetrics.registerFont(TTFont(_BENGALI_FONT, _FONT_PATH))
    else:
        _BENGALI_FONT = "Helvetica"
    _FONT_REGISTERED = True


# ── Styles ────────────────────────────────────────────────────────────────────
def _build_styles():
    _register_font()
    base = getSampleStyleSheet()

    heading = ParagraphStyle(
        "SkinAIHeading",
        parent=base["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=16,
        textColor=colors.HexColor("#1a5276"),
        spaceAfter=4,
    )
    section = ParagraphStyle(
        "SkinAISection",
        parent=base["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        textColor=colors.HexColor("#1a5276"),
        spaceBefore=12,
        spaceAfter=4,
        borderPad=4,
    )
    body = ParagraphStyle(
        "SkinAIBody",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=10,
        spaceAfter=4,
    )
    bengali = ParagraphStyle(
        "SkinAIBengali",
        parent=base["Normal"],
        fontName=_BENGALI_FONT,
        fontSize=10,
        spaceAfter=4,
    )
    small = ParagraphStyle(
        "SkinAISmall",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=8,
        textColor=colors.grey,
        spaceAfter=2,
    )
    disclaimer = ParagraphStyle(
        "SkinAIDisclaimer",
        parent=base["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8,
        textColor=colors.HexColor("#922b21"),
        spaceAfter=2,
    )
    return heading, section, body, bengali, small, disclaimer


# ── Tier colours ──────────────────────────────────────────────────────────────
_TIER_COLOR = {
    1: colors.HexColor("#1e8449"),   # green
    2: colors.HexColor("#d68910"),   # orange
    3: colors.HexColor("#922b21"),   # red
}


# ── Helpers ───────────────────────────────────────────────────────────────────
def _section_rule(story, label, section_style):
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(label, section_style))


def _kv_table(rows, body_style, bengali_style):
    """Build a two-column label|value table."""
    data = []
    for label_en, label_bn, value in rows:
        label_cell = Paragraph(f"<b>{label_en}</b><br/>{label_bn}", bengali_style)
        val_cell = Paragraph(str(value) if value else "—", body_style)
        data.append([label_cell, val_cell])
    t = Table(data, colWidths=[5 * cm, 12 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eaf4fb")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#aed6f1")),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def _heatmap_to_image(heatmap: np.ndarray, max_width_px: int = 300) -> Image:
    """Convert numpy overlay array → reportlab Image object."""
    pil = PILImage.fromarray(heatmap.astype(np.uint8))
    aspect = pil.height / pil.width
    w_pt = max_width_px * 0.75        # px → pt (72dpi)
    h_pt = w_pt * aspect
    buf = io.BytesIO()
    pil.save(buf, format="PNG")
    buf.seek(0)
    return Image(buf, width=w_pt, height=h_pt)


# ── Main function ─────────────────────────────────────────────────────────────
def generate_referral_pdf(session_data: dict) -> bytes:
    """
    Generate a 4-section AI referral letter PDF.
    Returns raw PDF bytes. No file is written to disk.
    """
    heading_style, section_style, body_style, bengali_style, small_style, disclaimer_style = _build_styles()

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    story = []

    # ── Header ────────────────────────────────────────────────────────────────
    story.append(Paragraph("SkinAI Bangladesh — AI Referral Letter", heading_style))
    story.append(Paragraph(f"Generated: {now}", small_style))
    story.append(Paragraph(
        "AI-powered dermatological screening & triage | SciBlitz AI Challenge 2026",
        small_style,
    ))
    story.append(Spacer(1, 0.4 * cm))

    # ── Section 1 — Patient History ───────────────────────────────────────────
    _section_rule(story, "Section 1 — Patient History | রোগীর ইতিহাস", section_style)

    symptoms_val = ", ".join(session_data.get("symptoms") or []) or "—"
    rows_s1 = [
        ("Name", "নাম", session_data.get("patient_name")),
        ("Age", "বয়স", session_data.get("patient_age")),
        ("Chief Complaint", "প্রধান অভিযোগ", session_data.get("chief_complaint")),
        ("Symptoms", "লক্ষণসমূহ", symptoms_val),
        ("Affected Area", "আক্রান্ত স্থান", session_data.get("affected_area")),
        ("Duration", "সময়কাল", session_data.get("duration")),
        ("Progression", "অগ্রগতি", session_data.get("progression")),
        ("Previous Treatment", "পূর্ববর্তী চিকিৎসা", session_data.get("previous_treatment")),
    ]
    story.append(_kv_table(rows_s1, body_style, bengali_style))

    # ── Section 2 — Clinical Observation ─────────────────────────────────────
    _section_rule(story, "Section 2 — Clinical Observation | ক্লিনিক্যাল পর্যবেক্ষণ", section_style)

    heatmap = session_data.get("heatmap")
    coverage_pct = session_data.get("coverage_pct", 0.0)

    if heatmap is not None:
        story.append(_heatmap_to_image(heatmap))
        story.append(Paragraph(
            "লাল এলাকা মডেলের মনোযোগের কেন্দ্র",
            bengali_style,
        ))
    else:
        story.append(Paragraph("Image not provided", body_style))

    story.append(Paragraph(f"Lesion coverage: {coverage_pct:.1f}%", body_style))
    story.append(Paragraph(f"Assessment datetime: {now}", small_style))

    # ── Section 3 — AI Diagnostic Assessment ─────────────────────────────────
    _section_rule(story, "Section 3 — AI Diagnostic Assessment | AI রোগ নির্ণয়", section_style)

    disease_class = session_data.get("disease_class", "Unknown")
    disease_bengali = session_data.get("disease_bengali", "")
    confidence = session_data.get("confidence", 0.0)
    top2 = session_data.get("top2") or []

    story.append(Paragraph(
        f"<b>Primary Diagnosis:</b> {disease_class} ({disease_bengali}) — {confidence:.1%} confidence",
        body_style,
    ))

    if len(top2) > 1 and top2[1].get("confidence", 0.0) > 0.15:
        diff_class = top2[1].get("class", "")
        diff_conf = top2[1].get("confidence", 0.0)
        story.append(Paragraph(
            f"<b>Differential Diagnosis:</b> {diff_class} ({diff_conf:.1%})",
            body_style,
        ))

    story.append(Paragraph(
        "Model: BD-SkinNet (Swin-B + CBAM, INT8) | F1 = 92.46% | "
        "Trained on Faridpur MCH + Rangpur MCH clinical data",
        small_style,
    ))
    story.append(Paragraph(
        "This is an AI-assisted screening tool, not a medical diagnosis.",
        disclaimer_style,
    ))

    # ── Section 4 — Triage Recommendation ────────────────────────────────────
    _section_rule(story, "Section 4 — Triage Recommendation | ট্রিয়াজ সুপারিশ", section_style)

    tier = session_data.get("tier", 1)
    urgency_label = session_data.get("urgency_label", "NON-URGENT")
    action = session_data.get("action", "")
    facility = session_data.get("facility", "")
    bengali_text = session_data.get("bengali_text", "")
    hospital_name = session_data.get("hospital_name")
    hospital_address = session_data.get("hospital_address")

    tier_color = _TIER_COLOR.get(tier, colors.grey)
    badge_data = [[Paragraph(
        f"<b>{urgency_label}</b>",
        ParagraphStyle("badge", fontName="Helvetica-Bold", fontSize=13,
                       textColor=colors.white),
    )]]
    badge = Table(badge_data, colWidths=[17 * cm])
    badge.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), tier_color),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("ROUNDEDCORNERS", [4, 4, 4, 4]),
    ]))
    story.append(badge)
    story.append(Spacer(1, 0.2 * cm))

    story.append(Paragraph(f"<b>Action:</b> {action}", body_style))
    story.append(Paragraph(f"<b>Facility:</b> {facility}", body_style))
    story.append(Paragraph(bengali_text, bengali_style))

    if tier == 3 and hospital_name:
        addr = hospital_address or ""
        story.append(Paragraph(
            f"<b>Nearest Hospital:</b> {hospital_name} — {addr}",
            body_style,
        ))

    # ── Footer ────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.6 * cm))
    story.append(Paragraph(
        "⚠ Not a medical device. Always consult a licensed physician. | "
        "SkinAI Bangladesh © 2026",
        disclaimer_style,
    ))

    doc.build(story)
    return buf.getvalue()
