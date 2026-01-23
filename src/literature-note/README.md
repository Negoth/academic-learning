# Create Literature Note CLI

Interactive literature note creation tool with BibTeX integration and vim-style navigation.

## Prerequisites

1. **bibtexparser**: Install with `uv add bibtexparser`
2. **BibTeX file**: Either:
   - Symlink at `src/literature-note/references.bib`
   - Or default path: `~/Zotero/better-bibtex/My Library.bib`

## Usage

```bash
# Run directly
python src/literature-note/create_literature_note_cli.py

# Or via shell script
./scripts/create_literature_note_cli.sh
```

## Actions

### create-reference

Creates a reference note for a BibTeX entry:
- Parses your BibTeX file and displays entries sorted by year (newest first)
- Creates a directory: `literature-notebook/<citekey>-<year>-<title-slug>/`
- Creates reference note with structured sections for reading comprehension

### create-subnote

Creates sub-notes within an existing reference directory:

| Type | Description |
|------|-------------|
| `chapter` | Chapter-level notes (e.g., `ch1-introduction.md`) |
| `section` | Section-level notes (e.g., `sec2_5-methods.md`) |
| `concept` | Concept notes linked to a parent note |

Sub-notes are automatically linked in the "Related Notes" section of their parent.

## Navigation

| Key | Action |
|-----|--------|
| `j` / `↓` | Move down |
| `k` / `↑` | Move up |
| `gg` | Jump to top |
| `G` | Jump to bottom |
| `Enter` | Select |
| `q` | Quit |

## Reference Selection

- Type a number to select from the displayed list
- Type text to search by citekey or title
- Exact citekey matches are selected immediately

## Output Structure

```
literature-notebook/
└── author-2024-paper-title/
    ├── author-2024-reference-note.md
    ├── ch1-introduction.md
    ├── ch2-methods.md
    ├── sec2_1-data-collection.md
    └── bayesian-inference.md (concept note)
```

## Reference Note Template

Includes structured sections:
- Before You Read (5 guiding questions)
- Notes (Keywords, Memo, Summary)
- Post-Reading Assessment
- Questions
