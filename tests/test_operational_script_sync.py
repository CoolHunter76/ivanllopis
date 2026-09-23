from pathlib import Path

SYNC_PATH = Path("server/sync-ivanllopis-operational-scripts")
WORKFLOWS = (
    Path(".github/workflows/deploy-staging.yml"),
    Path(".github/workflows/deploy-production.yml"),
)


def test_sync_script_uses_fixed_repositories_and_closed_targets():
    source = SYNC_PATH.read_text(encoding="utf-8")
    assert 'REPOSITORY_DIR="/opt/ivanllopis/app"' in source
    assert 'REPOSITORY_DIR="/opt/ivanllopis/staging"' in source
    assert "production)" in source
    assert "staging)" in source
    assert 'TARGET_GROUP="${1:-}"' in source
    assert "Usage: sync-ivanllopis-operational-scripts production|staging" in source
    assert "No such" not in source


def test_sync_script_validates_and_verifies_every_installation():
    source = SYNC_PATH.read_text(encoding="utf-8")
    assert 'bash -n "$source_path"' in source
    assert 'install -o root -g root -m 0755 "$source_path" "$destination_path"' in source
    assert 'bash -n "$destination_path"' in source
    assert 'cmp --silent "$source_path" "$destination_path"' in source
    assert "trap rollback ERR" in source
    assert "mktemp -d" in source


def test_sync_script_only_names_authorized_executables():
    source = SYNC_PATH.read_text(encoding="utf-8")
    for name in (
        "deploy-ivanllopis",
        "deploy-ivanllopis-staging",
        "verify-ivanllopis-isolation",
        "sync-ivanllopis-operational-scripts",
    ):
        assert name in source
    assert "/usr/local/sbin/$" not in source


def test_deployment_workflows_sync_before_deploying():
    for path in WORKFLOWS:
        source = path.read_text(encoding="utf-8")
        sync_position = source.index("sync-ivanllopis-operational-scripts")
        deploy_position = source.index("sudo /usr/local/sbin/deploy-ivanllopis")
        assert sync_position < deploy_position


def test_sudoers_allows_only_explicit_environment_commands():
    lines = Path("server/ivanllopis-script-sync.sudoers").read_text(encoding="utf-8").splitlines()
    assert lines == [
        "deploy ALL=(root) NOPASSWD: /usr/local/sbin/sync-ivanllopis-operational-scripts production",
        "deploy ALL=(root) NOPASSWD: /usr/local/sbin/sync-ivanllopis-operational-scripts staging",
    ]
