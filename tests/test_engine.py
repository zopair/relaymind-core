import json
import shutil
import subprocess

import pytest
from PIL import Image

from engine import media_factory
from engine.prompt_enhancer import detect_language, enhance_prompt, fallback
from engine.resolver import check_url


def test_language_detection_supports_arabic_and_english():
    assert detect_language("فكرة فيديو") == "ar"
    assert detect_language("short video idea") == "en"
    assert detect_language("مرحبا", "en") == "en"


def test_rule_fallback_returns_four_scenes_and_complete_script():
    brief = fallback("قهوة عربية", "ar")
    assert brief["language"] == "ar"
    assert len(brief["visual_prompts"]) == 4
    assert all("9:16" in prompt for prompt in brief["visual_prompts"])
    assert brief["hook"] in brief["narration_script"]
    assert brief["hashtags"]


def test_enhancer_rejects_empty_topic(monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    with pytest.raises(ValueError, match="TOPIC"):
        enhance_prompt("   ")


def test_enhancer_uses_local_fallback_without_token(monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("RELAYMIND_LLAMA_CLI", raising=False)
    monkeypatch.delenv("RELAYMIND_MODEL_PATH", raising=False)
    brief = enhance_prompt("coffee roasting", "en")
    assert brief["source"] == "rule_fallback"
    assert len(brief["visual_prompts"]) == 4


def test_caption_timestamps_follow_audio_duration(tmp_path):
    target = tmp_path / "captions.srt"
    media_factory._captions("First sentence. Second sentence.", target, 8)
    content = target.read_text(encoding="utf-8")
    assert "00:00:00,000 --> 00:00:04,000" in content
    assert "00:00:04,000 --> 00:00:08,000" in content


def test_video_filter_uses_single_zoompan_output_per_input_frame(tmp_path):
    captions = tmp_path / "captions.srt"
    captions.write_text("", encoding="utf-8")
    vf = media_factory._build_video_filter(captions)
    assert "zoompan=" in vf
    assert ":d=1:" in vf
    assert "1080x1920" in vf


def test_fallback_image_is_vertical_and_valid(tmp_path):
    target = tmp_path / "fallback.jpg"
    media_factory._fallback_image(target, 0, "test scene")
    with Image.open(target) as image:
        assert image.size == (1080, 1920)
        assert image.format == "JPEG"


def test_offline_render_produces_valid_vertical_mp4(tmp_path, monkeypatch):
    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    if not ffmpeg or not ffprobe:
        pytest.skip("ffmpeg/ffprobe unavailable")
    monkeypatch.setattr(media_factory, "OUTPUT", tmp_path)

    def fake_image(prompt, path, index):
        Image.new("RGB", (1080, 1920), (20 + index * 20, 40, 80)).save(path, "JPEG")
        return "test_fixture"

    def fake_voice(script, lang, target):
        subprocess.run([ffmpeg, "-y", "-f", "lavfi", "-i",
                        "anullsrc=r=44100:cl=stereo", "-t", "4", str(target)],
                       check=True, capture_output=True, timeout=10)
        return "test_silence"

    monkeypatch.setattr(media_factory, "_image", fake_image)
    monkeypatch.setattr(media_factory, "_voice", fake_voice)
    monkeypatch.setattr(media_factory, "_duration", lambda _: 4.0)

    brief = fallback("test topic", "en")
    result = media_factory.render_video(brief)
    video = tmp_path / "final_short.mp4"
    assert video.exists() and video.stat().st_size > 1000
    assert result["resolution"] == "1080x1920"
    probe = subprocess.run([ffprobe, "-v", "error", "-select_streams", "v:0",
                            "-show_entries", "stream=width,height", "-of", "json", str(video)],
                           check=True, capture_output=True, text=True, timeout=10)
    stream = json.loads(probe.stdout)["streams"][0]
    assert (stream["width"], stream["height"]) == (1080, 1920)


def test_invalid_endpoint_fails_closed():
    assert check_url("not-a-valid-url") is False



def test_local_qwen_model_is_used_without_remote_api(monkeypatch, tmp_path):
    from types import SimpleNamespace
    from engine import prompt_enhancer

    cli = tmp_path / "llama-cli"
    model = tmp_path / "model.gguf"
    cli.write_text("binary-placeholder")
    model.write_bytes(b"model-placeholder")
    monkeypatch.setenv("RELAYMIND_LLAMA_CLI", str(cli))
    monkeypatch.setenv("RELAYMIND_MODEL_PATH", str(model))
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    expected = {
        "title": "قهوة عربية",
        "hook": "هل تعرف سر القهوة؟",
        "narration_script": "هل تعرف سر القهوة؟ جرّبها اليوم.",
        "visual_prompts": [
            "مشهد 1 عمودي 9:16", "مشهد 2 عمودي 9:16",
            "مشهد 3 عمودي 9:16", "مشهد 4 عمودي 9:16"
        ],
        "hashtags": ["#قهوة", "#ريلز"]
    }
    monkeypatch.setattr(
        prompt_enhancer.subprocess, "run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=0, stdout=json.dumps(expected, ensure_ascii=False), stderr=""
        )
    )

    brief = enhance_prompt("قهوة عربية", "ar")
    assert brief["source"] == "local_qwen"
    assert brief["title"] == expected["title"]
    assert len(brief["visual_prompts"]) == 4
