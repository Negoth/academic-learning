#!/usr/bin/env bash
# Cleans up /tmp/anki_request.json after send_anki_request.py runs.
input=$(cat)
command=$(echo "$input" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('tool_input', {}).get('command', ''))" 2>/dev/null)

if echo "$command" | grep -q "send_anki_request.py"; then
  trash /tmp/anki_request.json 2>/dev/null || rm -f /tmp/anki_request.json 2>/dev/null
fi
