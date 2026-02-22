---
description: Generate Anki cards from academic content
---

Generate Anki flashcards from academic content (general academic subjects) – $ARGUMENTS.

**Target Deck:** `Learn::Academic`

**Typical content:** Development economics, global development, econometrics, and other academic subjects

## Instructions

1. Invoke the Anki Generator skill: @.claude/skills/anki-generator/SKILL.md

2. Process content based on $ARGUMENTS:
   - **If $ARGUMENTS is a file path(s)**: Process the markdown file(s) directly
   - **If $ARGUMENTS is a brief description**: Extract relevant content from the conversation history based on the description, then create Anki cards from that content

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

# From conversation content
/anki-academic standard errorについて
/anki-academic 先ほどの回帰分析の説明から
```
