# Literature Note CLI Tool

Interactive CLI tool for creating and organizing literature notes with BibTeX integration.

## Usage

```bash
./scripts/create_literature_note_cli.sh
```

## Features

### Two Main Actions

1. **create-reference** - Create a new reference note from BibTeX entry
2. **create-subnote** - Create chapter/section/concept notes under a reference

### Interactive Menu (action/type selection)

- **Navigation**: `j`/`k` or arrow keys to move, `Enter` to select
- **Jump**: `gg` to top, `G` to bottom
- **Quit**: `q` exits immediately (no Enter needed)

### BibTeX Entry Selection

- **Select**: Enter a number from the displayed list
- **Search**: Type any text to filter by citekey or title
- **Quit**: `q` + Enter to cancel

### Visual Design

- Green `?` prefix for prompts
- Green `>` indicator for selected items
- Cyan highlighting for file paths
- Dim text for help hints
- Success ✓ and warning ⚠ indicators

## Workflow

### Reference Note Creation

1. Select from recent BibTeX entries or search by citekey/title
2. Tool creates directory and reference note automatically

**Directory naming**: `<slug-key>-<year>-<slug-title>/`
**File naming**: `<slug-key>-<year>-reference-note.md`

### Sub-Note Creation

1. Search and select a BibTeX reference (same interface as create-reference)
2. If directory doesn't exist, prompted to create reference note first
3. Choose note type: `chapter`, `section`, or `concept`
4. Enter details (number, title, tags)
5. Note created with automatic linking to parent

#### Chapter Notes

- Filename: `ch<num>-<slug-title>.md`
- Links to: main reference note

#### Section Notes

- Filename: `sec<num>-<slug-title>.md` (dots → underscores)
- Links to: corresponding chapter note (or reference if no chapter)

#### Concept Notes

- Filename: `<slug-title>.md`
- Links to: user-selected note in same directory

## BibTeX Integration

**File locations** (in order of preference):

1. `src/literature-note/references.bib` (symlink)
2. `~/Zotero/better-bibtex/My Library.bib`

**Parsed fields**: citekey, title, authors, year, type, url

## Directory Structure

```
literature-notebook/
├── kawaguchi-sawada-2024-econometrics-of-causal-inference/
│   ├── kawaguchi-sawada-2024-reference-note.md
│   ├── ch1-introduction.md
│   ├── ch2-potential-outcomes.md
│   ├── sec2_3-assumptions.md
│   └── average-treatment-effect.md
└── ...
```

## Technical Details

### Terminal Handling

- Inline rendering with cursor movement (no screen clearing)
- Raw mode for instant key response in menus
- Proper terminal restoration on exit/interrupt
- Signal handlers for SIGINT/SIGTERM cleanup

### Dependencies

- `bibtexparser` - Parse BibTeX files
- Standard library: `pathlib`, `termios`, `tty`, `shutil`

### File Naming Sanitization

- Lowercase, spaces → hyphens
- Remove special characters: `[\\/:*?"<>|]`
- `&` → `and`

## Note Templates

### Reference Note

```yaml
---
title: "{{title}}"
authors: {{authors}}
year: {{year}}
type: {{entry_type}}
citekey: {{citekey}}
url: {{url}}
tags:
printed:
---

## Related Notes

## Before You Read
1. Why am I reading this?
2. What are the authors trying to do in writing this?
3. What are the authors saying that is relevant to what I want to find out?
4. How convincing is what the authors saying?
5. In conclusion, what use can I make of this?

## Notes

### Keywords

## Summary

### Writing Assessment

## Questions
```

### Chapter/Section Note

```yaml
---
title: "{{title}}"
created: {{datetime}}
tags: {{tags}}
---
# {{title}}

## Related Notes
## Keywords
## Memo
## Summary
## Key Concepts
## Important Formulas/Theorems
## Examples
## Questions
```

### Concept Note

```yaml
---
title: "{{title}}"
created: {{datetime}}
tags: {{tags}}
---
# {{title}}

## Related Notes
## Memo
## Definition
## Examples
## Applications
## Questions
```
