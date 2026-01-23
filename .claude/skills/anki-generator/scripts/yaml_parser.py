#!/usr/bin/env python3
"""Parse YAML input from language tutor agents.

This module handles parsing of YAML strings and files, with validation
for the expected structure from language tutor agents.

Usage:
    from yaml_parser import parse_yaml_string, validate_note_structure

    yaml_str = '''
    note_type: language_vocab
    deck: English
    fields:
      front: "Example"
      back: "example"
    tags:
      - language::english
    '''

    note = parse_yaml_string(yaml_str)
    if validate_note_structure(note):
        print("Valid note structure!")
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml


def parse_yaml_string(yaml_str: str) -> Dict[str, Any]:
    """Parse YAML string to dictionary.

    Args:
        yaml_str: YAML-formatted string

    Returns:
        Dictionary representation of YAML

    Raises:
        yaml.YAMLError: If YAML is malformed
    """
    return yaml.safe_load(yaml_str)


def parse_yaml_file(filepath: str) -> Dict[str, Any]:
    """Parse YAML file to dictionary.

    Args:
        filepath: Path to YAML file

    Returns:
        Dictionary representation of YAML file contents

    Raises:
        FileNotFoundError: If file doesn't exist
        yaml.YAMLError: If YAML is malformed
    """
    file_path = Path(filepath)
    if not file_path.exists():
        raise FileNotFoundError(f"YAML file not found: {filepath}")

    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def validate_note_structure(note: Dict[str, Any]) -> bool:
    """Validate that a note dictionary has the required structure.

    Expected structure:
    {
        "note_type": "language_vocab",
        "deck": "English",
        "fields": {"front": "...", "back": "..."},
        "tags": ["language::english"]
    }

    Args:
        note: Note dictionary to validate

    Returns:
        True if structure is valid, False otherwise
    """
    required_keys = {"note_type", "deck", "fields", "tags"}

    # Check all required keys exist
    if not all(key in note for key in required_keys):
        return False

    # Validate types
    if not isinstance(note["note_type"], str):
        return False

    if not isinstance(note["deck"], str):
        return False

    if not isinstance(note["fields"], dict):
        return False

    if not isinstance(note["tags"], list):
        return False

    return True


def parse_multi_note_yaml(yaml_str: str) -> List[Dict[str, Any]]:
    """Parse YAML that may contain multiple notes.

    Handles both single note and multiple note YAML formats.

    Args:
        yaml_str: YAML string (can contain single note or list of notes)

    Returns:
        List of note dictionaries
    """
    data = yaml.safe_load(yaml_str)

    # If data is a list, assume it's multiple notes
    if isinstance(data, list):
        return data

    # If data is a dict with note structure, wrap in list
    if isinstance(data, dict) and validate_note_structure(data):
        return [data]

    # Otherwise, return empty list
    return []


def extract_note_fields(note: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Extract fields from a note dictionary.

    Args:
        note: Note dictionary with expected structure

    Returns:
        Fields dictionary if valid, None otherwise
    """
    if not validate_note_structure(note):
        return None

    return note["fields"]


if __name__ == "__main__":
    # Test the parser with examples
    print("Testing yaml_parser.py\n")

    # Test single note parsing
    single_note_yaml = """
note_type: language_vocab
deck: English
fields:
  front: "Someone who is a bit more reserved."
  back: "A reserved person is quiet and shy"
  pronunciation: "ri'zervd"
tags:
  - language::english::vocabulary
"""

    print("=== Single Note Parsing ===")
    try:
        note = parse_yaml_string(single_note_yaml)
        print(f"Parsed successfully: {note}")
        print(f"Valid structure: {validate_note_structure(note)}")
        print(f"Fields: {extract_note_fields(note)}")
    except yaml.YAMLError as e:
        print(f"Parse error: {e}")

    # Test multiple notes parsing
    multi_note_yaml = """
- note_type: language_cloze
  deck: English
  fields:
    Text: "Before we go, {{c1::do you have any questions::any questions}}?"
    clozeHint: "asking questions"
  tags:
    - language::english::phrases

- note_type: language_vocab
  deck: English
  fields:
    front: "reserved"
    back: "quiet and shy"
  tags:
    - language::english
"""

    print("\n=== Multiple Notes Parsing ===")
    try:
        notes = parse_multi_note_yaml(multi_note_yaml)
        print(f"Parsed {len(notes)} notes")
        for i, note in enumerate(notes, 1):
            print(f"\nNote {i}:")
            print(f"  Type: {note.get('note_type')}")
            print(f"  Deck: {note.get('deck')}")
            print(f"  Valid: {validate_note_structure(note)}")
    except yaml.YAMLError as e:
        print(f"Parse error: {e}")

    # Test invalid structure
    invalid_yaml = """
note_type: language_vocab
fields:
  front: "Example"
"""

    print("\n=== Invalid Structure Test ===")
    try:
        note = parse_yaml_string(invalid_yaml)
        print(f"Parsed: {note}")
        print(f"Valid structure: {validate_note_structure(note)}")
    except yaml.YAMLError as e:
        print(f"Parse error: {e}")
