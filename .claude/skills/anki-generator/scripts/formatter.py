#!/usr/bin/env python3
"""Format fields for Anki cards with HTML styling.

This module transforms markdown-style bold markers (**word**) into HTML span tags
with specific colors for different note types.

Usage:
    from formatter import format_fields_by_note_type

    fields = {"sentence1": "I'm trying to make it more **efficient**"}
    formatted = format_fields_by_note_type("language_pattern", fields)
"""

from __future__ import annotations

import re
from typing import Any, Dict

# Color constants
ORANGE_COLOR = "rgb(251, 159, 42)"
LIGHT_ORANGE_COLOR = "rgb(255, 170, 127)"

ORANGE_SPAN = f'<span style="color: {ORANGE_COLOR};">{{0}}</span>'
LIGHT_ORANGE_SPAN = f'<span style="color: {LIGHT_ORANGE_COLOR};">{{0}}</span>'


def format_bold_to_span(text: str, color: str = "orange") -> str:
    """Convert **word** to <span style="color: ...">word</span>.

    Args:
        text: Text containing **bold** markers
        color: Either "orange" or "light_orange"

    Returns:
        Text with **bold** replaced by colored spans
    """
    if not text:
        return text

    span_template = ORANGE_SPAN if color == "orange" else LIGHT_ORANGE_SPAN
    return re.sub(r'\*\*(.+?)\*\*', lambda m: span_template.format(m.group(1)), text)


def format_cloze_fields(fields: Dict[str, Any]) -> Dict[str, Any]:
    """Format cloze deletion fields.

    No transformation needed - tutors already generate {{c1::word::hint}} format.

    Args:
        fields: Field dictionary for language_cloze note type

    Returns:
        Unchanged fields dictionary
    """
    return fields


def format_pattern_fields(fields: Dict[str, Any]) -> Dict[str, Any]:
    """Format pattern synonym fields.

    Transforms:
    - sentence: **word** -> <span>[...]</span>
    - sentenceAnswer: **word** -> <span>word</span>

    Args:
        fields: Field dictionary for language_pattern note type

    Returns:
        Fields with HTML formatting applied
    """
    formatted = fields.copy()

    for i in range(1, 6):  # Support up to 5 patterns
        sentence_key = f"sentence{i}"
        answer_key = f"sentenceAnswer{i}"

        if sentence_key in fields and fields[sentence_key]:
            # Replace **word** with [...] wrapped in orange span
            sentence = fields[sentence_key]
            formatted[sentence_key] = re.sub(
                r'\*\*(.+?)\*\*',
                ORANGE_SPAN.format('[...]'),
                sentence
            )

        if answer_key in fields and fields[answer_key]:
            # Replace **word** with word wrapped in orange span
            formatted[answer_key] = format_bold_to_span(fields[answer_key], "orange")

    return formatted


def format_polysemy_fields(fields: Dict[str, Any]) -> Dict[str, Any]:
    """Format polysemy fields.

    No special formatting needed - polysemy fields are plain text.

    Args:
        fields: Field dictionary for language_polysemy note type

    Returns:
        Unchanged fields dictionary
    """
    return fields


def format_vocab_fields(fields: Dict[str, Any]) -> Dict[str, Any]:
    """Format vocabulary fields.

    Transforms:
    - front: **word** -> <span style="color: rgb(255, 170, 127);">word</span>
    - back: **word** -> <span style="color: rgb(255, 170, 127);">word</span>

    Args:
        fields: Field dictionary for language_vocab note type

    Returns:
        Fields with HTML formatting applied (light orange color)
    """
    formatted = fields.copy()

    if "front" in fields and fields["front"]:
        formatted["front"] = format_bold_to_span(fields["front"], "light_orange")

    if "back" in fields and fields["back"]:
        formatted["back"] = format_bold_to_span(fields["back"], "light_orange")

    return formatted


def format_fields_by_note_type(note_type: str, fields: Dict[str, Any]) -> Dict[str, Any]:
    """Apply note-type-specific formatting to fields.

    Args:
        note_type: The Anki note type (e.g., "language_pattern", "language_vocab")
        fields: Dictionary of field names to values

    Returns:
        Formatted fields dictionary with HTML transformations applied

    Example:
        >>> fields = {"sentence1": "Make it more **efficient**"}
        >>> formatted = format_fields_by_note_type("language_pattern", fields)
        >>> print(formatted["sentence1"])
        'Make it more <span style="color: rgb(251, 159, 42);">[...]</span>'
    """
    formatters = {
        "language_cloze": format_cloze_fields,
        "language_pattern": format_pattern_fields,
        "language_polysemy": format_polysemy_fields,
        "language_vocab": format_vocab_fields,
    }

    formatter = formatters.get(note_type)
    if formatter:
        return formatter(fields)

    # For unknown note types, return fields unchanged
    return fields


if __name__ == "__main__":
    # Test the formatter with examples
    print("Testing formatter.py\n")

    # Test pattern formatting
    pattern_fields = {
        "source": "efficient",
        "sentence1": "I'm trying to make the process more **efficient**",
        "sentenceAnswer1": "I'm trying to make the process more efficient",
        "sentence2": "We need to **streamline** the workflow",
        "sentenceAnswer2": "We need to streamline the workflow"
    }

    print("=== Pattern Type ===")
    print("Before:", pattern_fields)
    formatted_pattern = format_fields_by_note_type("language_pattern", pattern_fields)
    print("\nAfter:")
    for key, value in formatted_pattern.items():
        print(f"  {key}: {value}")

    # Test vocab formatting
    vocab_fields = {
        "front": "Someone who is a bit more **reserved**.",
        "back": "A **reserved** person is quiet and shy",
        "pronunciation": "ri'zervd"
    }

    print("\n=== Vocab Type ===")
    print("Before:", vocab_fields)
    formatted_vocab = format_fields_by_note_type("language_vocab", vocab_fields)
    print("\nAfter:")
    for key, value in formatted_vocab.items():
        print(f"  {key}: {value}")

    # Test cloze (should be unchanged)
    cloze_fields = {
        "Text": "Before we go, {{c1::do you have any questions::any questions}}?",
        "clozeHint": "asking questions"
    }

    print("\n=== Cloze Type ===")
    print("Before:", cloze_fields)
    formatted_cloze = format_fields_by_note_type("language_cloze", cloze_fields)
    print("\nAfter:")
    for key, value in formatted_cloze.items():
        print(f"  {key}: {value}")
