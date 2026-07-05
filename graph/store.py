"""
graph/store.py
Kuzu embedded graph database — disease-symptom-triage knowledge graph.

Schema
------
  Nodes  : Disease · Symptom · BodyPart · TierAction · KnowledgeSource
  Edges  : HAS_SYMPTOM · MAPS_TO · COMMONLY_AFFECTS · DOCUMENTED_BY · ESCALATES_TO

All data is hardcoded clinical knowledge from CDC/NIH/WHO/DGHS Bangladesh.
No patient data enters the graph. Build is idempotent via a sentinel flag file.

Public API
----------
  build_graph()           → bool   called once at app startup
  get_symptoms(disease)   → list[dict]  {name, name_bn, is_escalation}
  get_body_parts(disease) → list[dict]  {name, name_bn}
  get_related(disease)    → list[str]   diseases sharing ≥2 symptoms
  get_stats()             → dict        node/edge counts for /docs dashboard
  is_available()          → bool
"""
import logging
import os

logger = logging.getLogger(__name__)

_DB_PATH    = os.path.join(os.path.dirname(__file__), "skinai_knowledge.kuzu")
_SEED_FLAG  = os.path.join(os.path.dirname(__file__), ".graph_seeded")

_db   = None
_conn = None
_available = False

# --- Seed data (7 BD-SkinNet classes + clinical knowledge) ---

_DISEASES = [
    ("Atopic_Dermatitis",     "অ্যাটোপিক ডার্মাটাইটিস", 2),
    ("Contact_Dermatitis",    "কন্টাক্ট ডার্মাটাইটিস",   1),
    ("Eczema",                "একজিমা",                   2),
    ("Scabies",               "খোস-পাঁচড়া",              2),
    ("Seborrheic_Dermatitis", "সেবোরিক ডার্মাটাইটিস",    1),
    ("Tinea",                 "দাদ",                      1),
    ("Vitiligo",              "শ্বেতী",                    2),
]

_SYMPTOMS = [
    # (name, name_bn, is_escalation)
    ("itching",              "চুলকানি",           False),
    ("dry_skin",             "শুষ্ক ত্বক",         False),
    ("redness",              "লালভাব",             False),
    ("scaling",              "আঁশ পড়া",           False),
    ("blistering",           "ফোসকা",             False),
    ("burning",              "জ্বালাপোড়া",         False),
    ("swelling",             "ফোলা",              False),
    ("night_itching",        "রাতে চুলকানি",       False),
    ("burrow_tracks",        "গর্তের দাগ",         False),
    ("circular_rash",        "গোলাকার ফুসকুড়ি",   False),
    ("white_patches",        "সাদা দাগ",           False),
    ("dandruff",             "খুশকি",             False),
    ("oily_skin",            "তৈলাক্ত ত্বক",       False),
    ("skin_thickening",      "ত্বক মোটা হওয়া",     False),
    ("hair_loss",            "চুল পড়া",           False),
    ("secondary_infection",  "সেকেন্ডারি সংক্রমণ", False),
    ("spreading",            "ছড়িয়ে পড়া",         True),
    ("fever",                "জ্বর",              True),
    ("pain",                 "ব্যথা",             True),
    ("bleeding",             "রক্তপাত",           True),
]

_BODY_PARTS = [
    ("face",   "মুখ"),   ("hands",  "হাত"),    ("feet",    "পা"),
    ("scalp",  "মাথার তালু"), ("elbows", "কনুই"), ("knees",  "হাঁটু"),
    ("groin",  "কুঁচকি"), ("armpits","বগল"),   ("wrists", "কব্জি"),
    ("back",   "পিঠ"),   ("chest",  "বুক"),    ("neck",   "ঘাড়"),
]

_TIERS = [
    (1, "NON-URGENT", "Consult local pharmacist within 3-5 days",         "Local Pharmacy"),
    (2, "ROUTINE",    "Visit Upazila Health Complex within 48 hours",      "Upazila Health Complex"),
    (3, "URGENT",     "Seek emergency care TODAY at District Hospital",    "District Hospital"),
]

_SOURCES = [
    ("CDC",  "US Centers for Disease Control and Prevention"),
    ("NIH",  "US National Institutes of Health"),
    ("WHO",  "World Health Organization"),
    ("DGHS", "Directorate General of Health Services Bangladesh"),
]

_DISEASE_SYMPTOMS = {
    "Atopic_Dermatitis":     ["itching", "dry_skin", "redness", "skin_thickening", "secondary_infection"],
    "Contact_Dermatitis":    ["redness", "itching", "blistering", "burning", "swelling"],
    "Eczema":                ["itching", "dry_skin", "scaling", "redness", "blistering"],
    "Scabies":               ["night_itching", "burrow_tracks", "redness", "spreading", "secondary_infection"],
    "Seborrheic_Dermatitis": ["dandruff", "oily_skin", "scaling", "redness", "itching"],
    "Tinea":                 ["circular_rash", "scaling", "itching", "hair_loss", "spreading"],
    "Vitiligo":              ["white_patches", "spreading"],
}

