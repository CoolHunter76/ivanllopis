# GitFlow pipelines for IvanLlopis.net

Baseline:

- Current production: `master` at `v1.7.0`.
- Integration branch: `develop`.
- Next planned feature release: `release/1.8.0` and tag `v1.8.0`.
- Next urgent production patch: `hotfix/1.7.1` and tag `v1.7.1`.

Included pipelines:

1. `ci.yml`: validates pull requests to `develop` and `master`, plus pushes to `develop`.
2. `gitflow-policy.yml`: enforces valid GitFlow source and target branch combinations.
3. `deploy-production.yml`: deploys only after a merge or push reaches `master`.
4. `release-tag.yml`: validates semantic version tags and confirms that they belong to `master`.

The production deployment uses the GitHub environment `production` and these secrets:

- `VPS_HOST`
- `VPS_USER`
- `VPS_SSH_PRIVATE_KEY`
