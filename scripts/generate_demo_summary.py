"""
scripts/generate_demo_summary.py
Generate a realistic demo Post-Consultation Care Summary PDF without a live
Gemini API call. Hardcoded consultation data mirrors a real Tinea Corporis
session for the SciBlitz AI Challenge 2026 demo.

Run from project root:
    python scripts/generate_demo_summary.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import patch
import json

# ── Realistic consultation data (what Gemini would extract) ───────────────────
_DEMO_GEMINI_DATA = {
    "diagnosis_confirmed": "Tinea Corporis (Ringworm of the Body)",
    "prescribed_medicines": [
        {
            "name": "Clotrimazole 1% Cream",
            "name_bn": "ক্লোট্রিমাজল ১% ক্রিম",
            "dose": "Thin layer",
            "frequency": "Twice daily (morning & night)",
            "duration": "14 days",
            "instructions": "Apply after washing and thoroughly drying the area",
        },
        {
            "name": "Cetirizine 10 mg Tablet",
            "name_bn": "সেটিরিজিন ১০ মিগ্রা",
            "dose": "1 tablet",
            "frequency": "Once daily at night",
            "duration": "7 days",
            "instructions": "Take with water after dinner — may cause drowsiness",
        },
    ],
    "dos": [
        "Keep the affected area clean and completely dry at all times",
        "Wash the area gently with mild soap and pat dry before applying cream",
        "Wash all clothing, bedsheets, and towels in hot water (above 60°C)",
        "Wear loose-fitting, breathable cotton clothing",
        "Complete the full 14-day course even if rash improves earlier",
        "Wash hands thoroughly after applying the cream",
    ],
    "donts": [
        "Do not share towels, clothing, or bedsheets with other family members",
        "Do not scratch the affected area — it spreads the infection",
        "Do not apply any talcum powder, coconut oil, or home remedies on the rash",
        "Do not stop the medicine early even if the rash seems healed",
        "Avoid tight or synthetic clothing on the affected area",
        "Do not let pets sleep on your bed — ringworm can spread from animals",
    ],
    "diet_instructions": [
        "Reduce intake of refined sugar and white rice — fungal infections thrive on sugar",
        "Increase probiotic foods: yogurt (টক দই), fermented foods",
        "Drink at least 8 glasses of water per day",
        "Avoid alcohol completely during the treatment course",
    ],
    "activity_restrictions": [
        "Avoid public swimming pools and shared bathing areas for 3 weeks",
        "Avoid heavy physical labour that causes excessive sweating on the affected area",
        "Do not share gym equipment or sports gear without disinfecting",
    ],
    "follow_up_date": "2026-06-06",
    "follow_up_condition": "If rash spreads beyond current area, develops blisters, or does not begin improving within 7 days",
    "warning_signs": [
        "Fever above 100°F (38°C) with spreading rash",
        "Rash spreads rapidly to face, hands, or genitals",
        "Skin becomes swollen, warm to touch, or develops pus-filled blisters",
        "Severe difficulty breathing or swallowing (possible allergic reaction to medicine)",
        "Rash does not respond at all after 7 days of treatment",
    ],
    "warning_signs_bn": [
        "১০০°F (৩৮°C) এর উপরে জ্বর এবং দাগ ছড়িয়ে পড়া",
        "মুখ, হাত বা লজ্জাস্থানে দ্রুত ছড়িয়ে পড়া",
        "ত্বক ফুলে যাওয়া, গরম অনুভব হওয়া বা পুঁজ ভরা ফোসকা দেখা দেওয়া",
        "শ্বাস নিতে বা গিলতে কষ্ট — ওষুধে অ্যালার্জির লক্ষণ হতে পারে",
        "৭ দিন চিকিৎসার পরেও কোনো উন্নতি না হওয়া",
    ],
    "doctor_notes": (
        "Patient presents with a classical annular (ring-shaped) erythematous plaque "
        "on the left forearm, approximately 4 cm diameter, with central clearing. "
        "Consistent with Tinea Corporis. KOH preparation not available at this facility — "
        "clinical diagnosis made on appearance. AI screening (SkinAI Bangladesh) concurs: "
        "Tinea, 82% confidence. Prognosis is excellent with compliance. "
        "Advise patient to inform household members for screening."
    ),
    "consultation_date": "2026-05-23",
    "consultation_duration": "30 minutes",
}

# ── Session state (mirrors what app.py would hold after triage) ───────────────
_DEMO_SESSION_STATE = {
    "prediction": {
        "disease": "Tinea",
        "confidence": 0.82,
        "top2": [
            {"disease": "Tinea", "confidence": 0.82},
            {"disease": "Contact_Dermatitis", "confidence": 0.09},
        ],
        "heatmap": None,
        "coverage_pct": 22.5,
    },
    "history": {
        "chief_complaint": "Ring-shaped itchy rash on left forearm",
        "symptoms": ["itching", "ring-shaped rash", "redness", "dry flaky skin"],
        "affected_area": "left forearm",
        "duration": "3 weeks",
        "progression": "slowly spreading outward",
        "previous_treatment": "Coconut oil applied by family — no improvement",
        "associated_symptoms": [],
        "patient_name": "Rahim Uddin",
        "patient_age": "35",
    },
    "tier_result": {
        "tier": 1,
        "urgency_label": "NON-URGENT",
        "action": "Consult local pharmacist within 3-5 days",
        "facility": "Local Pharmacy",
        "bengali_text": "৩-৫ দিনের মধ্যে নিকটস্থ ফার্মাসিস্টের সাথে পরামর্শ করুন",
    },
    "booking_confirmed": True,
    "booking_details": {
        "doctor_name": "Dr. Nusrat Jahan",
        "doctor_credentials": "MBBS, DDV — Chittagong Medical College",
        "hospital": "Chittagong Medical College Hospital",
        "appointment_date": "2026-05-23",
        "appointment_time": "11:00 AM",
        "booking_id": "SKN-2026-0523-001",
    },
}


def main():
    from pdf_gen.consultation_summary import generate_consultation_summary_pdf

    mock_resp = type("R", (), {"text": json.dumps(_DEMO_GEMINI_DATA)})()
    mock_client = type("C", (), {
        "models": type("M", (), {
            "generate_content": staticmethod(lambda **kw: mock_resp)
        })()
    })()

    with patch(
        "pdf_gen.consultation_summary._get_gemini_client",
        return_value=mock_client,
    ):
        pdf_bytes = generate_consultation_summary_pdf(
            consultation_transcript=(
                "Dr. Nusrat: Good morning Rahim. I can see from the AI report that "
                "you have a ring-shaped rash on your left forearm for 3 weeks. "
                "This is Tinea Corporis — a common fungal infection. Completely treatable. "
                "I am prescribing Clotrimazole 1% cream — apply a thin layer twice daily "
                "after washing and drying the area, morning and night, for 14 full days. "
                "Also take Cetirizine 10mg tablet once at night for 7 days to reduce itching. "
                "Keep the area dry. Wash all clothing and bedsheets in hot water. "
                "Do not share towels with family members. Do not scratch. "
                "Reduce sugar in your diet. Avoid swimming pools for 3 weeks. "
                "If the rash spreads to your face or develops blisters, go to the "
                "district hospital immediately. Otherwise come back in 14 days on "
                "June 6th, or sooner if it is not improving after 7 days. "
                "The AI system did an excellent job catching this early. "
                "Good luck Rahim — full recovery in 2 weeks."
            ),
            session_state=_DEMO_SESSION_STATE,
            consultation_duration_minutes=30,
        )

    out_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "demo_consultation_summary.pdf",
    )
    with open(out_path, "wb") as f:
        f.write(pdf_bytes)

    size_kb = len(pdf_bytes) / 1024
    print(f"[OK] Demo PDF written: {out_path}  ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
