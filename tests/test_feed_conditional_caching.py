from email.utils import parsedate_to_datetime

from fastapi.testclient import TestClient

from main import SUPPORTED, app

client = TestClient(app)
FEEDS = ("updates.json", "updates.atom")


def test_feeds_expose_stable_cache_validators_in_every_language():
    for language in SUPPORTED:
        for feed in FEEDS:
            first = client.get(f"/{language}/{feed}")
            second = client.get(f"/{language}/{feed}")

            assert first.status_code == 200
            assert first.headers["cache-control"] == "public, max-age=300"
            assert first.headers["etag"] == second.headers["etag"]
            assert first.headers["last-modified"] == second.headers["last-modified"]
            assert first.headers["etag"].startswith('"')
            assert first.headers["etag"].endswith('"')
            assert parsedate_to_datetime(first.headers["last-modified"]).tzinfo is not None


def test_if_none_match_returns_empty_304_for_json_and_atom():
    for feed in FEEDS:
        initial = client.get(f"/es/{feed}")
        response = client.get(f"/es/{feed}", headers={"If-None-Match": initial.headers["etag"]})

        assert response.status_code == 304
        assert response.content == b""
        assert response.headers["etag"] == initial.headers["etag"]
        assert response.headers["last-modified"] == initial.headers["last-modified"]
        assert response.headers["cache-control"] == "public, max-age=300"


def test_weak_and_multiple_etags_are_supported():
    initial = client.get("/es/updates.json")
    etag = initial.headers["etag"]
    response = client.get(
        "/es/updates.json",
        headers={"If-None-Match": f'"other", W/{etag}'},
    )

    assert response.status_code == 304
    assert response.content == b""


def test_if_modified_since_returns_304_and_invalid_date_is_ignored():
    initial = client.get("/es/updates.atom")
    cached = client.get(
        "/es/updates.atom",
        headers={"If-Modified-Since": initial.headers["last-modified"]},
    )
    invalid = client.get(
        "/es/updates.atom",
        headers={"If-Modified-Since": "not-an-http-date"},
    )

    assert cached.status_code == 304
    assert cached.content == b""
    assert invalid.status_code == 200
    assert invalid.content == initial.content


def test_if_none_match_takes_precedence_over_if_modified_since():
    initial = client.get("/es/updates.json")
    response = client.get(
        "/es/updates.json",
        headers={
            "If-None-Match": '"different"',
            "If-Modified-Since": initial.headers["last-modified"],
        },
    )

    assert response.status_code == 200
    assert response.content == initial.content
