#!/usr/bin/env python3
"""
Replicate Anki decks and note types from JSON export files.

Usage:
    python .claude/skills/anki-generator/replicate_anki_structure.py -n .claude/skills/anki-generator/anki_note_types.json -d data/decks.json
    python .claude/skills/anki-generator/replicate_anki_structure.py -n .claude/skills/anki-generator/anki_note_types.json --url http://localhost:8766
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict, List

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, project_root)

from src.anki_connect import DEFAULT_ANKI_CONNECT_URL, invoke, ensure_deck


def convert_templates_for_create_model(templates: Dict[str, Any]) -> List[Dict[str, str]]:
    """Convert templates from export format to createModel format.

    Export format: {"Card 1": {"Front": "...", "Back": "...", "Name": "Card 1"}}
    createModel format: [{"Name": "Card 1", "Front": "...", "Back": "..."}]
    """
    card_templates = []
    for template_name, template_data in templates.items():
        if isinstance(template_data, dict):
            # Extract Name, Front, Back fields
            card_template = {
                "Name": template_data.get("Name", template_name),
                "Front": template_data.get("Front", ""),
                "Back": template_data.get("Back", ""),
            }
            card_templates.append(card_template)
    return card_templates


def create_model(
    model_name: str,
    fields: List[str],
    templates: Dict[str, Any],
    css: str,
    is_cloze: bool,
    url: str,
    update_existing: bool = False,
) -> None:
    """Create a note type model in Anki."""
    # Check if model already exists
    models_resp = invoke("modelNames", url=url)
    if models_resp.error:
        raise RuntimeError(f"modelNames failed: {models_resp.error}")
    existing_models = set(models_resp.result or [])

    if model_name in existing_models:
        if update_existing:
            print(f"    Model {model_name} already exists. Updating...", file=sys.stderr)
            # Note: AnkiConnect doesn't have a direct updateModel action
            # We could delete and recreate, but that's risky if there are cards
            # For now, we'll skip and warn
            print(f"    Warning: Cannot update existing model {model_name}. Skipping.", file=sys.stderr)
            return
        else:
            print(f"    Model {model_name} already exists. Skipping.", file=sys.stderr)
            return

    # Convert templates to createModel format
    card_templates = convert_templates_for_create_model(templates)

    # Create model
    params: Dict[str, Any] = {
        "modelName": model_name,
        "inOrderFields": fields,
        "cardTemplates": card_templates,
    }
    if css:
        params["css"] = css
    if is_cloze:
        params["isCloze"] = True

    create_resp = invoke("createModel", params, url=url)
    if create_resp.error:
        raise RuntimeError(f"createModel failed for {model_name}: {create_resp.error}")

    print(f"    Created model {model_name}", file=sys.stderr)


def replicate_decks(decks: List[str], url: str) -> None:
    """Create all decks in Anki."""
    print(f"Creating {len(decks)} deck(s)...", file=sys.stderr)
    for i, deck_name in enumerate(decks, 1):
        print(f"  [{i}/{len(decks)}] Creating deck: {deck_name}", file=sys.stderr)
        try:
            ensure_deck(deck_name, url)
            print(f"    Deck '{deck_name}' ready", file=sys.stderr)
        except Exception as e:
            print(f"    Error creating deck {deck_name}: {e}", file=sys.stderr)
            raise


def replicate_note_types(note_types: List[Dict[str, Any]], url: str, update_existing: bool = False) -> None:
    """Create all note types in Anki."""
    print(f"Creating {len(note_types)} note type(s)...", file=sys.stderr)
    for i, note_type in enumerate(note_types, 1):
        model_name = note_type["name"]
        print(f"  [{i}/{len(note_types)}] Creating note type: {model_name}", file=sys.stderr)
        try:
            create_model(
                model_name=model_name,
                fields=note_type["fields"],
                templates=note_type["templates"],
                css=note_type.get("css", ""),
                is_cloze=note_type.get("is_cloze", False),
                url=url,
                update_existing=update_existing,
            )
        except Exception as e:
            print(f"    Error creating note type {model_name}: {e}", file=sys.stderr)
            raise


def replicate_structure(
    note_types_path: str,
    decks_path: str | None,
    url: str,
    update_existing: bool = False,
) -> None:
    """Replicate decks and note types from JSON files."""
    print(f"Connecting to AnkiConnect at {url}...", file=sys.stderr)

    # Load note types
    print(f"Loading note types from {note_types_path}...", file=sys.stderr)
    with open(note_types_path, "r", encoding="utf-8") as f:
        note_types_data = json.load(f)
    note_types = note_types_data.get("note_types", [])
    if not note_types:
        print("Warning: No note types found in JSON file.", file=sys.stderr)
    else:
        print(f"Found {len(note_types)} note type(s) in export.", file=sys.stderr)

    # Load decks (if provided)
    decks: List[str] = []
    if decks_path:
        print(f"Loading decks from {decks_path}...", file=sys.stderr)
        with open(decks_path, "r", encoding="utf-8") as f:
            decks_data = json.load(f)
        decks = decks_data.get("decks", [])
        if not decks:
            print("Warning: No decks found in JSON file.", file=sys.stderr)
        else:
            print(f"Found {len(decks)} deck(s) in configuration.", file=sys.stderr)

    # Replicate decks first (so note types can reference them)
    if decks:
        replicate_decks(decks, url)
        print()

    # Replicate note types
    if note_types:
        replicate_note_types(note_types, url, update_existing)

    print("\nReplication complete!", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Replicate Anki decks and note types from JSON export files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "-n",
        "--note-types",
        required=True,
        help="Path to note types JSON file (from export_anki_structure.py)",
    )
    parser.add_argument(
        "-d",
        "--decks",
        default="data/decks.json",
        help="Path to decks JSON file (default: %(default)s)",
    )
    parser.add_argument(
        "--url",
        default=DEFAULT_ANKI_CONNECT_URL,
        help=f"AnkiConnect URL (default: %(default)s)",
    )
    parser.add_argument(
        "--update-existing",
        action="store_true",
        help="Update existing models (default: skip existing models)",
    )

    args = parser.parse_args()

    # Check if note types file exists
    if not os.path.exists(args.note_types):
        print(f"Error: Note types file not found: {args.note_types}", file=sys.stderr)
        sys.exit(1)

    # Check if decks file exists (if specified)
    decks_path = args.decks if os.path.exists(args.decks) else None
    if args.decks != "data/decks.json" and not decks_path:
        print(f"Warning: Decks file not found: {args.decks}. Skipping deck creation.", file=sys.stderr)

    try:
        replicate_structure(args.note_types, decks_path, args.url, args.update_existing)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
