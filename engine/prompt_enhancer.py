"""Multilingual short-video prompt enhancement using local Qwen GGUF inference."""
import json
import os
import re
import subprocess
from pathlib import Path

MODELS = ("Qwen2.5-0.5B-Instruct-Q4_K_M",)


def detect_language(topic, requested="auto"):
    if requested in ("ar", "arabic"):
        return "ar"
    if requested in ("en", "english"):
        return "en"
    return "ar" if re.search(r"[\u0600-\u06ff]", topic) else "en"


def fallback(topic, lang):
    if lang == "ar":
        hook = f"تخيّل أن تكتشف سر {topic} في أقل من دقيقة!"
        body = (f"كل ما تحتاج معرفته عن {topic}: ابدأ بهذه المعلومة، "
                "لاحظ التفاصيل التي تصنع الفرق، وجرّب الخطوة بنفسك.")
        cta = "احفظ الفيديو وشاركه، واكتب لنا تجربتك في التعليقات."
        title, tags = f"سر {topic} الذي يستحق أن تعرفه", ["#ريلز", "#معلومات", "#اكتشف", "#RelayMind"]
    else:
        hook = f"Here is the surprising part about {topic}."
        body = (f"Let's break down {topic}: start with this key idea, "
                "notice the detail that changes everything, and try it yourself.")
        cta = "Save this video, share it, and tell us what you think."
        title, tags = f"The key to understanding {topic}", ["#Shorts", "#Learn", "#Discover", "#RelayMind"]
    visuals = [
        f"Cinematic vertical 9:16 opening shot introducing {topic}, strong visual hook, realistic lighting, no text",
        f"Vertical 9:16 close-up showing the key detail of {topic}, rich texture, cinematic depth, no text",
        f"Vertical 9:16 dynamic demonstration of {topic} in action, realistic camera movement, no text",
        f"Vertical 9:16 memorable final hero shot about {topic}, premium cinematic lighting, no text",
    ]
    return {"title": title, "hook": hook, "narration_script": f"{hook} {body} {cta}",
            "visual_prompts": visuals, "hashtags": tags, "language": lang, "source": "rule_fallback"}


def _parse(text):
    text = re.sub(r"^\\s*```(?:json)?\\s*|\\s*```\\s*$", "", text.strip(), flags=re.I)
    left, right = text.find("{"), text.rfind("}")
    if left < 0 or right <= left:
        raise ValueError("No JSON object in model response")
    return json.loads(text[left:right + 1])


def _normalise(obj, language, topic, source):
    if not all(isinstance(obj.get(k), str) and obj[k].strip()
               for k in ("title", "hook", "narration_script")):
        raise ValueError("Missing text fields")
    visuals = obj.get("visual_prompts")
    if not isinstance(visuals, list) or len(visuals) < 4:
        raise ValueError("Four visual prompts required")
    tags = obj.get("hashtags", [])
    if not isinstance(tags, list):
        tags = []
    return {"title": obj["title"][:120], "hook": obj["hook"][:500],
            "narration_script": obj["narration_script"][:5000],
            "visual_prompts": [str(x)[:700] for x in visuals[:4]],
            "hashtags": [str(x).replace(" ", "")[:50] for x in tags[:15]],
            "language": language, "source": source, "topic": topic}


def _local_model(topic, language):
    cli = os.getenv("RELAYMIND_LLAMA_CLI", "").strip()
    model = os.getenv("RELAYMIND_MODEL_PATH", "").strip()
    if not cli or not model or not Path(cli).is_file() or not Path(model).is_file():
        return None
    system = ("You are a concise viral short-video writer. Return ONLY valid JSON with keys "
              "title, hook, narration_script, visual_prompts, hashtags. Use the requested language. "
              "Write a powerful first-two-second hook, useful body and natural CTA. "
              "Return exactly four cinematic vertical 9:16 scene prompts, no text or logos. "
              "Avoid fabricated facts. Keep narration concise.")
    prompt = (f"<|im_start|>system\\n{system}<|im_end|>\\n"
              f"<|im_start|>user\\nLanguage: {language}. Idea: {topic}<|im_end|>\\n"
              "<|im_start|>assistant\\n")
    result = subprocess.run(
        [cli, "-m", model, "-p", prompt, "-n", "700", "--temp", "0.65",
         "--top-p", "0.85", "--ctx-size", "4096", "--threads", "2",
         "--no-display-prompt", "--simple-io", "--no-warmup"],
        capture_output=True, text=True, timeout=50, check=False)
    if result.returncode:
        raise RuntimeError(f"llama-cli exited with code {result.returncode}")
    return _normalise(_parse(result.stdout), language, topic, "local_qwen")


def enhance_prompt(topic, lang="auto"):
    topic = " ".join((topic or "").split())[:180]
    if not topic:
        raise ValueError("TOPIC is required")
    language = detect_language(topic, lang)
    try:
        generated = _local_model(topic, language)
        if generated:
            return generated
    except (OSError, subprocess.SubprocessError, TimeoutError, ValueError, TypeError) as exc:
        print(f"[prompt] local Qwen unavailable: {type(exc).__name__}")
    return fallback(topic, language)