_DISEASE_PARTS = {
    "Atopic_Dermatitis":     ["face", "elbows", "knees", "hands"],
    "Contact_Dermatitis":    ["hands", "face", "neck"],
    "Eczema":                ["hands", "feet", "face", "elbows", "knees"],
    "Scabies":               ["wrists", "hands", "armpits", "groin"],
    "Seborrheic_Dermatitis": ["scalp", "face", "chest"],
    "Tinea":                 ["feet", "groin", "scalp", "back"],
    "Vitiligo":              ["face", "hands", "back", "neck"],
}

_DISEASE_TIER = {
    "Atopic_Dermatitis": 2, "Contact_Dermatitis": 1, "Eczema": 2,
    "Scabies": 2, "Seborrheic_Dermatitis": 1, "Tinea": 1, "Vitiligo": 2,
}

_DISEASE_SOURCES = {
    "Atopic_Dermatitis":     ["NIH", "WHO", "CDC"],
    "Contact_Dermatitis":    ["CDC", "NIH", "DGHS"],
    "Eczema":                ["NIH", "CDC", "WHO"],
    "Scabies":               ["CDC", "WHO", "DGHS"],
    "Seborrheic_Dermatitis": ["NIH", "DGHS"],
    "Tinea":                 ["CDC", "NIH", "WHO", "DGHS"],
    "Vitiligo":              ["NIH", "WHO"],
}

_ESCALATION_SYMPTOMS = {"spreading", "fever", "pain", "bleeding"}


# --- Internal helpers ---

def _get_conn():
    global _db, _conn
    if _conn is not None:
        return _conn
    import kuzu
    _db   = kuzu.Database(_DB_PATH)
    _conn = kuzu.Connection(_db)
    return _conn


def _exec(conn, cypher: str, params: dict | None = None):
    return conn.execute(cypher, params) if params else conn.execute(cypher)


# --- Public API ---

def build_graph() -> bool:
    """
    Build the knowledge graph. Idempotent — skips if already seeded.
    Called once at app startup. Never raises.
    """
    global _available
    try:
        if os.path.exists(_SEED_FLAG):
            _available = True
            logger.info("Graph DB: existing knowledge graph loaded.")
            return True

        conn = _get_conn()

        # Node tables
        _exec(conn, "CREATE NODE TABLE Disease(name STRING, name_bn STRING, tier_base INT64, PRIMARY KEY(name))")
        _exec(conn, "CREATE NODE TABLE Symptom(name STRING, name_bn STRING, is_escalation BOOLEAN, PRIMARY KEY(name))")
        _exec(conn, "CREATE NODE TABLE BodyPart(name STRING, name_bn STRING, PRIMARY KEY(name))")
        _exec(conn, "CREATE NODE TABLE TierAction(tier INT64, urgency_label STRING, action_en STRING, facility STRING, PRIMARY KEY(tier))")
        _exec(conn, "CREATE NODE TABLE KnowledgeSource(name STRING, description STRING, PRIMARY KEY(name))")

        # Relationship tables
        _exec(conn, "CREATE REL TABLE HAS_SYMPTOM(FROM Disease TO Symptom)")
        _exec(conn, "CREATE REL TABLE MAPS_TO(FROM Disease TO TierAction)")
        _exec(conn, "CREATE REL TABLE COMMONLY_AFFECTS(FROM Disease TO BodyPart)")
        _exec(conn, "CREATE REL TABLE DOCUMENTED_BY(FROM Disease TO KnowledgeSource)")
        _exec(conn, "CREATE REL TABLE ESCALATES_TO(FROM Symptom TO TierAction)")

        # Seed nodes
        for name, name_bn, tier in _DISEASES:
            _exec(conn, "CREATE (:Disease {name: $n, name_bn: $b, tier_base: $t})",
                  {"n": name, "b": name_bn, "t": tier})

        for name, name_bn, is_esc in _SYMPTOMS:
            _exec(conn, "CREATE (:Symptom {name: $n, name_bn: $b, is_escalation: $e})",
                  {"n": name, "b": name_bn, "e": is_esc})

        for name, name_bn in _BODY_PARTS:
            _exec(conn, "CREATE (:BodyPart {name: $n, name_bn: $b})",
                  {"n": name, "b": name_bn})

        for tier, label, action, facility in _TIERS:
            _exec(conn, "CREATE (:TierAction {tier: $t, urgency_label: $l, action_en: $a, facility: $f})",
                  {"t": tier, "l": label, "a": action, "f": facility})

        for name, desc in _SOURCES:
            _exec(conn, "CREATE (:KnowledgeSource {name: $n, description: $d})",
                  {"n": name, "d": desc})

        # Seed relationships
        for disease, symptoms in _DISEASE_SYMPTOMS.items():
            for symptom in symptoms:
                _exec(conn,
                      "MATCH (d:Disease {name: $d}), (s:Symptom {name: $s}) CREATE (d)-[:HAS_SYMPTOM]->(s)",
                      {"d": disease, "s": symptom})

        for disease, tier in _DISEASE_TIER.items():
            _exec(conn,
                  "MATCH (d:Disease {name: $d}), (t:TierAction {tier: $t}) CREATE (d)-[:MAPS_TO]->(t)",
                  {"d": disease, "t": tier})

        for disease, parts in _DISEASE_PARTS.items():
            for part in parts:
                _exec(conn,
                      "MATCH (d:Disease {name: $d}), (b:BodyPart {name: $b}) CREATE (d)-[:COMMONLY_AFFECTS]->(b)",
                      {"d": disease, "b": part})

        for disease, sources in _DISEASE_SOURCES.items():
            for src in sources:
                _exec(conn,
                      "MATCH (d:Disease {name: $d}), (k:KnowledgeSource {name: $k}) CREATE (d)-[:DOCUMENTED_BY]->(k)",
                      {"d": disease, "k": src})

        for name in _ESCALATION_SYMPTOMS:
            _exec(conn,
                  "MATCH (s:Symptom {name: $s}), (t:TierAction {tier: 3}) CREATE (s)-[:ESCALATES_TO]->(t)",
                  {"s": name})

        # Mark seeded
        with open(_SEED_FLAG, "w") as f:
            f.write("ok")

        _available = True
        logger.info(
            "Graph DB: built — %d diseases, %d symptoms, %d body parts.",
            len(_DISEASES), len(_SYMPTOMS), len(_BODY_PARTS),
        )
        return True

    except Exception as exc:
        logger.warning("Graph DB build failed — app continues without graph: %s", exc)
        _available = False
        return False


