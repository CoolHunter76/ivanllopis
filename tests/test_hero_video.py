from pathlib import Path

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_hero_video_is_idle_and_plays_randomly():
    html = client.get("/es").text
    assert 'id="hero-video"' in html
    assert "autoplay" not in html
    assert " loop" not in html
    assert "/static/videos/ivan-hero.webm" in html
    assert "/static/videos/ivan-hero.mp4" in html
    for asset in (
        "static/videos/ivan-hero.webm",
        "static/videos/ivan-hero.mp4",
        "static/images/ivan-hero-video-poster.webp",
    ):
        assert Path(asset).stat().st_size > 0


def test_video_random_scheduler_and_seamless_blend():
    css = Path("static/css/site.css").read_text(encoding="utf-8")
    javascript = Path("static/js/site.js").read_text(encoding="utf-8")
    assert "mix-blend-mode:screen" in css
    assert "mask-image:radial-gradient" in css
    assert 'video.addEventListener("ended"' in javascript
    assert "15000" in javascript
    assert "Math.random()" in javascript
