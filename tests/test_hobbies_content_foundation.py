import json
from pathlib import Path

from fastapi.testclient import TestClient

from hobbies_content import HOBBY_SLUGS, load_hobby
from main import SUPPORTED, app

client = TestClient(app)


def test_hobby_data_schema_and_unique_ids():
    for slug in HOBBY_SLUGS:
        payload = json.loads(Path(f"data/hobbies/{slug}.json").read_text(encoding="utf-8"))
        assert {"slug", "theme", "hero", "categories", "media", "places", "events"}.issubset(
            payload
        )
        identifiers = [item["id"] for item in payload["media"]]
        assert len(identifiers) == len(set(identifiers))
        assert payload["slug"] == slug


def test_all_hobby_detail_routes_render_for_every_language():
    for language in SUPPORTED:
        for slug in HOBBY_SLUGS:
            response = client.get(f"/{language}/hobbies/{slug}")
            assert response.status_code == 200, (language, slug)


def test_gallery_places_events_and_safe_external_links_render():
    for slug in ("drums", "travel", "dance", "sea"):
        html = client.get(f"/es/hobbies/{slug}").text
        assert "data-hobby-detail" in html
        assert "data-hobby-filter" in html
        assert "hobby-media-grid" in html
        assert 'rel="noopener noreferrer"' in html
    assert "Eventos y agenda" in client.get("/es/hobbies/dance").text


def test_hobby_assets_are_local_and_motion_safe():
    css = Path("static/css/hobbies.css").read_text(encoding="utf-8")
    javascript = Path("static/js/hobby-detail.js").read_text(encoding="utf-8")
    assert "Hobbies content foundation V1" in css
    assert "prefers-reduced-motion:reduce" in css
    assert "fetch(" not in javascript


def test_loader_exposes_localized_copy():
    hobby = load_hobby("drums", "es")
    assert hobby["copy"]["title"] == "Batería"


def test_trekking_has_routes_nature_and_pending_content():
    hobby = load_hobby("trekking", "es")
    assert hobby["copy"]["title"] == "Senderismo"
    expected = {"Rutas", "Montaña", "Naturaleza", "Excursiones", "Pendientes"}
    assert expected.issubset(set(hobby["categories"]))
    html = client.get("/es/hobbies/trekking").text
    assert 'data-hobby-slug="trekking"' in html
    assert "Rutas por descubrir" in html


def test_gamer_renders_gallery_and_event_list(monkeypatch):
    import main

    monkeypatch.setattr(
        main,
        "gamer_youtube_data",
        lambda: {
            "available": False,
            "channel_url": "https://www.youtube.com/@CoolHunter76",
            "channel_handle": "@CoolHunter76",
            "live": None,
            "recordings": [],
        },
    )
    html = client.get("/es/hobbies/gamer").text
    assert 'data-hobby-slug="gamer"' in html
    assert 'id="gamer-gallery"' in html
    assert 'id="gamer-events"' in html
    assert "Galería gamer" in html
    assert "Eventos de gaming" in html
    assert "VIII Retromaniacs Arcandreu" in html
    assert "SAGA Barcelona Game Fest" in html
    assert "Google Maps" in html


def test_gamer_events_always_render_an_image(monkeypatch):
    import main

    monkeypatch.setattr(
        main,
        "gamer_youtube_data",
        lambda: {
            "available": False,
            "channel_url": "https://www.youtube.com/@CoolHunter76",
            "channel_handle": "@CoolHunter76",
            "live": None,
            "recordings": [],
        },
    )
    hobby = load_hobby("gamer", "es")
    assert hobby["events"]
    for event in hobby["events"]:
        assert event["image_url"]
        assert event["image_alt"]
        assert event["image_source_url"]
        assert event["image_type"] in {
            "official_poster",
            "official_banner",
            "promotional_banner",
            "official_logo",
            "local_fallback",
        }
    html = client.get("/es/hobbies/gamer").text
    assert html.count("hobby-event-poster") >= len(hobby["events"])
    assert "Fuente del cartel" in html
