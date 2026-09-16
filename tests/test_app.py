import json
from pathlib import Path

from fastapi.testclient import TestClient

from main import SUPPORTED, app

client = TestClient(app)


def test_health_contract():
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert set(payload["languages"]) == set(SUPPORTED)


def test_root_redirects_to_spanish():
    response = client.get("/", follow_redirects=False)
    assert response.status_code in {301, 302, 307, 308}
    assert response.headers["location"] == "/es"


def test_all_language_routes():
    for language in SUPPORTED:
        response = client.get(f"/{language}")
        assert response.status_code == 200, language
        assert f'lang="{language}"' in response.text


def test_all_hobbies_routes():
    for language in SUPPORTED:
        assert client.get(f"/{language}/hobbies").status_code == 200


def test_unknown_language_redirects():
    response = client.get("/xx", follow_redirects=False)
    assert response.status_code in {301, 302, 307, 308}
    assert response.headers["location"] == "/es"


def test_translation_files_and_keys():
    paths = sorted(Path("translations").glob("*.json"))
    assert {path.stem for path in paths} == set(SUPPORTED)
    reference = None
    for path in paths:
        keys = set(json.loads(path.read_text(encoding="utf-8")))
        if reference is None:
            reference = keys
        assert keys == reference, path.name
