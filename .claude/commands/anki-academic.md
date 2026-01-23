---
description: Generate Anki cards from academic markdown files
---

Generate Anki flashcards from academic content (general academic subjects).

**Target Deck:** `Learn::Academic`

**Typical content:** Development economics, global development, econometrics, and other academic subjects

## Instructions

1. Invoke the Anki Generator skill: @.claude/skills/anki-generator/SKILL.md

2. Process the markdown file(s): $ARGUMENTS

3. Expected content tags:
   - `development/*`
   - `economics/*`
   - `econometrics/*`
   - Other general academic topics

4. Default note type: `academic_cloze` (unless specified otherwise)

5. Follow the complete workflow in the Anki Generator skill to create AnkiConnect JSON requests

## Usage Examples

```bash
# Single file
/anki-academic projects/global-development/notes/aid-effectiveness.md

# Multiple files
/anki-academic projects/economics/notes/*.md
```
