#!/usr/bin/env bash
set -euo pipefail

BASE_REF="${1:-origin/main}"
BUF_BIN="${BUF_BIN:-buf}"

git rev-parse --verify "$BASE_REF" >/dev/null
BASE_COMMIT="$(git rev-parse "${BASE_REF}^{commit}")"

PROTO_FILES="$(git ls-tree -r --name-only "$BASE_COMMIT")"
if grep -qE '\.proto$' <<<"$PROTO_FILES"; then
    echo "Existing Protobuf baseline detected; running buf breaking"
    "$BUF_BIN" breaking --against ".git#ref=$BASE_COMMIT"
else
    echo "Initial Protobuf baseline: no breaking comparison is possible"
fi
