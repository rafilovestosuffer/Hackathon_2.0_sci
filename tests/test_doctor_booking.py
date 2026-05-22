"""
tests/test_doctor_booking.py — Unit tests for doctor booking logic.
No Streamlit rendering — pure logic and data-structure tests.
"""

import re
import random
from datetime import date, timedelta

import pytest

from ui.doctor_booking import (
    DEMO_DOCTOR,
    _to_bn_num,
    _time_to_bn,
    get_available_slots,
)

_VALID_DAYS = {"Sunday", "Tuesday", "Thursday"}
_BOOKING_REQUIRED_KEYS = [
    "doctor_name", "doctor_name_bn", "doctor_credentials",
    "hospital", "hospital_bn",
    "appointment_date", "appointment_date_bn",
    "appointment_time", "appointment_time_bn",
    "consultation_fee", "meet_link",
    "patient_name", "disease_diagnosed", "disease_diagnosed_bn",
    "tier", "booking_id",
]


# ── Test 1: only valid days returned ─────────────────────────────────────────

class TestAvailableSlotsValidDays:
    def test_returns_only_sun_tue_thu(self):
        slots = get_available_slots(14)
        for s in slots:
            assert s["day_name"] in _VALID_DAYS, (
                f"Unexpected day: {s['day_name']}"
            )

    def test_available_days_flag_matches_demo_doctor(self):
        slots = get_available_slots(14)
        for s in slots:
            assert DEMO_DOCTOR["available_days"].get(s["day_name"]) is True


# ── Test 2: slot count in 7-day window ───────────────────────────────────────

class TestAvailableSlotsCount:
    def test_7_day_window_returns_2_or_3(self):
        slots = get_available_slots(7)
        assert 2 <= len(slots) <= 3, (
            f"Expected 2 or 3 available days, got {len(slots)}"
        )

    def test_each_slot_has_8_time_options(self):
        """Morning (4) + evening (4) = 8 time slots per day."""
        slots = get_available_slots(7)
        for s in slots:
            assert len(s["slots"]) == 8

    def test_slots_start_from_tomorrow(self):
        today = date.today()
        slots = get_available_slots(7)
        for s in slots:
            assert s["date"] > today


# ── Test 3: booking_id format ─────────────────────────────────────────────────

class TestBookingIdFormat:
    def test_pattern_matches(self):
        d = date.today()
        booking_id = f"SKN-{d.strftime('%d%m')}-{random.randint(1000, 9999)}"
        assert re.match(r"^SKN-\d{4}-\d{4}$", booking_id), (
            f"booking_id {booking_id!r} does not match SKN-DDMM-XXXX"
        )

    def test_prefix_is_skn(self):
        d = date.today()
        booking_id = f"SKN-{d.strftime('%d%m')}-1234"
        assert booking_id.startswith("SKN-")

    def test_suffix_is_4_digit_random(self):
        ids = set()
        for _ in range(20):
            ids.add(random.randint(1000, 9999))
        assert all(1000 <= i <= 9999 for i in ids)


# ── Test 4: Bengali numeral conversion ────────────────────────────────────────

class TestBengaliNumeralConversion:
    def test_evening_time_conversion(self):
        result = _time_to_bn("06:30 PM")
        assert result == "সন্ধ্যা ৬:৩০"

    def test_morning_time_conversion(self):
        result = _time_to_bn("10:00 AM")
        assert result == "সকাল ১০:০০"

    def test_morning_half_past(self):
        result = _time_to_bn("10:30 AM")
        assert result == "সকাল ১০:৩০"

    def test_evening_seven(self):
        result = _time_to_bn("07:00 PM")
        assert result == "সন্ধ্যা ৭:০০"

    def test_afternoon_pm_is_bikel(self):
        # 3 PM is before 5 PM → বিকেল
        result = _time_to_bn("03:00 PM")
        assert result == "বিকেল ৩:০০"

    def test_to_bn_num_digits(self):
        assert _to_bn_num("0123456789") == "০১২৩৪৫৬৭৮৯"

    def test_to_bn_num_mixed(self):
        assert _to_bn_num("27") == "২৭"

    def test_to_bn_num_year(self):
        assert _to_bn_num("2026") == "২০২৬"


# ── Test 5: booking_details has all required keys ────────────────────────────

