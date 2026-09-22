from pathlib import Path

from fastapi.testclient import TestClient

from main import SUPPORTED, app

client = TestClient(app)
PAGES = ("home", "technologies", "projects", "work-life", "hobbies")
SUFFIXES = {
    "home": "",
    "technologies": "/technologies",
    "projects": "/projects",
    "work-life": "/work-life",
    "hobbies": "/hobbies",
}


def test_v3_navigation_is_global_when_portal_is_enabled(monkeypatch):
    monkeypatch.setenv("V3_PORTAL_ENABLED", "true")
    for page in PAGES:
        html = client.get(f"/es{SUFFIXES[page]}").text
        assert 'class="v3-portal"' in html
        assert "data-v3-header" in html
        assert "data-v3-dock" in html
        assert "v3-navigation.css" in html
        assert "v3-navigation.js" in html
        assert f'data-v3-page="{page}"' in html


def test_exactly_one_current_destination_on_each_page(monkeypatch):
    monkeypatch.setenv("V3_PORTAL_ENABLED", "true")
    for language in SUPPORTED:
        for page in PAGES:
            html = client.get(f"/{language}{SUFFIXES[page]}").text
            assert html.count('aria-current="page"') == 3
            destination = page
            assert html.count(f'data-v3-destination="{destination}" aria-current="page"') == 2


def test_global_navigation_contains_all_destinations_in_every_language(monkeypatch):
    monkeypatch.setenv("V3_PORTAL_ENABLED", "true")
    for language in SUPPORTED:
        for page in PAGES:
            html = client.get(f"/{language}{SUFFIXES[page]}").text
            for suffix in SUFFIXES.values():
                assert html.count(f'href="/{language}{suffix}"') >= 2


def test_matrix_progress_and_accessibility_guards_exist():
    css = Path("static/css/v3-navigation.css").read_text(encoding="utf-8")
    javascript = Path("static/js/v3-navigation.js").read_text(encoding="utf-8")
    template = Path("templates/base.html").read_text(encoding="utf-8")

    assert "data-v3-nav-matrix" in template
    assert "localStorage" in javascript
    assert "matrixBurst" in javascript
    assert "430" in javascript
    assert "210" in javascript
    assert "145" in javascript
    assert "prefers-reduced-motion: reduce" in css
    assert "safe-area-inset-bottom" in Path("static/css/v3-tokens.css").read_text(encoding="utf-8")
    assert "fetch(" not in javascript


def test_v3_portal_is_disabled_by_default(monkeypatch):
    monkeypatch.delenv("V3_PORTAL_ENABLED", raising=False)
    monkeypatch.delenv("V3_LANDING_ENABLED", raising=False)
    html = client.get("/es").text

    assert 'class="v3-portal"' not in html
    assert "data-v3-dock" not in html


def test_legacy_landing_flag_remains_a_temporary_compatibility_fallback(monkeypatch):
    monkeypatch.delenv("V3_PORTAL_ENABLED", raising=False)
    monkeypatch.setenv("V3_LANDING_ENABLED", "true")
    assert 'class="v3-portal"' in client.get("/es/technologies").text


def test_neural_glitch_transition_is_progressive_and_mobile_safe():
    css = Path("static/css/v3-navigation.css").read_text(encoding="utf-8")
    javascript = Path("static/js/v3-navigation.js").read_text(encoding="utf-8")
    template = Path("templates/base.html").read_text(encoding="utf-8")

    assert "data-v3-glitch-layer" in template
    assert "data-v3-main" in template
    assert "v3-glitch-exit" in javascript
    assert "v3-glitch-enter" in javascript
    assert "sessionStorage" in javascript
    assert "v3-content-fragment-out" in css
    assert "v3-content-rebuild" in css
    assert "@media (max-width: 760px)" in css
    assert "prefers-reduced-motion: reduce" in css
