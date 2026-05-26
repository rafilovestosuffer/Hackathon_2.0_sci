# UI OVERHAUL — 2026-05-20
"""
ui/styles.py — Championship-grade medical CSS for SkinAI Bangladesh.
Call inject_css() once at app startup (top of app.py).
"""

import streamlit as st

# ── Design tokens (imported by components.py) ────────────────────────────────
PRIMARY       = "#1A6FA8"   # medical trust blue
TEAL          = "#0D9E75"   # health accent teal
ALERT_RED     = "#C0392B"   # Tier 3 urgent
AMBER         = "#E67E22"   # Tier 2 warning
SUCCESS       = "#27AE60"   # Tier 1 success
BG_PAGE       = "#F8FAFC"   # off-white clinical
CARD_BG       = "#FFFFFF"
BORDER_COLOR  = "#E2E8F0"
TEXT_DARK     = "#1A202C"
TEXT_MID      = "#4A5568"
TEXT_LIGHT    = "#718096"

# Legacy aliases — keep so components.py imports don't break
PRIMARY_LIGHT = "#E8F4FD"
TIER1_BG      = "#D5F5E3"
TIER1_BORDER  = SUCCESS
TIER1_TEXT    = "#1E8449"
TIER2_BG      = "#FDEBD0"
TIER2_BORDER  = AMBER
TIER2_TEXT    = "#A04000"
TIER3_BG      = "#FADBD8"
TIER3_BORDER  = ALERT_RED
TIER3_TEXT    = "#922B21"


