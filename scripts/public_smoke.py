from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

SECURITY_HEADERS = {
    "x-content-type-options": "nosniff",
    "x-frame-options": "DENY",
    "referrer-policy": "strict-origin-when-cross-origin",
    "permissions-policy": "camera=(), microphone=(), geolocation=(), payment=(), usb=()",
}
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")
FEEDS = (
    ("updates.json", "application/json"),
    ("updates.atom", "application/atom+xml"),
)


def request(url: str, method: str = "GET", headers: dict[str, str] | None = None):
    outbound = Request(url, method=method, headers=headers or {})
    try:
        return urlopen(outbound, timeout=20)
    except HTTPError as error:
        return error
    except URLError as error:
        raise RuntimeError(f"Network error for {url}: {error.reason}") from error


def response_headers(response) -> dict[str, str]:
    return {name.lower(): value for name, value in response.headers.items()}


def assert_equal(label: str, actual, expected) -> None:
    if actual != expected:
        raise RuntimeError(f"{label}: expected {expected!r}, got {actual!r}")


def assert_security_headers(headers: dict[str, str], label: str) -> None:
    for name, expected in SECURITY_HEADERS.items():
        assert_equal(f"{label} header {name}", headers.get(name), expected)


def verify_health(
    base_url: str,
    expected_environment: str,
    expected_version: str,
    expected_commit: str,
) -> dict[str, object]:
    if not COMMIT_PATTERN.fullmatch(expected_commit):
        raise RuntimeError(f"expected deployment commit is not a full Git SHA: {expected_commit!r}")

    response = request(f"{base_url}/health")
    assert_equal("health HTTP status", response.status, 200)
    headers = response_headers(response)
    assert_security_headers(headers, "health")
    payload = json.loads(response.read().decode("utf-8"))
    assert_equal("health status", payload.get("status"), "ok")

    deployment = payload.get("deployment", {})
    published_environment = deployment.get("environment")
    published_version = deployment.get("version")
    published_commit = deployment.get("commit")

    if not COMMIT_PATTERN.fullmatch(published_commit or ""):
        raise RuntimeError(
            f"published deployment commit is not a full Git SHA: {published_commit!r}"
        )

    assert_equal(
        "deployment environment",
        published_environment,
        expected_environment,
    )
    assert_equal("deployment version", published_version, expected_version)
    assert_equal("deployment commit", published_commit, expected_commit)

    return {
        "expected": {
            "environment": expected_environment,
            "version": expected_version,
            "commit": expected_commit,
        },
        "published": {
            "environment": published_environment,
            "version": published_version,
            "commit": published_commit,
        },
    }


def verify_feed(base_url: str, feed: str, expected_media_type: str) -> dict[str, str]:
    url = f"{base_url}/es/{feed}"
    head = request(url, method="HEAD")
    assert_equal(f"{feed} HEAD status", head.status, 200)
    headers = response_headers(head)
    assert_security_headers(headers, f"{feed} HEAD")
    if not headers.get("content-type", "").startswith(expected_media_type):
        raise RuntimeError(f"{feed} has unexpected content type: {headers.get('content-type')!r}")
    assert_equal(
        f"{feed} cache control",
        headers.get("cache-control"),
        "public, max-age=300",
    )
    for name in ("etag", "last-modified", "content-length"):
        if not headers.get(name):
            raise RuntimeError(f"{feed} HEAD is missing {name}")

    conditional = request(url, headers={"If-None-Match": headers["etag"]})
    assert_equal(f"{feed} conditional status", conditional.status, 304)
    conditional_headers = response_headers(conditional)
    assert_security_headers(conditional_headers, f"{feed} 304")
    assert_equal(
        f"{feed} conditional ETag",
        conditional_headers.get("etag"),
        headers["etag"],
    )
    return {"etag": headers["etag"], "last_modified": headers["last-modified"]}


def verify_environment(
    name: str,
    base_url: str,
    expected_environment: str,
    expected_version: str,
    expected_commit: str,
) -> dict[str, object]:
    result: dict[str, object] = {
        "name": name,
        "base_url": base_url,
        "health": verify_health(
            base_url,
            expected_environment,
            expected_version,
            expected_commit,
        ),
        "feeds": {},
    }
    feeds = result["feeds"]
    if not isinstance(feeds, dict):
        raise RuntimeError("internal feed result is invalid")
    for feed, media_type in FEEDS:
        feeds[feed] = verify_feed(base_url, feed, media_type)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run public smoke checks for IvanLlopis.net")
    parser.add_argument("--output", type=Path, default=Path("public-smoke-report.json"))
    parser.add_argument("--production-version", required=True)
    parser.add_argument("--production-commit", required=True)
    parser.add_argument("--staging-version", required=True)
    parser.add_argument("--staging-commit", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    environments = (
        (
            "production",
            "https://ivanllopis.net",
            "production",
            args.production_version,
            args.production_commit,
        ),
        (
            "staging",
            "https://staging.ivanllopis.net",
            "staging",
            args.staging_version,
            args.staging_commit,
        ),
    )
    report: dict[str, object] = {"status": "ok", "environments": []}
    try:
        results = report["environments"]
        if not isinstance(results, list):
            raise RuntimeError("internal environment result is invalid")
        for environment in environments:
            name, base_url, expected_environment, expected_version, expected_commit = environment
            print(f"Checking {name}: {base_url}")
            results.append(
                verify_environment(
                    name,
                    base_url,
                    expected_environment,
                    expected_version,
                    expected_commit,
                )
            )
            print(f"PASS {name}")
    except (RuntimeError, ValueError, json.JSONDecodeError) as error:
        report["status"] = "failed"
        report["error"] = str(error)
        print(f"FAIL {error}", file=sys.stderr)
    args.output.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return 0 if report["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
