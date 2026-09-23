import json
from email.message import Message
from io import BytesIO

import pytest

from scripts import public_smoke


class Response:
    def __init__(self, status, body=b"", headers=None):
        self.status = status
        self._body = BytesIO(body)
        self.headers = Message()
        for name, value in (headers or {}).items():
            self.headers[name] = value

    def read(self):
        return self._body.read()


def security_headers():
    return dict(public_smoke.SECURITY_HEADERS)


def test_verify_health_requires_exact_environment_and_full_commit(monkeypatch):
    payload = {
        "status": "ok",
        "deployment": {
            "environment": "staging",
            "version": "3.0.0.0",
            "commit": "a" * 40,
        },
    }
    monkeypatch.setattr(
        public_smoke,
        "request",
        lambda url, method="GET", headers=None: Response(
            200,
            json.dumps(payload).encode(),
            security_headers(),
        ),
    )
    assert public_smoke.verify_health("https://example.test", "staging")["commit"] == "a" * 40


def test_verify_health_rejects_unknown_commit(monkeypatch):
    payload = {
        "status": "ok",
        "deployment": {
            "environment": "production",
            "version": "3.0.0.0",
            "commit": "unknown",
        },
    }
    monkeypatch.setattr(
        public_smoke,
        "request",
        lambda url, method="GET", headers=None: Response(
            200,
            json.dumps(payload).encode(),
            security_headers(),
        ),
    )
    with pytest.raises(RuntimeError, match="full Git SHA"):
        public_smoke.verify_health("https://example.test", "production")


def test_verify_feed_checks_head_cache_and_conditional_304(monkeypatch):
    headers = {
        **security_headers(),
        "Content-Type": "application/json",
        "Cache-Control": "public, max-age=300",
        "ETag": '"feed"',
        "Last-Modified": "Mon, 21 Sep 2026 00:00:00 GMT",
        "Content-Length": "42",
    }

    def fake_request(url, method="GET", headers=None):
        if headers and headers.get("If-None-Match"):
            conditional_headers = {**security_headers(), "ETag": '"feed"'}
            return Response(304, headers=conditional_headers)
        return Response(200, headers=headers_for_response)

    headers_for_response = headers
    monkeypatch.setattr(public_smoke, "request", fake_request)
    result = public_smoke.verify_feed(
        "https://example.test",
        "updates.json",
        "application/json",
    )
    assert result["etag"] == '"feed"'
