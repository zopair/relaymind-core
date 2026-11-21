"""Bounded endpoint checks and GitHub metadata search; never executes discovered code."""
import json
import os
import urllib.parse
import urllib.request
import urllib.error
from urllib.parse import urlsplit

UA = "RelayMind-Core/1.0"


def check_url(url, timeout=5):
    try:
        parsed = urlsplit(url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            return False
        req = urllib.request.Request(url, headers={"User-Agent": UA})
    except (TypeError, ValueError):
        return False
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            return 200 <= res.status < 400
    except (urllib.error.URLError, TimeoutError, ValueError):
        return False


def search_open_source(query, limit=3):
    params = urllib.parse.urlencode({"q": f"{query} language:Python", "sort": "stars",
                                    "per_page": min(max(int(limit), 1), 5)})
    headers = {"Accept": "application/vnd.github+json", "User-Agent": UA}
    token = os.getenv("GITHUB_TOKEN", "")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request("https://api.github.com/search/repositories?" + params,
                                 headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=7) as res:
            items = json.loads(res.read().decode()).get("items", [])
        return [{"full_name": x.get("full_name", ""), "url": x.get("html_url", ""),
                 "description": (x.get("description") or "")[:160]} for x in items[:limit]]
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError):
        return []


def diagnose():
    return {name: check_url(url) for name, url in {
        "pollinations": "https://image.pollinations.ai/",
        "github_models": "https://models.github.ai/",
        "github_api": "https://api.github.com/"}.items()}


def alternatives_for(component):
    terms = {"tts": "offline text to speech neural", "images": "open source image generation",
             "video": "ffmpeg python video editing"}
    return search_open_source(terms.get(component, component))
