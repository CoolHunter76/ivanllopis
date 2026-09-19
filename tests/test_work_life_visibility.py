from pathlib import Path

from fastapi.testclient import TestClient

from main import SUPPORTED, app

client = TestClient(app)


def test_work_life_recruiter_journey_renders_for_all_languages():
    for language in SUPPORTED:
        html = client.get(f"/{language}/work-life").text
        assert 'id="career-story"' in html
        assert "career-list" in html
        assert "career-entry" in html
        assert f'href="/{language}/request-cv"' in html
        assert "career-scroll-cue" in html


def test_work_life_company_content_and_conversion_are_present():
    html = client.get("/es/work-life").text
    for company in ("HP Hewlett-Packard", "Repsol", "MAPFRE", "ADIF", "EnergyaVM"):
        assert company in html
    assert "work-life-conversion" in html
    css = Path("static/css/site.css").read_text(encoding="utf-8")
    assert "Work-life modern recruiter journey v2" in css
    assert ".career-entry" in css
    assert "opacity:1!important" in css
