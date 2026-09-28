from __future__ import annotations

import json
import logging
import os
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

YOUTUBE_CHANNEL_HANDLE = "CoolHunter76"
YOUTUBE_CHANNEL_URL = f"https://www.youtube.com/@{YOUTUBE_CHANNEL_HANDLE}"
YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3"
_CACHE: dict[str, object] = {"expires": 0.0, "data": None, "last_valid": None}
_CACHE_SECONDS = 600
_ERROR_CACHE_SECONDS = 60
_RECORDING_LIMIT = 8
_LOGGER = logging.getLogger(__name__)


def _fallback() -> dict[str, object]:
    return {
        "available": False,
        "channel_url": YOUTUBE_CHANNEL_URL,
        "channel_handle": f"@{YOUTUBE_CHANNEL_HANDLE}",
        "live": None,
        "recordings": [],
    }


def _request(resource: str, parameters: dict[str, str]) -> dict[str, object]:
    api_key = os.getenv("YOUTUBE_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("YouTube API key is not configured")

    query = urlencode({**parameters, "key": api_key})
    request = Request(
        f"{YOUTUBE_API_URL}/{resource}?{query}",
        headers={"Accept": "application/json", "User-Agent": "IvanLlopis.net-gamer"},
    )
    with urlopen(request, timeout=8) as response:
        payload = json.loads(response.read().decode("utf-8"))
        return payload if isinstance(payload, dict) else {}


def _items(payload: dict[str, object]) -> list[dict[str, object]]:
    items = payload.get("items", [])
    if not isinstance(items, list):
        return []
    return [item for item in items if isinstance(item, dict)]


def _channel() -> tuple[str, str]:
    payload = _request(
        "channels",
        {
            "part": "id,contentDetails",
            "forHandle": YOUTUBE_CHANNEL_HANDLE,
            "maxResults": "1",
        },
    )
    items = _items(payload)
    if not items:
        raise RuntimeError("YouTube channel could not be resolved")

    channel = items[0]
    channel_id = str(channel.get("id", ""))
    content_details = channel.get("contentDetails", {})
    related = (
        content_details.get("relatedPlaylists", {}) if isinstance(content_details, dict) else {}
    )
    uploads_id = str(related.get("uploads", "")) if isinstance(related, dict) else ""
    if not channel_id or not uploads_id:
        raise RuntimeError("YouTube channel metadata is incomplete")
    return channel_id, uploads_id


def _upload_video_ids(uploads_id: str) -> list[str]:
    payload = _request(
        "playlistItems",
        {
            "part": "contentDetails",
            "playlistId": uploads_id,
            "maxResults": "15",
        },
    )
    result: list[str] = []
    for item in _items(payload):
        details = item.get("contentDetails", {})
        video_id = str(details.get("videoId", "")) if isinstance(details, dict) else ""
        if video_id:
            result.append(video_id)
    return result


def _video_details(video_ids: list[str]) -> list[dict[str, object]]:
    if not video_ids:
        return []
    payload = _request(
        "videos",
        {
            "part": "snippet,status,liveStreamingDetails",
            "id": ",".join(video_ids),
            "maxResults": str(len(video_ids)),
        },
    )
    return _items(payload)


def _thumbnail(snippet: dict[str, object]) -> str:
    thumbnails = snippet.get("thumbnails", {})
    if not isinstance(thumbnails, dict):
        return ""
    for key in ("medium", "high", "default"):
        candidate = thumbnails.get(key, {})
        if isinstance(candidate, dict) and candidate.get("url"):
            return str(candidate["url"])
    return ""


def _public_embeddable(item: dict[str, object]) -> bool:
    status = item.get("status", {})
    if not isinstance(status, dict):
        return False
    return status.get("privacyStatus") == "public" and status.get("embeddable", True) is not False


def _build_feed(
    details: list[dict[str, object]],
) -> tuple[dict[str, str] | None, list[dict[str, str]]]:
    live: dict[str, str] | None = None
    recordings: list[dict[str, str]] = []

    for item in details:
        if not _public_embeddable(item):
            continue
        video_id = str(item.get("id", ""))
        snippet = item.get("snippet", {})
        if not video_id or not isinstance(snippet, dict):
            continue
        video = {
            "video_id": video_id,
            "title": str(snippet.get("title", "")),
            "thumbnail": _thumbnail(snippet),
        }
        broadcast = str(snippet.get("liveBroadcastContent", "none"))
        live_details = item.get("liveStreamingDetails", {})
        is_live = broadcast == "live" or (
            isinstance(live_details, dict)
            and bool(live_details.get("actualStartTime"))
            and not live_details.get("actualEndTime")
        )
        if is_live and live is None:
            live = {"video_id": video_id, "title": video["title"]}
        else:
            recordings.append(video)
        if len(recordings) >= _RECORDING_LIMIT:
            break
    return live, recordings


def gamer_youtube_data() -> dict[str, object]:
    now = time.monotonic()
    cached = _CACHE.get("data")
    if isinstance(cached, dict) and float(_CACHE.get("expires", 0.0)) > now:
        return cached

    try:
        _channel_id, uploads_id = _channel()
        details = _video_details(_upload_video_ids(uploads_id))
        live, recordings = _build_feed(details)
        result: dict[str, object] = {
            "available": bool(live or recordings),
            "channel_url": YOUTUBE_CHANNEL_URL,
            "channel_handle": f"@{YOUTUBE_CHANNEL_HANDLE}",
            "live": live,
            "recordings": recordings,
        }
        _CACHE.update(data=result, last_valid=result, expires=now + _CACHE_SECONDS)
        return result
    except (
        RuntimeError,
        HTTPError,
        URLError,
        TimeoutError,
        json.JSONDecodeError,
        ValueError,
    ) as error:
        _LOGGER.warning("YouTube Gamer feed unavailable: %s", type(error).__name__)
        last_valid = _CACHE.get("last_valid")
        result = last_valid if isinstance(last_valid, dict) else _fallback()
        _CACHE.update(data=result, expires=now + _ERROR_CACHE_SECONDS)
        return result
