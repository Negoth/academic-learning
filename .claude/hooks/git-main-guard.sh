#!/usr/bin/env bash
# Blocks git commit and git push when on the main branch.
input=$(cat)
command=$(echo "$input" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('tool_input', {}).get('command', ''))" 2>/dev/null)

if echo "$command" | grep -qE "git (commit|push)"; then
  branch=$(git -C "$CLAUDE_PROJECT_DIR" branch --show-current 2>/dev/null)
  if [[ "$branch" == "main" ]]; then
    echo "Blocked: currently on 'main' branch. Switch to a feature branch before committing." >&2
    exit 2
  fi
fi
