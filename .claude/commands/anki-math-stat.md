---
description: Generate Anki cards from math/statistics markdown files
---

Generate Anki flashcards from mathematics and statistics content.

**Target Deck:** `Learn::Math-Stat`

**Typical content:** Statistics, probability, mathematics, regression analysis, etc.

## Instructions

1. Invoke the Anki Generator skill: @.claude/skills/anki-generator/SKILL.md

2. Process content based on $ARGUMENTS:
   - **If $ARGUMENTS is a file path(s)**: Process the markdown file(s) directly
   - **If $ARGUMENTS is a brief description**: Extract relevant content from the conversation history based on the description, then create Anki cards from that content

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
/anki-math-stat projects/QMA-7106A/notes/statistics.md

# Multiple files
/anki-math-stat projects/QMA-7106A/notes/Chapter*.md

# From conversation content
/anki-math-stat t統計量と標準誤差について
/anki-math-stat 先ほどの説明から
```
