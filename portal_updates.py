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
