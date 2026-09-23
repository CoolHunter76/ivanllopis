from pathlib import Path

from app_version import APP_VERSION, VERSION_FILE, read_version
from main import app

DEPLOYMENT_FILES = (
    Path("server/deploy-ivanllopis"),
    Path("server/deploy-ivanllopis-staging"),
)
COMPOSE_FILES = (
    Path("compose.yaml"),
    Path("deploy/staging/compose.staging.yaml"),
)


def test_version_file_is_the_application_source_of_truth():
    assert Path(__file__).resolve().parents[1] / "VERSION" == VERSION_FILE
    assert read_version() == "3.0.2"
    assert read_version() == APP_VERSION
    assert app.version == APP_VERSION


def test_deployment_scripts_read_version_file_without_hardcoded_release():
    for path in DEPLOYMENT_FILES:
        source = path.read_text(encoding="utf-8")
        assert "< VERSION" in source
        assert 'export APP_VERSION="$(tr -d' in source
        assert "3.0.0.0" not in source
        assert 'APP_VERSION="3.0.2"' not in source


def test_compose_files_do_not_duplicate_the_release_version():
    for path in COMPOSE_FILES:
        source = path.read_text(encoding="utf-8")
        assert 'APP_VERSION: "${APP_VERSION:-}"' in source
        assert "3.0.0.0" not in source
        assert "3.0.2" not in source


def test_main_has_no_hardcoded_release_version():
    source = Path("main.py").read_text(encoding="utf-8")
    assert "version=APP_VERSION" in source
    assert "3.0.0.0" not in source
    assert 'version="3.0.2"' not in source
