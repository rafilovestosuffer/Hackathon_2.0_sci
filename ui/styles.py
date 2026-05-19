"""
ui/styles.py — Bengali Noto Sans font + professional medical CSS.
Call inject_css() once at app startup (top of app.py).
"""

import streamlit as st

# ── Design tokens ─────────────────────────────────────────────────────────────
PRIMARY       = "#1a56db"   # deep medical blue
PRIMARY_LIGHT = "#e8f0fe"
TEAL          = "#0e9f6e"   # health green
TIER1_BG      = "#d1fae5"   # soft green
TIER1_BORDER  = "#059669"
TIER1_TEXT    = "#065f46"
TIER2_BG      = "#fef3c7"   # soft amber
TIER2_BORDER  = "#d97706"
TIER2_TEXT    = "#92400e"
TIER3_BG      = "#fee2e2"   # soft red
TIER3_BORDER  = "#dc2626"
TIER3_TEXT    = "#991b1b"
CARD_BG       = "#f8fafc"
BORDER_COLOR  = "#e2e8f0"
TEXT_DARK     = "#1e293b"
TEXT_MID      = "#475569"
TEXT_LIGHT    = "#94a3b8"


def inject_css() -> None:
    """Inject Bengali font + full app CSS. Call once at Streamlit startup."""
    st.markdown(
        f"""
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Bengali:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">

        <style>
        /* ── Global font ──────────────────────────────────────────────── */
        html, body, [class*="css"] {{
            font-family: 'Noto Sans Bengali', 'Inter', sans-serif !important;
            color: {TEXT_DARK};
        }}
        .stApp {{
            background: #f1f5f9;
        }}
        .main .block-container {{
            padding-top: 1.5rem;
            padding-bottom: 2rem;
            max-width: 900px;
        }}

        /* ── Sidebar ──────────────────────────────────────────────────── */
        section[data-testid="stSidebar"] {{
            background: #0f172a;
        }}
        section[data-testid="stSidebar"] * {{
            color: #e2e8f0 !important;
            font-family: 'Noto Sans Bengali', 'Inter', sans-serif !important;
        }}
        section[data-testid="stSidebar"] hr {{
            border-color: #334155;
        }}
        section[data-testid="stSidebar"] .sidebar-logo {{
            font-size: 1.6rem;
            font-weight: 700;
            color: #60a5fa !important;
            text-align: center;
            padding: 0.5rem 0 0.25rem 0;
        }}
        section[data-testid="stSidebar"] .sidebar-tagline {{
            font-size: 0.78rem;
            color: #94a3b8 !important;
            text-align: center;
            margin-bottom: 1rem;
            font-style: italic;
        }}
        section[data-testid="stSidebar"] .sidebar-stat {{
            background: #1e293b;
            border-radius: 8px;
            padding: 0.5rem 0.75rem;
            margin: 0.3rem 0;
            font-size: 0.8rem;
            color: #cbd5e1 !important;
        }}
        section[data-testid="stSidebar"] .sidebar-stat strong {{
            color: #60a5fa !important;
        }}

        /* ── Tab bar ──────────────────────────────────────────────────── */
        .stTabs [data-baseweb="tab-list"] {{
            background: white;
            border-radius: 12px;
            padding: 4px;
            gap: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        }}
        .stTabs [data-baseweb="tab"] {{
            border-radius: 8px;
            font-family: 'Noto Sans Bengali', 'Inter', sans-serif !important;
            font-weight: 500;
            font-size: 0.95rem;
            padding: 0.5rem 1.2rem;
            color: {TEXT_MID} !important;
        }}
        .stTabs [aria-selected="true"] {{
            background: {PRIMARY} !important;
            color: white !important;
        }}

        /* ── Cards ────────────────────────────────────────────────────── */
        .sk-card {{
            background: white;
            border-radius: 14px;
            padding: 1.25rem 1.5rem;
            box-shadow: 0 1px 4px rgba(0,0,0,0.07);
            border: 1px solid {BORDER_COLOR};
            margin-bottom: 1rem;
        }}
        .sk-card-title {{
            font-size: 0.78rem;
            font-weight: 600;
            color: {TEXT_LIGHT};
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.4rem;
        }}
        .sk-card-value {{
            font-size: 1.6rem;
            font-weight: 700;
            color: {TEXT_DARK};
            line-height: 1.2;
        }}
        .sk-card-sub {{
            font-size: 0.82rem;
            color: {TEXT_MID};
            margin-top: 0.25rem;
        }}

        /* ── Triage badges ────────────────────────────────────────────── */
        .badge-tier1 {{
            background: {TIER1_BG};
            border: 2px solid {TIER1_BORDER};
            color: {TIER1_TEXT};
            border-radius: 12px;
            padding: 1rem 1.5rem;
            margin: 0.75rem 0;
        }}
        .badge-tier2 {{
            background: {TIER2_BG};
            border: 2px solid {TIER2_BORDER};
            color: {TIER2_TEXT};
            border-radius: 12px;
            padding: 1rem 1.5rem;
            margin: 0.75rem 0;
        }}
        .badge-tier3 {{
            background: {TIER3_BG};
            border: 2px solid {TIER3_BORDER};
            color: {TIER3_TEXT};
            border-radius: 12px;
            padding: 1rem 1.5rem;
            margin: 0.75rem 0;
            animation: pulse-border 1.8s ease-in-out infinite;
        }}
        @keyframes pulse-border {{
            0%, 100% {{ box-shadow: 0 0 0 0 rgba(220,38,38,0.25); }}
            50%       {{ box-shadow: 0 0 0 6px rgba(220,38,38,0); }}
        }}
        .badge-label {{
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            opacity: 0.8;
        }}
        .badge-urgency {{
            font-size: 1.35rem;
            font-weight: 700;
            margin: 0.2rem 0;
        }}
        .badge-action {{
            font-size: 0.9rem;
            margin-top: 0.25rem;
            font-weight: 500;
        }}
        .badge-action-bn {{
            font-size: 0.9rem;
            font-weight: 500;
            margin-top: 0.1rem;
            opacity: 0.85;
        }}

        /* ── Disease card ─────────────────────────────────────────────── */
        .disease-name-en {{
            font-size: 1.4rem;
            font-weight: 700;
            color: {TEXT_DARK};
            margin-bottom: 0.1rem;
        }}
        .disease-name-bn {{
            font-size: 1.1rem;
            font-weight: 600;
            color: {PRIMARY};
            margin-bottom: 0.75rem;
        }}
        .conf-bar-wrap {{
            background: {BORDER_COLOR};
            border-radius: 99px;
            height: 10px;
            margin: 0.4rem 0;
            overflow: hidden;
        }}
        .conf-bar-fill {{
            height: 10px;
            border-radius: 99px;
            transition: width 0.6s ease;
        }}
        .conf-label {{
            font-size: 0.8rem;
            color: {TEXT_MID};
            display: flex;
            justify-content: space-between;
        }}
        .differential-pill {{
            display: inline-block;
            background: #eff6ff;
            border: 1px solid #bfdbfe;
            color: #1d4ed8;
            font-size: 0.78rem;
            border-radius: 99px;
            padding: 0.15rem 0.75rem;
            margin-top: 0.5rem;
        }}

        /* ── History table ────────────────────────────────────────────── */
        .history-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.88rem;
        }}
        .history-table tr:nth-child(even) td {{
            background: #f8fafc;
        }}
        .history-table td {{
            padding: 0.45rem 0.75rem;
            border-bottom: 1px solid {BORDER_COLOR};
            vertical-align: top;
        }}
        .history-table td:first-child {{
            font-weight: 600;
            color: {TEXT_MID};
            width: 38%;
            white-space: nowrap;
        }}
        .history-table td:last-child {{
            color: {TEXT_DARK};
        }}

        /* ── RAG answer ───────────────────────────────────────────────── */
        .rag-answer-box {{
            background: #f0fdf4;
            border-left: 4px solid {TEAL};
            border-radius: 0 10px 10px 0;
            padding: 1rem 1.25rem;
            font-size: 0.95rem;
            line-height: 1.65;
            color: {TEXT_DARK};
        }}
        .rag-source-tag {{
            display: inline-block;
            background: #dcfce7;
            color: #166534;
            font-size: 0.72rem;
            font-weight: 600;
            border-radius: 99px;
            padding: 0.1rem 0.6rem;
            margin: 0.5rem 0.2rem 0 0;
        }}

        /* ── Coverage bar ─────────────────────────────────────────────── */
        .coverage-wrap {{
            background: {BORDER_COLOR};
            border-radius: 99px;
            height: 8px;
            margin: 0.3rem 0;
            overflow: hidden;
        }}
        .coverage-fill {{
            height: 8px;
            border-radius: 99px;
            background: linear-gradient(90deg, #6366f1, #a855f7);
        }}

        /* ── Section headings ─────────────────────────────────────────── */
        .sk-section-head {{
            font-size: 1rem;
            font-weight: 700;
            color: {TEXT_DARK};
            border-bottom: 2px solid {PRIMARY_LIGHT};
            padding-bottom: 0.35rem;
            margin-bottom: 0.85rem;
        }}

        /* ── Disclaimer footer ────────────────────────────────────────── */
        .sk-disclaimer {{
            font-size: 0.72rem;
            color: {TEXT_LIGHT};
            font-style: italic;
            text-align: center;
            margin-top: 1.5rem;
            padding-top: 0.75rem;
            border-top: 1px solid {BORDER_COLOR};
        }}

        /* ── Buttons ──────────────────────────────────────────────────── */
        .stButton > button {{
            font-family: 'Noto Sans Bengali', 'Inter', sans-serif !important;
            font-weight: 600;
            border-radius: 8px;
        }}
        .stDownloadButton > button {{
            font-family: 'Noto Sans Bengali', 'Inter', sans-serif !important;
            font-weight: 600;
            border-radius: 8px;
            background: {PRIMARY};
            color: white;
            border: none;
        }}
        .stDownloadButton > button:hover {{
            background: #1e40af;
        }}

        /* ── Metric ───────────────────────────────────────────────────── */
        [data-testid="metric-container"] {{
            background: white;
            border-radius: 12px;
            padding: 0.75rem 1rem;
            border: 1px solid {BORDER_COLOR};
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}

        /* ── Upload area ──────────────────────────────────────────────── */
        [data-testid="stFileUploadDropzone"] {{
            border-radius: 12px !important;
            border-color: {PRIMARY} !important;
        }}

        /* ── Info / warning / error boxes ─────────────────────────────── */
        .stAlert {{
            border-radius: 10px;
            font-family: 'Noto Sans Bengali', 'Inter', sans-serif !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
