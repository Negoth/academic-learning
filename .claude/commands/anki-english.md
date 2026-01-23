---
description: Generate English language learning Anki cards
---

Generate Anki flashcards for English language learning.

**Target Deck:** `English`

**Workflow:** english-tutor agent -> anki-generator skill

## Instructions

Invoke the English Tutor agent: @.claude/agents/english-tutor.md

Pass user arguments: $ARGUMENTS

The agent will:
1. Parse input (YAML file or CLI string)
2. Determine note type from input structure
3. Generate YAML output with proper formatting
4. Delegate to anki-generator skill for HTML formatting and card creation

## Usage Examples

```bash
# YAML file input
/anki-english tmp/language-input.yml

# CLI string input - polysemy
/anki-english polysemy: "stumble"

# CLI string input - pattern/synonyms
/anki-english synonyms for "efficient"

# CLI string input - vocab
/anki-english vocab: "reserved person"

# CLI string input - cloze (sentence with **bold**)
/anki-english "Before we go, **do you have any questions**?"
```

## Note Types

- **language_cloze**: Fill-in-the-blank (user bolds words: `**word**`)
- **language_pattern**: Synonym sets (user provides word)
- **language_polysemy**: Multiple meanings (user provides English word)
- **language_vocab**: Simple vocabulary (user describes what they want)

## Input File Format

Create input file and edit `tmp/language-input.yml`:

```yaml
cloze:
  - "Before we go, **do you have any questions** or **is there anything**?"

pattern:
  - "efficient"
  - "confusing"

polysemy:
  - "lump"
  - "stumble"

vocab:
  - "reserved person"
  - "Shy bairns get nowt (naught)."
```
