"""
analytics/db.py
Anonymised usage analytics — SQLite, no patient data.

Records aggregate events (triage / rag / voice) for system monitoring
and /docs dashboard stats. Zero patient identifiers stored.

Schema
------
  events(id, ts, event_type, disease_class, tier, lang, rag_chunks, conf_bucket)

event_type values : "triage" | "rag" | "voice"
conf_bucket values: "high" (≥0.60) | "medium" (0.40–0.60) | "low" (<0.40)
"""
import datetime
import logging
import os
import sqlite3

logger = logging.getLogger(__name__)

_DB_PATH = os.path.join(os.path.dirname(__file__), "skinai_analytics.db")

_CREATE_SQL = """
CREATE TABLE IF NOT EXISTS events (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    ts            TEXT    NOT NULL,
    event_type    TEXT    NOT NULL,
    disease_class TEXT    DEFAULT '',
    tier          INTEGER DEFAULT 0,
    lang          TEXT    DEFAULT '',
    rag_chunks    INTEGER DEFAULT 0,
    conf_bucket   TEXT    DEFAULT ''
)
"""


def _get_conn() -> sqlite3.Connection:
    con = sqlite3.connect(_DB_PATH, check_same_thread=False)
    con.execute(_CREATE_SQL)
    con.commit()
    return con


def log_event(
    event_type: str,
    disease_class: str = "",
    tier: int = 0,
    lang: str = "",
    rag_chunks: int = 0,
    conf_bucket: str = "",
) -> None:
    """
    Append one anonymised event row.

    Never raises — analytics must never crash the main app.
    """
    try:
        con = _get_conn()
        con.execute(
            "INSERT INTO events "
            "(ts, event_type, disease_class, tier, lang, rag_chunks, conf_bucket) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                datetime.datetime.utcnow().isoformat(),
                event_type[:32],
                disease_class[:64],
                int(tier),
                lang[:8],
                int(rag_chunks),
                conf_bucket[:16],
            ),
        )
        con.commit()
        con.close()
    except Exception as exc:
        logger.debug("analytics.log_event skipped (non-critical): %s", exc)


def get_summary() -> dict:
    """
    Return aggregate counts for /docs dashboard live stats widget.
    Returns safe defaults on any error.
    """
    empty = {
        "total_triage": 0,
        "total_rag": 0,
        "total_voice": 0,
        "top_diseases": [],
        "tier_distribution": {},
    }
    try:
        con = _get_conn()
        cur = con.cursor()

        cur.execute("SELECT event_type, COUNT(*) FROM events GROUP BY event_type")
        counts = dict(cur.fetchall())

        cur.execute(
            "SELECT disease_class, COUNT(*) FROM events "
            "WHERE event_type='triage' AND disease_class != '' "
            "GROUP BY disease_class ORDER BY COUNT(*) DESC LIMIT 5"
        )
        top_diseases = cur.fetchall()

        cur.execute(
            "SELECT tier, COUNT(*) FROM events "
            "WHERE tier > 0 GROUP BY tier"
        )
        tier_dist = dict(cur.fetchall())

        con.close()
        return {
            "total_triage": counts.get("triage", 0),
            "total_rag":    counts.get("rag", 0),
            "total_voice":  counts.get("voice", 0),
            "top_diseases": top_diseases,
            "tier_distribution": tier_dist,
        }
    except Exception as exc:
        logger.debug("analytics.get_summary failed: %s", exc)
        return empty
