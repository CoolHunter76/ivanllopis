from fastapi.testclient import TestClient

import assistant
from main import app

client = TestClient(app)


def test_disabled(monkeypatch):
    monkeypatch.setenv("AI_ASSISTANT_ENABLED", "false")
    assert client.get("/api/assistant/status").json() == {
        "enabled": False,
        "model": None,
    }
    response = client.post("/api/assistant/chat", json={"message": "Hola"})
    assert response.status_code == 404


def test_success(monkeypatch):
    monkeypatch.setenv("AI_ASSISTANT_ENABLED", "true")
    monkeypatch.setattr(
        assistant,
        "call_ollama",
        lambda payload: "Respuesta pública",
    )
    response = client.post(
        "/api/assistant/chat",
        json={"message": "Tecnologías", "language": "es"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "answer": "Respuesta pública",
        "model": assistant.OLLAMA_MODEL,
    }


def test_limits(monkeypatch):
    monkeypatch.setenv("AI_ASSISTANT_ENABLED", "true")
    assert client.post(
        "/api/assistant/chat",
        json={"message": "x" * 501},
    ).status_code == 422

    history = [{"role": "user", "content": str(index)} for index in range(7)]
    response = client.post(
        "/api/assistant/chat",
        json={"message": "Hola", "history": history},
    )
    assert response.status_code == 422


def test_widget(monkeypatch):
    monkeypatch.setenv("AI_ASSISTANT_ENABLED", "true")
    html = client.get("/es").text
    assert 'id="ai-toggle"' in html
    assert 'id="ai-chat-shell"' in html
    assert 'id="ai-close"' in html
    assert "/static/images/ai-robot-floating.png" in html


def test_widget_is_not_injected_when_disabled(monkeypatch):
    monkeypatch.setenv("AI_ASSISTANT_ENABLED", "false")
    assert 'id="ai-toggle"' not in client.get("/es").text
