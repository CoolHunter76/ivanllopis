from __future__ import annotations

import json
import os
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

REPOSITORY = "CoolHunter76/ivanllopis"
REPOSITORY_URL = f"https://github.com/{REPOSITORY}"
API_URL = f"https://api.github.com/repos/{REPOSITORY}"
_CACHE: dict[str, object] = {"expires": 0.0, "data": None}


def _request(path: str) -> object:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "IvanLlopis.net-project-world",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.getenv("GITHUB_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(f"{API_URL}{path}", headers=headers)
    with urlopen(request, timeout=4) as response:
        return json.loads(response.read().decode("utf-8"))


def project_world_data() -> dict[str, object]:
    now = time.monotonic()
    cached = _CACHE.get("data")
    if isinstance(cached, dict) and float(_CACHE.get("expires", 0.0)) > now:
        return cached
    try:
        repository = _request("")
        commits = _request("/commits?per_page=6")
        languages = _request("/languages")
        branches = _request("/branches?per_page=20")
        workflows = _request("/actions/runs?per_page=5")
        data = {
            "available": True,
            "repository": repository if isinstance(repository, dict) else {},
            "commits": commits if isinstance(commits, list) else [],
            "languages": languages if isinstance(languages, dict) else {},
            "branches": branches if isinstance(branches, list) else [],
            "runs": workflows.get("workflow_runs", []) if isinstance(workflows, dict) else [],
            "url": REPOSITORY_URL,
            "synced": int(time.time()),
        }
        _CACHE.update(data=data, expires=now + 600)
        return data
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, ValueError):
        return {
            "available": False,
            "url": REPOSITORY_URL,
            "commits": [],
            "languages": {},
            "branches": [],
            "runs": [],
        }