def get_symptoms(disease_name: str) -> list[dict]:
    """
    Return symptoms linked to a disease.
    Returns [] silently on any error.
    """
    if not _available:
        return []
    try:
        conn = _get_conn()
        r = _exec(conn,
                  "MATCH (d:Disease {name: $d})-[:HAS_SYMPTOM]->(s:Symptom) "
                  "RETURN s.name, s.name_bn, s.is_escalation",
                  {"d": disease_name})
        out = []
        while r.has_next():
            row = r.get_next()
            out.append({"name": row[0], "name_bn": row[1], "is_escalation": row[2]})
        return out
    except Exception:
        return []


def get_body_parts(disease_name: str) -> list[dict]:
    """
    Return body parts commonly affected by a disease.
    Returns [] silently on any error.
    """
    if not _available:
        return []
    try:
        conn = _get_conn()
        r = _exec(conn,
                  "MATCH (d:Disease {name: $d})-[:COMMONLY_AFFECTS]->(b:BodyPart) "
                  "RETURN b.name, b.name_bn",
                  {"d": disease_name})
        out = []
        while r.has_next():
            row = r.get_next()
            out.append({"name": row[0], "name_bn": row[1]})
        return out
    except Exception:
        return []


def get_related(disease_name: str, min_shared: int = 2) -> list[str]:
    """
    Return diseases sharing >= min_shared symptoms with the given disease.
    Used for differential diagnosis context in RAG prompt.
    """
    if not _available:
        return []
    try:
        conn = _get_conn()
        r = _exec(conn,
                  "MATCH (d1:Disease {name: $d})-[:HAS_SYMPTOM]->(s:Symptom)"
                  "<-[:HAS_SYMPTOM]-(d2:Disease) "
                  "WHERE d2.name <> $d "
                  "RETURN d2.name, count(s) AS shared "
                  "ORDER BY shared DESC",
                  {"d": disease_name})
        out = []
        while r.has_next():
            row = r.get_next()
            if row[1] >= min_shared:
                out.append(row[0])
        return out
    except Exception:
        return []


def get_stats() -> dict:
    """Node and edge counts for /docs dashboard. Returns {} on failure."""
    if not _available:
        return {}
    try:
        conn = _get_conn()
        stats = {}
        for table in ("Disease", "Symptom", "BodyPart", "TierAction", "KnowledgeSource"):
            r = _exec(conn, f"MATCH (n:{table}) RETURN count(n)")
            stats[table.lower()] = r.get_next()[0] if r.has_next() else 0
        for rel in ("HAS_SYMPTOM", "MAPS_TO", "COMMONLY_AFFECTS", "DOCUMENTED_BY", "ESCALATES_TO"):
            r = _exec(conn, f"MATCH ()-[e:{rel}]->() RETURN count(e)")
            stats[rel.lower()] = r.get_next()[0] if r.has_next() else 0
        return stats
    except Exception:
        return {}


def is_available() -> bool:
    return _available
