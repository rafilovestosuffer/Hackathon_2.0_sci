"""
scripts/make_demo_clip.py
─────────────────────────
One-time generator for the bundled Bengali demo clip used by the
"🎧 No mic? Try a sample Bengali clip" button in the Voice tab.

Produces assets/demo_bn_sample.wav (mono, 16 kHz, ~30 KB) by calling
Google's free TTS endpoint via gTTS, then transcoding MP3 → WAV with
faster-whisper's own PyAV-based decoder (already a runtime dep), so we
do not need ffmpeg on PATH.

Run once locally:
    pip install gtts
    python scripts/make_demo_clip.py
"""

from __future__ import annotations

import io
import sys
import wave
from pathlib import Path

import numpy as np
from gtts import gTTS

SAMPLE_TEXT = (
    "আমার নাম রহিম, বয়স পঁয়ত্রিশ। "
    "সারা শরীরে চুলকানি হচ্ছে, পাঁচ দিন ধরে। "
    "জ্বরও আছে।"
)

OUT_PATH = Path(__file__).resolve().parents[1] / "assets" / "demo_bn_sample.wav"


def synthesize_mp3(text: str) -> bytes:
    tts = gTTS(text=text, lang="bn", slow=False)
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    return buf.getvalue()


def mp3_to_wav16k_mono(mp3_bytes: bytes) -> bytes:
    """Decode MP3 → 16 kHz mono float32 via faster_whisper's PyAV wrapper,
    then re-encode as 16-bit PCM WAV."""
    from faster_whisper.audio import decode_audio

    audio = decode_audio(io.BytesIO(mp3_bytes))  # float32 mono @ 16kHz
    pcm16 = np.clip(audio * 32767.0, -32768, 32767).astype(np.int16)

    out = io.BytesIO()
    with wave.open(out, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(pcm16.tobytes())
    return out.getvalue()


def main() -> int:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    print(f"Synthesizing Bengali speech: {SAMPLE_TEXT!r}")
    mp3 = synthesize_mp3(SAMPLE_TEXT)
    print(f"  → got {len(mp3)} bytes of MP3 from gTTS")

    wav = mp3_to_wav16k_mono(mp3)
    OUT_PATH.write_bytes(wav)
    print(f"  → wrote {len(wav)} bytes WAV to {OUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
