"""
whatsapp/state.py — In-memory per-user conversation state.

No DB. State is keyed by phone number (Meta) or chat_id (Telegram).
TTL eviction: 10 minutes idle → reset to NEW.
Idempotency: dedupe last 100 message IDs per user (Meta retries on 5xx).
Rate limit: max 10 messages per minute per user.
"""

from __future__ import annotations

import time
import threading
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class State(Enum):
    NEW = "new"
    AWAITING_DISTRICT = "awaiting_district"
    AWAITING_IMAGE = "awaiting_image"
    AWAITING_VOICE = "awaiting_voice"
    PROCESSING = "processing"
    RESULT_SENT = "result_sent"
    RAG_CHAT = "rag_chat"


TTL_SECONDS = 10 * 60
RATE_LIMIT_WINDOW_SEC = 60
RATE_LIMIT_MAX_MSGS = 10
DEDUPE_WINDOW = 100


@dataclass
class Session:
    user_id: str
    state: State = State.NEW
    district: Optional[str] = None
    district_coords: Optional[tuple[float, float]] = None
    image_bytes: Optional[bytes] = None
    voice_transcript: Optional[str] = None
    patient_history: dict = field(default_factory=dict)
    last_prediction: Optional[dict] = None
    last_tier_result: Optional[dict] = None
    nearest_hospital: Optional[dict] = None
    last_activity_ts: float = field(default_factory=time.time)
    seen_message_ids: deque = field(default_factory=lambda: deque(maxlen=DEDUPE_WINDOW))
    msg_timestamps: deque = field(default_factory=lambda: deque(maxlen=RATE_LIMIT_MAX_MSGS))

    def touch(self) -> None:
        self.last_activity_ts = time.time()

    def is_expired(self, now: Optional[float] = None) -> bool:
        return (now or time.time()) - self.last_activity_ts > TTL_SECONDS

    def reset(self) -> None:
        """Reset conversation data but keep dedupe + rate-limit history."""
        self.state = State.NEW
        self.district = None
        self.district_coords = None
        self.image_bytes = None
        self.voice_transcript = None
        self.patient_history = {}
        self.last_prediction = None
        self.last_tier_result = None
        self.nearest_hospital = None
        self.touch()


class SessionStore:
    """Thread-safe in-memory session store."""

    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}
        self._lock = threading.Lock()

    def get_or_create(self, user_id: str) -> Session:
        with self._lock:
            sess = self._sessions.get(user_id)
            if sess is None or sess.is_expired():
                sess = Session(user_id=user_id)
                self._sessions[user_id] = sess
            return sess

    def reset(self, user_id: str) -> Session:
        with self._lock:
            sess = self._sessions.get(user_id)
            if sess is None:
                sess = Session(user_id=user_id)
                self._sessions[user_id] = sess
            else:
                sess.reset()
            return sess

    def seen_message(self, user_id: str, message_id: str) -> bool:
        """Return True if this message_id has already been processed."""
        with self._lock:
            sess = self._sessions.get(user_id)
            if sess and message_id in sess.seen_message_ids:
                return True
            if sess is None:
                sess = Session(user_id=user_id)
                self._sessions[user_id] = sess
            sess.seen_message_ids.append(message_id)
            return False

    def check_rate_limit(self, user_id: str) -> bool:
        """Return True if user is within rate limit, False if blocked."""
        now = time.time()
        with self._lock:
            sess = self._sessions.get(user_id)
            if sess is None:
                sess = Session(user_id=user_id)
                self._sessions[user_id] = sess
            # drop timestamps outside the window
            while sess.msg_timestamps and now - sess.msg_timestamps[0] > RATE_LIMIT_WINDOW_SEC:
                sess.msg_timestamps.popleft()
            if len(sess.msg_timestamps) >= RATE_LIMIT_MAX_MSGS:
                return False
            sess.msg_timestamps.append(now)
            return True

    def gc(self) -> int:
        """Drop expired sessions. Returns count removed."""
        now = time.time()
        with self._lock:
            stale = [uid for uid, s in self._sessions.items() if s.is_expired(now)]
            for uid in stale:
                del self._sessions[uid]
            return len(stale)

    def active_count(self) -> int:
        with self._lock:
            return len(self._sessions)


# Module-level singleton (the process is the only user)
store = SessionStore()
