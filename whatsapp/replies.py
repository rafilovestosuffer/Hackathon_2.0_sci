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
