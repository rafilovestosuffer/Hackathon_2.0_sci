"""
whatsapp/replies.py — Bilingual (Bengali + English) message templates.

Every medical reply ends with the standard AI disclaimer.
"""

DISCLAIMER = (
    "\n\n⚠ এটি AI বিশ্লেষণ, চিকিৎসকের পরামর্শের বিকল্প নয়।\n"
    "This is an AI assessment, not a substitute for medical advice."
)

WELCOME = (
    "👋 স্বাগতম! SkinAI Bangladesh — ত্বকের সমস্যার AI স্ক্রিনিং।\n\n"
    "শুরু করার জন্য, আপনার জেলার নাম বাংলায় বা ইংরেজিতে লিখুন।\n"
    "উদাহরণ: ঢাকা · Rangpur · Chittagong\n\n"
    "Welcome! To begin, please type your district name."
)

INVALID_DISTRICT = (
    "❌ জেলা চিনতে পারিনি। আবার চেষ্টা করুন।\n"
    "District not recognised. Please try again.\n\n"
    "উদাহরণ · Examples: ঢাকা, রংপুর, চট্টগ্রাম, সিলেট, খুলনা"
)

ASK_IMAGE = (
    "✅ জেলা: {district}\n\n"
    "📸 এখন আপনার ত্বকের সমস্যার একটি স্পষ্ট ছবি পাঠান।\n"
    "আলোতে তুলুন, খুব কাছ থেকে নয় — ১৫–৩০ সেমি দূর থেকে।\n\n"
    "Please send a clear photo of the affected skin area."
)

ASK_VOICE = (
    "✅ ছবি পেয়েছি।\n\n"
    "🎙️ এখন একটি ভয়েস বার্তা পাঠান (১৫–৩০ সেকেন্ড) — বাংলায় বলুন:\n"
    "• সমস্যা কী?\n"
    "• কতদিন ধরে?\n"
    "• চুলকানি/জ্বর/ব্যথা আছে কি?\n\n"
    "অথবা টাইপ করুন: skip — শুধু ছবি দিয়ে বিশ্লেষণ\n\n"
    "Now send a voice note describing your symptoms, or type 'skip'."
)

PROCESSING = (
    "📋 পেয়েছি, বিশ্লেষণ করছি... ৩০ সেকেন্ড অপেক্ষা করুন।\n"
    "Received. Analysing... please wait ~30 seconds."
)

BLURRY_IMAGE = (
    "⚠ ছবি অস্পষ্ট মনে হচ্ছে। অনুগ্রহ করে আলোতে আবার তুলে পাঠান।\n"
    "Image appears blurry. Please retake in better lighting."
)

UNSUPPORTED_MEDIA = (
    "❌ এই ধরনের ফাইল সমর্থিত নয়। ছবি (JPG/PNG) বা ভয়েস (audio) পাঠান।\n"
    "Unsupported file type. Please send an image or voice note."
)

RATE_LIMITED = (
    "⏳ অনেক দ্রুত বার্তা পাঠাচ্ছেন। ১ মিনিট অপেক্ষা করুন।\n"
    "Too many messages. Please wait a minute."
)

UNKNOWN_ERROR = (
    "❌ একটি ত্রুটি হয়েছে। 'নতুন' লিখে আবার শুরু করুন।\n"
    "An error occurred. Type 'নতুন' or 'new' to restart."
)

ASK_SHARE_WITH_DOCTOR = (
    "👩‍⚕️ একজন ডাক্তার কি আপনার ছবি ও ফলাফল দেখে মতামত দেবেন?\n"
    "নাম বা ফোন নম্বর পাঠানো হবে না; ৭ দিন পর সব মুছে ফেলা হবে।\n"
    "উত্তর দিন: হ্যাঁ / না\n\n"
    "Share your photo and result (no name or phone) with a doctor for review? "
    "Deleted after 7 days. Reply: yes / no"
)

SHARED_OK = (
    "✅ পাঠানো হয়েছে। ডাক্তার দেখলে এখানেই জানানো হবে।\n"
    "জরুরি লক্ষণ থাকলে অপেক্ষা করবেন না — উপরের পরামর্শ মেনে আজই যান।\n"
    "Sent. You'll get the doctor's reply here. Don't wait if you have urgent signs."
)

NOT_SHARED = "ঠিক আছে, কিছু পাঠানো হয়নি। · OK, nothing was shared."

SHARE_FAILED = (
    "⚠ এখন পাঠানো যায়নি। উপরের পরামর্শ অনুযায়ী চলুন।\n"
    "Could not share right now. Please follow the advice above."
)


