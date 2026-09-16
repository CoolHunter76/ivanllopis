# Automated environment isolation verification

This package verifies:

- Production repository is on `master`.
- Staging repository is on `develop`.
- Production and staging paths differ.
- Production listens on `127.0.0.1:8000`.
- Staging listens on `127.0.0.1:8001`.
- Neither application port is publicly exposed.
- Different Docker containers serve each environment.
- Staging uses Compose project `ivanllopis-staging`.
- Local and public health endpoints return HTTP 200 and `status: ok`.
- Nginx routes production to 8000 and staging to 8001.
- TLS certificates cover both hostnames.

The GitHub Actions workflow runs manually, after infrastructure changes on `develop` or `master`, and once per day at 05:17 UTC.
