# Academic Learning Environment Template

A comprehensive template for academic learning, note-taking, and productivity enhancement using Claude Code (claude.ai/code).

## Features

- **AI-Assisted Learning**: Claude Code agents for tutoring, proofreading, and LaTeX help
- **Anki Integration**: Generate flashcards from markdown notes via AnkiConnect
- **Literature Notes**: BibTeX-integrated note-taking for academic papers
- **Language Learning**: English and French tutors with Anki card generation
- **VS Code Integration**: Snippets, workspace settings, and recommended extensions

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url> learn
cd learn

# Install Python dependencies with uv
uv sync
```

### 2. Replicate Anki Structure (Optional)

If you want to use the Anki integration, first install [Anki](https://apps.ankiweb.net/) and the [AnkiConnect](https://ankiweb.net/shared/info/2055492159) add-on.

Then replicate the note types and decks:

```bash
# Make sure Anki is running
# Create the decks first
uv run python .claude/skills/anki-generator/replicate_anki_structure.py \
  -n .claude/skills/anki-generator/anki_note_types.json \
  -d decks.json
```

**Note**: You are encouraged to replicate the Anki setup as Claude Code and scripts are optimised for the structure. Please be sure to update `.claude/` documents if your own Anki setup.

### 3. Setup Literature Notes (Optional)

For literature note creation, symlink your Zotero BibTeX export:

```bash
# If using Zotero with Better BibTeX
ln -s ~/Zotero/better-bibtex/My\ Library.bib src/literature-note/references.bib
```

### 4. Open in VS Code

```bash
code learn.code-workspace
```

## Project Structure

```
learn/
|-- .claude/                          # Claude Code configuration
|   |-- agents/                       # AI tutors and assistants
|   |   |-- english-tutor.md          # English language tutor
|   |   |-- tex-mentor.md             # LaTeX/TeX expert
|   |   +-- academic-proofreader.md   # Writing reviewer
|   |-- commands/                     # Slash commands
|   |   |-- anki-academic.md          # /anki-academic
|   |   |-- anki-english.md           # /anki-english
|   |   |-- anki-french.md            # /anki-french
|   |   |-- anki-math-stat.md         # /anki-math-stat
|   |   +-- tag.md                    # /tag
|   +-- skills/                       # Agent skills
|       +-- anki-generator/           # Anki card generation
|           |-- SKILL.md
|           |-- note-type.json
|           |-- anki_note_types.json  # Anki structure export
|           |-- decks.json            # Anki deck set
|           |-- replicate_anki_structure.py
|           +-- scripts/
|-- .vscode/                          # VS Code configuration
|   +-- learn.code-snippets           # Markdown snippets
|-- projects/                         # Your projects and coursework
|-- literature-notebook/              # Literature notes
|-- scripts/                          # CLI scripts
|   |-- create_literature_note_cli.sh
|   |-- create_note_cli.sh
|   +-- send_anki_request.py
|-- src/                              # Python modules
|   |-- anki_connect/                 # AnkiConnect wrapper
|   |-- create-note/                  # Note creation CLI
|   +-- literature-note/              # Literature note CLI
|-- images/                           # Image assets
|-- tmp/                              # Temporary files
|-- CLAUDE.md                         # Claude Code instructions
|-- pyproject.toml                    # Python dependencies
+-- learn.code-workspace              # VS Code workspace
```

## Usage

### Claude Code Commands

Available slash commands when using Claude Code:

| Command | Description |
|---------|-------------|
| `/anki-academic` | Generate flashcards from academic markdown |
| `/anki-english` | Create English vocabulary Anki cards |
| `/anki-french` | Create French vocabulary Anki cards |
| `/anki-math-stat` | Generate math/statistics flashcards |
| `/tag` | Auto-tag markdown files |

### CLI Scripts

```bash
# Create a new literature note
./scripts/create_literature_note_cli.sh

# Create a general note
./scripts/create_note_cli.sh

# Send Anki request manually
uv run python scripts/send_anki_request.py -f tmp/anki_request.json
```

### VS Code Snippets

| Prefix | Description |
|--------|-------------|
| `sect` | Section link |
| `img` | Image link |
| `imgcap` | Image with caption |
| `3h` | Level 3 header |
| `4h` | Level 4 header |
| `cb` | Checkbox |
| `tip` | Tip callout |
| `note` | Note callout |
| `aigen` | AI-generated content disclaimer |

## Anki Note Types

The template includes these note types:

| Note Type | Fields | Description |
|-----------|--------|-------------|
| `academic_cloze` | title, Text, figures, image, spoiler, source | Academic cloze deletions |
| `language_cloze` | Text, clozeHint, hintNegative, followUp | Language learning cloze |
| `language_pattern` | source, description1-5, sentence1-5, ... | Synonym patterns |
| `language_polysemy` | vocabulary, pronunciation, definitions, ... | Multiple meanings |
| `language_vocab` | front, back, pronunciation | Basic vocabulary |
| `image_occlusion` | Occlusion, Image, Header, ... | Image-based learning |

## Recommended Tools

- **Linear + GitHub CLI**: For issue and PR management with Linear integration
  - Install: `npm install -g linear-github-cli`
  - Repository: <https://github.com/Negoth/linear-github-cli>
  - Commands: `lg create-parent`, `lg create-sub`

## Dependencies

Python packages (managed with uv):
- numpy, pandas, matplotlib, scipy, scikit-learn, seaborn
- jupyter, ipython, ipykernel
- markitdown
- python-dotenv, requests, pyyaml, bibtexparser

## License

MIT
