from pathlib import Path

REQUIRED_ASSETS = (
    "static/css/site.css",
    "static/js/site.js",
    "static/images/favicon.ico",
    "static/site.webmanifest",
)


def test_required_assets_exist_and_are_not_empty():
    for asset in REQUIRED_ASSETS:
        path = Path(asset)
        assert path.is_file(), asset
        assert path.stat().st_size > 0, asset


def test_no_insecure_static_urls():
    for template in Path("templates").glob("*.html"):
        assert "http://ivanllopis.net/static" not in template.read_text(encoding="utf-8")
