from fastapi.testclient import TestClient

import assistant
from main import app

client = TestClient(app)


def test_disabled(monkeypatch):
    monkeypatch.setenv("AI_ASSISTANT_ENABLED", "false")
    assert client.get("/api/assistant/status").json()["enabled"] is False
    assert client.post("/api/assistant/chat", json={"message": "Hola"}).status_code == 404


def test_success(monkeypatch):
    monkeypatch.setenv("AI_ASSISTANT_ENABLED", "true")
    monkeypatch.setattr(assistant, "call_ollama", lambda payload: "Respuesta pública")
    response = client.post("/api/assistant/chat", json={"message": "Tecnologías", "language": "es"})
    assert response.status_code == 200
    assert response.json()["answer"] == "Respuesta pública"


def test_limits(monkeypatch):
    monkeypatch.setenv("AI_ASSISTANT_ENABLED", "true")
    assert client.post("/api/assistant/chat", json={"message": "x" * 501}).status_code == 422
    history = [{"role": "user", "content": str(i)} for i in range(7)]
    assert (
        client.post("/api/assistant/chat", json={"message": "Hola", "history": history}).status_code
        == 422
    )


def test_widget(monkeypatch):
    monkeypatch.setenv("AI_ASSISTANT_ENABLED", "true")
    assert 'id="ai-toggle"' in client.get("/es").text
