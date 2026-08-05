#!/usr/bin/env bash
set -euo pipefail

BASE_REF="${1:-origin/main}"
BUF_BIN="${BUF_BIN:-buf}"

git rev-parse --verify "$BASE_REF" >/dev/null

PROTO_FILES="$(git ls-tree -r --name-only "$BASE_REF")"
if grep -qE '\.proto$' <<<"$PROTO_FILES"; then
    echo "Existing Protobuf baseline detected; running buf breaking"
    "$BUF_BIN" breaking --against ".git#branch=$BASE_REF"
else
    echo "Initial Protobuf baseline: no breaking comparison is possible"
fi
