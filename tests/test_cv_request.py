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


def test_cv_mail_defaults_use_ionos_mailbox_and_cv_alias(monkeypatch):
    captured = {}

    class FakeSmtp:
        def __init__(self, host, port, context, timeout):
            captured.update(host=host, port=port, timeout=timeout)

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return False

        def login(self, username, password):
            captured.update(username=username, password=password)

        def send_message(self, message):
            captured.update(
                sender=message["From"],
                recipient=message["To"],
                reply_to=message["Reply-To"],
            )

    for variable in (
        "CV_SMTP_HOST",
        "CV_SMTP_PORT",
        "CV_SMTP_USERNAME",
        "CV_MAIL_FROM",
        "CV_MAIL_TO",
    ):
        monkeypatch.delenv(variable, raising=False)
    monkeypatch.setenv("CV_SMTP_PASSWORD", "test-password")
    monkeypatch.setattr(main.smtplib, "SMTP_SSL", FakeSmtp)

    main.send_cv_request(main.CvRequest(**payload()))

    assert captured == {
        "host": "smtp.ionos.es",
        "port": 465,
        "timeout": 15,
        "username": "contact@ivanllopis.net",
        "password": "test-password",
        "sender": "contact@ivanllopis.net",
        "recipient": "cv@ivanllopis.net",
        "reply_to": "sender@example.com",
    }
