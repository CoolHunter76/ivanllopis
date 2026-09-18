from pathlib import Path

from fastapi.testclient import TestClient

from main import SUPPORTED, app

client = TestClient(app)


def test_new_languages_and_flags():
    for language in ("ru", "zh-Hans", "ja"):
        assert language in SUPPORTED
        assert Path(f"translations/{language}.json").stat().st_size > 0
        assert Path(f"static/icons/flags/{language}.svg").stat().st_size > 0
        response = client.get(f"/{language}")
        assert response.status_code == 200
        assert f'lang="{language}"' in response.text


def test_source_vision_layers_and_accessibility():
    html = client.get("/es").text
    for marker in ("source-vision", "source-base", "source-matrix", "source-canvas", "source-scan"):
        assert marker in html
    css = Path("static/css/site.css").read_text(encoding="utf-8")
    assert "prefers-reduced-motion:reduce" in css
