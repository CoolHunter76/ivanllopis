from __future__ import annotations

import json
import os
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

YOUTUBE_CHANNEL_HANDLE = "CoolHunter76"
YOUTUBE_CHANNEL_URL = f"https://www.youtube.com/@{YOUTUBE_CHANNEL_HANDLE}"
YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3"
_CACHE: dict[str, object] = {"expires": 0.0, "data": None}


def _request(resource: str, parameters: dict[str, str]) -> dict[str, object]:
    api_key = os.getenv("YOUTUBE_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("YouTube API key is not configured")
    query = urlencode({**parameters, "key": api_key})
    request = Request(
        f"{YOUTUBE_API_URL}/{resource}?{query}",
        headers={"Accept": "application/json", "User-Agent": "IvanLlopis.net-gamer"},
    )
    with urlopen(request, timeout=4) as response:
        payload = json.loads(response.read().decode("utf-8"))
        return payload if isinstance(payload, dict) else {}


def _search(**parameters: str) -> list[dict[str, object]]:
    payload = _request("search", {"part": "snippet", "type": "video", **parameters})
    items = payload.get("items", [])
    return items if isinstance(items, list) else []


def _video_id(item: dict[str, object]) -> str:
    identifier = item.get("id", {})
    return str(identifier.get("videoId", "")) if isinstance(identifier, dict) else ""


def _channel_id() -> str:
    items = _search(q=f"@{YOUTUBE_CHANNEL_HANDLE}", maxResults="1")
    if not items:
        raise RuntimeError("YouTube channel could not be resolved")
    snippet = items[0].get("snippet", {})
    channel_id = str(snippet.get("channelId", "")) if isinstance(snippet, dict) else ""
    if not channel_id:
        raise RuntimeError("YouTube channel id is missing")
    return channel_id


def _recorded_streams(channel_id: str) -> list[dict[str, str]]:
    candidates = _search(
        channelId=channel_id,
        eventType="completed",
        order="viewCount",
        maxResults="8",
    )
    if not candidates:
        candidates = _search(channelId=channel_id, order="viewCount", maxResults="8")
    result: list[dict[str, str]] = []
    for item in candidates:
        video_id = _video_id(item)
        snippet = item.get("snippet", {})
        if video_id and isinstance(snippet, dict):
            thumbnails = snippet.get("thumbnails", {})
            medium = thumbnails.get("medium", {}) if isinstance(thumbnails, dict) else {}
            result.append(
                {
                    "video_id": video_id,
                    "title": str(snippet.get("title", "")),
                    "thumbnail": str(medium.get("url", "")) if isinstance(medium, dict) else "",
                }
            )
    return result


def gamer_youtube_data() -> dict[str, object]:
    now = time.monotonic()
    cached = _CACHE.get("data")
    if isinstance(cached, dict) and float(_CACHE.get("expires", 0.0)) > now:
        return cached
    fallback: dict[str, object] = {
        "available": False,
        "channel_url": YOUTUBE_CHANNEL_URL,
        "channel_handle": f"@{YOUTUBE_CHANNEL_HANDLE}",
        "live": None,
        "recordings": [],
    }
    try:
        channel_id = _channel_id()
        live_items = _search(channelId=channel_id, eventType="live", maxResults="1")
        live = None
        if live_items:
            item = live_items[0]
            snippet = item.get("snippet", {})
            video_id = _video_id(item)
            if video_id and isinstance(snippet, dict):
                live = {"video_id": video_id, "title": str(snippet.get("title", ""))}
        result = {
            **fallback,
            "available": True,
            "live": live,
            "recordings": _recorded_streams(channel_id),
        }
        _CACHE.update(data=result, expires=now + 300)
        return result
    except (RuntimeError, HTTPError, URLError, TimeoutError, json.JSONDecodeError, ValueError):
        _CACHE.update(data=fallback, expires=now + 60)
        return fallback
