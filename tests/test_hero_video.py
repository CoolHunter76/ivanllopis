from pathlib import Path

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_hero_uses_local_video_with_fallbacks():
    html = client.get("/es").text
    assert 'id="hero-video"' in html
    assert "autoplay muted loop playsinline" in html
    assert "/static/videos/ivan-hero.webm" in html
    assert "/static/videos/ivan-hero.mp4" in html
    assert "source-vision" not in html
    for asset in (
        "static/videos/ivan-hero.webm",
        "static/videos/ivan-hero.mp4",
        "static/images/ivan-hero-video-poster.webp",
    ):
        assert Path(asset).stat().st_size > 0


def test_video_is_blended_and_accessible():
    css = Path("static/css/site.css").read_text(encoding="utf-8")
    javascript = Path("static/js/site.js").read_text(encoding="utf-8")
    assert "mix-blend-mode:screen" in css
    assert "mask-image:radial-gradient" in css
    assert "prefers-reduced-motion:reduce" in css
    assert "video.pause()" in javascript
