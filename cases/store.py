"""
cases/store.py
Consented case store for clinician review — SQLite, shared by the web app,
the Telegram/WhatsApp webhook and the /api endpoint (same container).

A case is written ONLY when the patient ticks / answers "yes" to sharing.
Stored: a ≤256 px lesion thumbnail (EXIF stripped), the AI output, the
triage reasons, red-flag answers and district. Never stored: name, phone,
voice transcript. Telegram chat ids are kept only until the doctor's
decision has been sent, then cleared. Everything older than RETENTION_DAYS
is deleted on every write.

Schema
------
  cases(id, created_ts, source, district, thumb_jpeg, ai_disease, ai_conf,
        ai_tier, reasons_json, red_flags_json, status, dr_disease, dr_tier,
        dr_note, dr_ts, notify_chat_id)
  audit(id, ts, case_id, action, from_tier, to_tier, actor)

status values: "pending" | "confirmed" | "overridden"
"""
from __future__ import annotations

import csv
import datetime
import io
import json
import logging
import os
import sqlite3
import uuid
from typing import Optional

from PIL import Image

logger = logging.getLogger(__name__)

_DB_PATH = os.environ.get(
    "SKINAI_CASES_DB", os.path.join(os.path.dirname(__file__), "cases.db"))
RETENTION_DAYS = 7
THUMB_MAX_PX = 256

_CREATE_SQL = [
    """
    CREATE TABLE IF NOT EXISTS cases (
        id             TEXT PRIMARY KEY,
        created_ts     TEXT NOT NULL,
        source         TEXT NOT NULL,
        district       TEXT DEFAULT '',
        thumb_jpeg     BLOB,
        ai_disease     TEXT NOT NULL,
        ai_conf        REAL NOT NULL,
        ai_tier        INTEGER NOT NULL,
        reasons_json   TEXT DEFAULT '[]',
        red_flags_json TEXT DEFAULT '[]',
        status         TEXT NOT NULL DEFAULT 'pending',
        dr_disease     TEXT,
        dr_tier        INTEGER,
        dr_note        TEXT,
        dr_ts          TEXT,
        notify_chat_id TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS audit (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        ts        TEXT NOT NULL,
        case_id   TEXT NOT NULL,
        action    TEXT NOT NULL,
        from_tier INTEGER,
        to_tier   INTEGER,
        actor     TEXT DEFAULT ''
    )
    """,
]

# Columns safe to export (no image, no chat id)
EXPORT_COLUMNS = [
    "id", "created_ts", "source", "district", "ai_disease", "ai_conf", "ai_tier",
    "red_flags_json", "status", "dr_disease", "dr_tier", "dr_ts",
]


def _now() -> str:
    return datetime.datetime.utcnow().isoformat(timespec="seconds")


def _get_conn() -> sqlite3.Connection:
    con = sqlite3.connect(_DB_PATH, check_same_thread=False, timeout=10)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    for sql in _CREATE_SQL:
        con.execute(sql)
    con.commit()
    return con


def make_thumbnail(image) -> Optional[bytes]:
    """Downscale to ≤256 px JPEG. Re-encoding from pixels drops EXIF/GPS."""
    try:
        if isinstance(image, (bytes, bytearray)):
            image = Image.open(io.BytesIO(image))
        img = image.convert("RGB")
        img.thumbnail((THUMB_MAX_PX, THUMB_MAX_PX))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=80)
        return buf.getvalue()
    except Exception as exc:
        logger.warning("thumbnail failed: %s", exc)
        return None


def purge_older_than(days: int = RETENTION_DAYS, con: Optional[sqlite3.Connection] = None) -> int:
    own = con is None
    con = con or _get_conn()
    cutoff = (datetime.datetime.utcnow() - datetime.timedelta(days=days)).isoformat(timespec="seconds")
    ids = [r["id"] for r in con.execute("SELECT id FROM cases WHERE created_ts < ?", (cutoff,))]
    if ids:
        con.executemany("DELETE FROM cases WHERE id = ?", [(i,) for i in ids])
        con.executemany("DELETE FROM audit WHERE case_id = ?", [(i,) for i in ids])
        con.commit()
    if own:
        con.close()
    return len(ids)


def add_case(
    *,
    consent: bool,
    source: str,
    image,
    ai_disease: str,
    ai_conf: float,
    ai_tier: int,
    reasons: Optional[list] = None,
    red_flags: Optional[list] = None,
    district: str = "",
    notify_chat_id: Optional[str] = None,
) -> Optional[str]:
    """Store a case for doctor review. Returns the case id, or None if not stored."""
    if not consent:
        return None
    case_id = uuid.uuid4().hex
    try:
        con = _get_conn()
        purge_older_than(con=con)
        con.execute(
            "INSERT INTO cases (id, created_ts, source, district, thumb_jpeg, ai_disease, "
            "ai_conf, ai_tier, reasons_json, red_flags_json, status, notify_chat_id) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?)",
            (
                case_id, _now(), source[:16], (district or "")[:64],
                make_thumbnail(image) if image is not None else None,
                ai_disease[:64], float(ai_conf), int(ai_tier),
                json.dumps(reasons or [], ensure_ascii=False),
                json.dumps(red_flags or [], ensure_ascii=False),
                str(notify_chat_id) if notify_chat_id else None,
            ),
        )
        con.execute(
            "INSERT INTO audit (ts, case_id, action, from_tier, to_tier, actor) "
            "VALUES (?, ?, 'created', NULL, ?, ?)",
            (_now(), case_id, int(ai_tier), source[:16]),
        )
        con.commit()
        con.close()
        return case_id
    except Exception as exc:
        logger.warning("add_case failed: %s", exc)
        return None


