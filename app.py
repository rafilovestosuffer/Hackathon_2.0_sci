import streamlit as st

st.set_page_config(
    page_title="SkinAI Bangladesh",
    page_icon="🏥",
    layout="wide",
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏥 SkinAI Bangladesh")
    st.markdown("**AI-powered dermatological screening & triage**")
    st.markdown("---")
    st.markdown("**প্রতিযোগিতা:** SciBlitz AI Challenge 2026")
    st.markdown("**আয়োজক:** IEEE SB CUET")
    st.markdown("**ট্র্যাক:** A — স্বাস্থ্য ও সমাজ")
    st.markdown("---")
    st.markdown("**দল:** Rafiur Rahman")
    st.markdown("---")
    st.caption(
        "⚠️ এটি একটি চিকিৎসা যন্ত্র নয়। "
        "সর্বদা একজন লাইসেন্সপ্রাপ্ত চিকিৎসকের পরামর্শ নিন।"
    )

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🏥 SkinAI Bangladesh")
st.markdown("### *সঠিক রোগী → সঠিক ডাক্তার → সঠিক সময়*")

st.info(
    "পরীক্ষামূলক সংস্করণ — সম্পূর্ণ সিস্টেম শীঘ্রই আসছে | "
    "Experimental version — full pipeline coming soon."
)

st.markdown("---")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🔬 রোগ নির্ণয়", "💬 প্রশ্ন করুন", "📄 রেফারেল পত্র"])

with tab1:
    st.subheader("রোগ নির্ণয় ও ট্রিয়াজ")
    st.markdown("AI ব্যবহার করে ত্বকের রোগ সনাক্ত করুন এবং সঠিক চিকিৎসা স্তর নির্ধারণ করুন।")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🎙️ ভয়েস ইনপুট (Bengali)")
        st.info("বাংলায় আপনার লক্ষণ বলুন — শীঘ্রই আসছে।\n\n"
                "_Speak your symptoms in Bengali — coming soon._")

    with col2:
        st.markdown("#### 📷 ছবি আপলোড করুন")
        st.info("ত্বকের ছবি আপলোড করুন — শীঘ্রই আসছে।\n\n"
                "_Upload a skin image for AI diagnosis — coming soon._")

    st.markdown("---")
    st.markdown("#### 📊 ট্রিয়াজ ফলাফল")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric(label="রোগের নাম", value="—", delta=None)
    with col_b:
        st.metric(label="আত্মবিশ্বাস", value="—", delta=None)
    with col_c:
        st.metric(label="জরুরিতা স্তর", value="—", delta=None)

with tab2:
    st.subheader("প্রশ্ন করুন")
    st.markdown("ত্বকের রোগ সম্পর্কে বাংলা বা ইংরেজিতে প্রশ্ন করুন।")
    st.info(
        "RAG চ্যাটবট শীঘ্রই আসছে — CDC, NIH, WHO এবং DGHS বাংলাদেশের "
        "তথ্যের উপর ভিত্তি করে উত্তর দেবে।\n\n"
        "_RAG chatbot coming soon — answers grounded in CDC, NIH, WHO & DGHS Bangladesh._"
    )

with tab3:
    st.subheader("রেফারেল পত্র")
    st.markdown("রোগ নির্ণয়ের পর একটি সম্পূর্ণ রেফারেল পত্র ডাউনলোড করুন।")
    st.info(
        "PDF রেফারেল পত্র শীঘ্রই আসছে — রোগীর ইতিহাস, AI নির্ণয়, "
        "ট্রিয়াজ সুপারিশ এবং নিকটতম হাসপাতালের তথ্য সহ।\n\n"
        "_PDF referral letter coming soon — patient history, AI diagnosis, "
        "triage recommendation & nearest hospital._"
    )
    st.button("📥 রেফারেল পত্র ডাউনলোড করুন", disabled=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption(
    "⚠️ Not a medical device. Always consult a licensed physician. | "
    "SkinAI Bangladesh — SciBlitz AI Challenge 2026 — IEEE SB CUET"
)
