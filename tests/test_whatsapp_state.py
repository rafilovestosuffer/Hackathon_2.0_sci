"""Tests for whatsapp/state.py."""

import time
import pytest

from whatsapp.state import (
    Session,
    SessionStore,
    State,
    TTL_SECONDS,
    RATE_LIMIT_MAX_MSGS,
)


def test_new_session_starts_in_NEW():
    store = SessionStore()
    s = store.get_or_create("+880123")
    assert s.state == State.NEW
    assert s.district is None
    assert store.active_count() == 1


def test_get_or_create_returns_same_instance():
    store = SessionStore()
    s1 = store.get_or_create("u1")
    s1.district = "Dhaka"
    s2 = store.get_or_create("u1")
    assert s2.district == "Dhaka"


def test_reset_clears_state_but_keeps_session():
    store = SessionStore()
    s = store.get_or_create("u1")
    s.state = State.RESULT_SENT
    s.district = "Rangpur"
    s.image_bytes = b"\x89PNG"
    store.reset("u1")
    s2 = store.get_or_create("u1")
    assert s2.state == State.NEW
    assert s2.district is None
    assert s2.image_bytes is None


def test_expired_session_replaced_on_get():
    store = SessionStore()
    s = store.get_or_create("u1")
    s.last_activity_ts = time.time() - TTL_SECONDS - 1
    s.district = "stale"
    new = store.get_or_create("u1")
    assert new.district is None
    assert new.state == State.NEW


def test_dedupe_message_id():
    store = SessionStore()
    assert store.seen_message("u1", "msg1") is False
    assert store.seen_message("u1", "msg1") is True
    assert store.seen_message("u1", "msg2") is False
    # different user, same id → not deduped
    assert store.seen_message("u2", "msg1") is False


def test_dedupe_window_evicts_oldest():
    store = SessionStore()
    for i in range(150):
        store.seen_message("u1", f"m{i}")
    # m0 should have been evicted
    assert store.seen_message("u1", "m0") is False
    # recent ones still deduped
    assert store.seen_message("u1", "m149") is True


def test_rate_limit_blocks_after_threshold():
    store = SessionStore()
    for _ in range(RATE_LIMIT_MAX_MSGS):
        assert store.check_rate_limit("u1") is True
    assert store.check_rate_limit("u1") is False


def test_rate_limit_resets_after_window():
    store = SessionStore()
    s = store.get_or_create("u1")
    # fill up
    for _ in range(RATE_LIMIT_MAX_MSGS):
        store.check_rate_limit("u1")
    assert store.check_rate_limit("u1") is False
    # backdate timestamps
    fake_old = time.time() - 70
    s.msg_timestamps.clear()
    for _ in range(RATE_LIMIT_MAX_MSGS):
        s.msg_timestamps.append(fake_old)
    assert store.check_rate_limit("u1") is True


def test_gc_removes_expired():
    store = SessionStore()
    s1 = store.get_or_create("u1")
    s2 = store.get_or_create("u2")
    s1.last_activity_ts = time.time() - TTL_SECONDS - 1
    removed = store.gc()
    assert removed == 1
    assert store.active_count() == 1


def test_session_is_expired_uses_ttl():
    s = Session(user_id="u1")
    assert s.is_expired() is False
    s.last_activity_ts = time.time() - TTL_SECONDS - 1
    assert s.is_expired() is True


def test_thread_safety_smoke():
    """Concurrent get_or_create on same user → one Session instance."""
    import threading
    store = SessionStore()
    results = []

    def worker():
        results.append(store.get_or_create("shared"))

    threads = [threading.Thread(target=worker) for _ in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    # All should be the same object
    assert all(r is results[0] for r in results)
