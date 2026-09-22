from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

EXPECTED_SECURITY_HEADERS = {
    "x-content-type-options": "nosniff",
    "x-frame-options": "DENY",
    "referrer-policy": "strict-origin-when-cross-origin",
    "permissions-policy": "camera=(), microphone=(), geolocation=(), payment=(), usb=()",
}


def assert_security_headers(response) -> None:
    for name, value in EXPECTED_SECURITY_HEADERS.items():
        assert response.headers[name] == value


def test_security_headers_cover_html_health_static_and_redirects():
    paths = (
        "/es",
        "/health",
        "/static/site.webmanifest",
        "/",
        "/xx",
    )
    for path in paths:
        response = client.get(path, follow_redirects=False)
        assert_security_headers(response)


def test_security_headers_cover_json_atom_head_and_not_modified_responses():
    for feed in ("updates.json", "updates.atom"):
        initial = client.get(f"/es/{feed}")
        head = client.head(f"/es/{feed}")
        not_modified = client.get(
            f"/es/{feed}",
            headers={"If-None-Match": initial.headers["etag"]},
        )

        assert initial.status_code == 200
        assert head.status_code == 200
        assert not_modified.status_code == 304
        for response in (initial, head, not_modified):
            assert_security_headers(response)
