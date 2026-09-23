from __future__ import annotations

import re
from pathlib import Path

VERSION_FILE = Path(__file__).resolve().parent / "VERSION"
VERSION_PATTERN = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")


def read_version() -> str:
    version = VERSION_FILE.read_text(encoding="utf-8").strip()
    if not VERSION_PATTERN.fullmatch(version):
        raise RuntimeError(f"Invalid application version in {VERSION_FILE.name}: {version!r}")
    return version


APP_VERSION = read_version()