def inject_css() -> None:
    """Inject full medical-grade CSS. Call once at app startup."""
    st.markdown(
        """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Bengali:wght@400;500;600;700&family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">

<style>
/* ─── CSS Custom Properties — refined clinical SaaS palette ────────────────── */
:root {
  --c-primary:  #0B4F6C;   /* deep medical navy — anchors the brand */
  --c-primary-2:#0F6E8C;   /* primary hover / lighter accent */
  --c-teal:     #10B981;   /* single emerald accent */
  --c-red:      #DC2626;
  --c-amber:    #F59E0B;
  --c-green:    #10B981;
  --c-bg:       #F1F5F9;   /* refined slate canvas */
  --c-bg-2:     #F8FAFC;
  --c-card:     #FFFFFF;
  --c-border:   #E5EAF0;   /* hairline, cooler */
  --c-border-2: #EEF2F6;   /* even softer for inner separators */
  --c-t1:       #0F172A;   /* slate-900 — premium ink */
  --c-t2:       #475569;   /* slate-600 */
  --c-t3:       #94A3B8;   /* slate-400 */
  --r-card:     14px;
  --shadow:     0 1px 2px rgba(15,23,42,0.04), 0 1px 1px rgba(15,23,42,0.03);
  --shadow-md:  0 4px 14px rgba(15,23,42,0.06), 0 1px 3px rgba(15,23,42,0.04);
  --shadow-lg:  0 10px 30px rgba(15,23,42,0.08), 0 2px 6px rgba(15,23,42,0.04);
}

/* ─── Global font & background ─────────────────────────────────────────────── */
html, body, [class*="css"] {
  font-family: 'Inter', 'Noto Sans Bengali', sans-serif !important;
  color: var(--c-t1) !important;
}

/* Premium clinical canvas — restrained slate with a single navy wash on
   the top edge and a hairline dot-grid for depth. No color blobs. */
.stApp {
  background:
    radial-gradient(ellipse 80% 50% at 50% -10%,
      rgba(11,79,108,0.10) 0%, transparent 60%),
    radial-gradient(circle at 1px 1px, rgba(15,23,42,0.045) 1px, transparent 0),
    linear-gradient(180deg, #F1F5F9 0%, #F8FAFC 100%) !important;
  background-size: auto, 22px 22px, auto !important;
  min-height: 100vh;
}

/* Main container — slate canvas so white cards visibly elevate.
   High specificity to defeat the override in app.py. */
.main .block-container,
[data-testid="stAppViewContainer"] .main .block-container,
[data-testid="stAppViewContainer"] section.main .block-container {
  padding-top: 1.8rem !important;
  padding-bottom: 3.5rem !important;
  padding-left: 2rem !important;
  padding-right: 2rem !important;
  background: #EEF2F7 !important;          /* DISTINCT slate — cards must POP */
  border-radius: 18px !important;
  border: 1px solid #D9E0E8 !important;
  box-shadow:
    0 1px 2px rgba(15,23,42,0.04),
    0 12px 36px rgba(15,23,42,0.08) !important;
  margin-top: 1.2rem !important;
  margin-bottom: 1.5rem !important;
  position: relative;
  z-index: 1;
}

/* ─── Hide Streamlit chrome ─────────────────────────────────────────────────── */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
[data-testid="stToolbar"] { display: none !important; }
header[data-testid="stHeader"] { background: transparent !important; box-shadow: none !important; }

/* ─── Custom scrollbar ──────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--c-teal); border-radius: 99px; }

/* ─── Sidebar ───────────────────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
  background: #0B1929 !important;
}
section[data-testid="stSidebar"] > div { padding-top: 0.75rem; }
section[data-testid="stSidebar"] * {
  color: #CBD5E1 !important;
  font-family: 'Inter', 'Noto Sans Bengali', sans-serif !important;
}
section[data-testid="stSidebar"] hr { border-color: #1E3A5F !important; margin: 0.5rem 0; }

.sidebar-logo {
  font-size: 1.35rem;
  font-weight: 800;
  color: #60B8E8 !important;
  text-align: center;
  padding: 0.2rem 0 0.05rem 0;
  letter-spacing: -0.02em;
}
.sidebar-tagline {
  font-size: 0.72rem;
  color: #4A6080 !important;
  text-align: center;
  margin-bottom: 0.65rem;
  font-style: italic;
  font-family: 'Noto Sans Bengali', sans-serif !important;
}
.sidebar-stat {
  background: #132236;
  border-radius: 8px;
  padding: 0.4rem 0.7rem;
  margin: 0.2rem 0;
  font-size: 0.78rem;
  color: #94A3B8 !important;
}
.sidebar-stat strong { color: #60B8E8 !important; }

/* Sidebar expander override */
section[data-testid="stSidebar"] [data-testid="stExpander"] {
  background: #132236;
  border: 1px solid #1E3A5F;
  border-radius: 8px;
}
section[data-testid="stSidebar"] [data-testid="stExpander"] summary {
  color: #94A3B8 !important;
  font-size: 0.8rem;
}

/* ─── Pipeline steps ────────────────────────────────────────────────────────── */
.pipeline-step {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  padding: 0.42rem 0.7rem;
  border-radius: 8px;
  margin: 0.18rem 0;
  font-size: 0.76rem;
  background: #132236;
  border: 1px solid transparent;
  transition: all 0.25s;
}
.pipeline-step.done   { border-color: var(--c-teal); background: #0A2018; color: #34D399 !important; }
.pipeline-step.active { border-color: var(--c-primary); background: #0D1F35; color: #60B8E8 !important;
                        animation: pulse-step 2s ease-in-out infinite; }
.pipeline-step.pending { color: #3D5166 !important; }
.pipeline-dot {
  width: 18px; height: 18px; border-radius: 50%; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.6rem; font-weight: 700;
}
.pipeline-dot.done   { background: var(--c-teal); color: white; }
.pipeline-dot.active { background: var(--c-primary); color: white; }
.pipeline-dot.pending { border: 2px solid #2D4560; }
@keyframes pulse-step {
  0%,100% { box-shadow: 0 0 0 0 rgba(13,158,117,0.35); }
  50%     { box-shadow: 0 0 0 5px rgba(13,158,117,0); }
}

/* ─── Source pills (sidebar) ────────────────────────────────────────────────── */
.source-pill {
  display: inline-block;
  background: #1E3A5F;
  color: #60B8E8 !important;
  font-size: 0.62rem;
  font-weight: 700;
  border-radius: 99px;
  padding: 0.12rem 0.5rem;
  margin: 0.12rem 0.08rem;
  letter-spacing: 0.04em;
}

/* Stat card (inside expander) */
.stat-card-sb {
  background: #0B1929;
  border: 1px solid #1E3A5F;
  border-radius: 8px;
  padding: 0.55rem 0.75rem;
  margin: 0.25rem 0;
  text-align: center;
}
.stat-card-sb-label {
  font-size: 0.62rem;
  font-weight: 600;
  color: #4A6080 !important;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  margin-bottom: 0.15rem;
}
.stat-card-sb-value {
  font-size: 1.25rem;
  font-weight: 800;
  color: #60B8E8 !important;
  line-height: 1.15;
}

/* ─── Tab bar — segmented control, premium SaaS feel ────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
  background: var(--c-bg);
  border-radius: 12px;
  border: 1px solid var(--c-border);
  padding: 4px;
  gap: 2px;
  box-shadow: none;
  display: flex;
  width: 100%;
}
.stTabs [data-baseweb="tab"] {
  font-family: 'Inter', 'Noto Sans Bengali', sans-serif !important;
  font-weight: 500;
  font-size: 0.86rem;
  padding: 0.6rem 0;
  color: var(--c-t2) !important;
  border: none !important;
  border-radius: 8px;
  background: transparent !important;
  flex: 1;
  text-align: center;
  transition: color 0.15s ease, background 0.15s ease;
  cursor: pointer;
  white-space: nowrap;
  letter-spacing: -0.005em;
}
.stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) {
  color: var(--c-primary) !important;
  background: rgba(11,79,108,0.04) !important;
}
.stTabs [aria-selected="true"] {
  color: var(--c-primary) !important;
  font-weight: 600 !important;
  background: #FFFFFF !important;
  box-shadow: 0 1px 3px rgba(15,23,42,0.06), 0 0 0 1px var(--c-border) !important;
  border: none !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.4rem; }

/* ─── Hero banner ───────────────────────────────────────────────────────────── */
.hero-banner {
  background: linear-gradient(135deg, #0B1929 0%, #1A3A5C 52%, #0A2E22 100%);
  border-radius: 18px;
  padding: 2.2rem 2.6rem 2rem 2.6rem;
  margin-bottom: 1.4rem;
  position: relative;
  overflow: hidden;
  text-align: center;
  box-shadow:
    0 12px 40px rgba(0,0,0,0.32),
    0 2px 8px rgba(0,0,0,0.15),
    inset 0 1px 0 rgba(255,255,255,0.06);
}
.hero-glow {
  position: absolute; top: -35%; right: -6%;
  width: 560px; height: 560px; border-radius: 50%;
  background: radial-gradient(ellipse, rgba(13,158,117,0.24) 0%, transparent 65%);
  pointer-events: none;
}
.hero-glow-2 {
  position: absolute; bottom: -55%; left: -5%;
  width: 400px; height: 400px; border-radius: 50%;
  background: radial-gradient(ellipse, rgba(26,111,168,0.18) 0%, transparent 62%);
  pointer-events: none;
}
.hero-title {
  font-size: 2.85rem;
  font-weight: 800;
  color: #FFFFFF !important;
  letter-spacing: -0.04em;
  line-height: 1.05;
  margin-bottom: 0.55rem;
  border-bottom: none;
  padding-bottom: 0;
}
.hero-subtitle {
  font-size: 0.88rem;
  color: #94A3B8 !important;
  max-width: 520px;
  margin: 0 auto 1.8rem auto;
  line-height: 1.55;
}
.hero-tagline-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0;
  flex-wrap: wrap;
  margin-bottom: 1.9rem;
}
.hero-step {
  background: rgba(255,255,255,0.07);
  border: 1px solid rgba(255,255,255,0.11);
  border-radius: 10px;
  padding: 0.55rem 1.25rem;
  min-width: 118px;
  font-family: 'Noto Sans Bengali', sans-serif !important;
  font-size: 0.98rem;
  font-weight: 600;
  color: #E2E8F0 !important;
  line-height: 1.25;
}
.hero-step small {
  display: block;
  font-size: 0.62rem;
  color: #64748B !important;
  font-family: 'Inter', sans-serif !important;
  font-weight: 400;
  margin-top: 0.15rem;
  letter-spacing: 0.02em;
}
.hero-arrow {
  font-size: 1.2rem;
  color: #34D399 !important;
  margin: 0 0.55rem;
  font-weight: 700;
  flex-shrink: 0;
}
.stat-bar { display: flex; flex-wrap: wrap; gap: 0.5rem; justify-content: center; margin-bottom: 0; }
.stat-chip {
  border-radius: 99px;
  padding: 0.32rem 0.95rem;
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.01em;
  display: inline-flex; align-items: center; gap: 0.3rem;
}
.stat-chip-blue  { background: rgba(26,111,168,0.88);  color: #fff !important; border: 1px solid rgba(96,184,232,0.4); }
.stat-chip-green { background: rgba(39,174,96,0.88);   color: #fff !important; border: 1px solid rgba(52,211,153,0.4); }
.stat-chip-teal  { background: rgba(13,158,117,0.88);  color: #fff !important; border: 1px solid rgba(52,211,153,0.4); }
.stat-chip-dark  { background: rgba(45,55,72,0.88);    color: #fff !important; border: 1px solid rgba(148,163,184,0.3); }

/* ─── Generic card ──────────────────────────────────────────────────────────── */
.card {
  background: var(--c-card);
  border: 1px solid var(--c-border);
  border-radius: var(--r-card);
  padding: 1.25rem 1.5rem;
  box-shadow: var(--shadow);
  margin-bottom: 1rem;
}
.sk-card {
  background: var(--c-card);
  border: 1px solid var(--c-border);
  border-radius: var(--r-card);
  padding: 1.25rem 1.5rem;
  box-shadow: var(--shadow);
  margin-bottom: 1rem;
}
.sk-card-title  { font-size: 0.72rem; font-weight: 700; color: var(--c-t3); text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.35rem; }
.sk-card-value  { font-size: 1.5rem; font-weight: 700; color: var(--c-t1); line-height: 1.2; }
.sk-card-sub    { font-size: 0.8rem; color: var(--c-t2); margin-top: 0.2rem; }

/* Card header row */
.card-section-header {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
  margin-bottom: 0.9rem;
  padding-bottom: 0.55rem;
  border-bottom: 1.5px solid var(--c-border);
}
.card-section-title { font-size: 1.05rem; font-weight: 700; color: var(--c-t1); }
.card-section-sub   { font-size: 0.75rem; color: var(--c-t3); font-weight: 400; }

/* ─── Professional typography hierarchy (use these instead of inline styles) ─── */
.sk-section-h2 {
  font-size: 1.08rem;
  font-weight: 700;
  color: var(--c-t1);
  letter-spacing: -0.005em;
  margin: 0 0 0.25rem 0;
  line-height: 1.3;
}
.sk-section-h3 {
  font-size: 0.78rem;
  font-weight: 600;
  color: #64748B;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin: 1rem 0 0.4rem 0;
}
.sk-meta {
  font-size: 0.82rem;
  color: #64748B;
  font-weight: 400;
  line-height: 1.5;
}
.sk-meta-bn {
  font-size: 0.78rem;
  color: #94A3B8;
  font-weight: 400;
  margin-top: 0.15rem;
  display: block;
  font-family: 'Noto Sans Bengali', 'Inter', sans-serif;
}

/* ─── Columns as cards — premium white cards on slate canvas ───────────────── */
[data-testid="stHorizontalBlock"] > [data-testid="column"],
[data-testid="stHorizontalBlock"] > div[data-testid="column"],
div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
  background: #FFFFFF !important;
  border: 1px solid #DDE3EB !important;
  border-radius: 14px !important;
  padding: 1.7rem 1.8rem 1.5rem 1.8rem !important;
  box-shadow:
    0 1px 3px rgba(15,23,42,0.06),
    0 10px 28px rgba(15,23,42,0.08) !important;
  margin: 0 0.4rem !important;
  position: relative;
  overflow: hidden;
}
/* Top brand accent stripe — full-bleed 4px gradient, clearly visible */
[data-testid="stHorizontalBlock"] > [data-testid="column"]::before,
[data-testid="stHorizontalBlock"] > div[data-testid="column"]::before {
  content: "";
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 4px;
  background: linear-gradient(90deg, #0B4F6C 0%, #0F6E8C 45%, #10B981 100%);
  z-index: 2;
}
/* Nested columns (e.g. the form's 2-col layout inside a card) — strip the
   card styling so we don't get cards-inside-cards. */
[data-testid="column"] [data-testid="stHorizontalBlock"] > [data-testid="column"] {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  padding: 0 0.4rem !important;
  margin: 0 !important;
  border-radius: 0 !important;
}
[data-testid="column"] [data-testid="stHorizontalBlock"] > [data-testid="column"]::before {
  display: none !important;
}

/* ─── Info boxes ────────────────────────────────────────────────────────────── */
.info-box {
  background: #EBF5FB;
  border: 1px solid #AED6F1;
  border-radius: 8px;
  padding: 0.6rem 0.9rem;
  font-size: 0.81rem;
  color: #1A5276;
  margin: 0.45rem 0;
  line-height: 1.5;
}
.info-box-teal {
  background: #E8F8F5;
  border: 1px solid #A9DFBF;
  border-left: 4px solid var(--c-teal);
  border-radius: 0 8px 8px 0;
  padding: 0.6rem 0.9rem;
  font-size: 0.81rem;
  color: #1E8449;
}
.info-source-pill {
  display: inline-block;
  background: #D5EEF7;
  color: #1A5276;
  font-size: 0.65rem;
  font-weight: 700;
  border-radius: 99px;
  padding: 0.1rem 0.55rem;
  margin: 0 0.15rem;
  letter-spacing: 0.04em;
}

/* ─── Transcript box ────────────────────────────────────────────────────────── */
.transcript-box {
  background: #F0FBF7;
  border-left: 5px solid var(--c-teal);
  border-top: 1px solid #A9DFBF;
  border-right: 1px solid #A9DFBF;
  border-bottom: 1px solid #A9DFBF;
  border-radius: 0 10px 10px 0;
  padding: 0.85rem 1.1rem;
  font-size: 0.92rem;
  color: #1A202C !important;
  font-weight: 500;
  font-family: 'Noto Sans Bengali', sans-serif !important;
  line-height: 1.65;
  margin: 0.45rem 0;
}

/* ─── History chips grid ────────────────────────────────────────────────────── */
.history-chip-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.45rem;
  margin-top: 0.5rem;
}
.history-chip {
  background: var(--c-bg);
  border: 1px solid var(--c-border);
  border-radius: 8px;
  padding: 0.38rem 0.65rem;
}
.history-chip-label {
  font-size: 0.62rem;
  font-weight: 700;
  color: var(--c-t3);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-bottom: 0.12rem;
}
.history-chip-value {
  font-size: 0.82rem;
  color: var(--c-t1);
  font-weight: 500;
  font-family: 'Noto Sans Bengali', sans-serif !important;
}

/* ─── Disease card ──────────────────────────────────────────────────────────── */
.disease-name-en {
  font-size: 1.6rem;
  font-weight: 800;
  color: var(--c-t1);
  margin-bottom: 0.05rem;
  letter-spacing: -0.02em;
}
.disease-name-bn {
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--c-primary);
  margin-bottom: 0.8rem;
  font-family: 'Noto Sans Bengali', sans-serif !important;
}
.conf-bar-wrap {
  background: var(--c-border);
  border-radius: 99px;
  height: 10px;
  margin: 0.4rem 0;
  overflow: hidden;
}
.conf-bar-fill {
  height: 10px;
  border-radius: 99px;
  transition: width 0.65s ease;
}
.conf-label {
  font-size: 0.78rem;
  color: var(--c-t2);
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.conf-value-mono {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 600;
  font-size: 0.85rem;
}
.conf-caption {
  font-size: 0.76rem;
  font-weight: 600;
  border-radius: 6px;
  padding: 0.18rem 0.62rem;
  margin-top: 0.42rem;
  display: inline-block;
  font-family: 'Noto Sans Bengali', sans-serif !important;
}
.conf-high { background: #D5F5E3; color: #1E8449; }
.conf-mid  { background: #FDEBD0; color: #A04000; }
.conf-low  { background: #FADBD8; color: #922B21; }
.differential-pill {
  display: inline-block;
  background: #EBF5FB;
  border: 1px solid #AED6F1;
  color: #1A5276;
  font-size: 0.74rem;
  border-radius: 99px;
  padding: 0.18rem 0.75rem;
  margin-top: 0.5rem;
  font-weight: 500;
}

/* ─── Confidence bar v2 (new component) ─────────────────────────────────────── */
.conf-bar-wrap-v2 {
  background: var(--c-border);
  border-radius: 99px;
  height: 13px;
  margin: 0.45rem 0;
  overflow: hidden;
}
.conf-bar-fill-v2 {
  height: 13px;
  border-radius: 99px;
  transition: width 0.8s ease;
}
.conf-label-v2 {
  font-size: 0.78rem;
  color: var(--c-t2);
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.18rem;
}

/* ─── Tier banners ──────────────────────────────────────────────────────────── */
.tier-banner {
  border-radius: var(--r-card);
  padding: 1.15rem 1.5rem;
  margin: 0.9rem 0;
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}
.tier-banner-0 {
  background: #E8FDF1;
  border-left: 6px solid #0D9E75;
  border-top: 1px solid #6FCFA5; border-right: 1px solid #6FCFA5; border-bottom: 1px solid #6FCFA5;
  box-shadow: 0 4px 20px rgba(13,158,117,0.15);
}
.tier-banner-1 {
  background: #F0FBF4;
  border-left: 5px solid #27AE60;
  border-top: 1px solid #A9DFBF; border-right: 1px solid #A9DFBF; border-bottom: 1px solid #A9DFBF;
}
.tier-banner-2 {
  background: #FEF9F0;
  border-left: 5px solid #E67E22;
  border-top: 1px solid #FAD7A0; border-right: 1px solid #FAD7A0; border-bottom: 1px solid #FAD7A0;
}
.tier-banner-3 {
  background: #FDF1F0;
  border-left: 6px solid #C0392B;
  border-top: 1px solid #F1948A; border-right: 1px solid #F1948A; border-bottom: 1px solid #F1948A;
  box-shadow: 0 4px 20px rgba(192,57,43,0.18);
  animation: pulse-urgent 2s ease-in-out infinite;
}
@keyframes pulse-urgent {
  0%,100% { box-shadow: 0 0 0 0 rgba(192,57,43,0.2); }
  50%     { box-shadow: 0 0 0 9px rgba(192,57,43,0); }
}
.tier-banner-icon { font-size: 2rem; line-height: 1; flex-shrink: 0; margin-top: 0.1rem; }
.tier-badge-pill {
  display: inline-block;
  font-size: 0.62rem;
  font-weight: 800;
  letter-spacing: 0.1em;
  border-radius: 99px;
  padding: 0.12rem 0.6rem;
  margin-bottom: 0.32rem;
}
.tier-badge-0 { background: #6FCFA5; color: #064E3B; }
.tier-badge-1 { background: #A9DFBF; color: #1E8449; }
.tier-badge-2 { background: #FAD7A0; color: #A04000; }
.tier-badge-3 { background: #F1948A; color: #922B21; }
.tier-urgency { font-size: 1.3rem; font-weight: 800; margin-bottom: 0.18rem; line-height: 1.2; }
.tier-urgency-0 { color: #064E3B; }
.tier-urgency-1 { color: #1E8449; }
.tier-urgency-2 { color: #A04000; }
.tier-urgency-3 { font-size: 1.45rem; color: #C0392B !important; }
.tier-action    { font-size: 0.88rem; font-weight: 500; color: var(--c-t2); }
.tier-action-bn {
  font-size: 0.88rem; font-weight: 600; margin-top: 0.18rem;
  font-family: 'Noto Sans Bengali', sans-serif !important;
}
.tier-action-bn-0 { color: #064E3B; font-weight: 700; }
.tier-action-bn-1 { color: #1E8449; }
.tier-action-bn-2 { color: #A04000; }
.tier-action-bn-3 { color: #922B21; font-weight: 700; }
.tier-facility { font-size: 0.72rem; color: var(--c-t3); margin-top: 0.28rem; font-weight: 500; }

/* Legacy badge classes (render_triage_badge compat) */
.badge-tier1 { background:#D5F5E3; border:2px solid #27AE60; color:#1E8449; border-radius:12px; padding:1rem 1.5rem; margin:0.75rem 0; }
.badge-tier2 { background:#FDEBD0; border:2px solid #E67E22; color:#A04000; border-radius:12px; padding:1rem 1.5rem; margin:0.75rem 0; }
.badge-tier3 { background:#FADBD8; border:2px solid #C0392B; color:#922B21; border-radius:12px; padding:1rem 1.5rem; margin:0.75rem 0; animation:pulse-urgent 1.8s ease-in-out infinite; }
.badge-label   { font-size:0.72rem; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; opacity:0.8; }
.badge-urgency { font-size:1.35rem; font-weight:700; margin:0.2rem 0; }
.badge-action, .badge-action-bn { font-size:0.9rem; margin-top:0.25rem; font-weight:500; }

/* ─── GradCAM ────────────────────────────────────────────────────────────────── */
.gradcam-caption {
  font-size: 0.73rem; color: var(--c-t3); text-align: center;
  margin-top: 0.35rem; font-style: italic;
  font-family: 'Noto Sans Bengali', sans-serif !important;
}
.coverage-wrap { background: var(--c-border); border-radius: 99px; height: 8px; overflow: hidden; }
.coverage-fill { height: 8px; border-radius: 99px; }

/* ─── Chat interface ─────────────────────────────────────────────────────────── */
.chat-outer-info {
  background: #EBF5FB;
  border: 1px solid #AED6F1;
  border-radius: 10px;
  padding: 0.65rem 1rem;
  font-size: 0.8rem;
  color: #1A5276;
  margin-bottom: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}
.chat-container {
  height: 490px;
  overflow-y: auto;
  border: 1px solid var(--c-border);
  border-radius: var(--r-card);
  padding: 1rem;
  background: var(--c-bg);
  margin-bottom: 0.6rem;
  scroll-behavior: smooth;
}
.chat-bubble-wrap-user { display: flex; justify-content: flex-end; margin-bottom: 0.8rem; }
.chat-bubble-wrap-ai   { display: flex; justify-content: flex-start; gap: 0.55rem; margin-bottom: 0.8rem; align-items: flex-start; }
.chat-bubble-user {
  background: var(--c-primary);
  color: white;
  border-radius: 18px 18px 4px 18px;
  padding: 0.6rem 1rem;
  max-width: 76%;
  font-size: 0.88rem;
  line-height: 1.55;
  box-shadow: 0 2px 6px rgba(26,111,168,0.22);
}
.chat-bubble-ai {
  background: var(--c-card);
  border: 1px solid var(--c-border);
  border-radius: 4px 18px 18px 18px;
  padding: 0.6rem 1rem;
  max-width: 76%;
  font-size: 0.88rem;
  line-height: 1.55;
  color: var(--c-t1);
  box-shadow: var(--shadow);
}
.ai-avatar {
  width: 28px; height: 28px; border-radius: 50%;
  background: linear-gradient(135deg, var(--c-primary), var(--c-teal));
  display: flex; align-items: center; justify-content: center;
  font-size: 0.6rem; font-weight: 800; color: white; flex-shrink: 0;
  margin-top: 2px;
}
.chat-source-chips { margin-top: 0.35rem; display: flex; gap: 0.22rem; flex-wrap: wrap; }
.chat-source-chip {
  background: #D5EEF7; color: #1A5276;
  font-size: 0.62rem; font-weight: 700;
  border-radius: 99px; padding: 0.08rem 0.45rem;
  letter-spacing: 0.03em;
}
.chat-empty {
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  height: 100%; color: var(--c-t3); text-align: center; gap: 0.45rem;
}
.chat-empty-icon { font-size: 2.5rem; }
.chat-empty-text { font-size: 0.88rem; font-family: 'Noto Sans Bengali', sans-serif !important; }

/* Suggested question buttons */
.stButton > button[data-testid*="sq_"] {
  background: var(--c-card) !important;
  border: 1.5px solid var(--c-teal) !important;
  color: var(--c-teal) !important;
  border-radius: 99px !important;
  font-size: 0.82rem !important;
}

/* ─── Section headings ───────────────────────────────────────────────────────── */
.sk-section-head {
  font-size: 0.98rem; font-weight: 700; color: var(--c-t1);
  border-bottom: 2px solid #EBF5FB;
  padding-bottom: 0.3rem; margin-bottom: 0.8rem;
}

/* ─── Referral preview ───────────────────────────────────────────────────────── */
.referral-section-card {
  background: var(--c-card);
  border-left: 4px solid var(--c-primary);
  border-top: 1px solid var(--c-border);
  border-right: 1px solid var(--c-border);
  border-bottom: 1px solid var(--c-border);
  border-radius: 0 12px 12px 0;
  padding: 1rem 1.3rem;
  margin-bottom: 0.65rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  display: flex; gap: 0.8rem; align-items: flex-start;
}
.referral-section-num {
  background: var(--c-primary); color: white;
  width: 26px; height: 26px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.72rem; font-weight: 700; flex-shrink: 0;
}
.referral-section-title {
  font-size: 0.68rem; font-weight: 700; color: var(--c-t3);
  text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.22rem;
}
.referral-section-content { font-size: 0.86rem; color: var(--c-t1); line-height: 1.5; }
.referral-section-content strong { color: var(--c-primary); }

/* Referral empty state */
.referral-empty {
  background: var(--c-card); border: 1.5px dashed var(--c-border);
  border-radius: var(--r-card); padding: 2.5rem 2rem; text-align: center;
}
.referral-progress-row {
  display: flex; align-items: center; gap: 0.75rem;
  padding: 0.55rem 1rem; border-radius: 10px;
  margin: 0.28rem auto; max-width: 320px;
  font-size: 0.8rem; color: var(--c-t2);
  font-family: 'Noto Sans Bengali', sans-serif !important;
}
.prog-dot {
  width: 28px; height: 28px; border-radius: 50%; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  border: 2px solid #CBD5E1; background: #F8FAFC; color: #A0AEC0;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.58rem;
}
.prog-dot-done { background: #27AE60 !important; border-color: #27AE60 !important; color: white !important; }
.prog-dot-next { background: var(--c-primary) !important; border-color: var(--c-primary) !important;
                 color: white !important; animation: pulse-step 2s ease-in-out infinite; }
.referral-progress-row.done-row { background: #F0FBF4; }
.referral-progress-row.next-row { background: #EBF5FB; font-weight: 600; }

/* ─── RAG answer ─────────────────────────────────────────────────────────────── */
.rag-answer-box {
  background: #F0FBF4; border-left: 4px solid var(--c-teal);
  border-radius: 0 10px 10px 0; padding: 1rem 1.25rem;
  font-size: 0.93rem; line-height: 1.65; color: var(--c-t1);
}
.rag-source-tag {
  display: inline-block; background: #D5F5E3; color: #1E8449;
  font-size: 0.7rem; font-weight: 600; border-radius: 99px;
  padding: 0.1rem 0.6rem; margin: 0.45rem 0.18rem 0 0;
}

/* ─── History table ──────────────────────────────────────────────────────────── */
.history-table { width: 100%; border-collapse: collapse; font-size: 0.86rem; }
.history-table tr:nth-child(even) td { background: #F8FAFC; }
.history-table td { padding: 0.42rem 0.72rem; border-bottom: 1px solid var(--c-border); vertical-align: top; }
.history-table td:first-child { font-weight: 600; color: var(--c-t2); width: 38%; white-space: nowrap; }
.history-table td:last-child  { color: var(--c-t1); }

/* ─── Buttons ────────────────────────────────────────────────────────────────── */
.stButton > button {
  font-family: 'Inter', 'Noto Sans Bengali', sans-serif !important;
  font-weight: 600; border-radius: 9px;
  background: var(--c-primary); color: white; border: 1px solid var(--c-primary);
  transition: background 0.15s, box-shadow 0.15s, transform 0.05s;
  letter-spacing: -0.005em;
  box-shadow: 0 1px 2px rgba(11,79,108,0.18);
}
.stButton > button:hover {
  background: var(--c-primary-2) !important;
  border-color: var(--c-primary-2) !important;
  box-shadow: 0 2px 8px rgba(11,79,108,0.22) !important;
}
.stButton > button:active { transform: translateY(0.5px); }
.stDownloadButton > button {
  font-family: 'Inter', 'Noto Sans Bengali', sans-serif !important;
  font-weight: 600 !important; border-radius: 10px !important;
  background: var(--c-teal) !important; color: white !important;
  border: 1px solid var(--c-teal) !important; font-size: 0.95rem !important;
  padding: 0.75rem 1.4rem !important; transition: all 0.15s;
  box-shadow: 0 1px 2px rgba(16,185,129,0.20);
  letter-spacing: -0.005em;
}
.stDownloadButton > button:hover {
  background: #0EA371 !important;
  border-color: #0EA371 !important;
  box-shadow: 0 2px 8px rgba(16,185,129,0.28) !important;
}

/* ─── File uploader — force light theme ─────────────────────────────────────── */
[data-testid="stFileUploaderDropzone"],
[data-testid="stFileUploadDropzone"] {
  background: var(--c-bg-2) !important;
  border: 1.5px dashed #BFD3DD !important;
  border-radius: 12px !important;
  color: var(--c-t2) !important;
  transition: border-color 0.2s, background 0.2s;
}
[data-testid="stFileUploaderDropzone"] > div,
[data-testid="stFileUploadDropzone"] > div {
  background: transparent !important;
}
[data-testid="stFileUploaderDropzone"]:hover,
[data-testid="stFileUploadDropzone"]:hover {
  background: #FFFFFF !important;
  border-color: var(--c-primary) !important;
}
[data-testid="stFileUploaderDropzone"] span,
[data-testid="stFileUploadDropzone"] span,
[data-testid="stFileUploaderDropzone"] p,
[data-testid="stFileUploadDropzone"] p {
  color: #4A5568 !important;
}
[data-testid="stFileUploaderDropzone"] small,
[data-testid="stFileUploadDropzone"] small {
  color: #718096 !important;
}
[data-testid="stFileUploaderDropzone"] button,
[data-testid="stFileUploadDropzone"] button {
  background: var(--c-primary) !important;
  color: white !important;
  border: none !important;
  border-radius: 8px !important;
  font-weight: 600 !important;
  padding: 0.4rem 1rem !important;
}
[data-testid="stFileUploaderDropzone"] button:hover,
[data-testid="stFileUploadDropzone"] button:hover {
  background: var(--c-primary-2) !important;
}
/* Audio input widget — minimal override only (waveform needs its own dark bg) */
[data-testid="stAudioInput"] { border-radius: 12px !important; overflow: hidden; }

/* ─── Image quality warning ──────────────────────────────────────────────────── */
.blur-warning {
  background: #FEFCE8; border: 1px solid #FCD34D;
  border-radius: 8px; padding: 0.48rem 0.82rem;
  font-size: 0.8rem; color: #92400E; margin-bottom: 0.45rem;
}

/* ─── Alerts ─────────────────────────────────────────────────────────────────── */
.stAlert { border-radius: 10px; font-family: 'Inter', 'Noto Sans Bengali', sans-serif !important; }

/* ─── Metric containers ──────────────────────────────────────────────────────── */
[data-testid="metric-container"] {
  background: white; border-radius: 12px;
  padding: 0.75rem 1rem; border: 1px solid var(--c-border); box-shadow: var(--shadow);
}

/* ─── App footer ─────────────────────────────────────────────────────────────── */
.sk-disclaimer {
  font-size: 0.68rem; color: var(--c-t3); font-style: italic;
  text-align: center; margin-top: 1.4rem;
  padding-top: 0.7rem; border-top: 1px solid var(--c-border);
}
.app-footer {
  font-size: 0.68rem; color: var(--c-t3); text-align: center;
  margin-top: 2rem; padding-top: 0.7rem; border-top: 1px solid var(--c-border);
  font-style: italic;
}

/* ─── Hospital cards ─────────────────────────────────────────────────────────── */
.hospital-card {
  background: var(--c-card); border: 1px solid var(--c-border);
  border-radius: 10px; padding: 0.7rem 1rem; margin-bottom: 0.45rem;
  display: flex; align-items: baseline; gap: 0.6rem;
}
.hospital-rank { font-weight: 800; color: var(--c-red); font-size: 0.95rem; flex-shrink: 0; }
.hospital-name { font-weight: 700; color: var(--c-t1); font-size: 0.9rem; }
.hospital-meta { font-size: 0.78rem; color: var(--c-t2); margin-top: 0.15rem; }

/* ─── Tab 1 — Diagnosis: premium clinical panel head ────────────────────────── */
.dx-panel-head {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  margin: -0.4rem 0 0.2rem 0;
  padding-bottom: 0.8rem;
  border-bottom: 1px solid var(--c-border-2);
}
.dx-step-badge {
  flex-shrink: 0;
  width: 32px; height: 32px;
  border-radius: 9px;
  background: #F0F7FA;
  color: var(--c-primary);
  border: 1px solid #D7E7EF;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 0.92rem;
  letter-spacing: -0.01em;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.7);
}
.dx-step-badge.dx-step-photo {
  background: #ECFDF5;
  color: #047857;
  border-color: #BBF7D0;
}
.dx-panel-titles { flex: 1; min-width: 0; }
.dx-panel-title-en {
  font-size: 1.02rem; font-weight: 650; color: var(--c-t1);
  letter-spacing: -0.015em; line-height: 1.25;
}
.dx-panel-title-bn {
  font-size: 0.74rem; color: var(--c-t3); font-weight: 500;
  font-family: 'Noto Sans Bengali', 'Inter', sans-serif !important;
  margin-top: 0.12rem;
  letter-spacing: 0;
}
.dx-panel-pill {
  flex-shrink: 0;
  font-size: 0.58rem; font-weight: 700; letter-spacing: 0.09em;
  padding: 0.24rem 0.65rem; border-radius: 6px;
  text-transform: uppercase;
  border: 1px solid transparent;
}
.dx-pill-required { background: #FEF2F2; color: #B91C1C; border-color: #FECACA; }
.dx-pill-optional { background: var(--c-bg); color: var(--c-t2); border-color: var(--c-border); }
.dx-panel-desc {
  font-size: 0.83rem; color: var(--c-t2);
  margin: 0.85rem 0 1rem 0; line-height: 1.6;
  letter-spacing: -0.005em;
}
.dx-divider {
  height: 1px;
  background: var(--c-border-2);
  margin: 1.4rem 0 1.2rem 0;
  border: none;
}

/* Quick-demo bar header — gold flash chip */
.dx-quickbar-head {
  display: inline-flex; align-items: center; gap: 0.5rem;
  font-size: 0.84rem; font-weight: 700; color: #1A202C;
  letter-spacing: -0.005em;
}
.dx-quickbar-flash {
  width: 22px; height: 22px; border-radius: 50%;
  background: linear-gradient(135deg, #FBBF24, #F59E0B);
  color: white; display: inline-flex; align-items: center; justify-content: center;
  font-size: 0.78rem; box-shadow: 0 2px 6px rgba(245,158,11,0.4);
  font-weight: 800;
}

/* Empty-state upload prompt — refined clinical card */
.dx-upload-empty {
  background: var(--c-bg-2);
  border: 1.5px dashed var(--c-border);
  border-radius: 14px;
  padding: 2.6rem 1.5rem;
  text-align: center;
  margin-top: 0.6rem;
}
.dx-upload-empty-icon {
  width: 54px; height: 54px;
  margin: 0 auto 0.7rem auto;
  border-radius: 12px;
  background: #FFFFFF;
  border: 1px solid var(--c-border);
  display: flex; align-items: center; justify-content: center;
  font-size: 1.6rem;
  box-shadow: var(--shadow);
}
.dx-upload-empty-title {
  font-size: 0.94rem; font-weight: 600; color: #334155;
  letter-spacing: -0.005em;
}
.dx-upload-empty-bn {
  font-size: 0.78rem; color: #94A3B8; margin-top: 0.3rem;
  font-family: 'Noto Sans Bengali', sans-serif !important;
}
.dx-upload-tips {
  display: flex; justify-content: center; gap: 1rem;
  margin-top: 0.95rem; font-size: 0.7rem; color: #64748B;
  flex-wrap: wrap;
}
.dx-upload-tips span {
  display: inline-flex; align-items: center; gap: 0.28rem;
  background: rgba(255,255,255,0.7);
  padding: 0.2rem 0.55rem; border-radius: 99px;
  border: 1px solid #E2E8F0;
}

/* Compact section sub-label for form groups */
.dx-form-sublabel {
  font-size: 0.64rem; font-weight: 800; color: #64748B;
  letter-spacing: 0.12em; text-transform: uppercase;
  margin: 0 0 0.55rem 0;
}

/* Mic + audio language row spacing inside the voice panel */
.dx-voice-hint {
  font-size: 0.74rem; color: #64748B;
  background: #F1F5F9; border: 1px solid #E2E8F0;
  border-radius: 8px; padding: 0.45rem 0.7rem;
  margin-top: 0.5rem; line-height: 1.5;
}

/* ─── Mobile ─────────────────────────────────────────────────────────────────── */
@media (max-width: 600px) {
  .main .block-container { padding-left: 0.65rem; padding-right: 0.65rem; }
  .hero-banner { padding: 1.8rem 1.4rem 1.6rem 1.4rem; border-radius: 16px; }
  .hero-title { font-size: 1.7rem; }
  .hero-subtitle { font-size: 0.8rem; }
  .hero-step { min-width: 90px; font-size: 0.85rem; padding: 0.45rem 0.8rem; }
  .hero-arrow { margin: 0 0.3rem; font-size: 1rem; }
  .stat-chip { font-size: 0.7rem; padding: 0.22rem 0.6rem; }
  [data-testid="stHorizontalBlock"] > [data-testid="column"] { padding: 0.75rem 0.85rem !important; }
  .tier-banner { flex-direction: column; gap: 0.4rem; }
  .tier-urgency { font-size: 1.05rem; }
  .tier-action, .tier-action-bn { font-size: 0.82rem; }
  .disease-name-en { font-size: 1.15rem; }
  .disease-name-bn { font-size: 0.92rem; }
  .stTabs [data-baseweb="tab"] { font-size: 0.72rem; padding: 0.5rem 0.2rem; }
  .history-table td { font-size: 0.78rem; }
  .chat-container { height: 360px; }
  .chat-bubble-user, .chat-bubble-ai { max-width: 90%; font-size: 0.84rem; }
  .history-chip-grid { grid-template-columns: 1fr; }
}
</style>
""",
        unsafe_allow_html=True,
    )
