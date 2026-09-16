# Sprint 6: Staging

## Isolation

- Production: `master`, `/opt/ivanllopis/app`, `127.0.0.1:8000`, `ivanllopis.net`.
- Staging: `develop`, `/opt/ivanllopis/staging`, `127.0.0.1:8001`, `staging.ivanllopis.net`.
- Docker Compose project: `ivanllopis-staging`.

## Trigger

Every push or merged pull request reaching `develop` runs `CD Staging`.
Production continues to deploy only from `master`.
