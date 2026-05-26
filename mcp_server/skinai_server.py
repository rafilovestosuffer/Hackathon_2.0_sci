"""
mcp_server/skinai_server.py
SkinAI Bangladesh — MCP Server (stdio transport)

Exposes three production-grade tools over the Model Context Protocol:

  • triage_skin_condition  — 4-signal clinical triage engine
  • ask_skin_question      — Bengali/English RAG chatbot (BM25 + FAISS + Gemini)
  • find_emergency_hospitals — Overpass API hospital finder for Tier 3 emergencies

Usage
-----
  python -m mcp_server.skinai_server          # stdio (Claude Desktop / Cursor)

Compatible MCP clients: Claude Desktop, Cursor Composer, any MCP-compliant agent.
Transport: stdio (default). Streamable HTTP available via --transport http.

Environment
-----------
  GEMINI_API_KEY  — required for ask_skin_question (set in .env or shell)
"""

import os
import sys

# ── Ensure project root is on sys.path so module imports resolve correctly ──────
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from mcp.server.fastmcp import FastMCP

from severity.engine import compute_tier
from rag.retriever import answer_question, load_index
from map.hospital_finder import find_nearest_hospitals, get_district_coords

# ── Server bootstrap ─────────────────────────────────────────────────────────
mcp = FastMCP(
    name="SkinAI Bangladesh",
    instructions=(
        "SkinAI Bangladesh MCP server. "
        "Provides clinical skin-disease triage, a Bengali/English RAG medical chatbot, "
        "and emergency hospital lookup — all optimised for rural Bangladesh. "
        "Never diagnoses. Never prescribes. Triage and referral only."
    ),
)

# Pre-load the RAG knowledge index once at server startup
load_index()


# ── Tool 1: Triage engine ─────────────────────────────────────────────────────

@mcp.tool()
def triage_skin_condition(
    disease_class: str,
    confidence: float,
    coverage_pct: float,
    transcript: str = "",
) -> dict:
    """
    Run the SkinAI 4-signal clinical triage engine.

    Combines four independent signals to compute an urgency tier:
      Signal 1 — Disease class base tier (hardcoded clinical lookup)
      Signal 2 — Model confidence modifier  (<0.40 → Tier 3 regardless)
      Signal 3 — GradCAM++ lesion coverage  (>40 % → escalate one tier)
      Signal 4 — Bengali voice keywords     (জ্বর/ছড়িয়ে/ব্যথা/রক্ত → escalate)

    Returns
    -------
    dict with keys:
      tier          : int  — 1 (pharmacy), 2 (clinic), 3 (emergency)
      urgency_label : str  — "NON-URGENT" | "ROUTINE" | "URGENT"
      action        : str  — English action instruction
      facility      : str  — recommended facility type
      bengali_text  : str  — bilingual instruction in Bengali script

    Args
    ----
    disease_class : One of Atopic_Dermatitis, Contact_Dermatitis, Eczema, Scabies,
                    Seborrheic_Dermatitis, Tinea, Vitiligo, Normal
    confidence    : BD-SkinNet softmax confidence score  (0.0 – 1.0)
    coverage_pct  : GradCAM++ lesion coverage percentage (0.0 – 100.0)
    transcript    : Optional Bengali voice transcript for keyword escalation
    """
    return compute_tier(disease_class, confidence, coverage_pct, transcript)


# ── Tool 2: RAG chatbot ───────────────────────────────────────────────────────

@mcp.tool()
def ask_skin_question(
    question: str,
    language: str = "auto",
    disease_context: str = "",
) -> str:
    """
    Answer a dermatology question using the SkinAI RAG knowledge base.

    Knowledge sources (100 disease-specific chunks, no DermNet):
      CDC × 32  |  NIH × 32  |  WHO × 16  |  DGHS Bangladesh × 20

    Retrieval: BM25 keyword search (primary), FAISS semantic upgrade if index exists.
    Generation: Gemini 2.5 Flash with 3-retry and medicine-name redaction.

    Constraints enforced server-side:
      — Never recommends specific medication names or dosages
      — Never makes a diagnosis
      — Always refers to a licensed professional for treatment decisions

    Args
    ----
    question        : Patient question in Bengali (বাংলা) or English
    language        : "bn" = force Bengali reply  |  "en" = force English
                      "auto" = detect from question script/keywords (default)
    disease_context : Active BD-SkinNet diagnosis to ground the answer, e.g.
                      "Tinea Corporis (Confidence: 82%)"
    """
    lang = None if language == "auto" else language
    ctx = disease_context.strip() if disease_context else None
    return answer_question(question, lang=lang, disease_context=ctx)


# ── Tool 3: Emergency hospital finder ────────────────────────────────────────

@mcp.tool()
def find_emergency_hospitals(
    district: str,
    max_results: int = 5,
) -> list[dict]:
    """
    Find the nearest emergency hospitals for a Bangladesh district.

    Designed for Tier 3 (URGENT) triage results only.

    Data source: OpenStreetMap Overpass API (no API key required).
    Fallback:    DGHS static division-level hospital list (always returns results).
    Distance:    Haversine formula from district headquarters coordinates.

    Supports 64 Bangladesh districts. Common names accepted (e.g. "chittagong"
    and "chattogram" both resolve correctly).

    Args
    ----
    district    : Bangladesh district name, case-insensitive
                  e.g. "rangpur", "dhaka", "chittagong", "cox's bazar"
    max_results : Maximum hospitals to return, sorted by distance (default 5)

    Returns
    -------
    List of dicts: [{name, address, distance_km, phone}]
    Returns [{error: ...}] if district name is not recognised.
    """
    coords = get_district_coords(district)
    if coords is None:
        return [{
            "error": (
                f"District '{district}' not recognised. "
                "Please use a valid Bangladesh district name, e.g. "
                "'rangpur', 'dhaka', 'chittagong', 'sylhet'."
            )
        }]

    lat, lon = coords
    hospitals = find_nearest_hospitals(lat, lon, n=max_results)

    return [
        {
            "name":        h["name"],
            "address":     h["address"],
            "distance_km": h["dist_km"],
            "phone":       h.get("phone", ""),
        }
        for h in hospitals
    ]


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(transport="stdio")
