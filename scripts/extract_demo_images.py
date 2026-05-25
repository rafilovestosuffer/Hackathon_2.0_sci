"""One-shot helper: pull the 3 most-recent image attachments out of the Claude
Code session log and save them as assets/demo/{tinea,eczema,scabies}.jpg.

Order is preserved from the chat (oldest → newest of the last 3):
  1st attachment → tinea.jpg
  2nd attachment → eczema.jpg
  3rd attachment → scabies.jpg
"""
import base64
import json
from pathlib import Path

REPO     = Path(__file__).resolve().parent.parent
JSONL    = Path.home() / ".claude" / "projects" / \
           "C--Users-Rafi-Desktop-skinai-bangladesh" / \
           "82d86b85-ada9-40ff-84b9-6b724a577824.jsonl"
OUT_DIR  = REPO / "assets" / "demo"
OUT_DIR.mkdir(parents=True, exist_ok=True)

TARGETS = ["tinea.jpg", "eczema.jpg", "scabies.jpg"]


def iter_images_in_message(msg):
    """Yield (media_type, base64_data) for every image block in a message."""
    if not isinstance(msg, dict):
        return
    content = msg.get("content")
    if not isinstance(content, list):
        return
    for block in content:
        if not isinstance(block, dict):
            continue
        if block.get("type") != "image":
            continue
        src = block.get("source") or {}
        if src.get("type") == "base64":
            yield src.get("media_type", "image/jpeg"), src.get("data", "")


def find_last_n_user_messages_with_images(jsonl_path, n=3):
    """Return list of (media_type, b64) — most recent USER message with
    >= n images wins, otherwise scan backwards collecting from successive
    user messages."""
    rows = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            rows.append(row)

    # Walk backwards. Take all images from the most recent user message that
    # has at least one image. If <3, also pull from the previous one, etc.
    images = []
    for row in reversed(rows):
        msg = row.get("message") or row
        if msg.get("role") != "user":
            continue
        batch = list(iter_images_in_message(msg))
        if batch:
            images = batch + images  # keep chronological order within message
            if len(images) >= n:
                return images[-n:]
    return images[-n:] if images else []


def main():
    if not JSONL.exists():
        raise SystemExit(f"Session log not found: {JSONL}")

    # Grab the last 6 attachments and keep only the largest 3 by file size —
    # UI screenshots are typically much smaller than skin photos and we don't
    # want them creeping in. (Empirically: skin photos 30 KB – 200 KB, UI
    # screenshots ~10 KB-ish or oddly-sized PNGs.)
    grabbed = find_last_n_user_messages_with_images(JSONL, n=6)
    print(f"Found {len(grabbed)} attachment(s) in recent user messages.")
    if len(grabbed) < 3:
        raise SystemExit(
            f"Expected ≥3 images, got {len(grabbed)}. Aborting."
        )

    # Decode all, sort by aspect ratio + size, pick the 3 most square-ish JPEGs
    from PIL import Image
    import io as _io
    decoded = []
    for mtype, b64 in grabbed:
        raw = base64.b64decode(b64)
        try:
            im = Image.open(_io.BytesIO(raw))
            w, h = im.size
            # Square-ish aspect (skin photos are usually framed close to 1:1
            # or 4:3); UI screenshots are very wide (16:9 or wider).
            aspect = max(w, h) / max(1, min(w, h))
        except Exception:
            aspect = 99.0
            w, h = 0, 0
        decoded.append({"mtype": mtype, "raw": raw, "w": w, "h": h, "aspect": aspect})

    # Keep only images that are roughly square (aspect ≤ 1.8) — drops UI screenshots
    skin = [d for d in decoded if d["aspect"] <= 1.8]
    if len(skin) < 3:
        # Fallback: just keep last 3 anyway
        skin = decoded[-3:]
    else:
        skin = skin[-3:]   # most-recent 3 square-ish images (correct order)

    for fname, d in zip(TARGETS, skin):
        out = OUT_DIR / fname
        out.write_bytes(d["raw"])
        print(f"  wrote {out.relative_to(REPO)}  "
              f"({len(d['raw']):,} bytes, {d['w']}x{d['h']}, {d['mtype']})")

    print("Done.")


if __name__ == "__main__":
    main()
