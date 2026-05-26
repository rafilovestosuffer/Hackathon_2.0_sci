"""Telemedicine integration layer.

Pluggable providers for handing off SkinAI patients to licensed
Bangladeshi telemedicine platforms. Phase 1: DocTime (live handoff).
Phase 3 stubs: Praava, MediCal, Maya.
"""

from telemedicine.providers import (
    HandoffPayload,
    TelemedicineProvider,
    REGISTRY,
    get_provider,
    payload_from_session,
)
from telemedicine import doctime  # noqa: F401 — registers provider on import

__all__ = [
    "HandoffPayload",
    "TelemedicineProvider",
    "REGISTRY",
    "get_provider",
    "payload_from_session",
]
