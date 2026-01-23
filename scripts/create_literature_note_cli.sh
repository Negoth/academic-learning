#!/usr/bin/env zsh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
UV_BIN="${UV_BIN:-uv}"
CLI_PATH="$ROOT_DIR/src/literature-note/create_literature_note_cli.py"

if [[ ! -f "$CLI_PATH" ]]; then
  echo "CLI not found: $CLI_PATH" >&2
  exit 1
fi

"$UV_BIN" run python "$CLI_PATH"
