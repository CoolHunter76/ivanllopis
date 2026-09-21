from pathlib import Path

from fastapi.testclient import TestClient

from main import SUPPORTED, app

client = TestClient(app)


def test_v3_impact_landing_renders_for_every_language(monkeypatch):
    monkeypatch.setenv("V3_PORTAL_ENABLED", "true")
    for language in SUPPORTED:
        html = client.get(f"/{language}").text
        assert "data-v3-landing" in html
        assert "data-v3-neural-canvas" in html
        assert "CURRENT SIGNAL" in html
        assert "v3-landing.css" in html
        assert "v3-landing.js" in html


def test_landing_has_four_direct_portals(monkeypatch):
    monkeypatch.setenv("V3_PORTAL_ENABLED", "true")
    html = client.get("/es").text
    for destination, suffix in (
        ("technologies", "technologies"),
        ("projects", "projects"),
        ("work-life", "work-life"),
        ("hobbies", "hobbies"),
    ):
        assert f'data-v3-destination="{destination}"' in html
        assert f'href="/es/{suffix}"' in html
    assert html.count("v3-portal-card") >= 4


def test_landing_assets_are_isolated_from_inner_pages(monkeypatch):
    monkeypatch.setenv("V3_PORTAL_ENABLED", "true")
    inner = client.get("/es/technologies").text
    assert "v3-landing.css" not in inner
    assert "v3-landing.js" not in inner
    assert "data-v3-landing" not in inner


def test_landing_performance_and_accessibility_guards():
    css = Path("static/css/v3-landing.css").read_text(encoding="utf-8")
    javascript = Path("static/js/v3-landing.js").read_text(encoding="utf-8")
    template = Path("templates/home.html").read_text(encoding="utf-8")
    assert "prefers-reduced-motion:reduce" in css
    assert "pointer:coarse" in css
    assert "IntersectionObserver" in javascript
    assert "document.hidden" in javascript
    assert "devicePixelRatio" in javascript
    assert "aria-hidden" in template
    assert "autoplay" not in template
