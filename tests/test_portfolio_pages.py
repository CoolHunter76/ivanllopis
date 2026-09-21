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
    menu_pages = ("technologies", "projects", "work-life", "hobbies")
    for page in PAGES:
        html = client.get(f"/es/{page}").text
        assert 'href="/es"' in html
        for target in menu_pages:
            assert f'href="/es/{target}"' in html


def test_profile_and_capabilities_are_not_in_main_navigation():
    for page in PAGES:
        html = client.get(f"/es/{page}").text
        nav = html.split('<nav id="site-nav"', 1)[1].split("</nav>", 1)[0]
        assert 'href="/es/profile"' not in nav
        assert 'href="/es/capabilities"' not in nav


def test_flags_and_company_assets_exist():
    for language in SUPPORTED:
        assert Path(f"static/icons/flags/{language}.svg").stat().st_size > 0
    for slug in ("hp", "repsol", "mapfre", "adif", "energyavm"):
        assert Path(f"static/images/companies/{slug}.svg").stat().st_size > 0
