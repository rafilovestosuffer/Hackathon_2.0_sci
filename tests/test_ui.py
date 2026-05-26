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


# ── TestRenderSidebarPipeline ─────────────────────────────────────────────────

class TestRenderSidebarPipeline:
    def _call(self, **kwargs):
        with patch("ui.components.st") as mock_st:
            from ui.components import render_sidebar_pipeline
            render_sidebar_pipeline(**kwargs)
            return _captured_html(mock_st.markdown)

    def test_renders_four_steps(self):
        html = self._call(voice_done=False, image_done=False,
                          diagnosis_done=False, referral_done=False)
        assert html.count("pipeline-step") == 4

    def test_done_step_gets_done_class(self):
        html = self._call(voice_done=True, image_done=False,
                          diagnosis_done=False, referral_done=False)
        assert "pipeline-step done" in html

    def test_active_step_present_when_not_all_done(self):
        html = self._call(voice_done=False, image_done=False,
                          diagnosis_done=False, referral_done=False)
        assert "pipeline-step active" in html

    def test_pending_step_present(self):
        html = self._call(voice_done=True, image_done=False,
                          diagnosis_done=False, referral_done=False)
        assert "pending" in html

    def test_all_done_no_active_step(self):
        html = self._call(voice_done=True, image_done=True,
                          diagnosis_done=True, referral_done=True)
        assert "active" not in html

    def test_done_dot_shows_checkmark(self):
        html = self._call(voice_done=True, image_done=False,
                          diagnosis_done=False, referral_done=False)
        assert "✓" in html


# ── TestRenderStatCard ────────────────────────────────────────────────────────

class TestRenderStatCard:
    def _call(self, label, value, color="#1A6FA8"):
        with patch("ui.components.st") as mock_st:
            from ui.components import render_stat_card
            render_stat_card(label, value, color)
            return _captured_html(mock_st.markdown)

    def test_label_in_html(self):
        html = self._call("Clinical Accuracy", "92.46%")
        assert "Clinical Accuracy" in html

    def test_value_in_html(self):
        html = self._call("Clinical Accuracy", "92.46%")
        assert "92.46%" in html

    def test_custom_color_in_html(self):
        html = self._call("Conditions", "7", color="#27AE60")
        assert "#27AE60" in html

    def test_renders_stat_card_class(self):
        html = self._call("Source", "BD Hospitals")
        assert "stat-card-sb" in html


# ── TestRenderTierBanner ──────────────────────────────────────────────────────

class TestRenderTierBanner:
    def _call(self, tier=1, urgency="NON-URGENT", action="See pharmacist",
              bn="ফার্মাসিস্ট", facility="Local Pharmacy"):
        with patch("ui.components.st") as mock_st:
            from ui.components import render_tier_banner
            render_tier_banner(tier, urgency, action, bn, facility)
            return _captured_html(mock_st.markdown)

    def test_tier1_banner_class(self):
        html = self._call(tier=1)
        assert "tier-banner-1" in html

    def test_tier2_banner_class(self):
        html = self._call(tier=2, urgency="ROUTINE", action="Visit clinic",
                          bn="ক্লিনিকে যান")
        assert "tier-banner-2" in html

    def test_tier3_banner_class(self):
        html = self._call(tier=3, urgency="URGENT", action="Emergency",
                          bn="জরুরি")
        assert "tier-banner-3" in html

    def test_urgency_label_shown(self):
        html = self._call(tier=2, urgency="ROUTINE VISIT", action="Go clinic",
                          bn="ক্লিনিক")
        assert "ROUTINE VISIT" in html

    def test_bengali_text_shown(self):
        html = self._call(tier=1, bn="ফার্মাসিস্টে যান")
        assert "ফার্মাসিস্টে যান" in html

    def test_facility_shown(self):
        html = self._call(tier=2, facility="Upazila Health Complex")
        assert "Upazila Health Complex" in html

    def test_tier3_has_urgent_label(self):
        html = self._call(tier=3, urgency="URGENT")
        assert "URGENT" in html


# ── TestRenderConfidenceBar ───────────────────────────────────────────────────

