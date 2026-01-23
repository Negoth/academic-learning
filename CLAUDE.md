# Personal Learning & Productivity Enhancement Guide

This file provides guidance to Claude Code (claude.ai/code) and cursor agent when working with code and files in this repository.

## Git Workflow

**Branch naming**:
- `<username>/<linear issue ID>-<title>` for branches created by using linear-github-cli tool.
- `<username>/<description>` for manually created branches

**Commit format (conventional commits)**:

```
feat(scope): add new feature
fix(scope): fix bug
docs(scope): update documentation
research(scope): conduct research
style: lint/format
```

**Commit and PR workflow**:
- Use `gh` CLI to create PRs
- Include `close: #<issue ID>` in the body when creating PRs to close issues.

## Python Conventions

**Python version**: `>=3.10` (per `pyproject.toml`)

**Code style**:
- Follow PEP 8 guidelines
- Use `snake_case` for functions and variables
- Use `UPPER_CASE` for constants
- Use `pathlib.Path` for file operations
- Prefer f-strings for string formatting
- Import order: standard library -> third-party -> local

**Scripts structure**:
- Include shebang: `#!/usr/bin/env python3`
- Add docstrings with Usage section
- Use `if __name__ == "__main__":` for executable code

**Dependencies**:
- Use `uv add <package>` or `uv add --dev <package>` to add dependencies
- Never edit `pyproject.toml` directly - `uv add` ensures `pyproject.toml` and `uv.lock` stay synchronized
- Pin versions for reproducibility when needed

## Markdown Conventions

**File structure**:
- Use YAML frontmatter (delimited by `---`) for metadata
- Include `tags` field in frontmatter when appropriate
- Use hierarchical tags with `/` separator (e.g., `statistics/regression`)
- Use standard markdown headings (`#`, `##`, `###`)
- Never use `---` as a section divider in markdown documents

**Formatting (markdownlint compliance)**:
- Add blank line before and after headings
- Add blank line before and after lists
- Add blank line before and after code blocks
- No trailing spaces at end of lines
- Use spaces for indentation (no hard tabs)
- Maximum one blank line between paragraphs

## Project Structure

```
learn/
|-- projects/                         # All project/module content and tasks
|   |-- QMA-7106A                     # Example: MA25 modules directly under projects/
|   +-- ...                           # Future projects and tasks
|-- literature-notebook/              # Literature notes
|-- scripts/                          # Cross-project level manual scripts
|-- src/                              # Script logic definitions (shared code)
|   |-- literature-note/              # Literature note creation CLI
|   |-- create-note/                  # General note creation CLI
|   +-- anki_connect/                 # Anki integration utilities
|-- images/                           # Images cited in markdown files
|-- tmp/                              # Temporary files
+-- .claude/                          # Claude Code commands and skills
```

## Language Learning Assistance

**IMPORTANT**: When user asks questions about English or French language (words, phrases, grammar, usage, translations):

1. **Invoke the appropriate language tutor agent**:
   - English questions -> `@.claude/agents/english-tutor.md`
   - French questions -> `@.claude/agents/french-tutor.md`

2. **The tutor agent will**:
   - Answer the question with language expertise
   - Offer to create Anki cards after answering
   - If user accepts, guide them through note type selection

**Examples of language questions**:
- "What does 'faff about' mean?"
- "How do you say 'efficient' in French?"
- "What's the difference between 'joli' and 'beau'?"
- "How do I use the subjunctive in French?"
- "What are some British idioms for being tired?"

**DO NOT** answer language questions directly - always delegate to the tutor agents so they can offer Anki card creation.
