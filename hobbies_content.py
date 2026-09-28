from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

BASE = Path(__file__).resolve().parent
HOBBIES_DIR = BASE / "data" / "hobbies"
HOBBY_SLUGS = ("drums", "travel", "dance", "sea", "trekking", "gamer")
REQUIRED_KEYS = {"slug", "theme", "hero", "categories", "media", "places", "events"}


@lru_cache(maxsize=32)
def load_hobby(slug: str, language: str) -> dict[str, object]:
    if slug not in HOBBY_SLUGS:
        raise KeyError(slug)
    path = HOBBIES_DIR / f"{slug}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    missing = REQUIRED_KEYS.difference(data)
    if missing:
        raise ValueError(f"Invalid hobby data for {slug}: missing {sorted(missing)}")
    localized = data.get("locales", {})
    copy = localized.get(language) or localized.get("en") or localized.get("es") or {}
    return {**data, "copy": copy}