class TestRenderConfidenceBar:
    def _call(self, confidence, label_en="Confident", label_bn="নিশ্চিত"):
        with patch("ui.components.st") as mock_st:
            from ui.components import render_confidence_bar
            render_confidence_bar(confidence, label_en, label_bn)
            return _captured_html(mock_st.markdown)

    def test_renders_percentage(self):
        html = self._call(0.82)
        assert "82" in html

    def test_high_confidence_green(self):
        html = self._call(0.85)
        assert "#27AE60" in html

    def test_low_confidence_red(self):
        html = self._call(0.35)
        assert "#C0392B" in html

    def test_mid_confidence_amber(self):
        html = self._call(0.65)
        assert "#E67E22" in html

    def test_label_en_in_html(self):
        html = self._call(0.75, label_en="Model confident")
        assert "Model confident" in html

    def test_label_bn_in_html(self):
        html = self._call(0.75, label_bn="মডেল নিশ্চিত")
        assert "মডেল নিশ্চিত" in html

    def test_confidence_bar_class_present(self):
        html = self._call(0.80)
        assert "conf-bar-wrap-v2" in html or "conf-bar-fill-v2" in html


# ── TestRenderChatMessage ─────────────────────────────────────────────────────

class TestRenderChatMessage:
    """render_chat_message returns an HTML string — no st mocking needed."""

    def test_returns_string(self):
        from ui.components import render_chat_message
        result = render_chat_message("user", "Hello")
        assert isinstance(result, str)

    def test_user_bubble_class(self):
        from ui.components import render_chat_message
        html = render_chat_message("user", "Test question")
        assert "chat-bubble-user" in html

    def test_ai_bubble_class(self):
        from ui.components import render_chat_message
        html = render_chat_message("assistant", "Test answer")
        assert "chat-bubble-ai" in html

    def test_user_content_in_html(self):
        from ui.components import render_chat_message
        html = render_chat_message("user", "What is scabies?")
        assert "What is scabies?" in html

    def test_ai_content_in_html(self):
        from ui.components import render_chat_message
        html = render_chat_message("assistant", "Scabies is caused by mites.")
        assert "Scabies is caused by mites." in html

    def test_sources_rendered_as_chips(self):
        from ui.components import render_chat_message
        html = render_chat_message("assistant", "Answer", sources=["CDC", "WHO"])
        assert "CDC" in html
        assert "WHO" in html
        assert "chat-source-chip" in html

    def test_user_html_chars_escaped(self):
        from ui.components import render_chat_message
        html = render_chat_message("user", "<script>alert('xss')</script>")
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_ai_avatar_present(self):
        from ui.components import render_chat_message
        html = render_chat_message("assistant", "Hello")
        assert "ai-avatar" in html

    def test_empty_sources_no_chip_div(self):
        from ui.components import render_chat_message
        html = render_chat_message("assistant", "Hello", sources=[])
        assert "chat-source-chips" not in html


# ── TestRenderSuggestedQuestions ──────────────────────────────────────────────

class TestRenderSuggestedQuestions:
    def _mock_cols(self, n):
        col = MagicMock()
        col.__enter__ = MagicMock(return_value=col)
        col.__exit__ = MagicMock(return_value=False)
        return [col] * n

    def test_button_called_for_each_question(self):
        with patch("ui.components.st") as mock_st:
            mock_st.columns.return_value = self._mock_cols(3)
            mock_st.button.return_value = False
            from ui.components import render_suggested_questions
            render_suggested_questions(["Q1", "Q2", "Q3"])
            assert mock_st.button.call_count == 3

    def test_returns_none_when_no_click(self):
        with patch("ui.components.st") as mock_st:
            mock_st.columns.return_value = self._mock_cols(2)
            mock_st.button.return_value = False
            from ui.components import render_suggested_questions
            result = render_suggested_questions(["Q1", "Q2"])
            assert result is None

    def test_returns_question_when_clicked(self):
        with patch("ui.components.st") as mock_st:
            mock_st.columns.return_value = self._mock_cols(3)
            # First button click returns True
            mock_st.button.side_effect = [True, False, False]
            from ui.components import render_suggested_questions
            result = render_suggested_questions(["টিনিয়া কী?", "Q2", "Q3"])
            assert result == "টিনিয়া কী?"

    def test_columns_called_with_question_count(self):
        with patch("ui.components.st") as mock_st:
            mock_st.columns.return_value = self._mock_cols(3)
            mock_st.button.return_value = False
            from ui.components import render_suggested_questions
            render_suggested_questions(["A", "B", "C"])
            mock_st.columns.assert_called_once_with(3)


