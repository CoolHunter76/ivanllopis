from pathlib import Path

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_arcade_room_renders():
    response = client.get("/es/hobbies/gamer/arcade")

    assert response.status_code == 200
    assert "ARCADE 76" in response.text
    assert "IVANOID" in response.text
    assert "SKY PATROL" in response.text
    assert "PEDRIS" in response.text
    assert "data-arcade-modal" in response.text


def test_arcade_hall_of_fame_api():
    response = client.get("/api/arcade/hall-of-fame")
    assert response.status_code == 200
    assert "block-breaker-76" in response.json()["games"]


def test_arcade_assets_exist():
    for filename in (
        "static/css/arcade76.css",
        "static/js/arcade76-room.js",
        "templates/gamer_arcade_room.html",
        "arcade76.py",
    ):
        assert Path(filename).is_file()


def test_selected_arcade_games_are_available():
    html = client.get("/es/hobbies/gamer/arcade").text

    selected_slugs = (
        "sky-patrol-76",
        "block-breaker-76",
        "neon-blocks-76",
    )
    for slug in selected_slugs:
        assert f'data-game="{slug}"' in html

    removed_slugs = (
        "gamer-universe-76",
        "platform-quest-76",
        "metal-command-76",
        "island-hero-76",
    )
    for slug in removed_slugs:
        assert f'data-game="{slug}"' not in html

    script = Path("static/js/arcade76-room.js").read_text(encoding="utf-8")
    assert "CABINET UNDER RESTORATION" not in script


def test_pedris_branding_and_assets():
    html = client.get("/es/hobbies/gamer/arcade").text
    assert "PEDRIS" in html
    assert "NEON BLOCKS 76" not in html
    assert Path("static/images/arcade76/pedris-background.png").is_file()
    assert Path("static/images/arcade76/pedris-cover.png").is_file()
    script = Path("static/js/arcade76-room.js").read_text(encoding="utf-8")
    assert '"neon-blocks-76": "PEDRIS"' in script
    assert "#004d98" in script
    assert "#a50044" in script


def test_sky_patrol_artwork_and_updated_pedris_background():
    asset_names = (
        "pedris-background.png",
        "sky-patrol-cover.png",
        "sky-patrol-plane.png",
        "sky-patrol-enemy-plane.png",
    )
    for asset_name in asset_names:
        asset = Path("static/images/arcade76") / asset_name
        assert asset.is_file()
        assert asset.stat().st_size > 0

    template = Path("templates/gamer_arcade_room.html").read_text(encoding="utf-8")
    assert "/static/js/arcade76-room.js?v=5" in template

    script = Path("static/js/arcade76-room.js").read_text(encoding="utf-8")
    assert "sky-patrol-plane.png" in script
    assert "sky-patrol-enemy-plane.png" in script
    assert "pedris-background.png" in script

    stylesheet = Path("static/css/arcade76.css").read_text(encoding="utf-8")
    assert "sky-patrol-cover.png" in stylesheet
