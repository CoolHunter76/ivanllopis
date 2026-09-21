from pathlib import Path

from fastapi.testclient import TestClient

from main import SUPPORTED, app

client = TestClient(app)


def test_v3_navigation_is_isolated_to_landing(monkeypatch):
    monkeypatch.setenv("V3_LANDING_ENABLED", "true")
    landing = client.get("/es")
    technologies = client.get("/es/technologies")

    assert 'class="v3-landing"' in landing.text
    assert "data-v3-dock" in landing.text
    assert "data-v3-header" in landing.text
    assert "v3-navigation.css" in landing.text
    assert "v3-navigation.js" in landing.text
    assert 'class="site-header"' in technologies.text
    assert "data-v3-dock" not in technologies.text
    assert "v3-navigation.css" not in technologies.text


def test_v3_navigation_contains_all_destinations_in_every_language(monkeypatch):
    monkeypatch.setenv("V3_LANDING_ENABLED", "true")
    for language in SUPPORTED:
        html = client.get(f"/{language}").text
        destinations = (
            f"/{language}",
            f"/{language}/technologies",
            f"/{language}/projects",
            f"/{language}/work-life",
            f"/{language}/hobbies",
        )
        for destination in destinations:
            assert html.count(f'href="{destination}"') >= 2


def test_v3_navigation_has_mobile_safety_and_accessibility_guards():
    css = Path("static/css/v3-navigation.css").read_text(encoding="utf-8")
    tokens = Path("static/css/v3-tokens.css").read_text(encoding="utf-8")

    assert "safe-area-inset-bottom" in tokens
    assert "safe-area-inset-top" in tokens
    assert "prefers-reduced-motion: reduce" in css
    assert "min-height: 58px" in css
    assert "max-width: 340px" in css


def test_v3_is_disabled_by_default(monkeypatch):
    monkeypatch.delenv("V3_LANDING_ENABLED", raising=False)
    html = client.get("/es").text

    assert 'class="v3-landing"' not in html
    assert "data-v3-dock" not in html
