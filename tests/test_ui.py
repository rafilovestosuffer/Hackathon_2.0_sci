"""
Tests for ui/styles.py and ui/components.py.
All Streamlit calls are mocked — no browser or server required.
"""

from unittest.mock import MagicMock, call, patch

import numpy as np
import pytest


# ── Helpers ───────────────────────────────────────────────────────────────────

def _captured_html(mock_st_markdown) -> str:
    """Return the concatenated HTML from all st.markdown calls."""
    parts = []
    for c in mock_st_markdown.call_args_list:
        arg = c.args[0] if c.args else ""
        parts.append(str(arg))
    return "\n".join(parts)


# ── TestInjectCSS ─────────────────────────────────────────────────────────────

class TestInjectCSS:
    def test_inject_css_calls_st_markdown(self):
        with patch("ui.styles.st") as mock_st:
            from ui.styles import inject_css
            inject_css()
            mock_st.markdown.assert_called_once()

    def test_inject_css_contains_noto_sans(self):
        with patch("ui.styles.st") as mock_st:
            from ui.styles import inject_css
            inject_css()
            html = mock_st.markdown.call_args.args[0]
            assert "Noto+Sans+Bengali" in html or "Noto Sans Bengali" in html

    def test_inject_css_contains_badge_classes(self):
        with patch("ui.styles.st") as mock_st:
            from ui.styles import inject_css
            inject_css()
            html = mock_st.markdown.call_args.args[0]
            assert "badge-tier1" in html
            assert "badge-tier2" in html
            assert "badge-tier3" in html

    def test_inject_css_unsafe_allow_html_true(self):
        with patch("ui.styles.st") as mock_st:
            from ui.styles import inject_css
            inject_css()
            kwargs = mock_st.markdown.call_args.kwargs
            assert kwargs.get("unsafe_allow_html") is True

    def test_inject_css_contains_google_fonts_link(self):
        with patch("ui.styles.st") as mock_st:
            from ui.styles import inject_css
            inject_css()
            html = mock_st.markdown.call_args.args[0]
            assert "fonts.googleapis.com" in html


# ── TestRenderTriageBadge ─────────────────────────────────────────────────────

class TestRenderTriageBadge:
    def _call(self, tier_result):
        with patch("ui.components.st") as mock_st:
            from ui.components import render_triage_badge
            render_triage_badge(tier_result)
            return _captured_html(mock_st.markdown)

    def test_badge_tier1_rendered(self):
        html = self._call({"tier": 1, "urgency_label": "NON-URGENT",
                           "action": "Consult pharmacist", "bn": "ফার্মাসিস্ট"})
        assert "badge-tier1" in html

    def test_badge_tier2_rendered(self):
        html = self._call({"tier": 2, "urgency_label": "ROUTINE",
                           "action": "Visit clinic", "bn": "ক্লিনিকে যান"})
        assert "badge-tier2" in html

    def test_badge_tier3_rendered(self):
        html = self._call({"tier": 3, "urgency_label": "URGENT",
                           "action": "Emergency", "bn": "জরুরি"})
        assert "badge-tier3" in html

    def test_badge_shows_action_text(self):
        html = self._call({"tier": 2, "urgency_label": "ROUTINE",
                           "action": "Visit Upazila", "bn": "উপজেলায় যান"})
        assert "Visit Upazila" in html

    def test_badge_shows_bengali_action(self):
        html = self._call({"tier": 1, "urgency_label": "NON-URGENT",
                           "action": "Go pharmacist", "bn": "ফার্মাসিস্টে যান"})
        assert "ফার্মাসিস্টে যান" in html


# ── TestRenderPatientHistory ──────────────────────────────────────────────────

