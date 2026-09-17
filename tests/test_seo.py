import json
import re
from xml.etree import ElementTree

from fastapi.testclient import TestClient

from main import app
from seo import LANGUAGES, ORIGIN

client = TestClient(app)


def get(path, host="ivanllopis.net"):
    return client.get(path, headers={"host": host})


def test_metadata_all_languages():
    for language in LANGUAGES:
        html = get(f"/{language}").text
        assert html.count("<title>") == 1
        assert 'name="description"' in html
        assert f'rel="canonical" href="{ORIGIN}/{language}"' in html
        assert 'hreflang="x-default"' in html
        assert all(f'hreflang="{code}"' in html for code in LANGUAGES)
        match = re.search(
            r'<script type="application/ld\+json">(.*?)</script>',
            html,
            re.DOTALL,
        )
        assert match
        graph = json.loads(match.group(1))["@graph"]
        assert {item["@type"] for item in graph} == {"WebSite", "Person"}


def test_robots_and_staging_noindex(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    assert "Allow: /" in get("/robots.txt").text

    monkeypatch.setenv("APP_ENV", "staging")
    page = get("/es", "staging.ivanllopis.net")
    assert page.headers["x-robots-tag"] == "noindex, nofollow, noarchive"
    assert "noindex, nofollow, noarchive" in page.text
    robots = get("/robots.txt", "staging.ivanllopis.net")
    assert "Disallow: /" in robots.text


def test_sitemap():
    response = get("/sitemap.xml")
    root = ElementTree.fromstring(response.content)
    namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locations = [node.text for node in root.findall("s:url/s:loc", namespace)]
    assert len(locations) == 16
    assert len(set(locations)) == 16
    assert all(url.startswith(ORIGIN) for url in locations)
    assert all("staging." not in url for url in locations)
