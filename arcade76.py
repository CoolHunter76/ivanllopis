from __future__ import annotations

import json
import os
import re
import secrets
import threading
import time
from contextlib import suppress
from datetime import UTC, datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()
_STORE = Path(os.getenv("ARCADE_HOF_PATH", "data/arcade/hall_of_fame.json"))
_LOCK = threading.Lock()
_SESSIONS: dict[str, dict] = {}
_CLAIMS: dict[str, dict] = {}
_GAMES = {"sky-patrol-76", "block-breaker-76", "neon-blocks-76"}


class ScoreRequest(BaseModel):
    score: int = Field(ge=0, le=99_999_999)
    session_token: str = Field(min_length=20, max_length=200)


class ClaimRequest(BaseModel):
    initials: str = Field(min_length=3, max_length=3)
    claim_token: str = Field(min_length=20, max_length=200)


def _default_store() -> dict:
    return {
        "version": 1,
        "updated_at": None,
        "games": {
            slug: {"initials": "---", "score": 0, "achieved_at": None} for slug in sorted(_GAMES)
        },
    }


def _read_store() -> dict:
    if not _STORE.exists():
        data = _default_store()
        _write_store(data)
        return data
    try:
        data = json.loads(_STORE.read_text(encoding="utf-8"))
        if not isinstance(data.get("games"), dict):
            raise ValueError
    except (OSError, ValueError, json.JSONDecodeError):
        data = _default_store()
        _write_store(data)
    for slug in _GAMES:
        data["games"].setdefault(slug, {"initials": "---", "score": 0, "achieved_at": None})
    return data


def _write_store(data: dict) -> None:
    _STORE.parent.mkdir(parents=True, exist_ok=True)
    temp = _STORE.with_suffix(".tmp")
    backup = _STORE.with_suffix(".bak")
    data["updated_at"] = datetime.now(UTC).isoformat()
    if _STORE.exists():
        with suppress(OSError):
            backup.write_bytes(_STORE.read_bytes())
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temp, _STORE)


def _clean_expired() -> None:
    now = time.time()
    for bucket in (_SESSIONS, _CLAIMS):
        for token in list(bucket):
            if bucket[token]["expires"] < now:
                bucket.pop(token, None)


@router.get("/api/arcade/hall-of-fame")
def hall_of_fame():
    with _LOCK:
        return _read_store()


@router.post("/api/arcade/games/{game_slug}/session")
def start_session(game_slug: str):
    if game_slug not in _GAMES:
        raise HTTPException(404, "Unknown arcade game")
    _clean_expired()
    token = secrets.token_urlsafe(32)
    _SESSIONS[token] = {"game": game_slug, "started": time.time(), "expires": time.time() + 3600}
    with _LOCK:
        current = _read_store()["games"][game_slug]
    return {"session_token": token, "high_score": current}


@router.post("/api/arcade/games/{game_slug}/score")
def submit_score(game_slug: str, body: ScoreRequest):
    _clean_expired()
    session = _SESSIONS.pop(body.session_token, None)
    if not session or session["game"] != game_slug:
        raise HTTPException(400, "Invalid game session")
    elapsed = max(1.0, time.time() - session["started"])
    if elapsed < 5 or body.score > elapsed * 250_000:
        raise HTTPException(400, "Score validation failed")
    with _LOCK:
        current = _read_store()["games"][game_slug]
    if body.score <= int(current["score"]):
        return {"is_high_score": False, "current_high_score": current}
    claim = secrets.token_urlsafe(32)
    _CLAIMS[claim] = {"game": game_slug, "score": body.score, "expires": time.time() + 300}
    return {"is_high_score": True, "score": body.score, "claim_token": claim}


@router.post("/api/arcade/games/{game_slug}/high-score")
def claim_high_score(game_slug: str, body: ClaimRequest):
    initials = body.initials.upper()
    if not re.fullmatch(r"[A-Z0-9]{3}", initials):
        raise HTTPException(400, "Initials must contain three letters or digits")
    _clean_expired()
    claim = _CLAIMS.pop(body.claim_token, None)
    if not claim or claim["game"] != game_slug:
        raise HTTPException(400, "Invalid score claim")
    with _LOCK:
        data = _read_store()
        current = data["games"][game_slug]
        if claim["score"] <= int(current["score"]):
            return {"saved": False, "high_score": current}
        record = {
            "initials": initials,
            "score": claim["score"],
            "achieved_at": datetime.now(UTC).isoformat(),
        }
        data["games"][game_slug] = record
        _write_store(data)
    return {"saved": True, "high_score": record}