class TestRenderPatientHistory:
    def _call(self, history):
        with patch("ui.components.st") as mock_st:
            from ui.components import render_patient_history_table
            render_patient_history_table(history)
            return _captured_html(mock_st.markdown)

    def test_empty_fields_skipped(self):
        html = self._call({"chief_complaint": "", "patient_name": "none",
                           "symptoms": [], "duration": "N/A"})
        assert "<tr>" not in html

    def test_nonempty_fields_rendered(self):
        html = self._call({"chief_complaint": "Itchy rash", "patient_name": "Rahim",
                           "duration": "3 days"})
        assert "Itchy rash" in html
        assert "Rahim" in html

    def test_list_values_joined(self):
        html = self._call({"symptoms": ["itching", "redness", "swelling"]})
        assert "itching" in html
        assert "redness" in html

    def test_no_history_shows_placeholder(self):
        html = self._call({})
        assert "No history" in html or "no history" in html.lower()


# ── TestRenderDiseaseCard ─────────────────────────────────────────────────────

class TestRenderDiseaseCard:
    def _call(self, disease, confidence, top2):
        with patch("ui.components.st") as mock_st:
            from ui.components import render_disease_card
            render_disease_card(disease, confidence, top2)
            return _captured_html(mock_st.markdown)

    def test_disease_card_shows_english_name(self):
        html = self._call("Tinea", 0.82, [])
        assert "Tinea" in html

    def test_disease_card_shows_bengali_name(self):
        html = self._call("Tinea", 0.82, [])
        assert "দাদ" in html  # Bengali for Tinea

    def test_disease_card_shows_scabies_bengali(self):
        html = self._call("Scabies", 0.75, [])
        assert "খোস-পাঁচড়া" in html

    def test_differential_shown_when_above_threshold(self):
        top2 = [
            {"disease": "Tinea", "confidence": 0.82},
            {"disease": "Eczema", "confidence": 0.16},
        ]
        html = self._call("Tinea", 0.82, top2)
        assert "differential-pill" in html.lower() or "Differential" in html

    def test_differential_hidden_when_below_threshold(self):
        top2 = [
            {"disease": "Tinea", "confidence": 0.82},
            {"disease": "Eczema", "confidence": 0.10},
        ]
        html = self._call("Tinea", 0.82, top2)
        assert "differential-pill" not in html

    def test_confidence_percentage_shown(self):
        html = self._call("Vitiligo", 0.73, [])
        assert "73" in html or "73.0" in html


# ── TestRenderReferralButton ──────────────────────────────────────────────────

class TestRenderReferralButton:
    def test_download_button_enabled_with_bytes(self):
        with patch("ui.components.st") as mock_st:
            from ui.components import render_referral_download_button
            render_referral_download_button(b"%PDF-1.4 fake content")
            mock_st.download_button.assert_called_once()
            kwargs = mock_st.download_button.call_args.kwargs
            assert kwargs.get("mime") == "application/pdf"

    def test_download_button_disabled_when_none(self):
        with patch("ui.components.st") as mock_st:
            from ui.components import render_referral_download_button
            render_referral_download_button(None)
            mock_st.download_button.assert_not_called()
            mock_st.markdown.assert_called()

    def test_disabled_state_shows_instructions(self):
        with patch("ui.components.st") as mock_st:
            from ui.components import render_referral_download_button
            render_referral_download_button(None)
            html = _captured_html(mock_st.markdown)
            assert "diagnosis" in html.lower() or "referral" in html.lower()


# ── TestRenderGradcamOverlay ──────────────────────────────────────────────────

class TestRenderGradcamOverlay:
    def test_renders_without_error_with_image(self):
        with patch("ui.components.st") as mock_st:
            from ui.components import render_gradcam_overlay
            fake_img = np.zeros((224, 224, 3), dtype=np.uint8)
            render_gradcam_overlay(fake_img, 25.0)
            mock_st.image.assert_called_once()

    def test_renders_without_error_no_image(self):
        with patch("ui.components.st") as mock_st:
            from ui.components import render_gradcam_overlay
            render_gradcam_overlay(None, 0.0)
            mock_st.image.assert_not_called()

    def test_coverage_pct_shown_in_html(self):
        with patch("ui.components.st") as mock_st:
            from ui.components import render_gradcam_overlay
            render_gradcam_overlay(None, 38.5)
            html = _captured_html(mock_st.markdown)
            assert "38.5" in html


