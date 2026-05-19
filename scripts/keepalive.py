"""
keepalive.py — Ping HF Space every 20 minutes to prevent sleep.

CONSTRAINT 7: App must stay live until July 12, 2026.

Usage (manual):
    python scripts/keepalive.py

Automated: .github/workflows/keepalive.yml runs this on a cron schedule.
"""

import os
import time

import requests

HF_SPACE_URL = os.getenv(
    "HF_SPACE_URL",
    "https://rafilovestosuffer-skinai-bangladesh.hf.space",
)
INTERVAL_SECONDS = 20 * 60  # 20 minutes


def ping(url: str = HF_SPACE_URL) -> bool:
    """GET the HF Space URL. Returns True on HTTP 2xx/3xx, False otherwise."""
    try:
        r = requests.get(url, timeout=20, allow_redirects=True)
        print(f"[keepalive] Ping OK — HTTP {r.status_code} — {url}")
        return r.status_code < 400
    except requests.exceptions.Timeout:
        print(f"[keepalive] Ping timed out — {url}")
        return False
    except Exception as exc:
        print(f"[keepalive] Ping failed — {exc}")
        return False


def run_loop(url: str = HF_SPACE_URL, interval: int = INTERVAL_SECONDS) -> None:
    """Ping forever, sleeping interval seconds between pings."""
    print(f"[keepalive] Starting — pinging every {interval // 60} min → {url}")
    while True:
        ping(url)
        time.sleep(interval)


if __name__ == "__main__":
    run_loop()
