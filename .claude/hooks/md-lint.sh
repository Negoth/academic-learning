#!/usr/bin/env bash
# Runs markdownlint --fix on any .md file after Edit or Write.
input=$(cat)
file_path=$(echo "$input" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('tool_input', {}).get('file_path', ''))" 2>/dev/null)

if [[ "$file_path" == *.md ]]; then
  npx markdownlint-cli --fix "$file_path" 2>/dev/null
fi