# ── TestRenderReferralPreview ─────────────────────────────────────────────────

class TestRenderReferralPreview:
    _PRED = {
        "disease": "Tinea", "confidence": 0.82,
        "top2": [
            {"disease": "Tinea", "confidence": 0.82},
            {"disease": "Contact_Dermatitis", "confidence": 0.11},
        ],
    }
    _TIER = {
        "tier": 1, "urgency_label": "NON-URGENT",
        "action": "Consult local pharmacist within 3-5 days",
        "bengali_text": "৩-৫ দিনের মধ্যে ফার্মাসিস্ট",
        "facility": "Local Pharmacy",
    }
    _HISTORY = {
        "patient_name": "Rahim", "chief_complaint": "Itchy ring-shaped rash",
        "symptoms": ["itching", "redness"], "affected_area": "Arm",
    }

    def _call(self, pred=None, tier=None, history=None):
        with patch("ui.components.st") as mock_st:
            from ui.components import render_referral_preview
            render_referral_preview(
                pred    or self._PRED,
                tier    or self._TIER,
                history or self._HISTORY,
            )
            return _captured_html(mock_st.markdown)

    def test_four_section_cards_rendered(self):
        html = self._call()
        assert html.count("referral-section-card") == 4

    def test_section_numbers_present(self):
        html = self._call()
        assert "referral-section-num" in html

    def test_disease_name_shown(self):
        html = self._call()
        assert "Tinea" in html

    def test_patient_name_shown(self):
        html = self._call()
        assert "Rahim" in html

    def test_examination_section_shown(self):
        # Section 2 lists Examination Findings (affected area / duration /
        # progression / previous treatment).
        html = self._call()
        assert "Examination Findings" in html

    def test_tier1_color_applied(self):
        html = self._call()
        assert "#27AE60" in html  # Tier 1 green

    def test_tier3_color_applied(self):
        tier3 = dict(self._TIER, tier=3, urgency_label="URGENT",
                     bengali_text="জরুরি", facility="District Hospital")
        html = self._call(tier=tier3)
        assert "#C0392B" in html  # Tier 3 red

    def test_bengali_action_text_shown(self):
        html = self._call()
        assert "৩-৫ দিনের মধ্যে ফার্মাসিস্ট" in html

    def test_facility_shown(self):
        html = self._call()
        assert "Local Pharmacy" in html


# ── Infinity AI BuildFest — Tab 6 helpers ─────────────────────────────────────

class TestFairnessDisclosure:
    def test_renders_without_error(self):
        with patch("ui.components.st") as mock_st:
            from ui.components import render_fairness_disclosure
            render_fairness_disclosure()
            assert mock_st.markdown.called

    def test_mentions_fitzpatrick_scope(self):
        with patch("ui.components.st") as mock_st:
            from ui.components import render_fairness_disclosure
            render_fairness_disclosure()
            html = _captured_html(mock_st.markdown)
            assert "Fitzpatrick" in html

    def test_disclaims_final_diagnosis(self):
        with patch("ui.components.st") as mock_st:
            from ui.components import render_fairness_disclosure
            render_fairness_disclosure()
            html = _captured_html(mock_st.markdown)
            assert "never a final diagnosis" in html


class TestBusinessModel:
    def test_renders_three_streams(self):
        with patch("ui.components.st") as mock_st:
            from ui.components import render_business_model
            render_business_model()
            html = _captured_html(mock_st.markdown)
            assert "Teleconsult service fee" in html
            assert "NRB Sponsor-a-District" in html
            assert "grants" in html.lower()

    def test_includes_unit_economics(self):
        with patch("ui.components.st") as mock_st:
            from ui.components import render_business_model
            render_business_model()
            html = _captured_html(mock_st.markdown)
            assert "Unit economics" in html
            assert "Break-even" in html


