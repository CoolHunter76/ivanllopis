from pathlib import Path

from fastapi.testclient import TestClient

from main import SUPPORTED, app

client = TestClient(app)


def test_filters_render_and_preserve_server_side_selection():
    response = client.get("/es/updates?status=released&category=DELIVERY&q=staging")
    assert response.status_code == 200
    assert "data-updates-filters" in response.text
    assert 'value="released" selected' in response.text
    assert 'value="DELIVERY" selected' in response.text
    assert 'value="staging"' in response.text
    assert 'id="isolated-staging"' in response.text
    assert 'id="landing-v3"' not in response.text


def test_empty_state_and_reset_are_accessible():
    html = client.get("/es/updates?q=does-not-exist").text
    assert "data-update-empty" in html
    assert 'aria-live="polite"' in html
    assert 'href="/es/updates" data-update-reset' in html


def test_localized_json_feed_contract():
    for language in SUPPORTED:
        response = client.get(f"/{language}/updates.json")
        assert response.status_code == 200
        payload = response.json()
        assert payload["language"] == language
        assert len(payload["items"]) == 3
        assert all(item["status"] != "next" for item in payload["items"])
        assert all(item["language"] == language for item in payload["items"])
        assert all(item["url"].endswith(item["id"]) for item in payload["items"])
        assert response.headers["cache-control"] == "public, max-age=300"


def test_feed_is_not_in_sitemap_and_filter_canonical_stays_clean():
    sitemap = client.get("/sitemap.xml").text
    assert "updates.json" not in sitemap
    html = client.get("/es/updates?status=released").text
    assert '<link rel="canonical" href="https://ivanllopis.net/es/updates">' in html


def test_filter_assets_are_local_and_motion_safe():
    javascript = Path("static/js/updates.js").read_text(encoding="utf-8")
    css = Path("static/css/updates.css").read_text(encoding="utf-8")
    assert "fetch(" not in javascript
    assert "URLSearchParams" in javascript
    assert "prefers-reduced-motion:reduce" in css
