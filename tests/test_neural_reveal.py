from pathlib import Path

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_neural_reveal_layers_and_assets():
    html = client.get("/es").text
    for marker in (
        "neural-reveal",
        "neural-with-glasses",
        "neural-without-glasses",
        "neural-glasses",
        "cyber-hand",
        "neural-canvas",
    ):
        assert marker in html
    assert Path("static/images/hero-transparent-without-glasses.png").stat().st_size > 0


def test_neural_reveal_accessibility_and_timing():
    css = Path("static/css/site.css").read_text(encoding="utf-8")
    javascript = Path("static/js/site.js").read_text(encoding="utf-8")
    assert "prefers-reduced-motion:reduce" in css
    assert "18000" in javascript
    assert "14000" in javascript
