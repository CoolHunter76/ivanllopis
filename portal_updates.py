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
    return data
