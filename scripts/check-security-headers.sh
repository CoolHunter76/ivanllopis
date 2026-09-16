#!/usr/bin/env bash
set -Eeuo pipefail
for host in ivanllopis.net staging.ivanllopis.net; do
  echo "Checking $host"
  headers="$(curl --fail --silent --show-error --head "https://$host")"
  grep -qi '^strict-transport-security:' <<< "$headers"
  grep -qi '^x-content-type-options:' <<< "$headers"
  grep -qi '^x-frame-options:' <<< "$headers"
  grep -qi '^referrer-policy:' <<< "$headers"
done
