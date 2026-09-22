from fastapi.testclient import TestClient

from main import SUPPORTED, app

client = TestClient(app)
FEEDS = ("updates.json", "updates.atom")
REPRESENTATION_HEADERS = ("cache-control", "content-type", "etag", "last-modified")


def test_head_matches_get_headers_and_has_no_body_in_every_language():
    for language in SUPPORTED:
        for feed in FEEDS:
            get_response = client.get(f"/{language}/{feed}")
            head_response = client.head(f"/{language}/{feed}")

            assert head_response.status_code == 200
            assert head_response.content == b""
            for header in REPRESENTATION_HEADERS:
                assert head_response.headers[header] == get_response.headers[header]
            assert head_response.headers["content-length"] == str(len(get_response.content))


def test_conditional_head_supports_etag_and_last_modified():
    for feed in FEEDS:
        initial = client.get(f"/es/{feed}")
        by_etag = client.head(f"/es/{feed}", headers={"If-None-Match": initial.headers["etag"]})
        by_date = client.head(
            f"/es/{feed}",
            headers={"If-Modified-Since": initial.headers["last-modified"]},
        )

        for response in (by_etag, by_date):
            assert response.status_code == 304
            assert response.content == b""
            assert response.headers["etag"] == initial.headers["etag"]
            assert response.headers["last-modified"] == initial.headers["last-modified"]
            assert response.headers["cache-control"] == "public, max-age=300"


def test_head_if_none_match_keeps_precedence_over_if_modified_since():
    initial = client.get("/es/updates.json")
    response = client.head(
        "/es/updates.json",
        headers={
            "If-None-Match": '"different"',
            "If-Modified-Since": initial.headers["last-modified"],
        },
    )

    assert response.status_code == 200
    assert response.content == b""
    assert response.headers["content-length"] == str(len(initial.content))


def test_unknown_language_head_redirects_to_spanish_feed():
    for feed in FEEDS:
        response = client.head(f"/xx/{feed}", follow_redirects=False)

        assert response.status_code == 307
        assert response.content == b""
        assert response.headers["location"] == f"/es/{feed}"
