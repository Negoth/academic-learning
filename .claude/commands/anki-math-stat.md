---
description: Generate Anki cards from math/statistics markdown files
---

Generate Anki flashcards from mathematics and statistics content.

**Target Deck:** `Learn::Math-Stat`

**Typical content:** Statistics, probability, mathematics, regression analysis, etc.

## Instructions

1. Invoke the Anki Generator skill: @.claude/skills/anki-generator/SKILL.md

2. Process the markdown file(s): $ARGUMENTS

3. Expected content tags:
   - `statistics/*`
   - `mathematics/*`
   - `probability/*`
   - `regression/*`

4. Default note type: `academic_cloze` (unless specified otherwise)

5. Follow the complete workflow in the Anki Generator skill to create AnkiConnect JSON requests

## Usage Examples

```bash
# Single file
/anki-math-stat projects/statistics/notes/regression.md

# Multiple files
/anki-math-stat projects/statistics/notes/Chapter*.md
```
