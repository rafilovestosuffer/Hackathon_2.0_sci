"""cases/store.py — consent gate, retention, audit trail, anonymised export."""

import datetime
import io

import pytest
from PIL import Image

from cases import store


@pytest.fixture(autouse=True)
def tmp_db(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "_DB_PATH", str(tmp_path / "cases.db"))
    yield


def _img() -> Image.Image:
    img = Image.new("RGB", (800, 600), (200, 150, 120))
    return img


def _add(**kw):
    args = dict(consent=True, source="web", image=_img(), ai_disease="Tinea",
                ai_conf=0.82, ai_tier=1, reasons=[{"signal": "class", "en": "x", "bn": "y"}],
                red_flags=[], district="rangpur")
    args.update(kw)
    return store.add_case(**args)


def test_no_consent_stores_nothing():
    assert _add(consent=False) is None
    assert store.list_cases() == []


def test_add_and_get_roundtrip():
    cid = _add()
    case = store.get_case(cid)
    assert case["status"] == "pending"
    assert case["ai_disease"] == "Tinea" and case["ai_tier"] == 1
    assert case["reasons"][0]["signal"] == "class"
    thumb = Image.open(io.BytesIO(case["thumb_jpeg"]))
    assert max(thumb.size) <= store.THUMB_MAX_PX
    assert not thumb.getexif()


def test_list_orders_most_urgent_first():
    _add(ai_tier=1, ai_conf=0.9)
    _add(ai_tier=3, ai_conf=0.35)
    _add(ai_tier=2, ai_conf=0.5)
    assert [c["ai_tier"] for c in store.list_cases()] == [3, 2, 1]


def test_decide_writes_audit_and_stats():
    a = _add(ai_tier=1)
    b = _add(ai_tier=2, ai_disease="Eczema")
    store.decide(a, action="overridden", disease="Scabies", tier=2, note="burrows")
    store.decide(b, action="confirmed", disease="Eczema", tier=2)
    actions = [r["action"] for r in store.get_audit(a)]
    assert actions == ["created", "overridden"]
    st = store.get_stats()
    assert st["reviewed"] == 2 and st["pending"] == 0
    assert st["tier_agreement"] == 0.5
    assert st["overrides"] == 1
    assert st["under_triage"] == 1


def test_decide_rejects_unknown_action():
    cid = _add()
    with pytest.raises(ValueError):
        store.decide(cid, action="deleted", disease="Tinea", tier=1)


def test_decide_unknown_case_returns_none():
    assert store.decide("nope", action="confirmed", disease="Tinea", tier=1) is None


def test_purge_removes_old_cases():
    old = _add()
    con = store._get_conn()
    past = (datetime.datetime.utcnow() - datetime.timedelta(days=8)).isoformat()
    con.execute("UPDATE cases SET created_ts = ? WHERE id = ?", (past, old))
    con.commit(); con.close()
    new = _add()  # every write purges
    ids = [c["id"] for c in store.list_cases()]
    assert old not in ids and new in ids
    assert store.get_audit(old) == []


def test_export_has_no_image_chat_id_or_note():
    cid = _add(source="telegram", notify_chat_id="123456")
    store.decide(cid, action="confirmed", disease="Tinea", tier=1, note="private note")
    out = store.export_csv()
    header = out.splitlines()[0]
    assert "thumb" not in header and "chat" not in header and "note" not in header
    assert "123456" not in out and "private note" not in out


def test_clear_notify_chat_id():
    cid = _add(source="telegram", notify_chat_id="999")
    store.clear_notify_chat_id(cid)
    assert store.get_case(cid)["notify_chat_id"] is None


# --- cases/notify.py ---

from unittest.mock import patch

from cases import notify


def test_notify_sends_once_and_clears_chat_id():
    cid = _add(source="telegram", notify_chat_id="777", ai_tier=1)
    case = store.decide(cid, action="overridden", disease="Scabies", tier=2, note="see UHC")
    with patch("whatsapp.telegram_client.send_text") as send:
        assert notify.notify_patient(case) is True
    chat_id, body = send.call_args[0]
    assert chat_id == "777"
    assert "Scabies" in body and "see UHC" in body
    assert store.get_case(cid)["notify_chat_id"] is None


def test_notify_skips_web_cases_and_pending():
    web = store.get_case(_add(source="web"))
    tg_pending = store.get_case(_add(source="telegram", notify_chat_id="1"))
    with patch("whatsapp.telegram_client.send_text") as send:
        assert notify.notify_patient(web) is False
        assert notify.notify_patient(tg_pending) is False
    send.assert_not_called()


def test_notify_failure_keeps_chat_id_for_retry():
    cid = _add(source="telegram", notify_chat_id="5")
    case = store.decide(cid, action="confirmed", disease="Tinea", tier=1)
    with patch("whatsapp.telegram_client.send_text", side_effect=RuntimeError("net")):
        assert notify.notify_patient(case) is False
    assert store.get_case(cid)["notify_chat_id"] == "5"
