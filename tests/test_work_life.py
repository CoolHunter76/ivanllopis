import json
from pathlib import Path

from fastapi.testclient import TestClient

from main import SUPPORTED, app

client = TestClient(app)


def test_work_life_routes_render_in_all_languages():
    for language in SUPPORTED:
        response = client.get(f"/{language}/work-life", follow_redirects=False)
        assert response.status_code == 200
        for marker in (
            "career-list",
            "career-entry",
            "HP Hewlett-Packard",
            "Repsol",
            "MAPFRE",
            "ADIF",
            "EnergyaVM",
        ):
            assert marker in response.text


def test_home_and_work_life_navigation_are_present():
    for language in SUPPORTED:
        html = client.get(f"/{language}").text
        assert f'href="/{language}"' in html
        assert f'href="/{language}/work-life"' in html


def test_work_life_translation_structure_is_consistent():
    structures = []
    for path in sorted(Path("translations").glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        structures.append(_shape(data["work_life"]))
    assert len(set(structures)) == 1


def _shape(value):
    if isinstance(value, dict):
        return tuple((key, _shape(item)) for key, item in sorted(value.items()))
    if isinstance(value, list):
        return tuple(_shape(item) for item in value)
    return type(value).__name__
