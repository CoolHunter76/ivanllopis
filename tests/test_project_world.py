from pathlib import Path

from fastapi.testclient import TestClient

import main

client = TestClient(main.app)


def test_projects_promotes_flagship_project():
    html = client.get("/es/projects").text
    assert "flagship-project" in html
    assert 'href="/es/projects/ivanllopis-net"' in html
    assert "PROJECT://WORLD" in html


def test_project_world_renders_for_every_language(monkeypatch):
    monkeypatch.setattr(
        main,
        "project_world_data",
        lambda: {
            "available": False,
            "url": "https://github.com/CoolHunter76/ivanllopis",
            "commits": [],
            "runs": [],
        },
    )
    for language in main.SUPPORTED:
        response = client.get(f"/{language}/projects/ivanllopis-net")
        assert response.status_code == 200
        assert "project-world" in response.text
        assert "CoolHunter76/ivanllopis" in response.text


def test_project_world_assets_exist():
    assert Path("static/js/project-world.js").stat().st_size > 0
    css = Path("static/css/site.css").read_text(encoding="utf-8")
    assert "Project World v1" in css
    assert "prefers-reduced-motion" in css
