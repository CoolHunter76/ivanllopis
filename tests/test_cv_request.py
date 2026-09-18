from fastapi.testclient import TestClient

import main
from main import app

client = TestClient(app)


def payload(**overrides):
    data = {
        "name": "Example Company",
        "email": "sender@example.com",
        "phone": "",
        "message": "Please send me an updated copy of the CV.",
        "consent": True,
        "website": "",
        "language": "es",
    }
    data.update(overrides)
    return data


def test_cv_form_routes_render_for_all_languages():
    for language in main.SUPPORTED:
        response = client.get(f"/{language}/request-cv")
        assert response.status_code == 200
        assert 'id="cv-request-form"' in response.text
        assert f'href="/{language}/privacy"' in response.text


def test_cv_request_sends_message(monkeypatch):
    captured = []
    monkeypatch.setattr(main, "send_cv_request", captured.append)
    response = client.post("/api/cv-request", json=payload())
    assert response.status_code == 200
    assert response.json() == {"status": "sent"}
    assert captured[0].email == "sender@example.com"


def test_cv_request_validates_privacy_email_and_honeypot(monkeypatch):
    monkeypatch.setattr(main, "send_cv_request", lambda body: None)
    assert client.post("/api/cv-request", json=payload(consent=False)).status_code == 422
    assert client.post("/api/cv-request", json=payload(email="invalid")).status_code == 422
    assert client.post("/api/cv-request", json=payload(website="spam")).status_code == 400
