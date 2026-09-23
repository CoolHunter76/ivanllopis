from pathlib import Path

from fastapi.testclient import TestClient

from main import SUPPORTED, app

client = TestClient(app)


def test_talento_cercano_renders_for_every_language():
    for language in SUPPORTED:
        response = client.get(f"/{language}/talento-cercano")
        assert response.status_code == 200
        assert "data-talent-page" in response.text
        assert "NeoSamurai" in response.text
        assert "The Dirty Trickers" in response.text


def test_global_navigation_links_to_talento_cercano(monkeypatch):
    monkeypatch.setenv("V3_PORTAL_ENABLED", "true")
    for language in SUPPORTED:
        html = client.get(f"/{language}/talento-cercano").text
        assert f'href="/{language}/talento-cercano"' in html
        assert 'data-v3-destination="talent"' in html


def test_talent_assets_and_motion_guard_exist():
    css = Path("static/css/talento-cercano.css").read_text(encoding="utf-8")
    assert "prefers-reduced-motion:reduce" in css
    assert Path("static/js/talento-cercano.js").stat().st_size > 0
    assert Path("static/images/talento-cercano/neosamurai.webp").stat().st_size > 0
    assert Path("static/videos/talento-cercano/beat-place.mp4").stat().st_size > 0


def test_talent_page_is_in_sitemap():
    sitemap = client.get("/sitemap.xml").text
    for language in SUPPORTED:
        assert f"/{language}/talento-cercano" in sitemap


def test_talent_cloud_navigation_is_present():
    html = client.get("/es/talento-cercano").text
    assert html.count("data-talent-cloud") >= 7
    for talent in ("neosamurai", "beat-place", "dirty-trickers"):
        assert f'href="#{talent}"' in html
    css = Path("static/css/talento-cercano.css").read_text(encoding="utf-8")
    assert ".talent-cloud-field" in css
    assert "clamp(3rem,5.8vw,6rem)" in css


def test_verified_public_links_are_rendered():
    html = client.get("/es/talento-cercano").text
    for marker in (
        "gabysclub.com",
        "ritmoyvida_b52",
        "monosvoladores.com",
        "open.spotify.com/artist/0VpYHtKfeoyFV1StJsKSF3",
        "fenixmetalrock.org",
    ):
        assert marker in html


def test_cloud_navigation_is_inside_hero():
    template = Path("templates/talento_cercano.html").read_text(encoding="utf-8")
    hero_end = template.index("</section>")
    assert template.index("talent-cloud-field-hero") < hero_end
    assert "talent-orbit-stage" not in template


def test_every_talent_has_discovery_links_and_neosamurai_logo():
    from main import TALENTS

    assert len(TALENTS) == 7
    assert all(item["links"] for item in TALENTS)
    neo = next(item for item in TALENTS if item["id"] == "neosamurai")
    assert neo["logo"].endswith("neosamurai-logo.png")
    wilfredo = next(item for item in TALENTS if item["id"] == "wilfredo-lamothe")
    assert wilfredo["name"] == "Wilfredo Lamothe T"
    assert any(label == "INSTAGRAM" for label, _ in wilfredo["links"])


def test_dirty_trickers_instagram_and_gustavo_photo_mark():
    from main import TALENTS

    dirty = next(item for item in TALENTS if item["id"] == "dirty-trickers")
    assert ("INSTAGRAM", "https://www.instagram.com/thedirtytrickers/") in dirty["links"]
    gustavo = next(item for item in TALENTS if item["id"] == "gustavo-alonso")
    assert gustavo["logo"] == gustavo["image"]
    html = client.get("/es/talento-cercano").text
    assert "talent-person-mark" in html


def test_external_talent_links_open_in_new_tab_safely():
    html = client.get("/es/talento-cercano").text
    external_links = (
        "https://www.instagram.com/thedirtytrickers/",
        "https://www.instagram.com/wilfredolamothet/",
        "https://www.instagram.com/ritmoyvida_b52/",
        "https://www.instagram.com/neosamuraiio/",
    )
    for href in external_links:
        marker = f'href="{href}" target="_blank" rel="noopener noreferrer"'
        assert marker in html
