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


def commit(character):
    return character.ljust(40, character)


def mock_health(monkeypatch, deployment):
    payload = {"status": "ok", "deployment": deployment}
    monkeypatch.setattr(
        public_smoke,
        "request",
        lambda url, method="GET", headers=None: Response(
            200,
            json.dumps(payload).encode(),
            security_headers(),
        ),
    )


def test_verify_health_accepts_exact_deployment_identity(monkeypatch):
    expected_commit = commit("a")
    deployment = {
        "environment": "staging",
        "version": "3.0.3",
        "commit": expected_commit,
    }
    mock_health(monkeypatch, deployment)

    result = public_smoke.verify_health(
        "https://example.test",
        "staging",
        "3.0.3",
        expected_commit,
    )

    assert result["expected"] == deployment
    assert result["published"] == deployment


def test_verify_health_rejects_version_mismatch(monkeypatch):
    expected_commit = commit("a")
    mock_health(
        monkeypatch,
        {
            "environment": "staging",
            "version": "3.0.2",
            "commit": expected_commit,
        },
    )

    with pytest.raises(
        RuntimeError,
        match="deployment version: expected '3.0.3', got '3.0.2'",
    ):
        public_smoke.verify_health(
            "https://example.test",
            "staging",
            "3.0.3",
            expected_commit,
        )


def test_verify_health_rejects_commit_mismatch(monkeypatch):
    expected_commit = commit("a")
    published_commit = commit("b")
    mock_health(
        monkeypatch,
        {
            "environment": "production",
            "version": "3.0.3",
            "commit": published_commit,
        },
    )

    with pytest.raises(
        RuntimeError,
        match=f"deployment commit: expected '{expected_commit}', got '{published_commit}'",
    ):
        public_smoke.verify_health(
            "https://example.test",
            "production",
            "3.0.3",
            expected_commit,
        )


def test_verify_health_rejects_environment_mismatch(monkeypatch):
    expected_commit = commit("a")
    mock_health(
        monkeypatch,
        {
            "environment": "production",
            "version": "3.0.3",
            "commit": expected_commit,
        },
    )

    with pytest.raises(
        RuntimeError,
        match="deployment environment: expected 'staging', got 'production'",
    ):
        public_smoke.verify_health(
            "https://example.test",
            "staging",
            "3.0.3",
            expected_commit,
        )


def test_verify_health_rejects_malformed_expected_commit():
    with pytest.raises(RuntimeError, match="expected deployment commit is not a full Git SHA"):
        public_smoke.verify_health(
            "https://example.test",
            "production",
            "3.0.3",
            "short",
        )


def test_verify_health_rejects_malformed_published_commit(monkeypatch):
    mock_health(
        monkeypatch,
        {
            "environment": "production",
            "version": "3.0.3",
            "commit": "unknown",
        },
    )

    with pytest.raises(
        RuntimeError,
        match="published deployment commit is not a full Git SHA",
    ):
        public_smoke.verify_health(
            "https://example.test",
            "production",
            "3.0.3",
            commit("a"),
        )


def test_verify_feed_checks_head_cache_and_conditional_304(monkeypatch):
    headers_for_response = security_headers()
    headers_for_response.update(
        {
            "Content-Type": "application/json",
            "Cache-Control": "public, max-age=300",
            "ETag": '"feed"',
            "Last-Modified": "Mon, 21 Sep 2026 00:00:00 GMT",
            "Content-Length": "42",
        }
    )

    def fake_request(url, method="GET", headers=None):
        if headers and headers.get("If-None-Match"):
            conditional_headers = security_headers()
            conditional_headers["ETag"] = '"feed"'
            return Response(304, headers=conditional_headers)
        return Response(200, headers=headers_for_response)

    monkeypatch.setattr(public_smoke, "request", fake_request)
    result = public_smoke.verify_feed(
        "https://example.test",
        "updates.json",
        "application/json",
    )
    assert result["etag"] == '"feed"'
