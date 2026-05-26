"""
pages/docs.py — SkinAI Bangladesh Live Documentation
Accessible at: {hf_spaces_url}/docs
YC-style pitch deck + technical whitepaper + system dashboard
"""

import datetime
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="SkinAI Bangladesh — Docs",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Noto+Sans+Bengali:wght@400;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.docs-hero {
    background: linear-gradient(135deg, #0B1929 0%, #0f2744 50%, #0B1929 100%);
    border: 1px solid #1e3a5f;
    border-radius: 16px;
    padding: 56px 48px;
    text-align: center;
    margin-bottom: 40px;
}
.docs-hero h1 {
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(135deg, #00d4ff, #0088ff, #00d4ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 12px;
}
.docs-hero .tagline {
    font-size: 1.25rem;
    color: #94a3b8;
    margin-bottom: 24px;
}
.badge-row {
    display: flex;
    gap: 12px;
    justify-content: center;
    flex-wrap: wrap;
    margin-top: 20px;
}
.badge {
    background: #1e3a5f;
    color: #00d4ff;
    padding: 6px 16px;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 600;
    border: 1px solid #0088ff44;
}
.section-header {
    font-size: 1.6rem;
    font-weight: 700;
    color: #e2e8f0;
    border-left: 4px solid #00d4ff;
    padding-left: 16px;
    margin: 40px 0 20px 0;
}
.card {
    background: #0f1f35;
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 24px;
    height: 100%;
}
.card h3 { color: #00d4ff; font-size: 1rem; font-weight: 600; margin-bottom: 8px; }
.card p  { color: #94a3b8; font-size: 0.9rem; line-height: 1.6; margin: 0; }
.metric-card {
    background: linear-gradient(135deg, #0f1f35, #0f2744);
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
}
.metric-value { font-size: 2rem; font-weight: 800; color: #00d4ff; }
.metric-label { font-size: 0.8rem; color: #64748b; margin-top: 4px; }
.team-card {
    background: #0f1f35;
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
}
.team-avatar {
    width: 72px;
    height: 72px;
    border-radius: 50%;
    background: linear-gradient(135deg, #00d4ff, #0088ff);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.6rem;
    font-weight: 700;
    color: #0B1929;
    margin: 0 auto 12px auto;
}
.team-name   { font-weight: 700; color: #e2e8f0; font-size: 0.95rem; }
.team-role   { color: #00d4ff; font-size: 0.8rem; margin: 4px 0; }
.team-leader { border: 2px solid #00d4ff; }
.team-email  { color: #64748b; font-size: 0.75rem; }
.feature-pill {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    margin: 2px;
}
.pill-live    { background: #052e16; color: #4ade80; border: 1px solid #166534; }
.pill-planned { background: #1e1b4b; color: #818cf8; border: 1px solid #3730a3; }
.tier-1 { background: #052e16; color: #4ade80; padding: 3px 10px; border-radius: 6px; font-size: 0.8rem; }
.tier-2 { background: #431407; color: #fb923c; padding: 3px 10px; border-radius: 6px; font-size: 0.8rem; }
.tier-3 { background: #450a0a; color: #f87171; padding: 3px 10px; border-radius: 6px; font-size: 0.8rem; }
.nav-bar {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    background: #0f1f35;
    border: 1px solid #1e3a5f;
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 32px;
}
.nav-link {
    color: #64748b;
    font-size: 0.82rem;
    text-decoration: none;
    padding: 4px 10px;
    border-radius: 6px;
    transition: all 0.2s;
}
.nav-link:hover { background: #1e3a5f; color: #00d4ff; }
.divider { border: none; border-top: 1px solid #1e3a5f; margin: 48px 0; }
.stack-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 0;
    border-bottom: 1px solid #1e3a5f;
}
.stack-layer { color: #64748b; font-size: 0.78rem; width: 120px; flex-shrink: 0; }
.stack-value { color: #e2e8f0; font-size: 0.88rem; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def mermaid(diagram: str, height: int = 380):
    html = f"""
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <script>mermaid.initialize({{startOnLoad:true,theme:'dark',
        themeVariables:{{primaryColor:'#0f2744',primaryTextColor:'#e2e8f0',
        primaryBorderColor:'#1e3a5f',lineColor:'#00d4ff',background:'#0B1929'}}}});</script>
    <div class="mermaid" style="background:#0B1929;padding:16px;border-radius:8px">{diagram}</div>
    """
    components.html(html, height=height)


def section(title: str, anchor: str):
    st.markdown(f'<div class="section-header" id="{anchor}">{title}</div>', unsafe_allow_html=True)


# ── HERO ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="docs-hero">
    <h1>🩺 SkinAI Bangladesh</h1>
    <div class="tagline">AI-powered dermatological screening & triage for rural Bangladesh</div>
    <div style="color:#94a3b8;font-size:0.9rem;font-style:italic;font-family:'Noto Sans Bengali',sans-serif">
        "সঠিক রোগী → সঠিক ডাক্তার → সঠিক সময়"
    </div>
    <div class="badge-row">
        <span class="badge">🏆 SciBlitz AI Challenge 2026</span>
        <span class="badge">Track A: Health & Society</span>
        <span class="badge">IEEE SB CUET</span>
        <span class="badge">F1 = 92.46%</span>
        <span class="badge">310+ Tests</span>
        <span class="badge">Live on HF Spaces</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── NAV ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="nav-bar">
    <span style="color:#00d4ff;font-weight:600;font-size:0.82rem">Jump to →</span>
    <a class="nav-link" href="#problem">Problem</a>
    <a class="nav-link" href="#solution">Solution</a>
    <a class="nav-link" href="#traction">Traction</a>
    <a class="nav-link" href="#architecture">Architecture</a>
    <a class="nav-link" href="#ai-layer">AI Layer</a>
    <a class="nav-link" href="#features">Features</a>
    <a class="nav-link" href="#tech-stack">Tech Stack</a>
    <a class="nav-link" href="#business">Business Model</a>
    <a class="nav-link" href="#team">Team</a>
    <a class="nav-link" href="#roadmap">Roadmap</a>
</div>
""", unsafe_allow_html=True)


# ── 1. PROBLEM ────────────────────────────────────────────────────────────────
section("🚨 The Problem", "problem")
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("""<div class="card">
    <h3>1 per 250,000</h3>
    <p>Bangladesh has approximately <strong style="color:#f87171">1 dermatologist per 250,000 people</strong> — one of the lowest ratios in Asia.</p>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown("""<div class="card">
    <h3>80% Untreated</h3>
    <p>80% of skin conditions in rural Bangladesh go <strong style="color:#f87171">untreated or misdiagnosed</strong> by unlicensed practitioners (quacks).</p>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown("""<div class="card">
    <h3>The Rahim Story</h3>
    <p>A farmer in Rangpur notices a spreading rash. The nearest dermatologist is 4 hours away and costs 1,500 BDT he cannot spare. He goes to a quack instead.</p>
    </div>""", unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)


# ── 2. SOLUTION ───────────────────────────────────────────────────────────────
section("💡 The Solution", "solution")
st.markdown("""
<div class="card" style="margin-bottom:20px">
<h3>Right Patient → Right Doctor → Right Time</h3>
<p>SkinAI Bangladesh does not replace the doctor. It ensures the right patient reaches the right doctor at the right time —
instead of reaching the wrong practitioner too late. A Bengali voice input + skin photo produces a clinical triage decision,
bilingual referral letter, and emergency hospital map in under 30 seconds.</p>
</div>
""", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    st.markdown("""<div class="card">
    <h3>🎙️ Bengali Voice Input</h3>
    <p>Patient speaks in Bengali. faster-whisper ASR transcribes → Gemini 1.5 Flash extracts 9-field structured patient history JSON.</p>
    </div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""<div class="card">
    <h3>🗺️ Emergency Hospital Map</h3>
    <p>Tier 3 results trigger Overpass API query → 5 nearest hospitals on Folium map → injected into PDF referral letter.</p>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown("""<div class="card">
    <h3>🔬 3-Signal Triage Engine</h3>
    <p>Disease class + model confidence + Bengali voice keywords → urgency tier 1/2/3 with bilingual action text.</p>
    </div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""<div class="card">
    <h3>📄 PDF Referral Letter</h3>
    <p>4-section professional referral: patient history, clinical observation, AI diagnosis, triage recommendation. Single button. Zero manual input.</p>
    </div>""", unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)


# ── 3. TRACTION ───────────────────────────────────────────────────────────────
section("📊 Traction & Metrics", "traction")
cols = st.columns(5)
metrics = [
    ("92.46%", "Model F1 Score"),
    ("0.9937", "AUC-ROC"),
    ("7", "Disease Classes"),
    ("310+", "Tests Passing"),
    ("100", "RAG Chunks"),
]
for col, (val, label) in zip(cols, metrics):
    with col:
        st.markdown(f"""<div class="metric-card">
        <div class="metric-value">{val}</div>
        <div class="metric-label">{label}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    st.markdown("""<div class="card">
    <h3>📍 Training Data</h3>
    <p>Bangladesh-specific clinical dermatology data from <strong style="color:#e2e8f0">Faridpur Medical College Hospital</strong>
    and <strong style="color:#e2e8f0">Rangpur Medical College Hospital</strong>.
    7 disease classes. No DermNet (AI-generated images policy).</p>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown("""<div class="card">
    <h3>🚀 Deployment</h3>
    <p>Live on <strong style="color:#e2e8f0">Hugging Face Spaces</strong> (free CPU tier).
    GitHub Actions keepalive (every 20 min). Zero-click public URL.
    No login required for judges.</p>
    </div>""", unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)


# ── 4. ARCHITECTURE ───────────────────────────────────────────────────────────
section("🏗️ System Architecture", "architecture")
mermaid("""
graph TB
    subgraph INPUT["📥 Input Layer"]
        A[🎙️ Bengali Audio]
        B[📸 Skin Image]
    end
    subgraph PROCESSING["⚙️ Processing Layer"]
        C[faster-whisper ASR<br/>INT8 · language=bn]
        D[Gemini 1.5 Flash<br/>JSON Extraction]
        E[BD-SkinNet<br/>Swin-B + CBAM · INT8]
    end
    subgraph TRIAGE["🎯 Triage Engine"]
        G[3-Signal Engine<br/>Disease + Confidence<br/>+ Bengali Keywords]
    end
    subgraph OUTPUT["📤 Output Layer"]
        H[Tier 1: Pharmacy]
        I[Tier 2: Clinic]
        J[Tier 3: Emergency + Map]
        K[PDF Referral Letter]
        L[RAG Chatbot]
    end
    A --> C --> D --> G
    B --> E --> G
    G --> H & I & J & K
    L -.->|FAISS + Gemini| K
""", height=480)

st.markdown('<hr class="divider">', unsafe_allow_html=True)


# ── 5. DATA FLOW ─────────────────────────────────────────────────────────────
section("🔄 Data Flow Diagram", "dataflow")
mermaid("""
sequenceDiagram
    participant U as 🧑‍🌾 Patient
    participant V as Voice Pipeline
    participant M as BD-SkinNet
    participant T as Triage Engine
    participant R as RAG Chatbot
    participant P as PDF Generator

    U->>V: Bengali audio
    V->>V: faster-whisper ASR (INT8)
    V->>V: Gemini JSON extraction
    V-->>T: patient_history{}

    U->>M: skin_image (224×224)
    M->>M: Swin-B + CBAM inference
    M-->>T: {disease, confidence}

    T->>T: 3-signal fusion
    T-->>U: tier + bilingual action

    U->>R: Bengali/English question
    R->>R: BM25/FAISS retrieval
    R->>R: Gemini answer + redaction
    R-->>U: Safe medical guidance

    U->>P: Generate referral
    P-->>U: 4-section PDF
""", height=500)

st.markdown('<hr class="divider">', unsafe_allow_html=True)


# ── 6. AI LAYER ──────────────────────────────────────────────────────────────
section("🤖 AI Layer", "ai-layer")
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("""<div class="card">
    <h3>BD-SkinNet (Vision)</h3>
    <p><strong style="color:#e2e8f0">Swin Transformer Base + CBAM</strong><br/>
    4-stage attention (channel + spatial)<br/>
    INT8 dynamic quantization<br/>
    224×224 RGB input<br/>
    7 Bangladesh clinical classes<br/>
    F1=92.46% · AUC=0.9937</p>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown("""<div class="card">
    <h3>RAG Chatbot (NLP)</h3>
    <p><strong style="color:#e2e8f0">BM25 + FAISS + Gemini 2.5 Flash</strong><br/>
    100 disease-specific chunks<br/>
    CDC × 32 · NIH × 32<br/>
    WHO × 16 · DGHS BD × 20<br/>
    Auto Bengali/English detection<br/>
    Medicine-name redaction guardrail</p>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown("""<div class="card">
    <h3>Voice Pipeline (ASR)</h3>
    <p><strong style="color:#e2e8f0">faster-whisper + Gemini Flash</strong><br/>
    Whisper Base, language="bn"<br/>
    CTranslate2 INT8 runtime<br/>
    Gemini JSON extraction (9 fields)<br/>
    3-retry with graceful fallback<br/>
    Bengali keyword escalation</p>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)


# ── 7. FEATURE MATRIX ────────────────────────────────────────────────────────
section("✅ Feature Matrix", "features")

features = [
    ("Bengali Voice Input", "faster-whisper + Gemini JSON", "live"),
    ("Skin Image Analysis", "BD-SkinNet INT8 (Swin+CBAM)", "live"),
    ("3-Signal Triage Engine", "Disease + Confidence + Bengali Keywords", "live"),
    ("Emergency Hospital Map", "Overpass API + Folium, 64 districts", "live"),
    ("PDF Referral Letter", "4-section bilingual, single click", "live"),
    ("RAG Medical Chatbot", "BM25+FAISS+Gemini, CDC/NIH/WHO/DGHS", "live"),
    ("Bengali TTS", "gTTS reads triage recommendation aloud", "live"),
    ("Auto Image Enhancement", "CLAHE + unsharp mask pre-inference", "live"),
    ("CHW Simplified Mode", "Large-font binary refer/no-refer card", "live"),
    ("Doctor Booking Tab", "Triage-aware slot booking + video call", "live"),
    ("Epidemiology Map", "Division-level BD disease prevalence", "live"),
    ("Symptom Timeline", "Visual onset → today → recovery", "live"),
    ("Treatment Cost Estimate", "BDT cost card per triage tier", "live"),
    ("MCP Server", "3 tools over stdio for agent orchestration", "live"),
    ("WhatsApp / Telegram Bot", "Webhook server (FastAPI + uvicorn)", "planned"),
    ("ONNX Export", "Cross-platform inference without PyTorch", "planned"),
]

header_cols = st.columns([3, 3, 1])
header_cols[0].markdown("**Feature**")
header_cols[1].markdown("**Implementation**")
header_cols[2].markdown("**Status**")
st.markdown('<div style="border-top:1px solid #1e3a5f;margin:4px 0 8px 0"></div>', unsafe_allow_html=True)

for name, impl, status in features:
    c1, c2, c3 = st.columns([3, 3, 1])
    c1.markdown(f"<span style='color:#e2e8f0;font-size:0.88rem'>{name}</span>", unsafe_allow_html=True)
    c2.markdown(f"<span style='color:#64748b;font-size:0.82rem'>{impl}</span>", unsafe_allow_html=True)
    pill = "pill-live" if status == "live" else "pill-planned"
    label = "✅ Live" if status == "live" else "🔜 Planned"
    c3.markdown(f'<span class="feature-pill {pill}">{label}</span>', unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)


# ── 8. TECH STACK ─────────────────────────────────────────────────────────────
section("🔧 Technology Stack", "tech-stack")
c1, c2 = st.columns(2)

stack_left = [
    ("Frontend", "Streamlit 1.54 · Custom Bengali CSS · Noto Sans Bengali"),
    ("Vision Model", "Swin Transformer Base · CBAM · timm 1.0.27"),
    ("Quantization", "torch.quantization.quantize_dynamic (INT8)"),
    ("ASR", "faster-whisper (Whisper Base) · CTranslate2 INT8"),
    ("LLM / API", "Gemini 2.5 Flash · google-genai 1.63.0"),
    ("RAG Retrieval", "FAISS IndexFlatIP · BM25 keyword fallback"),
    ("Embeddings", "intfloat/multilingual-e5-small"),
]
stack_right = [
    ("PDF", "fpdf2 + uharfbuzz (HarfBuzz Bengali shaping)"),
    ("Hospital Map", "Overpass API · Folium · streamlit-folium"),
    ("TTS", "gTTS (Bengali audio readout)"),
    ("MCP Server", "FastMCP · mcp>=1.0.0 · stdio transport"),
    ("Keepalive", "GitHub Actions · cron */20 * * * *"),
    ("Infra", "HF Spaces CPU Basic · Docker"),
    ("Testing", "pytest · 310+ tests across 10 files"),
    ("Local LLM", "Ollama · Qwen 2.5 Coder (dev)"),
]

with c1:
    for layer, value in stack_left:
        st.markdown(f"""<div class="stack-row">
        <span class="stack-layer">{layer}</span>
        <span class="stack-value">{value}</span>
        </div>""", unsafe_allow_html=True)

with c2:
    for layer, value in stack_right:
        st.markdown(f"""<div class="stack-row">
        <span class="stack-layer">{layer}</span>
        <span class="stack-value">{value}</span>
        </div>""", unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)


# ── 9. TRIAGE LOGIC ───────────────────────────────────────────────────────────
section("⚖️ Clinical Triage Logic", "triage")
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("""<div class="card" style="border-top:3px solid #4ade80">
    <h3 style="color:#4ade80">Tier 1 — NON-URGENT</h3>
    <p>Contact Dermatitis · Seborrheic Dermatitis · Tinea<br/><br/>
    <strong style="color:#4ade80">Action:</strong> Consult pharmacist within 3–5 days<br/>
    <strong style="color:#4ade80">Cost:</strong> ৳50–200 (OTC)<br/>
    <strong style="color:#4ade80">Facility:</strong> Local Pharmacy</p>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown("""<div class="card" style="border-top:3px solid #fb923c">
    <h3 style="color:#fb923c">Tier 2 — ROUTINE</h3>
    <p>Atopic Dermatitis · Eczema · Scabies · Vitiligo<br/><br/>
    <strong style="color:#fb923c">Action:</strong> Visit Upazila Health Complex within 48h<br/>
    <strong style="color:#fb923c">Cost:</strong> ৳0–100 (subsidised)<br/>
    <strong style="color:#fb923c">Facility:</strong> Upazila Health Complex</p>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown("""<div class="card" style="border-top:3px solid #f87171">
    <h3 style="color:#f87171">Tier 3 — URGENT</h3>
    <p>Low confidence · Bengali escalation keywords<br/><br/>
    <strong style="color:#f87171">Action:</strong> Emergency care TODAY<br/>
    <strong style="color:#f87171">Cost:</strong> ৳0–500 (emergency)<br/>
    <strong style="color:#f87171">Facility:</strong> District Hospital + Map</p>
    </div>""", unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)


# ── 10. BUSINESS MODEL ───────────────────────────────────────────────────────
section("💼 Business Model", "business")
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("""<div class="card">
    <h3>🆓 Freemium (B2C)</h3>
    <p>5 free screenings per month → 150 BDT/month unlimited.
    Target: rural patients with smartphone access. Zero barrier to entry.</p>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown("""<div class="card">
    <h3>🏥 Institutional (B2B)</h3>
    <p>White-label licensing to Upazila Health Complexes, NGOs (BRAC, icddr,b),
    and community health worker programmes at district level.</p>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown("""<div class="card">
    <h3>🌐 Market Size</h3>
    <p>170M population · 80% rural (136M) · Growing smartphone penetration ·
    DGHS telemedicine push post-COVID. TAM: rural primary health market.</p>
    </div>""", unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)


# ── 11. TEAM ─────────────────────────────────────────────────────────────────
section("👥 Team", "team")

team = [
    ("Rafiur Rahman", "Team Leader · Backend / AI Engineer", "mdrafiurrahman123098@gmail.com", "R", True),
    ("MD. Farhad Hossain Ovi", "Business Analyst / Data Scientist", "farhad@example.com", "F", False),
    ("Miftahul Alam", "Business Analyst / Data Scientist", "miftahul@example.com", "M", False),
    ("Ankon Sinha", "Presentation / Communication Lead", "ankon@example.com", "A", False),
    ("Arif Hussain", "Presentation / Communication Lead", "arif@example.com", "AH", False),
    ("Syeda Maisha Anika", "UI/UX Frontend Developer", "maisha@example.com", "S", False),
]

cols = st.columns(3)
for i, (name, role, email, initial, is_leader) in enumerate(team):
    with cols[i % 3]:
        leader_class = "team-card team-leader" if is_leader else "team-card"
        leader_badge = '<span style="background:#00d4ff;color:#0B1929;font-size:0.7rem;font-weight:700;padding:2px 8px;border-radius:999px;margin-left:6px">LEADER</span>' if is_leader else ""
        st.markdown(f"""<div class="{leader_class}" style="margin-bottom:16px">
        <div class="team-avatar">{initial}</div>
        <div class="team-name">{name}{leader_badge}</div>
        <div class="team-role">{role}</div>
        <div class="team-email">{email}</div>
        </div>""", unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)


# ── 12. ROADMAP ──────────────────────────────────────────────────────────────
section("🗺️ Product Roadmap", "roadmap")
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("""<div class="card">
    <h3>✅ Phase 1 — Done</h3>
    <p>• BD-SkinNet INT8 training<br/>
    • 4-signal triage engine<br/>
    • Bengali voice pipeline<br/>
    • RAG chatbot (CDC/NIH/WHO/DGHS)<br/>
    • Emergency hospital map<br/>
    • PDF referral letter<br/>
    • Doctor booking + video call<br/>
    • MCP server (3 tools)<br/>
    • 310+ automated tests</p>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown("""<div class="card">
    <h3>🔜 Phase 2 — Next</h3>
    <p>• WhatsApp / Telegram bot<br/>
    • ONNX cross-platform export<br/>
    • Offline PWA for zero-connectivity<br/>
    • Multi-image analysis (lesion tracking)<br/>
    • CHW field app (Android APK)<br/>
    • Expanded to 20+ disease classes<br/>
    • DGHS API integration</p>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown("""<div class="card">
    <h3>🌟 Phase 3 — Vision</h3>
    <p>• National deployment via DGHS<br/>
    • Partnership with icddr,b / BRAC<br/>
    • Federated learning across hospitals<br/>
    • Multi-language (Chittagonian dialect)<br/>
    • Pediatric dermatology module<br/>
    • Real-time teledermatology handoff</p>
    </div>""", unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)


# ── 13. SECURITY & SAFETY ────────────────────────────────────────────────────
section("🔒 Safety, Guardrails & Privacy", "security")
c1, c2 = st.columns(2)
with c1:
    st.markdown("""<div class="card">
    <h3>Clinical Safety Constraints</h3>
    <p>• Medicine-name redaction regex (dosages, drug-class suffixes, Bengali medication terms)<br/>
    • Low-confidence hard-override → Tier 3 URGENT (&lt;40% confidence)<br/>
    • Gemini prompt: "Do NOT diagnose. Do NOT prescribe."<br/>
    • Bilingual disclaimer in every PDF referral<br/>
    • Triage + referral ONLY — never treatment advice</p>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown("""<div class="card">
    <h3>Privacy by Design</h3>
    <p>• Zero persistent storage — session_state only<br/>
    • No login, no user accounts, no PII collected<br/>
    • No audio sent to external API (local Whisper inference)<br/>
    • Knowledge base: vetted sources only (no open web)<br/>
    • DermNet explicitly excluded (AI-generated images)</p>
    </div>""", unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)


# ── 14. LINKS ────────────────────────────────────────────────────────────────
section("🔗 Links", "links")
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.link_button("🚀 Live App", "https://huggingface.co/spaces/rafilovestosuffer/skinai-bangladesh", use_container_width=True)
with c2:
    st.link_button("💻 GitHub", "https://github.com/rafilovestosuffer/Hackathon_2.0_sci", use_container_width=True)
with c3:
    st.link_button("🤗 HF Space", "https://huggingface.co/spaces/rafilovestosuffer/skinai-bangladesh", use_container_width=True)
with c4:
    st.link_button("📋 Competition", "https://sciblitz.ieee-sbcuet.org", use_container_width=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:32px 0 16px;color:#334155;font-size:0.8rem">
    SkinAI Bangladesh · SciBlitz AI Challenge 2026 · IEEE SB CUET · Track A: Health & Society<br/>
    <span style="font-family:'Noto Sans Bengali',sans-serif">⚕️ এই সিস্টেম রোগ নির্ণয় বা চিকিৎসার বিকল্প নয় — শুধুমাত্র ট্রাইয়েজ ও রেফারেল নির্দেশিকা।</span>
</div>
""", unsafe_allow_html=True)
