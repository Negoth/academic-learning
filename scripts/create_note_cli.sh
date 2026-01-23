#!/usr/bin/env zsh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
CLI_PATH="$ROOT_DIR/src/create-note/create_note_cli.py"

if [[ ! -f "$CLI_PATH" ]]; then
  echo "CLI not found: $CLI_PATH" >&2
  exit 1
fi

exec "$PYTHON_BIN" "$CLI_PATH"
