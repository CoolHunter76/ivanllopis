from pathlib import Path

from assistant import WIDGET_HTML
from seo import SEO_IMAGE

REQUIRED_ASSETS = (
    "static/css/site.css",
    "static/css/assistant.css",
    "static/js/site.js",
    "static/js/assistant.js",
    "static/images/favicon.ico",
    "static/images/ai-robot-floating.png",
    "static/images/ivan-hero-transparent.webp",
    "static/site.webmanifest",
)


def test_required_assets_exist_and_are_not_empty():
    for asset in REQUIRED_ASSETS:
        path = Path(asset)
        assert path.is_file(), asset
        assert path.stat().st_size > 0, asset


def test_assistant_widget_references_existing_robot():
    robot_url = "/static/images/ai-robot-floating.png"
    assert robot_url in WIDGET_HTML
    assert Path(robot_url.removeprefix("/")).is_file()


def test_seo_image_exists():
    static_path = SEO_IMAGE.split("/static/", maxsplit=1)[1]
    assert Path("static") / static_path
    assert (Path("static") / static_path).is_file()


def test_no_insecure_static_urls():
    for template in Path("templates").glob("*.html"):
        content = template.read_text(encoding="utf-8")
        assert "http://ivanllopis.net/static" not in content
        assert "http://staging.ivanllopis.net/static" not in content
