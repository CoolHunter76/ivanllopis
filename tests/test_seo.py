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
    for lang in LANGUAGES:
        html = get(f"/{lang}").text
        assert html.count("<title>") == 1
        assert '<meta name="description"' in html
        assert f'<link rel="canonical" href="{ORIGIN}/{lang}">' in html
        assert 'hreflang="x-default"' in html
        assert all(f'hreflang="{code}"' in html for code in LANGUAGES)
        assert '<meta property="og:title"' in html
        assert '<meta name="twitter:card"' in html


def test_json_ld():
    html = get("/es").text
    match = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    assert match
    assert {item["@type"] for item in json.loads(match.group(1))["@graph"]} == {"WebSite", "Person"}


def test_robots_and_staging_noindex(monkeypatch):
    assert "Allow: /" in get("/robots.txt").text
    monkeypatch.setenv("APP_ENV", "staging")
    page = get("/es", "staging.ivanllopis.net")
    assert page.headers["x-robots-tag"] == "noindex, nofollow, noarchive"
    assert "noindex, nofollow, noarchive" in page.text
    assert "Disallow: /" in get("/robots.txt", "staging.ivanllopis.net").text


def test_sitemap():
    response = get("/sitemap.xml")
    root = ElementTree.fromstring(response.content)
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locations = [node.text for node in root.findall("s:url/s:loc", ns)]
    assert len(locations) == 117
    assert len(set(locations)) == 117
    assert all(url.startswith(ORIGIN) and "staging." not in url for url in locations)
