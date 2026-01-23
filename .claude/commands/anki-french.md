---
description: Generate French language learning Anki cards
---

Generate Anki flashcards for French language learning.

**Target Deck:** `French`

**Workflow:** french-tutor agent -> anki-generator skill

## Instructions

Invoke the French Tutor agent: @.claude/agents/french-tutor.md

Pass user arguments: $ARGUMENTS

The agent will:
1. Parse input (YAML file or CLI string)
2. Determine note type from input structure
3. Generate YAML output with French-specific features
4. Delegate to anki-generator skill for HTML formatting and card creation

## Usage Examples

```bash
# YAML file input
/anki-french tmp/language-input.yml

# CLI string input - polysemy
/anki-french polysemy: "courir"

# CLI string input - pattern/synonyms
/anki-french synonyms for "polite"

# CLI string input - vocab
/anki-french vocab: "beautiful landscape in French"

# CLI string input - cloze (sentence with **bold**)
/anki-french "C'est un tres **joli** petit village"
```

## Note Types

- **language_cloze**: Fill-in-the-blank (user bolds words: `**word**`)
- **language_pattern**: Synonym sets (user provides word)
- **language_polysemy**: Multiple meanings (user provides French word)
- **language_vocab**: Simple vocabulary (user describes what they want)

## French-Specific Features

- **Diacritical marks**: Always included (e, e, e, a, u, c, etc.)
- **Gender markers**: Included for nouns (le/la/l'/les)
- **Formal/informal register**: Noted when relevant (tu vs vous)
- **Liaison notes**: Included where applicable

## Input File Format

Create input file and edit `tmp/language-input.yml`:

```yaml
cloze:
  - "Avant de partir, **avez-vous des questions**?"

pattern:
  - "polite"

polysemy:
  - "courir"

vocab:
  - "beautiful landscape in French"
```
