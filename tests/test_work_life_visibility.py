from pathlib import Path

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_work_life_content_is_rendered_and_has_visibility_guard():
    response = client.get("/es/work-life")
    assert response.status_code == 200
    html = response.text
    assert "career-list" in html
    assert "career-entry" in html
    assert "HP Hewlett-Packard" in html
    assert "Repsol" in html
    assert "MAPFRE" in html
    css = Path("static/css/site.css").read_text(encoding="utf-8")
    assert "Work-life visibility regression guard" in css
    assert "opacity: 1 !important" in css
    assert "visibility: visible !important" in css