def _row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    d["reasons"] = json.loads(d.pop("reasons_json") or "[]")
    d["red_flags"] = json.loads(d.pop("red_flags_json") or "[]")
    return d


def get_case(case_id: str) -> Optional[dict]:
    try:
        con = _get_conn()
        row = con.execute("SELECT * FROM cases WHERE id = ?", (case_id,)).fetchone()
        con.close()
        return _row_to_dict(row) if row else None
    except Exception as exc:
        logger.warning("get_case failed: %s", exc)
        return None


def list_cases(status: Optional[str] = None) -> list[dict]:
    """Most urgent first: tier desc, then least confident, then oldest."""
    try:
        con = _get_conn()
        sql = "SELECT * FROM cases"
        args: tuple = ()
        if status:
            sql += " WHERE status = ?"
            args = (status,)
        sql += " ORDER BY ai_tier DESC, ai_conf ASC, created_ts ASC"
        rows = [_row_to_dict(r) for r in con.execute(sql, args)]
        con.close()
        return rows
    except Exception as exc:
        logger.warning("list_cases failed: %s", exc)
        return []


def decide(
    case_id: str,
    *,
    action: str,
    disease: str,
    tier: int,
    note: str = "",
    actor: str = "doctor",
) -> Optional[dict]:
    """Record the doctor's decision ("confirmed" or "overridden"). Returns the updated case."""
    if action not in ("confirmed", "overridden"):
        raise ValueError(f"unknown action: {action}")
    con = _get_conn()
    row = con.execute("SELECT ai_tier FROM cases WHERE id = ?", (case_id,)).fetchone()
    if row is None:
        con.close()
        return None
    con.execute(
        "UPDATE cases SET status = ?, dr_disease = ?, dr_tier = ?, dr_note = ?, dr_ts = ? "
        "WHERE id = ?",
        (action, disease[:64], int(tier), (note or "")[:500], _now(), case_id),
    )
    con.execute(
        "INSERT INTO audit (ts, case_id, action, from_tier, to_tier, actor) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (_now(), case_id, action, int(row["ai_tier"]), int(tier), actor[:32]),
    )
    con.commit()
    con.close()
    return get_case(case_id)


def clear_notify_chat_id(case_id: str) -> None:
    con = _get_conn()
    con.execute("UPDATE cases SET notify_chat_id = NULL WHERE id = ?", (case_id,))
    con.commit()
    con.close()


def get_audit(case_id: Optional[str] = None) -> list[dict]:
    con = _get_conn()
    if case_id:
        rows = con.execute("SELECT * FROM audit WHERE case_id = ? ORDER BY id", (case_id,))
    else:
        rows = con.execute("SELECT * FROM audit ORDER BY id")
    out = [dict(r) for r in rows]
    con.close()
    return out


def get_stats() -> dict:
    """Live review KPIs for the Doctor Queue header."""
    try:
        con = _get_conn()
        total = con.execute("SELECT COUNT(*) FROM cases").fetchone()[0]
        pending = con.execute("SELECT COUNT(*) FROM cases WHERE status = 'pending'").fetchone()[0]
        reviewed = con.execute(
            "SELECT ai_tier, dr_tier, ai_disease, dr_disease FROM cases WHERE status != 'pending'"
        ).fetchall()
        con.close()
    except Exception as exc:
        logger.warning("get_stats failed: %s", exc)
        return {"total": 0, "pending": 0, "reviewed": 0, "tier_agreement": None,
                "overrides": 0, "under_triage": 0}
    n = len(reviewed)
    agree = sum(1 for r in reviewed if r["ai_tier"] == r["dr_tier"])
    return {
        "total": total,
        "pending": pending,
        "reviewed": n,
        "tier_agreement": (agree / n) if n else None,
        "overrides": sum(1 for r in reviewed
                         if r["ai_tier"] != r["dr_tier"] or r["ai_disease"] != r["dr_disease"]),
        # doctor raised the tier → the AI under-triaged
        "under_triage": sum(1 for r in reviewed if r["dr_tier"] > r["ai_tier"]),
    }


def export_csv() -> str:
    """Anonymised export — no thumbnail, no chat id, no note."""
    rows = list_cases()
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(EXPORT_COLUMNS)
    for r in rows:
        r = dict(r, red_flags_json=json.dumps(r.get("red_flags", []), ensure_ascii=False))
        w.writerow([r.get(c, "") for c in EXPORT_COLUMNS])
    return buf.getvalue()