class TestEthicsCard:
    def test_renders_all_sections(self):
        with patch("ui.components.st") as mock_st:
            from ui.components import render_ethics_card
            render_ethics_card()
            html = _captured_html(mock_st.markdown)
            for needle in [
                "Training data provenance",
                "Demographic coverage",
                "Known limitations",
                "When NOT to use",
                "Multi-signal safety",
                "Human-in-the-loop",
                "Data minimisation",
            ]:
                assert needle in html, f"missing section: {needle}"

    def test_names_training_hospitals(self):
        with patch("ui.components.st") as mock_st:
            from ui.components import render_ethics_card
            render_ethics_card()
            html = _captured_html(mock_st.markdown)
            assert "Faridpur" in html
            assert "Rangpur" in html


class TestScalabilityRoadmap:
    def test_renders_three_phases(self):
        with patch("ui.components.st") as mock_st:
            from ui.components import render_scalability_roadmap
            render_scalability_roadmap()
            html = _captured_html(mock_st.markdown)
            assert "Phase 1" in html
            assert "Phase 2" in html
            assert "Phase 3" in html

    def test_mentions_infrastructure_path(self):
        with patch("ui.components.st") as mock_st:
            from ui.components import render_scalability_roadmap
            render_scalability_roadmap()
            html = _captured_html(mock_st.markdown)
            assert "HF Spaces" in html
            assert "AWS" in html


class TestNRBSponsor:
    def _fresh_state(self):
        """Patch ui.components.st with a session_state-like dict that supports `in`."""
        return patch.dict("sys.modules", {})  # no-op; we patch st directly

    def test_seed_pledges_pre_populate_state(self):
        with patch("ui.components.st") as mock_st:
            mock_st.session_state = {}
            mock_st.columns.return_value = [MagicMock(), MagicMock()]
            mock_form = MagicMock()
            mock_form.__enter__ = MagicMock(return_value=mock_form)
            mock_form.__exit__ = MagicMock(return_value=False)
            mock_st.form.return_value = mock_form
            mock_st.form_submit_button.return_value = False
            mock_st.text_input.return_value = ""
            mock_st.selectbox.return_value = "USA"

            from ui.components import render_nrb_sponsor, _NRB_SEED_PLEDGES
            render_nrb_sponsor()

            # After render, session_state should contain the seed pledges
            assert "nrb_pledges" in mock_st.session_state
            assert len(mock_st.session_state["nrb_pledges"]) >= len(_NRB_SEED_PLEDGES)

    def test_seed_data_has_required_fields(self):
        from ui.components import _NRB_SEED_PLEDGES
        assert len(_NRB_SEED_PLEDGES) >= 8
        for p in _NRB_SEED_PLEDGES:
            assert {"name", "country", "district", "amount", "seed"}.issubset(p.keys())
            assert p["seed"] is True
            assert p["amount"] > 0

    def test_renders_partnership_pathway(self):
        with patch("ui.components.st") as mock_st:
            mock_st.session_state = {}
            mock_st.columns.return_value = [MagicMock(), MagicMock()]
            mock_form = MagicMock()
            mock_form.__enter__ = MagicMock(return_value=mock_form)
            mock_form.__exit__ = MagicMock(return_value=False)
            mock_st.form.return_value = mock_form
            mock_st.form_submit_button.return_value = False
            mock_st.text_input.return_value = ""
            mock_st.selectbox.return_value = "USA"

            from ui.components import render_nrb_sponsor
            render_nrb_sponsor()
            html = _captured_html(mock_st.markdown)
            assert "BMANA" in html
            assert "Probashi Kallyan Bank" in html


# ── Round 2: explainability, privacy, architecture, KPI strip ──────────────────

class TestPrivacyBadge:
    def test_renders_without_error(self):
        with patch("ui.components.st") as mock_st:
            from ui.components import render_privacy_badge
            render_privacy_badge()
            assert mock_st.markdown.called

    def test_states_no_persistence(self):
        with patch("ui.components.st") as mock_st:
            from ui.components import render_privacy_badge
            render_privacy_badge()
            html = _captured_html(mock_st.markdown)
            assert "Privacy by design" in html
            assert "never saved" in html

    def test_bilingual(self):
        with patch("ui.components.st") as mock_st:
            from ui.components import render_privacy_badge
            render_privacy_badge()
            html = _captured_html(mock_st.markdown)
            # Bengali text must be present
            assert "ব্রাউজার সেশনে" in html


