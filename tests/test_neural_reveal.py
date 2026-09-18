from pathlib import Path

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_neural_reveal_uses_smooth_image_transition():
    html = client.get("/es").text
    for marker in (
        "neural-reveal",
        "neural-with-glasses",
        "neural-without-glasses",
        "neural-canvas",
        "neural-scan",
    ):
        assert marker in html
    assert "cyber-hand" not in html
    assert "neural-glasses" not in html
    assert Path("static/images/hero-transparent-without-glasses.png").stat().st_size > 0


def test_neural_reveal_accessibility_and_random_timing():
    css = Path("static/css/site.css").read_text(encoding="utf-8")
    javascript = Path("static/js/site.js").read_text(encoding="utf-8")
    assert "glasses-soft-dissolve" in css
    assert "eyes-soft-reveal" in css
    assert "prefers-reduced-motion: reduce" in css
    assert "18000" in javascript
    assert "14000" in javascript
