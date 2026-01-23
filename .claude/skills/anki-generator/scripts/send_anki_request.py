#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict

# Add project root to Python path so we can import from src/
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.anki_connect import DEFAULT_ANKI_CONNECT_URL, invoke


def read_payload_from_file(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def read_payload_from_stdin() -> Dict[str, Any]:
    text = sys.stdin.read()
    return json.loads(text)


def main() -> None:
    parser = argparse.ArgumentParser(description="Send JSON payload to AnkiConnect")
    parser.add_argument("-f", "--file", help="Path to JSON payload file (if omitted, read from stdin)")
    parser.add_argument("-u", "--url", default=DEFAULT_ANKI_CONNECT_URL, help="AnkiConnect URL (default: %(default)s)")
    parser.add_argument("-a", "--action", help="If provided and payload lacks action, treat payload as params for this action")

    args = parser.parse_args()

    try:
        payload: Dict[str, Any]
        if args.file:
            payload = read_payload_from_file(args.file)
        else:
            if sys.stdin.isatty():
                print("Reading from stdin... (Ctrl-D to end)", file=sys.stderr)
            payload = read_payload_from_stdin()

        if "action" not in payload:
            if args.action:
                payload = {"action": args.action, "version": 6, "params": payload}
            else:
                raise ValueError("Payload must include 'action' or provide --action to wrap params.")

        resp = invoke(payload["action"], payload.get("params"), version=payload.get("version", 6), url=args.url)
        output = {"result": resp.result, "error": resp.error}
        print(json.dumps(output, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
