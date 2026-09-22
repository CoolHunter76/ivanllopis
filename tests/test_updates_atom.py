from xml.etree import ElementTree

from fastapi.testclient import TestClient

from main import SUPPORTED, app

client = TestClient(app)
ATOM = {"atom": "http://www.w3.org/2005/Atom"}


def test_localized_atom_feed_contract():
    for language in SUPPORTED:
        response = client.get(f"/{language}/updates.atom")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("application/atom+xml")
        assert response.headers["cache-control"] == "public, max-age=300"
        root = ElementTree.fromstring(response.content)
        assert root.tag == "{http://www.w3.org/2005/Atom}feed"
        assert root.attrib["{http://www.w3.org/XML/1998/namespace}lang"] == language
        entries = root.findall("atom:entry", ATOM)
        assert len(entries) == 3
        identifiers = [entry.findtext("atom:id", namespaces=ATOM) for entry in entries]
        assert all(
            identifier.startswith(f"http://testserver/{language}/updates/")
            for identifier in identifiers
        )
        assert all("project-world-evolution" not in identifier for identifier in identifiers)


def test_atom_autodiscovery_and_visible_link():
    for language in SUPPORTED:
        html = client.get(f"/{language}/updates").text
        expected = f"https://ivanllopis.net/{language}/updates.atom"
        assert 'type="application/atom+xml"' in html
        assert f'href="{expected}"' in html
        assert f'href="/{language}/updates.atom"' in html


def test_atom_feed_is_not_in_sitemap_and_unknown_language_redirects():
    assert "updates.atom" not in client.get("/sitemap.xml").text
    response = client.get("/xx/updates.atom", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/es/updates.atom"
