from fastapi.testclient import TestClient

from main import SUPPORTED, app

client = TestClient(app)


def test_health_keeps_existing_contract_and_safe_defaults(monkeypatch):
    for name in ("APP_ENV", "APP_VERSION", "APP_COMMIT"):
        monkeypatch.delenv(name, raising=False)
    payload = client.get("/health").json()
    assert payload["status"] == "ok"
    assert set(payload["languages"]) == set(SUPPORTED)
    assert payload["deployment"] == {
        "environment": "unknown",
        "version": app.version,
        "commit": "unknown",
    }


def test_health_exposes_configured_deployment_identity(monkeypatch):
    monkeypatch.setenv("APP_ENV", "staging")
    monkeypatch.setenv("APP_VERSION", "3.0.0.0")
    monkeypatch.setenv("APP_COMMIT", "c027091")
    payload = client.get("/health").json()
    assert payload["deployment"] == {
        "environment": "staging",
        "version": "3.0.0.0",
        "commit": "c027091",
    }


def test_health_rejects_unsafe_or_malformed_metadata(monkeypatch):
    monkeypatch.setenv("APP_ENV", "staging secret")
    monkeypatch.setenv("APP_VERSION", "<script>")
    monkeypatch.setenv("APP_COMMIT", "not-a-sha")
    payload = client.get("/health").json()
    assert payload["deployment"] == {
        "environment": "unknown",
        "version": app.version,
        "commit": "unknown",
    }
