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
import atexit
import re
import shutil
import signal
import sys
import termios
import tty


def _cleanup_terminal(*args) -> None:
    """Cleanup handler for signals and exit - ensures cursor is visible."""
    print("\033[?25h", end="", flush=True)
    if args:
        print()
        sys.exit(0)


# ANSI color codes
class _Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    GREEN = "\033[32m"
    BRIGHT_GREEN = "\033[1;32m"
    CYAN = "\033[36m"
    YELLOW = "\033[33m"


@dataclass(frozen=True)
class LocationChoice:
    label: str
    path: Path
    project: str


def _truncate_text(text: str, max_width: int) -> str:
    if len(text) <= max_width:
        return text
    if max_width <= 3:
        return text[:max_width]
    return text[: max_width - 3] + "..."


def _render_menu_inline(
    title: str,
    options: list[str],
    current_idx: int,
    prev_lines: int = 0,
) -> int:
    term_size = shutil.get_terminal_size(fallback=(80, 24))
    term_width = term_size.columns
    term_height = term_size.lines

    if prev_lines > 0:
        print(f"\033[{prev_lines}A", end="")

    c = _Colors
    lines: list[str] = []
    lines.append(f"{c.BRIGHT_GREEN}?{c.RESET} {c.BOLD}{title}{c.RESET}")
    lines.append(f"{c.DIM}  Use j/k (or arrows) to move, Enter to select.{c.RESET}")
    lines.append(f"{c.DIM}  gg: top, G: bottom, q: quit.{c.RESET}")

    total = len(options)
    header_lines = 5
    list_height = max(min(term_height - header_lines, 15), 5)

    if total <= list_height:
        start_idx = 0
        end_idx = total
    else:
        half_window = list_height // 2
        start_idx = max(current_idx - half_window, 0)
        end_idx = start_idx + list_height
        if end_idx > total:
            end_idx = total
            start_idx = max(end_idx - list_height, 0)

    lines.append(f"{c.DIM}  Showing {start_idx + 1}-{end_idx} of {total}.{c.RESET}")
    lines.append("")

    max_option_width = term_width - 6
    for idx in range(start_idx, end_idx):
        option = _truncate_text(options[idx], max_option_width)
        if idx == current_idx:
            lines.append(f"  {c.BRIGHT_GREEN}>{c.RESET} {c.CYAN}{option}{c.RESET}")
        else:
            lines.append(f"    {option}")

    for line in lines:
        sys.stdout.write(f"\033[K{line}\r\n")

    sys.stdout.flush()
    return len(lines)


def _clear_menu_lines(num_lines: int) -> None:
    if num_lines > 0:
        print(f"\033[{num_lines}A", end="")
        for _ in range(num_lines):
            print("\033[K")
        print(f"\033[{num_lines}A", end="", flush=True)


def _prompt_choice(title: str, options: list[str]) -> int:
    if not options:
        print("No options available.", file=sys.stderr)
        sys.exit(1)

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

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    print("\033[?25l", end="", flush=True)
    tty.setraw(fd)

    def _restore_and_exit(clear_lines: int, message: str | None = None) -> None:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        _clear_menu_lines(clear_lines)
        print("\033[?25h", end="", flush=True)
        if message:
            print(message)

    try:
        num_lines = _render_menu_inline(title, options, current_idx, prev_lines=0)
        while True:
            char = sys.stdin.read(1)
            if char == "\x1b":
                char += sys.stdin.read(2)

            if char in ("\r", "\n"):
                _restore_and_exit(num_lines)
                return current_idx
            if char in ("q", "Q"):
                _restore_and_exit(num_lines, "Cancelled.")
                sys.exit(0)
            if char in ("k", "\x1b[A"):
                current_idx = (current_idx - 1) % len(options)
                last_key = ""
            elif char in ("j", "\x1b[B"):
                current_idx = (current_idx + 1) % len(options)
                last_key = ""
            elif char == "G":
                current_idx = len(options) - 1
                last_key = ""
            elif char == "g":
                if last_key == "g":
                    current_idx = 0
                    last_key = ""
                else:
                    last_key = "g"
            num_lines = _render_menu_inline(title, options, current_idx, prev_lines=num_lines)
    except Exception:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        print("\033[?25h", end="", flush=True)
        raise


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
    cleaned = title.strip().lower()
    cleaned = cleaned.replace("&", "and")
    cleaned = re.sub(r"[^a-z0-9]+", "-", cleaned)
    cleaned = cleaned.strip("-")
    return cleaned or "untitled"


def _prompt_title() -> str:
    c = _Colors
    while True:
        title = input(f"{c.BRIGHT_GREEN}?{c.RESET} Note title: ").strip()
        if title:
            return title
        print(f"{c.YELLOW}Title cannot be empty.{c.RESET}")


def _prompt_tags() -> str:
    c = _Colors
    raw = input(f"{c.BRIGHT_GREEN}?{c.RESET} Tags {c.DIM}(comma-separated, optional){c.RESET}: ").strip()
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
        "\n"
        "## Readings\n"
        "\n"
        "## Cue (Keywords / Questions)\n"
        "<!-- Left column: prompts, keywords, or questions. Use short bullets. -->\n"
        "### English Vocabulary\n"
        "\n"
        "### Keywords\n"
        "\n"
        "## Notes (Lecture Notes)\n"
        "<!-- Right column: main lecture notes. Use concise bullets, examples, formulas. -->\n"
        "\n"
        "## Summary (After Class)\n"
        "<!-- Bottom summary: 3-5 sentence synthesis of the session. -->\n"
        "\n"
        "## Questions\n"
        "\n"
        "## Assignments / Next Steps\n"
        "<!-- Homework, readings, or actions before next session. -->\n"
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
    )


def main() -> None:
    atexit.register(_cleanup_terminal)
    signal.signal(signal.SIGINT, _cleanup_terminal)
    signal.signal(signal.SIGTERM, _cleanup_terminal)

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

    c = _Colors
    if output_path.exists():
        print(f"{c.YELLOW}File already exists: {output_path}{c.RESET}", file=sys.stderr)
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
    print(f"{c.BRIGHT_GREEN}Created:{c.RESET} {c.CYAN}{output_path}{c.RESET}")


if __name__ == "__main__":
    main()
