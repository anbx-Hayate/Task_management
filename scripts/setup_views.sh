#!/usr/bin/env bash
# GitHub Projects ビュー作成スクリプト
set -euo pipefail

GH="${GH:-gh}"
OWNER="anbx-Hayate"
PROJECT=3
BASE="users/${OWNER}/projectsV2/${PROJECT}/views"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

create_view() {
  local file="$1"
  echo "Creating view from ${file}..."
  "$GH" api -X POST \
    -H "Accept: application/vnd.github+json" \
    -H "X-GitHub-Api-Version: 2026-03-10" \
    "$BASE" --input "${SCRIPT_DIR}/${file}"
  echo ""
}

create_view view_board.json
create_view view_large_task.json
create_view view_small_task.json
create_view view_time.json

echo "Done. Open: https://github.com/users/${OWNER}/projects/${PROJECT}"