def format_doctor_decision(*, status: str, disease_bn: str, disease_en: str,
                           tier: int, bengali_action: str, english_action: str,
                           note: str = "") -> str:
    """Message sent to the patient after a doctor reviews their case."""
    head = ("✅ ডাক্তার এআই-এর মূল্যায়ন নিশ্চিত করেছেন।\nA doctor confirmed the AI assessment."
            if status == "confirmed" else
            "✎ ডাক্তার মূল্যায়ন পরিবর্তন করেছেন।\nA doctor updated the assessment.")
    lines = [
        "👩‍⚕️ ডাক্তারের মতামত · Doctor review",
        head,
        "",
        f"রোগ · Condition: {disease_bn} ({disease_en})",
        f"{TIER_LABELS_BN[tier]}",
        f"🇧🇩 {bengali_action}",
        f"🇬🇧 {english_action}",
    ]
    if note:
        lines.extend(["", f"📝 {note}"])
    lines.append(
        "\n\n⚠ এটি ছবির ভিত্তিতে দূর থেকে দেওয়া মতামত; সরাসরি পরীক্ষার বিকল্প নয়।\n"
        "This is a remote review of a photo, not a substitute for an in-person examination."
    )
    return "\n".join(lines)


MODEL_UNAVAILABLE = (
    "⏳ এআই মডেল এই মুহূর্তে চালু নেই, তাই কোনো ফলাফল দেওয়া হলো না।\n"
    "এক মিনিট পরে 'আবার' লিখে পাঠান — আপনার ছবি ও তথ্য রাখা আছে।\n"
    "জ্বর, দ্রুত ছড়ানো, রক্তপাত বা তীব্র ব্যথা থাকলে অপেক্ষা না করে আজই নিকটস্থ স্বাস্থ্যকেন্দ্রে যান।\n\n"
    "The AI model is not available right now, so no result was given.\n"
    "Send 'retry' in a minute — your photo and details are kept.\n"
    "If there is fever, fast spreading, bleeding or severe pain, go to the nearest health facility today."
)

RESET_OK = (
    "🔄 শুরু থেকে আবার করছি।\n"
    "Starting over.\n\n" + WELCOME
)

HELP = (
    "ℹ️ SkinAI সাহায্য · Help\n\n"
    "• ছবি পাঠান → ত্বক বিশ্লেষণ\n"
    "• ভয়েস পাঠান → লক্ষণ বিশ্লেষণ\n"
    "• 'নতুন' / 'new' → আবার শুরু\n"
    "• যেকোনো প্রশ্ন টাইপ করুন → AI উত্তর\n\n"
    "Send an image, a voice note, or any question."
)

TIER_LABELS_BN = {
    0: "✅ স্বাভাবিক · Normal",
    1: "🟢 হালকা · Non-urgent",
    2: "🟡 মাঝারি · Routine",
    3: "🔴 জরুরি · URGENT",
}


def format_triage_result(
    *,
    disease_bn: str,
    disease_en: str,
    confidence: float,
    tier: int,
    bengali_action: str,
    english_action: str,
    facility: str,
    nearest_hospital: dict | None,
    reasons: list | None = None,
) -> str:
    """Build the main triage result message."""
    lines = [
        f"📊 ফলাফল · Result",
        f"রোগ · Disease: {disease_bn} ({disease_en})",
        f"নিশ্চয়তা · Confidence: {int(confidence * 100)}%",
        "",
        f"{TIER_LABELS_BN[tier]}",
        f"📍 {facility}",
        "",
        f"🇧🇩 {bengali_action}",
        f"🇬🇧 {english_action}",
    ]
    if reasons:
        lines.extend(["", "❓ কেন এই স্তর? · Why this tier:"])
        lines.extend(f"• {r['bn']}" for r in reasons)
    if nearest_hospital and tier >= 2:
        lines.extend([
            "",
            f"🏥 নিকটস্থ হাসপাতাল · Nearest hospital:",
            f"   {nearest_hospital.get('name', 'N/A')}",
            f"   দূরত্ব · Distance: {nearest_hospital.get('dist_km', 0):.1f} km",
        ])
        if nearest_hospital.get("address"):
            lines.append(f"   {nearest_hospital['address']}")
    lines.append(DISCLAIMER)
    return "\n".join(lines)


def format_chat_followup() -> str:
    return (
        "💬 আপনার পরবর্তী পদক্ষেপ:\n"
        "• যেকোনো প্রশ্ন টাইপ করুন (বাংলা/English)\n"
        "• 'নতুন' / 'new' → পুনরায় শুরু\n\n"
        "What would you like to do next? Ask any question, or type 'new'."
    )


def format_rag_answer(answer: str) -> str:
    return f"💡 {answer}{DISCLAIMER}"
