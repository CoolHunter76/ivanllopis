import json
from pathlib import Path

from fastapi.testclient import TestClient

from main import AI_ENGINES, HOBBIES, SUPPORTED, TECHNOLOGIES, app

client = TestClient(app)


def test_all_routes_and_translations():
    files = sorted(Path("translations").glob("*.json"))
    assert {path.stem for path in files} == set(SUPPORTED)
    structures = []
    for path in files:
        data = json.loads(path.read_text(encoding="utf-8"))
        structures.append(_shape(data))
        assert client.get(f"/{path.stem}").status_code == 200
        assert client.get(f"/{path.stem}/hobbies").status_code == 200
    assert len(set(structures)) == 1


def _shape(value):
    if isinstance(value, dict):
        return tuple((key, _shape(item)) for key, item in sorted(value.items()))
    if isinstance(value, list):
        return tuple(_shape(item) for item in value)
    return type(value).__name__


def test_catalogue_assets_and_official_urls():
    for item in [*TECHNOLOGIES, *AI_ENGINES, *HOBBIES]:
        assert Path(item["icon"].removeprefix("/")).is_file()
        if "url" in item:
            assert item["url"].startswith("https://")


def test_no_mojibake_or_legacy_translation_access():
    for path in [Path("main.py"), *Path("templates").glob("*.html")]:
        text = path.read_text(encoding="utf-8")
        assert "ðŸ" not in text
        assert "âœ" not in text
        assert "t.nav[" not in text