# ── TestRenderRAGAnswer ───────────────────────────────────────────────────────

class TestRenderRAGAnswer:
    def test_answer_text_in_html(self):
        with patch("ui.components.st") as mock_st:
            from ui.components import render_rag_answer
            render_rag_answer("Tinea is caused by fungi.", "en")
            html = _captured_html(mock_st.markdown)
            assert "Tinea is caused by fungi." in html

    def test_source_tags_shown(self):
        with patch("ui.components.st") as mock_st:
            from ui.components import render_rag_answer
            render_rag_answer("Test answer", "en")
            html = _captured_html(mock_st.markdown)
            assert "CDC" in html or "WHO" in html

    def test_bengali_lang_tag(self):
        with patch("ui.components.st") as mock_st:
            from ui.components import render_rag_answer
            render_rag_answer("বাংলায় উত্তর।", "bn")
            html = _captured_html(mock_st.markdown)
            assert "Bengali" in html or "বাংলা" in html


# ── TestConfidenceCaption ─────────────────────────────────────────────────────

class TestConfidenceCaption:
    def _call(self, confidence):
        with patch("ui.components.st") as mock_st:
            from ui.components import render_disease_card
            render_disease_card("Tinea", confidence, [])
            return _captured_html(mock_st.markdown)

    def test_high_confidence_shows_certain_label(self):
        html = self._call(0.85)
        assert "মডেল নিশ্চিত" in html

    def test_mid_confidence_shows_moderate_label(self):
        html = self._call(0.70)
        assert "মোটামুটি নিশ্চিত" in html

    def test_low_confidence_shows_uncertain_label(self):
        html = self._call(0.35)
        assert "অনিশ্চিত" in html

    def test_boundary_exactly_080_is_high(self):
        html = self._call(0.80)
        assert "মডেল নিশ্চিত" in html

    def test_boundary_exactly_060_is_mid(self):
        html = self._call(0.60)
        assert "মোটামুটি নিশ্চিত" in html

    def test_low_confidence_includes_doctor_advice(self):
        html = self._call(0.30)
        assert "ডাক্তার" in html


# ── TestCheckImageQuality ─────────────────────────────────────────────────────

class TestCheckImageQuality:
    def test_sharp_image_returns_not_blurry(self):
        from PIL import Image
        from ui.components import check_image_quality
        # High-contrast checkerboard → very high Laplacian variance
        img_np = np.zeros((64, 64, 3), dtype=np.uint8)
        img_np[::2, ::2] = 255
        pil_img = Image.fromarray(img_np)
        is_blurry, var = check_image_quality(pil_img)
        assert is_blurry is False
        assert var > 80.0

    def test_flat_image_returns_blurry(self):
        from PIL import Image
        from ui.components import check_image_quality
        # Uniform grey image → Laplacian variance is 0
        pil_img = Image.fromarray(np.full((64, 64, 3), 128, dtype=np.uint8))
        is_blurry, var = check_image_quality(pil_img)
        assert is_blurry is True
        assert var < 80.0

    def test_returns_tuple_of_bool_and_float(self):
        from PIL import Image
        from ui.components import check_image_quality
        pil_img = Image.fromarray(np.zeros((32, 32, 3), dtype=np.uint8))
        result = check_image_quality(pil_img)
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], bool)
        assert isinstance(result[1], float)

    def test_error_returns_safe_defaults(self):
        from ui.components import check_image_quality
        is_blurry, var = check_image_quality(None)  # None will cause an exception
        assert is_blurry is False
        assert var == -1.0
