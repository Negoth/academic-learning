# Create Note CLI

Interactive note creation tool with vim-style navigation.

## Usage

```bash
# Run directly
python src/create-note/create_note_cli.py

# Or via shell script
./scripts/create_note_cli.sh
```

## Note Types

| Type | Description |
|------|-------------|
| `class` | Cornell-style lecture notes with cue/notes/summary sections |
| `brainstorm` | Assignment planning with brief, brainstorm, and plan sections |
| `temp` | Minimal note with just frontmatter and title |

## Location Options

1. **Current directory** - Saves note in the current working directory
2. **projects/** - Select from existing project directories under `projects/`

## Navigation

| Key | Action |
|-----|--------|
| `j` / `↓` | Move down |
| `k` / `↑` | Move up |
| `gg` | Jump to top |
| `G` | Jump to bottom |
| `Enter` | Select |
| `q` | Quit |

## Output

Creates a markdown file with:
- YAML frontmatter (title, project, created, tags)
- Template sections based on note type
- Filename sanitized from title
