from pathlib import Path

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


def test_send_cv_request_uses_resend(monkeypatch):
    captured = []
    monkeypatch.setenv("RESEND_API_KEY", "re_test")
    monkeypatch.setenv("CV_MAIL_FROM", "IvanLlopis.net <cv@ivanllopis.net>")
    monkeypatch.setenv("CV_MAIL_TO", "recipient@example.com")

    def fake_send(params):
        captured.append(params)
        return {"id": "email_test"}

    monkeypatch.setattr(main.resend.Emails, "send", fake_send)
    main.send_cv_request(main.CvRequest(**payload()))

    assert len(captured) == 2
    assert captured[0]["from"] == "IvanLlopis.net <cv@ivanllopis.net>"
    assert captured[0]["to"] == ["recipient@example.com"]
    assert captured[0]["reply_to"] == "sender@example.com"
    assert "Example Company" in captured[0]["text"]
    assert captured[1]["to"] == ["sender@example.com"]


def test_send_cv_request_requires_resend_configuration(monkeypatch):
    monkeypatch.delenv("RESEND_API_KEY", raising=False)
    monkeypatch.delenv("CV_MAIL_TO", raising=False)

    try:
        main.send_cv_request(main.CvRequest(**payload()))
    except RuntimeError as error:
        assert str(error) == "CV email service is not configured"
    else:
        raise AssertionError("Expected missing Resend configuration to fail")


def test_send_cv_request_sends_admin_and_requester_receipt(monkeypatch):
    captured = []
    monkeypatch.setenv("RESEND_API_KEY", "re_test")
    monkeypatch.setenv("CV_MAIL_FROM", "IvanLlopis.net <cv@ivanllopis.net>")
    monkeypatch.setenv("CV_MAIL_TO", "owner@example.com")
    monkeypatch.setattr(
        main.resend.Emails, "send", lambda params: captured.append(params) or {"id": "ok"}
    )
    main.send_cv_request(main.CvRequest(**payload(message="Hello <script>alert(1)</script>")))
    assert len(captured) == 2
    assert captured[0]["reply_to"] == "sender@example.com"
    assert captured[1]["to"] == ["sender@example.com"]
    assert "<script>" not in captured[0]["html"]
    assert "&lt;script&gt;" in captured[0]["html"]


def test_cv_page_has_trust_and_success_experience():
    html = client.get("/es/request-cv").text
    assert "request-trust" in html
    assert 'id="cv-form-success"' in html
    assert "request-reassurance" in html


def test_cv_form_is_protected_from_visibility_regressions():
    css = Path("static/css/site.css").read_text(encoding="utf-8")
    assert "Request-CV visibility regression guard" in css
    assert ".form-shell" in css
    html = client.get("/es/request-cv").text
    assert 'id="cv-request-form"' in html
    assert 'name="email"' in html
    assert 'name="message"' in html


def test_cv_emails_follow_request_language(monkeypatch):
    captured = []
    monkeypatch.setenv("RESEND_API_KEY", "re_test")
    monkeypatch.setenv("CV_MAIL_FROM", "IvanLlopis.net <cv@ivanllopis.net>")
    monkeypatch.setenv("CV_MAIL_TO", "owner@example.com")
    monkeypatch.setattr(
        main.resend.Emails, "send", lambda params: captured.append(params) or {"id": "ok"}
    )
    main.send_cv_request(main.CvRequest(**payload(language="es")))
    assert len(captured) == 2
    assert captured[0]["to"] == ["owner@example.com"]
    assert captured[0]["reply_to"] == "sender@example.com"
    assert captured[1]["to"] == ["sender@example.com"]
    assert captured[0]["subject"] == "Nueva solicitud de CV - IvanLlopis.net"
    assert "Nombre / empresa" in captured[0]["html"]
    assert captured[1]["subject"] == "Solicitud de CV recibida - IvanLlopis.net"


def test_cjk_language_codes_and_unicode_email_content(monkeypatch):
    monkeypatch.setenv("RESEND_API_KEY", "re_test")
    monkeypatch.setenv("CV_MAIL_FROM", "IvanLlopis.net <cv@ivanllopis.net>")
    monkeypatch.setenv("CV_MAIL_TO", "owner@example.com")

    for language, expected_text in (("zh-Hans", "简历"), ("ja", "リクエスト")):
        captured = []
        monkeypatch.setattr(
            main.resend.Emails,
            "send",
            lambda params, target=captured: target.append(params) or {"id": "ok"},
        )
        body = main.CvRequest(**payload(language=language))
        main.send_cv_request(body)

        assert body.language == language
        assert len(captured) == 2
        assert captured[0]["to"] == ["owner@example.com"]
        assert captured[0]["reply_to"] == "sender@example.com"
        assert captured[1]["to"] == ["sender@example.com"]
        assert expected_text in captured[0]["subject"] or expected_text in captured[0]["html"]
        assert expected_text in captured[1]["subject"] or expected_text in captured[1]["html"]


def test_zh_hans_api_request_is_not_rejected_by_language_length(monkeypatch):
    monkeypatch.setattr(main, "send_cv_request", lambda body: None)
    response = client.post("/api/cv-request", json=payload(language="zh-Hans"))
    assert response.status_code == 200
