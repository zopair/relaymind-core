"""edge-tts, Pollinations/Pillow visuals, captions and ffmpeg rendering."""
import asyncio
import json
import shutil
import subprocess
import time
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw
from engine.resolver import alternatives_for

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"
W, H = 1080, 1920


def _fallback_image(path, index, prompt):
    top = [(12, 18, 38), (24, 12, 44), (8, 34, 48), (35, 20, 20)][index % 4]
    bottom = [(30, 72, 92), (92, 43, 75), (24, 82, 72), (100, 58, 30)][index % 4]
    im = Image.new("RGB", (W, H))
    pix = im.load()
    for y in range(H):
        t = y / (H - 1)
        color = tuple(int(top[c] * (1-t) + bottom[c] * t) for c in range(3))
        for x in range(W):
            pix[x, y] = color
    draw = ImageDraw.Draw(im)
    draw.ellipse((130, 350, 950, 1170), outline=(230, 190, 120), width=8)
    draw.text((70, 1450), f"RELAYMIND | SCENE {index + 1}", fill="white")
    draw.text((70, 1520), prompt[:65], fill=(240, 220, 190))
    im.save(path, "JPEG", quality=88)


def _image(prompt, path, index):
    url = "https://image.pollinations.ai/prompt/" + urllib.parse.quote(prompt[:600], safe="")
    url += f"?width={W}&height={H}&nologo=true"
    for attempt in range(2):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "RelayMind-Core/1.0"})
            with urllib.request.urlopen(req, timeout=19) as res:
                data = res.read(12 * 1024 * 1024 + 1)
            if len(data) > 12 * 1024 * 1024:
                raise ValueError("image too large")
            temp = path.with_suffix(".tmp")
            temp.write_bytes(data)
            with Image.open(temp) as im:
                im.convert("RGB").resize((W, H), Image.Resampling.LANCZOS).save(path, "JPEG", quality=88)
            temp.unlink(missing_ok=True)
            return "pollinations"
        except Exception as exc:
            print(f"[image] scene {index + 1} attempt {attempt + 1}: {type(exc).__name__}")
            time.sleep(1)
    # Discover maintained free libraries for diagnostics; never install unreviewed code.
    print("[resolver] image alternatives:", alternatives_for("images"))
    _fallback_image(path, index, prompt)
    return "pillow_fallback"


def _voice(script, lang, target):
    voice = "ar-EG-SalmaNeural" if lang == "ar" else "en-US-AriaNeural"
    try:
        import edge_tts
        async def run():
            await edge_tts.Communicate(script, voice).save(str(target))
        asyncio.run(asyncio.wait_for(run(), timeout=32))
        if target.exists() and target.stat().st_size > 1000:
            return voice
    except Exception as exc:
        print(f"[tts] edge-tts unavailable: {type(exc).__name__}")
    print("[resolver] TTS alternatives:", alternatives_for("tts"))
    # Local eSpeak is a free offline fallback when installed on the runner.
    espeak = shutil.which("espeak-ng") or shutil.which("espeak")
    if espeak:
        subprocess.run([espeak, "-v", "ar" if lang == "ar" else "en", "-w",
                        str(target.with_suffix(".wav")), script[:4000]],
                       timeout=12, check=True)
        subprocess.run([shutil.which("ffmpeg"), "-y", "-i", str(target.with_suffix(".wav")),
                        str(target)], timeout=12, check=True)
        return "local_espeak"
    # Keep the video pipeline alive; metadata clearly identifies silent fallback.
    subprocess.run([shutil.which("ffmpeg"), "-y", "-f", "lavfi", "-i",
                    "anullsrc=r=44100:cl=stereo", "-t", "20", str(target)],
                   timeout=12, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return "silent_fallback"


def _duration(path):
    probe = shutil.which("ffprobe")
    if not probe:
        return 20.0
    try:
        result = subprocess.run([probe, "-v", "error", "-show_entries", "format=duration",
                                 "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
                                capture_output=True, text=True, timeout=6, check=True)
        return max(5.0, min(float(result.stdout.strip()), 55.0))
    except (ValueError, subprocess.SubprocessError):
        return 20.0


def _captions(script, target, duration):
    sentences = [x.strip() for x in script.replace("؟", "؟|").replace("!", "!|").replace(".", ".|").split("|") if x.strip()]
    sentences = sentences[:24] or [script]
    def stamp(sec):
        ms = int(sec * 1000)
        return f"{ms//3600000:02}:{(ms//60000)%60:02}:{(ms//1000)%60:02},{ms%1000:03}"
    count = len(sentences)
    target.write_text("\n\n".join(
        f"{i+1}\n{stamp(i*duration/count)} --> {stamp((i+1)*duration/count)}\n{s}"
        for i, s in enumerate(sentences)), encoding="utf-8")


def render_video(brief):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg is required")
    sources = []
    for i, prompt in enumerate(brief["visual_prompts"][:4]):
        path = OUTPUT / f"scene_{i+1:02}.jpg"
        sources.append(_image(prompt, path, i))
    audio = OUTPUT / "voiceover.mp3"
    voice = _voice(brief["narration_script"], brief["language"], audio)
    duration = _duration(audio)
    captions = OUTPUT / "captions.srt"
    _captions(brief["narration_script"], captions, duration)
    per_scene = duration / 4
    concat = OUTPUT / "scenes.txt"
    concat.write_text("".join(f"file '{(OUTPUT / f'scene_{i:02}.jpg').as_posix()}'\nduration {per_scene:.3f}\n"
                              for i in range(1, 5)) +
                      f"file '{(OUTPUT / 'scene_04.jpg').as_posix()}'\n", encoding="utf-8")
    subtitle = str(captions).replace("\\", "/").replace(":", "\\:")
    frames_per_scene = max(25, round(per_scene * 25))
    vf = (f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
          f"zoompan=z='min(zoom+0.0008,1.08)':d={frames_per_scene}:s={W}x{H}:fps=25,"
          f"subtitles='{subtitle}':force_style='FontName=DejaVu Sans,FontSize=22,Outline=2,Shadow=1,Alignment=2,MarginV=100'")
    final = OUTPUT / "final_short.mp4"
    subprocess.run([ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-f", "concat",
                    "-safe", "0", "-i", str(concat), "-i", str(audio), "-vf", vf,
                    "-t", f"{duration:.2f}", "-r", "25", "-c:v", "libx264", "-preset", "ultrafast",
                    "-crf", "27", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
                    "-shortest", "-movflags", "+faststart", str(final)],
                   timeout=95, check=True)
    return {"video": str(final), "voice": voice, "image_sources": sources,
            "duration_seconds": round(duration, 2), "resolution": "1080x1920"}
