from pathlib import Path


def test_production_compose_enables_v3_portal():
    compose = Path("compose.yaml").read_text(encoding="utf-8")
    assert 'V3_PORTAL_ENABLED: "true"' in compose


def test_deployment_scripts_validate_exact_identity():
    for path in (
        Path("server/deploy-ivanllopis"),
        Path("server/deploy-ivanllopis-staging"),
    ):
        source = path.read_text(encoding="utf-8")
        assert "verify_health" in source
        assert 'payload.get("status") != "ok"' in source
        assert '"environment": os.environ["EXPECTED_ENVIRONMENT"]' in source
        assert '"version": os.environ["EXPECTED_VERSION"]' in source
        assert '"commit": os.environ["EXPECTED_COMMIT"]' in source
        assert "Deployment identity mismatch" in source


def test_deployment_scripts_reject_unknown_commit_by_exact_comparison():
    for path in (
        Path("server/deploy-ivanllopis"),
        Path("server/deploy-ivanllopis-staging"),
    ):
        source = path.read_text(encoding="utf-8")
        assert 'EXPECTED_COMMIT="$expected_commit"' in source
        assert "deployment != expected" in source
