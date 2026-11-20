"""RelayMind main pipeline entrypoint."""
import json
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

from engine.prompt_enhancer import enhance_prompt
from engine.media_factory import OUTPUT, render_video


def send_telegram(video, caption):
    token, chat = os.getenv("TG_TOKEN", "").strip(), os.getenv("TG_CHAT_ID", "").strip()
    if not token or not chat:
        return False
    boundary = "----RelayMindFormBoundary"
    fields = [("chat_id", chat), ("caption", caption[:900]), ("supports_streaming", "true")]
    parts = []
    for key, value in fields:
        parts += [f"--{boundary}\r\n".encode(),
                  f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode(),
                  value.encode(), b"\r\n"]
    parts += [f"--{boundary}\r\n".encode(),
              f'Content-Disposition: form-data; name="video"; filename="{video.name}"\r\n'.encode(),
              b"Content-Type: video/mp4\r\n\r\n", video.read_bytes(), b"\r\n",
              f"--{boundary}--\r\n".encode()]
    req = urllib.request.Request(f"https://api.telegram.org/bot{token}/sendVideo",
        data=b"".join(parts), headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    try:
        with urllib.request.urlopen(req, timeout=22) as res:
            return bool(json.loads(res.read().decode()).get("ok"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError) as exc:
        print(f"[telegram] send failed: {type(exc).__name__}")
        return False


def main():
    topic = os.getenv("TOPIC", "").strip()
    if not topic:
        print("TOPIC is required", file=sys.stderr)
        return 2
    started = time.monotonic()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    brief = enhance_prompt(topic, os.getenv("LANG", "auto"))
    (OUTPUT / "brief.json").write_text(json.dumps(brief, ensure_ascii=False, indent=2), encoding="utf-8")
    media = render_video(brief)
    video = Path(media["video"])
    sent = send_telegram(video, brief["title"] + "\n" + " ".join(brief["hashtags"]))
    metadata = {**brief, "media": {**media, "video": "final_short.mp4"},
                "telegram_sent": sent, "elapsed_seconds": round(time.monotonic()-started, 2),
                "engine": "relaymind-core"}
    (OUTPUT / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    if os.getenv("WA_PHONE"):
        print("WA_PHONE is reserved; WhatsApp delivery is not implemented.")
    print(f"Video ready: {video} ({video.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
