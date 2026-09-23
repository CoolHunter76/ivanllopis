import json
import re
from pathlib import Path
from xml.etree import ElementTree

from fastapi.testclient import TestClient

from main import SUPPORTED, app
from portal_updates import load_portal_updates, portal_update_detail
from seo import ORIGIN

client = TestClient(app)


def test_every_update_has_a_localized_detail_page(monkeypatch):
    monkeypatch.setenv("V3_PORTAL_ENABLED", "true")
    for language in SUPPORTED:
        data = load_portal_updates(language)
        for update in data["items"]:
            response = client.get(f"/{language}/updates/{update['id']}")
            assert response.status_code == 200
            assert 'class="update-detail-page"' in response.text
            assert update["title"] in response.text
            assert f'href="/{language}/updates"' in response.text


def test_unknown_update_returns_404_and_unknown_language_redirects():
    assert client.get("/es/updates/not-found").status_code == 404
    response = client.get("/xx/updates/landing-v3", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/es/updates/landing-v3"


def test_detail_navigation_and_archive_links_are_stable(monkeypatch):
    monkeypatch.setenv("V3_PORTAL_ENABLED", "true")
    detail = portal_update_detail("es", "neural-navigation")
    assert detail is not None
    assert detail["previous"]["id"] == "landing-v3"
    assert detail["next"]["id"] == "isolated-staging"
    archive = client.get("/es/updates").text
    home = client.get("/es").text
    assert 'href="/es/updates/landing-v3"' in archive
    assert 'href="/es/updates/landing-v3"' in home


def test_detail_seo_uses_canonical_hreflang_and_structured_data():
    html = client.get("/es/updates/landing-v3").text
    assert f'<link rel="canonical" href="{ORIGIN}/es/updates/landing-v3">' in html
    assert f'hreflang="en" href="{ORIGIN}/en/updates/landing-v3"' in html
    payload = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    assert payload
    graph = json.loads(payload.group(1))["@graph"]
    assert any(item["@type"] == "Article" for item in graph)


def test_sitemap_includes_only_published_update_details():
    response = client.get("/sitemap.xml")
    root = ElementTree.fromstring(response.content)
    namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locations = [node.text for node in root.findall("s:url/s:loc", namespace)]
    assert f"{ORIGIN}/es/updates/landing-v3" in locations
    assert f"{ORIGIN}/es/updates/project-world-evolution" not in locations
    assert len(locations) == 156


def test_local_data_has_detail_copy_and_sections():
    for language in SUPPORTED:
        data = json.loads(Path(f"data/portal_updates/{language}.json").read_text(encoding="utf-8"))
        assert {"detail_title", "back_archive", "previous", "next"}.issubset(data["detail"])
        assert all(len(item["sections"]) == 3 for item in data["items"])
