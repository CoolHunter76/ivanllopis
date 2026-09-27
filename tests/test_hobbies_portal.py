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


def test_gamer_live_component_is_resilient_and_youtube_ready(monkeypatch):
    import main

    monkeypatch.setattr(
        main,
        "gamer_youtube_data",
        lambda: {
            "available": True,
            "channel_url": "https://www.youtube.com/@CoolHunter76",
            "channel_handle": "@CoolHunter76",
            "live": {"video_id": "ChkWbbPevh4", "title": "Live test"},
            "recordings": [],
        },
    )
    html = client.get("/es/hobbies/gamer").text
    assert "data-gamer-live" in html
    assert "youtube-nocookie.com/embed/ChkWbbPevh4" in html
    assert "@CoolHunter76" in html


def test_gamer_recordings_fallback_and_local_assets(monkeypatch):
    import main

    monkeypatch.setattr(
        main,
        "gamer_youtube_data",
        lambda: {
            "available": True,
            "channel_url": "https://www.youtube.com/@CoolHunter76",
            "channel_handle": "@CoolHunter76",
            "live": None,
            "recordings": [
                {"video_id": "one", "title": "Stream one", "thumbnail": ""},
                {"video_id": "two", "title": "Stream two", "thumbnail": ""},
            ],
        },
    )
    html = client.get("/es/hobbies/gamer").text
    assert "STREAM ARCHIVE" in html
    assert 'id="gamer-recordings"' in html
    assert "youtube-nocookie.com/embed/one" in html
    assert Path("static/js/gamer-live.js").stat().st_size > 0
