"""POST/GET /api/cases — the offline /lite page's sync endpoint."""

import io

import numpy as np
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from webhook import server
from webhook.server import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def tmp_cases_db(tmp_path, monkeypatch):
    from cases import store
    monkeypatch.setattr(store, "_DB_PATH", str(tmp_path / "cases.db"))
    server._api_hits.clear()
    yield store


def _sharp_jpeg() -> bytes:
    rng = np.random.default_rng(0)
    arr = rng.integers(0, 255, (240, 320, 3), dtype=np.uint8)
    buf = io.BytesIO()
    Image.fromarray(arr).save(buf, format="JPEG", quality=70)
    return buf.getvalue()


def _flat_jpeg() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (320, 240), (180, 130, 110)).save(buf, format="JPEG")
    return buf.getvalue()


def _post(img=None, flags=(), consent="true", district="rangpur"):
    data = {"consent": consent, "district": district}
    if flags:
        data["red_flags"] = list(flags)
    return client.post("/api/cases",
                       files={"image": ("lesion.jpg", img or _sharp_jpeg(), "image/jpeg")},
                       data=data)


def test_triage_without_red_flags():
    r = _post(consent="false")
    assert r.status_code == 200
    body = r.json()
    # conftest stub: Tinea 0.82 → base tier 1, no escalation
    assert body["disease"] == "Tinea" and body["tier"] == 1
    assert body["case_id"] is None
    assert body["reasons"] and body["action_bn"]


def test_red_flag_escalates_one_tier():
    body = _post(flags=["fever"], consent="false").json()
    assert body["tier"] == 2
    assert any(r["signal"] == "keywords" for r in body["reasons"])


def test_consent_stores_case_and_status_endpoint(tmp_cases_db):
    body = _post(flags=["pain"]).json()
    cid = body["case_id"]
    assert cid
    case = tmp_cases_db.get_case(cid)
    assert case["source"] == "lite" and case["red_flags"] == ["pain"]

    s = client.get(f"/api/cases/{cid}").json()
    assert s["status"] == "pending" and "dr_tier" not in s

    tmp_cases_db.decide(cid, action="overridden", disease="Scabies", tier=3, note="go today")
    s = client.get(f"/api/cases/{cid}").json()
    assert s["status"] == "overridden" and s["dr_tier"] == 3
    assert s["dr_note"] == "go today" and s["dr_action_bn"]
    assert "thumb_jpeg" not in s and "notify_chat_id" not in s


def test_unknown_case_404():
    assert client.get("/api/cases/doesnotexist").status_code == 404


def test_unknown_red_flag_rejected():
    assert _post(flags=["itchy"]).status_code == 400


def test_blurry_image_rejected():
    assert _post(img=_flat_jpeg()).status_code == 422


def test_unreadable_image_rejected():
    assert _post(img=b"not an image at all").status_code == 400


def test_too_large_rejected():
    assert _post(img=b"\xff" * (server.MAX_IMAGE_BYTES + 10)).status_code == 413


def test_model_unavailable_is_503_without_result(stub_model_inference, tmp_cases_db):
    from model.service import unavailable
    stub_model_inference.side_effect = lambda image: unavailable()
    r = _post()
    assert r.status_code == 503
    assert "disease" not in r.json() and r.json()["error"] == "model_unavailable"
    assert tmp_cases_db.list_cases() == []


def test_rate_limit():
    codes = [_post(consent="false").status_code for _ in range(server._API_RATE_MAX + 1)]
    assert codes[-1] == 429 and set(codes[:-1]) == {200}