class TestTechDecisions:
    def test_renders_all_four_decisions(self):
        with patch("ui.components.st") as mock_st:
            from ui.components import render_tech_decisions
            render_tech_decisions()
            html = _captured_html(mock_st.markdown)
            for needle in [
                "Swin Transformer Base + CBAM",
                "INT8 dynamic quantisation",
                "4-signal severity engine",
                "Gemini 1.5 Flash",
                "FAISS",
            ]:
                assert needle in html, f"missing decision: {needle}"

    def test_each_decision_has_metric(self):
        with patch("ui.components.st") as mock_st:
            from ui.components import render_tech_decisions
            render_tech_decisions()
            html = _captured_html(mock_st.markdown)
            assert "92.46%" in html
            assert "1.8 s" in html


class TestArchitectureDiagram:
    def test_renders_without_error(self):
        with patch("ui.components.st") as mock_st:
            from ui.components import render_architecture_diagram
            render_architecture_diagram()
            assert mock_st.markdown.called

    def test_includes_three_columns(self):
        with patch("ui.components.st") as mock_st:
            from ui.components import render_architecture_diagram
            render_architecture_diagram()
            html = _captured_html(mock_st.markdown)
            assert "Inputs" in html
            assert "Processing" in html
            assert "Outputs" in html

    def test_includes_key_pipeline_components(self):
        with patch("ui.components.st") as mock_st:
            from ui.components import render_architecture_diagram
            render_architecture_diagram()
            html = _captured_html(mock_st.markdown)
            for component in [
                "faster-whisper",
                "BD-SkinNet INT8",
                "4-signal severity engine",
                "FAISS-CPU",
                "Overpass API",
                "reportlab",
            ]:
                assert component in html, f"missing component: {component}"

    def test_includes_modularity_statement(self):
        with patch("ui.components.st") as mock_st:
            from ui.components import render_architecture_diagram
            render_architecture_diagram()
            html = _captured_html(mock_st.markdown)
            assert "Modularity" in html


class TestImpactKPIStrip:
    def _patched_st(self, mock_st, session=None):
        if session is None:
            session = {}
        mock_st.session_state = session
        return mock_st

    def test_renders_with_no_prediction(self):
        with patch("ui.components.st") as mock_st:
            self._patched_st(mock_st)
            from ui.components import render_impact_kpi_strip
            render_impact_kpi_strip(prediction_id=None)
            assert mock_st.markdown.called
            html = _captured_html(mock_st.markdown)
            # System metrics always present
            assert "92.46%" in html
            assert "402" in html

    def test_session_counter_increments_on_new_prediction(self):
        with patch("ui.components.st") as mock_st:
            session = {}
            self._patched_st(mock_st, session)
            from ui.components import render_impact_kpi_strip
            render_impact_kpi_strip(prediction_id="Tinea-0.85-22.5")
            assert session.get("_kpi_session_screenings") == 1
            # Same id again — no increment
            render_impact_kpi_strip(prediction_id="Tinea-0.85-22.5")
            assert session.get("_kpi_session_screenings") == 1
            # New id — increments
            render_impact_kpi_strip(prediction_id="Scabies-0.38-45.0")
            assert session.get("_kpi_session_screenings") == 2

    def test_phase_1_target_visible(self):
        with patch("ui.components.st") as mock_st:
            self._patched_st(mock_st)
            from ui.components import render_impact_kpi_strip
            render_impact_kpi_strip(prediction_id=None)
            html = _captured_html(mock_st.markdown)
            assert "Phase 1 pilot target" in html
            assert "200 patients" in html


class TestEthicsCardCompliance:
    """Verifies the Item 4 compliance line was added to render_ethics_card."""

    def test_compliance_section_present(self):
        with patch("ui.components.st") as mock_st:
            from ui.components import render_ethics_card
            render_ethics_card()
            html = _captured_html(mock_st.markdown)
            assert "International standards alignment" in html

    def test_compliance_mentions_named_standards(self):
        with patch("ui.components.st") as mock_st:
            from ui.components import render_ethics_card
            render_ethics_card()
            html = _captured_html(mock_st.markdown)
            for standard in [
                "Bangladesh Digital Security Act",
                "WHO Ethics",
                "GDPR Article 22",
                "WHO South-East Asia",
            ]:
                assert standard in html, f"missing standard: {standard}"
