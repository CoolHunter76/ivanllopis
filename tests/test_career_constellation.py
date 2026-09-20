from pathlib import Path

from fastapi.testclient import TestClient

from main import CLIENT_EXPERIENCES, SUPPORTED, app

client = TestClient(app)


def test_constellation_v2_renders_with_equal_food_brands():
    for language in SUPPORTED:
        html = client.get(f"/{language}/work-life").text
        assert "digital-universe" in html
        assert 'data-orb="caixabank"' in html
        assert 'data-orb="idilia"' in html and 'data-orb="adam"' in html
        assert html.count('href="#experience-food_sector"') == 2
        assert 'data-orb="nutrexpa"' not in html


def test_caixabank_links_are_semantically_restricted():
    js = Path("static/js/site.js").read_text(encoding="utf-8")
    assert "caixabank:invercaixa" in js
    assert "caixabank:fundacion_caixa" in js
    assert "caixabank:servihabitat" in js
    assert "caixabank:mapfre" not in js


def test_food_card_has_two_equal_logos_and_relational_database_context():
    html = client.get("/es/work-life").text
    assert "food-brand-pair" in html
    assert "idilia-foods.webp" in html and "adam-foods.webp" in html
    assert "Nutrexpa" in html
    food = next(x for x in CLIENT_EXPERIENCES if x["id"] == "food_sector")
    assert "Relational Databases" in food["technologies"]
    css = Path("static/css/site.css").read_text(encoding="utf-8")
    assert ".brand-orb-food{--size:120px}" in css


def test_required_brand_assets_exist_and_no_nutrexpa_logo():
    for name in (
        "caixabank.svg",
        "fundacion-la-caixa.svg",
        "servihabitat.svg",
        "idilia-foods.webp",
        "adam-foods.webp",
    ):
        assert Path("static/images/companies", name).stat().st_size > 0
    assert not Path("static/images/companies/nutrexpa.svg").exists()


def test_constellation_respects_performance_and_accessibility_guards():
    css = Path("static/css/site.css").read_text(encoding="utf-8")
    js = Path("static/js/site.js").read_text(encoding="utf-8")
    assert "prefers-reduced-motion:reduce" in css
    assert "IntersectionObserver" in js and "document.hidden" in js


def test_contact_cv_and_resend_contract_is_untouched():
    source = Path("main.py").read_text(encoding="utf-8")
    assert "RESEND_API_KEY" in source
    assert '"reply_to": body.email' in source
    assert source.count("resend.Emails.send(") >= 2
