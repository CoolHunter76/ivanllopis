from __future__ import annotations

import os
import re

UNKNOWN = "unknown"
ENVIRONMENT_PATTERN = re.compile(r"^[a-z][a-z0-9-]{0,31}$")
VERSION_PATTERN = re.compile(r"^[0-9A-Za-z][0-9A-Za-z._-]{0,63}$")
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{7,40}$")


def _safe_value(name: str, pattern: re.Pattern[str], default: str) -> str:
    value = os.getenv(name, "").strip()
    return value if pattern.fullmatch(value) else default


def deployment_metadata(default_version: str) -> dict[str, str]:
    return {
        "environment": _safe_value("APP_ENV", ENVIRONMENT_PATTERN, UNKNOWN),
        "version": _safe_value("APP_VERSION", VERSION_PATTERN, default_version),
        "commit": _safe_value("APP_COMMIT", COMMIT_PATTERN, UNKNOWN),
    }
