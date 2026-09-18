from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
TRANSLATIONS_DIR = BASE_DIR / "translations"
DEFAULT_LANGUAGE = "es"
SUPPORTED_LANGUAGES = (
    "es",
    "ca",
    "gl",
    "oc",
    "eu",
    "en",
    "fr",
    "uk",
    "it",
    "tr",
    "ru",
    "zh-Hans",
    "ja",
)


@lru_cache(maxsize=len(SUPPORTED_LANGUAGES))
def load_translations(language: str) -> dict[str, Any]:
    selected_language = language if language in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE
    path = TRANSLATIONS_DIR / f"{selected_language}.json"

    if not path.is_file():
        fallback = TRANSLATIONS_DIR / f"{DEFAULT_LANGUAGE}.json"
        if not fallback.is_file():
            return {}
        path = fallback

    with path.open(encoding="utf-8") as file:
        return json.load(file)


def translate(language: str, key: str, default: str | None = None) -> str:
    value: Any = load_translations(language)

    for section in key.split("."):
        if not isinstance(value, dict) or section not in value:
            return default if default is not None else key
        value = value[section]

    return value if isinstance(value, str) else default or key


def language_options() -> list[dict[str, str]]:
    return [
        {
            "code": language,
            "name": translate(language, "language_name", language.upper()),
        }
        for language in SUPPORTED_LANGUAGES
    ]
