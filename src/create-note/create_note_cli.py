#!/usr/bin/env python3
"""
Interactive note creation tool.

Usage:
    python src/create-note/create_note_cli.py
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import re
import sys
import termios
import tty


@dataclass(frozen=True)
class LocationChoice:
    label: str
    path: Path
    project: str


def _read_key() -> str:
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        char = sys.stdin.read(1)
        if char == "\x1b":
            char += sys.stdin.read(2)
        return char
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def _render_menu(title: str, options: list[str], current_idx: int) -> None:
    print("\033[H\033[J", end="")
    print(title)
    print("Use j/k (or arrows) to move, Enter to select.")
    print("gg: top, G: bottom, q: quit.\n")
    for idx, option in enumerate(options):
        prefix = ">" if idx == current_idx else " "
        print(f" {prefix} {option}")


def _prompt_choice(title: str, options: list[str]) -> int:
    if not sys.stdin.isatty():
        print(title)
        for idx, option in enumerate(options, start=1):
            print(f"  {idx}. {option}")
        print()
        while True:
            selection = input("Select number: ").strip()
            if not selection.isdigit():
                print("Please enter a number.")
                continue
            index = int(selection) - 1
            if 0 <= index < len(options):
                return index
            print("Invalid selection. Try again.")

    current_idx = 0
    last_key = ""
    _render_menu(title, options, current_idx)
    while True:
        key = _read_key()
        if key in ("\r", "\n"):
            print()
            return current_idx
        if key in ("q", "Q"):
            print("\nCancelled.")
            sys.exit(0)
        if key in ("k", "\x1b[A"):
            current_idx = (current_idx - 1) % len(options)
            last_key = ""
        elif key in ("j", "\x1b[B"):
            current_idx = (current_idx + 1) % len(options)
            last_key = ""
        elif key == "G":
            current_idx = len(options) - 1
            last_key = ""
        elif key == "g":
            if last_key == "g":
                current_idx = 0
                last_key = ""
            else:
                last_key = "g"
        _render_menu(title, options, current_idx)


def _list_project_dirs(projects_dir: Path) -> list[Path]:
    if not projects_dir.exists():
        return []
    return sorted(
        [d for d in projects_dir.iterdir() if d.is_dir() and not d.name.startswith(".")],
        key=lambda p: p.name.lower(),
    )


def _choose_location(root: Path) -> LocationChoice:
    current_dir = Path.cwd()
    projects_dir = root / "projects"

    options = [
        f"Current directory ({current_dir})",
        f"projects/ ({projects_dir})",
    ]
    choice_idx = _prompt_choice("Where do you want to save the note?", options)

    if choice_idx == 0:
        project = current_dir.name
        return LocationChoice(label="current", path=current_dir, project=project)

    project_dirs = _list_project_dirs(projects_dir)
    if not project_dirs:
        print("No project directories found under projects/.", file=sys.stderr)
        sys.exit(1)

    project_names = [p.name for p in project_dirs]
    project_idx = _prompt_choice("Select a project directory:", project_names)
    project = project_dirs[project_idx]
    return LocationChoice(label="projects", path=project, project=project.name)


def _sanitize_filename(title: str) -> str:
    sanitized = re.sub(r'[\\/:*?"<>|]', "_", title.strip())
    return sanitized or "untitled"


def _prompt_title() -> str:
    while True:
        title = input("Note title: ").strip()
        if title:
            return title
        print("Title cannot be empty.")


def _prompt_tags() -> str:
    raw = input("Tags (comma-separated, optional): ").strip()
    if not raw:
        return "[]"

    tags = []
    for tag in raw.split(","):
        tag_clean = tag.strip()
        if tag_clean:
            tags.append(tag_clean)

    if not tags:
        return "[]"

    return "\n" + "\n".join(f"  - {tag}" for tag in tags)


def _render_class_note(title: str, project: str, created: str, tags_yaml: str) -> str:
    return (
        "---\n"
        f'title: "{title}"\n'
        f'project: "{project}"\n'
        f"created: {created}\n"
        f"tags: {tags_yaml}\n"
        "---\n"
        f"# {title}\n"
        "\n"
        "## Readings\n"
        "\n"
        "## Cue (Keywords / Questions)\n"
        "<!-- Left column: prompts, keywords, or questions. Use short bullets. -->\n"
        "### English Vocabulary\n"
        "\n"
        "### Keywords\n"
        "\n"
        "### Questions\n"
        "\n"
        "## Notes (Lecture Notes)\n"
        "<!-- Right column: main lecture notes. Use concise bullets, examples, formulas. -->\n"
        "\n"
        "## Summary (After Class)\n"
        "<!-- Bottom summary: 3-5 sentence synthesis of the session. -->\n"
        "\n"
        "## Assignments / Next Steps\n"
        "<!-- Homework, readings, or actions before next session. -->\n"
        "\n"
        "## Personal Insights\n"
        "<!-- Thoughts, confusions to clarify, connections to prior knowledge. -->\n"
    )


def _render_brainstorm_note(
    title: str, project: str, created: str, tags_yaml: str
) -> str:
    return (
        "---\n"
        f'title: "{title}"\n'
        f'project: "{project}"\n'
        f"created: {created}\n"
        f"tags: {tags_yaml}\n"
        "---\n"
        f"# {title}\n"
        "\n"
        "## Brief\n"
        "<!-- What is the assignment asking? Scope, deliverables, evaluation criteria. -->\n"
        "\n"
        "## Brainstorm\n"
        "<!-- Ideas, angles, frameworks, hypotheses, possible contributions. -->\n"
        "\n"
        "## Questions\n"
        "<!-- Clarifications needed, assumptions, unknowns to resolve. -->\n"
        "\n"
        "## Data & Constraints\n"
        "<!-- Datasets, access, time constraints, tools, dependencies. -->\n"
        "\n"
        "## Plan (Draft Outline)\n"
        "<!-- Sections, key arguments, methods, expected results. -->\n"
    )


def _render_temp_note(
    title: str, created: str, tags_yaml: str, project: str | None = None
) -> str:
    project_line = f'project: "{project}"\n' if project else ""
    return (
        "---\n"
        f"title: {title}\n"
        f"{project_line}"
        f"created: {created}\n"
        f"tags: {tags_yaml}\n"
        "---\n"
        f"# {title}\n"
        "\n"
    )


def main() -> None:
    root = Path(__file__).resolve().parents[2]

    location = _choose_location(root)
    note_types = ["class", "brainstorm", "temp"]
    note_idx = _prompt_choice("Select note type:", note_types)
    note_type = note_types[note_idx]

    title = _prompt_title()
    tags_yaml = _prompt_tags()
    created = datetime.now().strftime("%Y-%m-%d %H:%M")

    filename = _sanitize_filename(title) + ".md"
    output_path = location.path / filename

    if output_path.exists():
        print(f"File already exists: {output_path}", file=sys.stderr)
        sys.exit(1)

    if note_type == "class":
        content = _render_class_note(title, location.project, created, tags_yaml)
    elif note_type == "brainstorm":
        content = _render_brainstorm_note(title, location.project, created, tags_yaml)
    elif note_type == "temp":
        project = location.project if location.label == "projects" else None
        content = _render_temp_note(title, created, tags_yaml, project)
    else:
        print(f"Unsupported note type: {note_type}", file=sys.stderr)
        sys.exit(1)

    output_path.write_text(content, encoding="utf-8")
    print(f"Created: {output_path}")


if __name__ == "__main__":
    main()
