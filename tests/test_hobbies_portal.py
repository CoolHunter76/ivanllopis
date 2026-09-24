from pathlib import Path

from fastapi.testclient import TestClient

from main import SUPPORTED, app

client = TestClient(app)


def test_hobbies_portal_and_gamer_render_for_every_language(monkeypatch):
    monkeypatch.setenv("V3_PORTAL_ENABLED", "true")
    for language in SUPPORTED:
        portal = client.get(f"/{language}/hobbies")
        gamer = client.get(f"/{language}/hobbies/gamer")
        assert portal.status_code == 200
        assert gamer.status_code == 200
        assert "data-hobbies-portal" in portal.text
        assert f'href="/{language}/hobbies/gamer"' in portal.text
        assert "GAMER" in gamer.text


def test_hobbies_portal_changes_swimming_to_sea_activities():
    html = client.get("/es/hobbies").text
    assert "Actividades en el Mar" in html
    assert "Paddle Surf" in html
    assert "Snorkel" in html
    assert "Navegación" in html
    assert ">Natación<" not in html


def test_gamer_is_the_first_live_hobby_portal():
    html = client.get("/es/hobbies").text
    assert html.count("is-live") == 1
    assert 'class="hobby-portal-card hobby-gaming is-live"' in html


def test_hobbies_assets_are_isolated_and_motion_safe(monkeypatch):
    monkeypatch.setenv("V3_PORTAL_ENABLED", "true")
    html = client.get("/es/hobbies").text
    assert "hobbies.css" in html
    assert "hobbies.js" in html
    css = Path("static/css/hobbies.css").read_text(encoding="utf-8")
    javascript = Path("static/js/hobbies.js").read_text(encoding="utf-8")
    assert "prefers-reduced-motion:reduce" in css
    assert "pointer:coarse" in css
    assert "prefers-reduced-motion: reduce" in javascript


def test_gamer_route_is_in_sitemap():
    sitemap = client.get("/sitemap.xml").text
    for language in SUPPORTED:
        assert f"/{language}/hobbies/gamer" in sitemap
