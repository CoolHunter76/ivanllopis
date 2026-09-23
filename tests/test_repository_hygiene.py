from pathlib import Path

FORBIDDEN_TRACKED_PATHS = (
    "main.py.backup",
    "fix_remaining_card_translations.py",
    "site-css-hobbies-addition.css",
    "test_work_life.py",
    "templates/companies.html",
    "static/css/companies.css",
    "scripts/apply-assistant.ps1",
    "scripts/apply-chat-layout-bugfix.py",
    "scripts/apply-chat-visual.py",
    "scripts/apply-seo.ps1",
    "scripts/install-sidecar-js-v5.py",
)

REQUIRED_OPERATIONAL_PATHS = (
    "docs/OPERATIONS.md",
    "docs/CONFIGURATION.md",
    "docs/RELEASE.md",
    "scripts/public_smoke.py",
    "scripts/check-security-headers.sh",
    "server/deploy-ivanllopis",
    "server/deploy-ivanllopis-staging",
    "server/verify-ivanllopis-isolation",
)


def test_consumed_installers_backups_and_legacy_files_are_absent():
    for item in FORBIDDEN_TRACKED_PATHS:
        assert not Path(item).exists(), item


def test_operational_documentation_and_runtime_tools_are_present():
    for item in REQUIRED_OPERATIONAL_PATHS:
        path = Path(item)
        assert path.is_file(), item
        assert path.stat().st_size > 0, item


def test_gitignore_covers_local_and_generated_artifacts():
    source = Path(".gitignore").read_text(encoding="utf-8")
    for pattern in (
        ".env.cv",
        ".venv/",
        "__pycache__/",
        ".pytest_cache/",
        ".ruff_cache/",
        "public-smoke-report.json",
    ):
        assert pattern in source
