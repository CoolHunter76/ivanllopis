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
    assert 'TARGET_GROUP="${1:-}"' in source
    assert "Usage: sync-ivanllopis-operational-scripts production|staging" in source


def test_sync_refreshes_authorized_branch_before_reading_sources():
    source = SYNC_PATH.read_text(encoding="utf-8")
    assert 'BRANCH="master"' in source
    assert 'BRANCH="develop"' in source
    assert 'git -C "$REPOSITORY_DIR" fetch --prune origin "$BRANCH"' in source
    assert 'git -C "$REPOSITORY_DIR" checkout "$BRANCH"' in source
    assert 'git -C "$REPOSITORY_DIR" reset --hard "origin/$BRANCH"' in source
    assert source.index('reset --hard "origin/$BRANCH"') < source.index(
        'SOURCE_DIR="$REPOSITORY_DIR/server"'
    )


def test_sync_runs_git_as_repository_owner():
    source = SYNC_PATH.read_text(encoding="utf-8")
    assert 'REPOSITORY_OWNER="$(stat -c' in source
    assert 'runuser -u "$REPOSITORY_OWNER" -- git' in source
    assert "Repository branch mismatch" in source


def test_sync_script_validates_and_verifies_every_installation():
    source = SYNC_PATH.read_text(encoding="utf-8")
    assert 'bash -n "$source_path"' in source
    assert 'install -o root -g root -m 0755 "$source_path" "$destination_path"' in source
    assert 'bash -n "$destination_path"' in source
    assert 'cmp --silent "$source_path" "$destination_path"' in source
    assert "trap rollback ERR" in source


def test_deployment_workflows_sync_before_deploying():
    for path in WORKFLOWS:
        source = path.read_text(encoding="utf-8")
        assert source.index("sync-ivanllopis-operational-scripts") < source.index(
            "sudo /usr/local/sbin/deploy-ivanllopis"
        )