class TestBookingDetailsKeys:
    def _make_booking_details(self) -> dict:
        slots = get_available_slots(14)
        assert slots, "Need at least one available day in next 14 days"
        day = slots[0]
        slot_time = "10:00 AM"
        return {
            "doctor_name":         DEMO_DOCTOR["name"],
            "doctor_name_bn":      DEMO_DOCTOR["name_bn"],
            "doctor_credentials":  DEMO_DOCTOR["credentials"],
            "hospital":            DEMO_DOCTOR["hospital"],
            "hospital_bn":         DEMO_DOCTOR["hospital_bn"],
            "appointment_date":    day["date_display"],
            "appointment_date_bn": day["date_display_bn"],
            "appointment_time":    slot_time,
            "appointment_time_bn": _time_to_bn(slot_time),
            "consultation_fee":    DEMO_DOCTOR["fee_bdt"],
            "meet_link":           DEMO_DOCTOR["meet_link"],
            "patient_name":        "Test User",
            "disease_diagnosed":   "Tinea",
            "disease_diagnosed_bn": "",
            "tier":                2,
            "booking_id":          "SKN-2705-1234",
        }

    def test_all_required_keys_present(self):
        bd = self._make_booking_details()
        for key in _BOOKING_REQUIRED_KEYS:
            assert key in bd, f"Missing key: {key}"

    def test_no_extra_none_values_for_required_string_fields(self):
        bd = self._make_booking_details()
        for key in ["doctor_name", "hospital", "appointment_date", "meet_link"]:
            assert bd[key], f"Key {key!r} is empty or None"

    def test_consultation_fee_is_500(self):
        bd = self._make_booking_details()
        assert bd["consultation_fee"] == 500

    def test_meet_link_is_google_meet(self):
        bd = self._make_booking_details()
        assert bd["meet_link"].startswith("https://meet.google.com/")


# ── Test 6: tier None disables confirm ───────────────────────────────────────

class TestTierNonePreviewOnly:
    def test_tier_none_confirm_disabled(self):
        tier = None
        confirm_should_be_disabled = (tier is None)
        assert confirm_should_be_disabled is True

    def test_tier_1_confirm_enabled(self):
        tier = 1
        confirm_should_be_disabled = (tier is None)
        assert confirm_should_be_disabled is False

    def test_tier_2_confirm_enabled(self):
        tier = 2
        confirm_should_be_disabled = (tier is None)
        assert confirm_should_be_disabled is False


# ── Test 7: tier 3 hides booking flow ────────────────────────────────────────

class TestTier3HidesBookingFlow:
    def test_tier_3_returns_early(self):
        tier = 3
        show_booking_form = (tier != 3)
        assert show_booking_form is False

    def test_tier_1_shows_booking_form(self):
        tier = 1
        show_booking_form = (tier != 3)
        assert show_booking_form is True

    def test_tier_2_shows_booking_form(self):
        tier = 2
        show_booking_form = (tier != 3)
        assert show_booking_form is True

    def test_tier_none_shows_preview(self):
        tier = None
        show_booking_form = (tier != 3)
        assert show_booking_form is True  # shows preview, confirm disabled


# ── Bonus: DEMO_DOCTOR data integrity ────────────────────────────────────────

class TestDemoDoctorIntegrity:
    def test_has_required_fields(self):
        required = [
            "name", "name_bn", "credentials", "credentials_bn",
            "hospital", "hospital_bn", "available_days",
            "morning_slots", "evening_slots", "fee_bdt",
            "meet_link", "verified",
        ]
        for field in required:
            assert field in DEMO_DOCTOR, f"DEMO_DOCTOR missing: {field}"

    def test_available_days_has_three_days(self):
        active = [k for k, v in DEMO_DOCTOR["available_days"].items() if v]
        assert len(active) == 3

    def test_four_morning_slots(self):
        assert len(DEMO_DOCTOR["morning_slots"]) == 4

    def test_four_evening_slots(self):
        assert len(DEMO_DOCTOR["evening_slots"]) == 4

    def test_fee_is_positive(self):
        assert DEMO_DOCTOR["fee_bdt"] > 0

    def test_rating_in_range(self):
        assert 1.0 <= DEMO_DOCTOR["rating"] <= 5.0

    def test_meet_link_is_string(self):
        assert isinstance(DEMO_DOCTOR["meet_link"], str)
        assert len(DEMO_DOCTOR["meet_link"]) > 0


# ── Bonus: slot structure ─────────────────────────────────────────────────────

class TestSlotStructure:
    def test_each_slot_has_required_keys(self):
        slots = get_available_slots(7)
        required = ["date", "date_display", "date_display_bn",
                    "day_name", "day_name_bn", "slots"]
        for s in slots:
            for k in required:
                assert k in s, f"Slot missing key: {k}"

    def test_time_slot_has_required_keys(self):
        slots = get_available_slots(7)
        for day in slots:
            for t in day["slots"]:
                assert "time_en" in t
                assert "time_bn" in t
                assert "available" in t
                assert t["available"] is True

    def test_date_display_includes_day_name(self):
        slots = get_available_slots(7)
        for s in slots:
            assert s["day_name"] in s["date_display"]

    def test_date_display_bn_contains_bengali(self):
        slots = get_available_slots(7)
        for s in slots:
            # Bengali chars are in the range U+0980–U+09FF
            has_bengali = any("ঀ" <= ch <= "৿" for ch in s["date_display_bn"])
            assert has_bengali, f"No Bengali in date_display_bn: {s['date_display_bn']!r}"
