from pathlib import Path

from fastapi.testclient import TestClient

from main import SUPPORTED, app

client = TestClient(app)
PAGES = ("profile", "capabilities", "technologies", "projects", "work-life", "hobbies")


def test_independent_pages_render_for_every_language():
    for language in SUPPORTED:
        for page in PAGES:
            response = client.get(f"/{language}/{page}")
            assert response.status_code == 200, (language, page)


def test_navigation_is_present_on_every_page():
    for page in PAGES:
        html = client.get(f"/es/{page}").text
        for target in PAGES:
            assert f'href="/es/{target}"' in html


def test_flags_and_company_assets_exist():
    for language in SUPPORTED:
        assert Path(f"static/icons/flags/{language}.svg").stat().st_size > 0
    for slug in ("hp", "repsol", "mapfre", "adif", "energyavm"):
        assert Path(f"static/images/companies/{slug}.svg").stat().st_size > 0
