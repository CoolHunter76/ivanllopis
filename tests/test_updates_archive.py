import json
from pathlib import Path

from fastapi.testclient import TestClient

from main import SUPPORTED, app
from portal_updates import load_portal_updates
from seo import ORIGIN

client = TestClient(app)


def test_updates_archive_renders_for_every_language(monkeypatch):
    monkeypatch.setenv("V3_PORTAL_ENABLED", "true")
    for language in SUPPORTED:
        response = client.get(f"/{language}/updates")
        assert response.status_code == 200
        assert 'class="updates-page"' in response.text
        assert 'id="landing-v3"' in response.text
        assert 'id="project-world-evolution"' in response.text
        assert f'href="/{language}/updates"' in client.get(f"/{language}").text


def test_archive_splits_and_sorts_released_and_next_signals():
    for language in SUPPORTED:
        load_portal_updates.cache_clear()
        data = load_portal_updates(language)
        dates = [item["date"] for item in data["published"]]
        assert dates == sorted(dates, reverse=True)
        assert all(item["status"] != "next" for item in data["published"])
        assert all(item["status"] == "next" for item in data["upcoming"])


def test_archive_copy_exists_in_every_local_data_file():
    for language in SUPPORTED:
        data = json.loads(Path(f"data/portal_updates/{language}.json").read_text(encoding="utf-8"))
        assert set(data["archive"]) == {
            "title",
            "intro",
            "published",
            "upcoming",
            "view_all",
            "back",
            "footer",
        }


def test_updates_are_in_sitemap_and_have_deep_links():
    response = client.get("/sitemap.xml")
    assert response.status_code == 200
    assert response.text.count("/updates</loc>") == len(SUPPORTED)
    assert f"{ORIGIN}/es/updates" in response.text
    html = client.get("/es/updates").text
    assert 'href="#landing-v3"' in html
    assert 'href="#project-world-evolution"' in html


def test_updates_archive_has_seo_and_accessibility_guards(monkeypatch):
    monkeypatch.setenv("V3_PORTAL_ENABLED", "true")
    html = client.get("/es/updates").text
    assert '<link rel="canonical" href="https://ivanllopis.net/es/updates">' in html
    assert 'hreflang="en" href="https://ivanllopis.net/en/updates"' in html
    assert 'aria-labelledby="updates-published"' in html
    assert '<time datetime="2026-09-21">' in html
    css = Path("static/css/updates.css").read_text(encoding="utf-8")
    assert "prefers-reduced-motion:reduce" in css
