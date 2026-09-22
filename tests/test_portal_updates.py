import json
from datetime import date
from pathlib import Path

from fastapi.testclient import TestClient

from main import SUPPORTED, app
from portal_updates import ALLOWED_STATUSES, load_portal_updates

client = TestClient(app)


def test_portal_updates_exist_for_every_language():
    files = {path.stem for path in Path("data/portal_updates").glob("?.json")}
    files.update(path.stem for path in Path("data/portal_updates").glob("??.json"))
    files.update(path.stem for path in Path("data/portal_updates").glob("??-????.json"))
    assert files == set(SUPPORTED)


def test_portal_update_identifiers_and_states_are_consistent():
    reference_ids = None
    for language in SUPPORTED:
        payload = json.loads(
            Path(f"data/portal_updates/{language}.json").read_text(encoding="utf-8")
        )
        items = payload["items"]
        identifiers = [item["id"] for item in items]
        if reference_ids is None:
            reference_ids = identifiers
        assert identifiers == reference_ids
        assert len(identifiers) == len(set(identifiers))
        assert {item["status"] for item in items}.issubset(ALLOWED_STATUSES)
        for item in items:
            if item["date"] is not None:
                date.fromisoformat(item["date"])


def test_evolution_stream_renders_in_every_language(monkeypatch):
    monkeypatch.setenv("V3_PORTAL_ENABLED", "true")
    load_portal_updates.cache_clear()
    for language in SUPPORTED:
        response = client.get(f"/{language}")
        assert response.status_code == 200
        assert 'id="v3-evolution"' in response.text
        assert response.text.count("v3-evolution-item is-") == 4
        assert 'datetime="2026-09-21"' in response.text


def test_portal_updates_are_local_and_accessible():
    source = Path("portal_updates.py").read_text(encoding="utf-8")
    template = Path("templates/home.html").read_text(encoding="utf-8")
    css = Path("static/css/v3-landing.css").read_text(encoding="utf-8")
    assert "urlopen" not in source
    assert "requests" not in source
    assert "aria-labelledby" in template
    assert "<time" in template
    assert "prefers-reduced-motion:reduce" in css
    assert "BUILD d6806f1" in template
