from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

BASE = Path(__file__).resolve().parent
UPDATES_DIR = BASE / "data" / "portal_updates"
ALLOWED_STATUSES = {"released", "active", "next"}


@lru_cache(maxsize=16)
def load_portal_updates(language: str) -> dict[str, object]:
    path = UPDATES_DIR / f"{language}.json"
    if not path.is_file():
        path = UPDATES_DIR / "es.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    items = data.get("items", [])
    if not isinstance(items, list):
        raise ValueError("Portal updates items must be a list")
    for item in items:
        if not isinstance(item, dict) or item.get("status") not in ALLOWED_STATUSES:
            raise ValueError("Portal update has an invalid status")
    published = sorted(
        (item for item in items if item.get("status") != "next"),
        key=lambda item: item.get("date") or "",
        reverse=True,
    )
    upcoming = [item for item in items if item.get("status") == "next"]
    data["published"] = published
    data["upcoming"] = upcoming
    return data


def portal_update_detail(language: str, update_id: str) -> dict[str, object] | None:
    data = load_portal_updates(language)
    items = data["items"]
    for index, item in enumerate(items):
        if item["id"] != update_id:
            continue
        return {
            "item": item,
            "previous": items[index - 1] if index > 0 else None,
            "next": items[index + 1] if index + 1 < len(items) else None,
            "copy": data["detail"],
        }
    return None


def published_update_ids() -> tuple[str, ...]:
    data = load_portal_updates("es")
    return tuple(item["id"] for item in data["published"])


def filter_portal_updates(
    language: str, status: str = "", category: str = "", query: str = ""
) -> dict[str, object]:
    data = load_portal_updates(language).copy()
    normalized_query = query.strip().casefold()
    normalized_category = category.strip().casefold()
    filtered = []
    for item in data["items"]:
        searchable = " ".join(
            str(item.get(field, "")) for field in ("title", "summary", "category", "version")
        ).casefold()
        if status and item.get("status") != status:
            continue
        if normalized_category and str(item.get("category", "")).casefold() != normalized_category:
            continue
        if normalized_query and normalized_query not in searchable:
            continue
        filtered.append(item)
    data["filtered"] = filtered
    data["selected_filters"] = {"status": status, "category": category, "query": query}
    return data


def localized_updates_feed(language: str, origin: str) -> dict[str, object]:
    data = load_portal_updates(language)
    items = []
    for item in data["published"]:
        items.append(
            {
                "id": item["id"],
                "url": f"{origin}/{language}/updates/{item['id']}",
                "status": item["status"],
                "date": item["date"],
                "version": item["version"],
                "category": item["category"],
                "title": item["title"],
                "summary": item["summary"],
                "language": language,
            }
        )
    return {
        "version": "1.0",
        "language": language,
        "home_url": f"{origin}/{language}/updates",
        "items": items,
    }
