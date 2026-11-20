"""Multilingual short-video prompt enhancement with a deterministic fallback."""
import json
import os
import re
import urllib.request
import urllib.error

API = "https://models.github.ai/inference/chat/completions"
MODELS = ("openai/gpt-4o-mini", "meta/Llama-3.3-70B-Instruct")


def detect_language(topic, requested="auto"):
    if requested in ("ar", "arabic"):
        return "ar"
    if requested in ("en", "english"):
        return "en"
    return "ar" if re.search(r"[\u0600-\u06ff]", topic) else "en"


def fallback(topic, lang):
    if lang == "ar":
        hook = f"هل تعرف السر وراء {topic}؟"
        body = f"إليك الفكرة: {topic}. شاهد التفاصيل، وتعرّف على أهم خطوة، وجرّبها بنفسك."
        cta = "تابعنا للمزيد واكتب رأيك في التعليقات."
        title, tags = f"اكتشف {topic}", ["#ريلز", "#معلومات", "#اكتشف", "#RelayMind"]
    else:
        hook = f"What if you could understand {topic} in seconds?"
        body = f"Here is the idea: {topic}. See the key details, understand how it works, and try it yourself."
        cta = "Follow for more and share your take below."
        title, tags = f"Discover {topic}", ["#Shorts", "#Learn", "#Discover", "#RelayMind"]
    visuals = [
        f"Cinematic vertical 9:16 opening shot introducing {topic}, dramatic close-up, realistic lighting, no text",
        f"Vertical 9:16 detailed visual explanation of {topic}, cinematic depth, realistic, no text",
        f"Vertical 9:16 demonstration of {topic} in action, dynamic camera, no text",
        f"Vertical 9:16 memorable final hero shot about {topic}, cinematic lighting, no text",
    ]
    return {"title": title, "hook": hook, "narration_script": f"{hook} {body} {cta}",
            "visual_prompts": visuals, "hashtags": tags, "language": lang, "source": "rule_fallback"}


def _parse(text):
    text = re.sub(r"^\s*```(?:json)?\s*|\s*```\s*$", "", text.strip(), flags=re.I)
    left, right = text.find("{"), text.rfind("}")
    if left < 0 or right <= left:
        raise ValueError("No JSON object in model response")
    return json.loads(text[left:right + 1])


def enhance_prompt(topic, lang="auto"):
    topic = " ".join((topic or "").split())[:180]
    if not topic:
        raise ValueError("TOPIC is required")
    language = detect_language(topic, lang)
    token = os.getenv("GITHUB_TOKEN", "").strip()
    if not token:
        return fallback(topic, language)
    system = ("Return only valid JSON keys title, hook, narration_script, visual_prompts, hashtags. "
              "Use the input language. Make a strong 2-second hook, concise useful body and CTA. "
              "Create exactly four distinct cinematic vertical 9:16 visual prompts without text/logos. "
              "Avoid unsupported factual claims.")
    for model in MODELS:
        payload = json.dumps({"model": model, "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": f"Language: {language}. Idea: {topic}"}],
            "temperature": 0.7, "max_tokens": 1100}).encode()
        req = urllib.request.Request(API, data=payload, method="POST", headers={
            "Authorization": f"Bearer {token}", "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=16) as response:
                raw = json.loads(response.read().decode())
            obj = _parse(raw["choices"][0]["message"]["content"])
            visuals = obj.get("visual_prompts")
            if not all(isinstance(obj.get(k), str) and obj[k].strip()
                       for k in ("title", "hook", "narration_script")):
                raise ValueError("Missing text fields")
            if not isinstance(visuals, list) or len(visuals) < 4:
                raise ValueError("Four visual prompts required")
            tags = obj.get("hashtags", [])
            return {"title": obj["title"][:120], "hook": obj["hook"][:500],
                    "narration_script": obj["narration_script"][:5000],
                    "visual_prompts": [str(x)[:700] for x in visuals[:4]],
                    "hashtags": [str(x).replace(" ", "")[:50] for x in tags[:15]],
                    "language": language, "source": "github_models", "topic": topic}
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, KeyError,
                IndexError, ValueError, TypeError) as exc:
            print(f"[prompt] {model} unavailable: {type(exc).__name__}")
    return fallback(topic, language)
