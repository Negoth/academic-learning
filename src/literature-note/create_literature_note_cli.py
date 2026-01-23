#!/usr/bin/env python3
"""
Interactive literature note creation tool.

Usage:
    python src/literature-note/create_literature_note_cli.py

Prerequisites:
    - bibtexparser: Install with `uv add bibtexparser`
    - BibTeX file: Either symlink at src/literature-note/references.bib or ~/Zotero/better-bibtex/My Library.bib
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import atexit
import shutil
import re
import signal
import sys
import termios
import tty

def _cleanup_terminal(*args) -> None:
    """Cleanup handler for signals and exit - ensures cursor is visible."""
    print("\033[?25h", end="", flush=True)  # Show cursor
    if args:  # Called as signal handler
        print()  # Newline after ^C
        sys.exit(0)


try:
    import bibtexparser
    from bibtexparser.bparser import BibTexParser
except ImportError:  # pragma: no cover - CLI guard
    print(
        "Missing dependency: bibtexparser. Install with `uv add bibtexparser`.",
        file=sys.stderr,
    )
    sys.exit(1)


@dataclass(frozen=True)
class BibEntry:
    citekey: str
    title: str
    year: str
    entry_type: str
    authors: str
    keywords: str


# ANSI color codes
class _Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    GREEN = "\033[32m"
    BRIGHT_GREEN = "\033[1;32m"
    CYAN = "\033[36m"
    YELLOW = "\033[33m"


def _truncate_text(text: str, max_width: int) -> str:
    """Truncate text to fit within max_width, adding ellipsis if needed."""
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
    """Render menu inline. Returns number of lines printed for next update."""
    term_size = shutil.get_terminal_size(fallback=(80, 24))
    term_width = term_size.columns
    term_height = term_size.lines

    # Move cursor up to overwrite previous render
    if prev_lines > 0:
        print(f"\033[{prev_lines}A", end="")

    c = _Colors
    lines: list[str] = []
    lines.append(f"{c.BRIGHT_GREEN}?{c.RESET} {c.BOLD}{title}{c.RESET}")
    lines.append(f"{c.DIM}  Use j/k (or arrows) to move, Enter to select.{c.RESET}")
    lines.append(f"{c.DIM}  gg: top, G: bottom, q: quit.{c.RESET}")

    total = len(options)
    header_lines = 5  # title + help + gg line + showing line + blank
    list_height = max(min(term_height - header_lines, 15), 5)  # Cap at 15 items

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

    # Reserve space for prefix " > " or "   " plus color codes
    max_option_width = term_width - 6
    for idx in range(start_idx, end_idx):
        option = _truncate_text(options[idx], max_option_width)
        if idx == current_idx:
            lines.append(f"  {c.BRIGHT_GREEN}>{c.RESET} {c.CYAN}{option}{c.RESET}")
        else:
            lines.append(f"    {option}")

    # Print all lines, clearing each line first
    for line in lines:
        sys.stdout.write(f"\033[K{line}\r\n")

    sys.stdout.flush()
    return len(lines)


def _clear_menu_lines(num_lines: int) -> None:
    """Clear the menu lines after selection."""
    if num_lines > 0:
        print(f"\033[{num_lines}A", end="")  # Move up
        for _ in range(num_lines):
            print("\033[K")  # Clear line and move down
        print(f"\033[{num_lines}A", end="", flush=True)  # Move back up


def _prompt_choice(title: str, options: list[str]) -> int:
    if not options:
        print("No options available.", file=sys.stderr)
        sys.exit(1)

    if not sys.stdin.isatty():
        filtered = list(enumerate(options, start=1))
        while True:
            print(title)
            print("Type a number, or enter a search term to filter.\n")

            window = filtered[:20]
            for idx, option in window:
                print(f"  {idx}. {option}")
            if len(filtered) > len(window):
                print(f"\nShowing {len(window)} of {len(filtered)} matches.")
            print()

            selection = input("Select number or search: ").strip()
            if selection.isdigit():
                index = int(selection) - 1
                if 0 <= index < len(options):
                    return index
                print("Invalid selection. Try again.")
                continue
            if not selection:
                continue
            term = selection.lower()
            filtered = [
                (idx, option)
                for idx, option in enumerate(options, start=1)
                if term in option.lower()
            ]
            if not filtered:
                print("No matches. Try another search.")
                filtered = list(enumerate(options, start=1))

    current_idx = 0
    last_key = ""

    # Set up terminal: hide cursor and enter raw mode for entire menu session
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    print("\033[?25l", end="", flush=True)  # Hide cursor
    tty.setraw(fd)

    def _restore_and_exit(clear_lines: int, message: str | None = None) -> None:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        _clear_menu_lines(clear_lines)
        print("\033[?25h", end="", flush=True)  # Show cursor
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


def _prompt_text(label: str) -> str:
    c = _Colors
    while True:
        value = input(f"{c.BRIGHT_GREEN}?{c.RESET} {label}: ").strip()
        if value:
            return value
        print(f"{c.YELLOW}Value cannot be empty.{c.RESET}")


def _prompt_yes_no(label: str, default: bool = False) -> bool:
    c = _Colors
    suffix = f" {c.DIM}[Y/n]{c.RESET}" if default else f" {c.DIM}[y/N]{c.RESET}"
    while True:
        value = input(f"{c.BRIGHT_GREEN}?{c.RESET} {label}{suffix}: ").strip().lower()
        if not value:
            return default
        if value in {"y", "yes"}:
            return True
        if value in {"n", "no"}:
            return False
        print(f"{c.YELLOW}Please enter y or n.{c.RESET}")


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


def _sanitize_slug(text: str) -> str:
    cleaned = text.strip().lower()
    cleaned = cleaned.replace("&", "and")
    cleaned = re.sub(r"[^a-z0-9]+", "-", cleaned)
    cleaned = cleaned.strip("-")
    return cleaned or "untitled"


def _sanitize_title(text: str) -> str:
    cleaned = text.replace("{", "").replace("}", "")
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def _split_citekey_year(citekey: str, year: str) -> str:
    if year and re.search(rf"[_-]{re.escape(year)}$", citekey):
        return citekey[: -(len(year) + 1)].rstrip("._-")
    return citekey


def _get_bibtex_path(root: Path) -> Path:
    symlink_path = root / "src" / "literature-note" / "references.bib"
    if symlink_path.exists():
        return symlink_path
    return Path("~/Zotero/better-bibtex/My Library.bib").expanduser()


def _parse_bibtex_entries(bib_path: Path) -> list[BibEntry]:
    if not bib_path.exists():
        print(f"BibTeX file not found: {bib_path}", file=sys.stderr)
        sys.exit(1)

    parser = BibTexParser(common_strings=True)
    content = bib_path.read_text(encoding="utf-8")
    database = bibtexparser.loads(content, parser=parser)

    entries: list[BibEntry] = []
    for entry in database.entries:
        title = _sanitize_title(entry.get("title", ""))
        if not title:
            continue
        year = entry.get("year") or ""
        if not year:
            date_field = entry.get("date", "")
            match = re.search(r"\d{4}", date_field)
            year = match.group(0) if match else ""

        authors_raw = entry.get("author", "")
        authors = (
            authors_raw.replace("{", "")
            .replace("}", "")
            .replace(" and ", ", ")
            .strip()
        )
        keywords = entry.get("keywords", "").strip()
        citekey = entry.get("ID", "").strip()
        entry_type = entry.get("ENTRYTYPE", "").strip()

        entries.append(
            BibEntry(
                citekey=citekey,
                title=title,
                year=year,
                entry_type=entry_type,
                authors=authors,
                keywords=keywords,
            )
        )

    def _year_key(entry: BibEntry) -> int:
        return int(entry.year) if entry.year.isdigit() else 0

    return sorted(entries, key=_year_key, reverse=True)


def _render_reference_note(entry: BibEntry) -> str:
    authors = entry.authors or ""
    keywords = entry.keywords or ""
    return (
        "---\n"
        f'title: "{entry.title}"\n'
        f"authors: {authors}\n"
        f"year: {entry.year}\n"
        f"type: {entry.entry_type}\n"
        f"keywords: {keywords}\n"
        f"citekey: {entry.citekey}\n"
        "tags:\n"
        "printed:\n"
        "---\n"
        f"# {entry.title}\n"
        "\n"
        "## Related Notes\n"
        "\n"
        "## Before You Read\n"
        "\n"
        "1. Why am I reading this?\n"
        "\n"
        "2. What are the authors trying to do in writing this?\n"
        "\n"
        "3. What are the authors saying that is relevant to what I want to find out?\n"
        "\n"
        "4. How convincing is what the authors saying?\n"
        "\n"
        "5. In conclusion, what use can I make of this?\n"
        "\n"
        "## Notes\n"
        "\n"
        "### Keywords\n"
        "\n"
        "### Memo\n"
        "\n"
        "### Summary\n"
        "\n"
        "## Post-Reading Assessment\n"
        "\n"
        "## Questions\n"
        "\n"
    )


def _render_chapter_section_note(title: str, created: str, tags_yaml: str) -> str:
    return (
        "---\n"
        f'title: "{title}"\n'
        f"created: {created}\n"
        f"tags: {tags_yaml}\n"
        "---\n"
        f"# {title}\n"
        "\n"
        "## Related Notes\n"
        "\n"
        "## Keywords\n"
        "<!-- Keywords found in reading -->\n"
        "\n"
        "## Memo\n"
        "<!-- Memo while reading -->\n"
        "\n"
        "## Summary\n"
        "<!-- Brief summary of this chapter -->\n"
        "\n"
        "## Key Concepts\n"
        "<!-- List of key concepts introduced in this chapter -->\n"
        "\n"
        "## Important Formulas/Theorems\n"
        "<!-- Important formulas, theorems, or principles -->\n"
        "\n"
        "## Examples\n"
        "<!-- Notable examples from the chapter -->\n"
        "\n"
        "## Questions\n"
        "\n"
    )


def _render_concept_note(title: str, created: str, tags_yaml: str) -> str:
    return (
        "---\n"
        f'title: "{title}"\n'
        f"created: {created}\n"
        f"tags: {tags_yaml}\n"
        "---\n"
        f"# {title}\n"
        "\n"
        "## Related Notes\n"
        "\n"
        "## Memo\n"
        "<!-- Memo while reading -->\n"
        "\n"
        "## Definition\n"
        "<!-- Clear definition of the concept -->\n"
        "\n"
        "## Examples\n"
        "<!-- Examples that illustrate the concept -->\n"
        "\n"
        "## Applications\n"
        "<!-- How this concept is applied -->\n"
        "\n"
        "## Questions\n"
        "\n"
    )


def _append_related_link(note_path: Path, link_stem: str) -> bool:
    link_line = f"- [[{link_stem}]]"
    content = note_path.read_text(encoding="utf-8")
    if link_line in content:
        return False

    if "## Related Notes" not in content:
        updated = content.rstrip() + "\n\n## Related Notes\n\n" + link_line + "\n"
        note_path.write_text(updated, encoding="utf-8")
        return True

    section_start = content.find("## Related Notes") + len("## Related Notes")
    remainder = content[section_start:]
    match = re.search(r"\n## ", remainder)
    section_end = section_start + match.start() if match else len(content)

    section_body = content[section_start:section_end]
    insert_line = ("\n" if section_body.endswith("\n") else "\n\n") + link_line
    updated = content[:section_end] + insert_line + content[section_end:]
    note_path.write_text(updated, encoding="utf-8")
    return True


def _read_input_with_quick_quit(prompt: str) -> str:
    """Read input, but quit immediately if 'q' is pressed alone."""
    sys.stdout.write(prompt)
    sys.stdout.flush()

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    # Read first char in raw mode to check for 'q'
    tty.setraw(fd)
    first_char = sys.stdin.read(1)

    if first_char.lower() == "q":
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        print()  # Newline after prompt
        sys.exit(0)

    # Restore cooked mode and read rest of line
    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    # Echo first char and read rest
    sys.stdout.write(first_char)
    sys.stdout.flush()

    if first_char in ("\r", "\n"):
        print()
        return ""

    rest = input()  # Read rest of line (already in cooked mode)
    return first_char + rest


def _select_bib_entry(entries: list[BibEntry]) -> BibEntry:
    c = _Colors
    current_list = entries[:10]
    while True:
        print(f"\n{c.BOLD}Recent references:{c.RESET}")
        for idx, entry in enumerate(current_list, start=1):
            year_label = entry.year or "n.d."
            title = _sanitize_title(entry.title)
            print(f"  {c.GREEN}{idx}.{c.RESET} {entry.citekey} {c.DIM}({year_label}){c.RESET} - {title}")

        raw = _read_input_with_quick_quit(f"\n{c.BRIGHT_GREEN}?{c.RESET} Select by number or search {c.DIM}(q to quit){c.RESET}: ").strip()
        if not raw:
            continue
        if raw.isdigit():
            index = int(raw) - 1
            if 0 <= index < len(current_list):
                return current_list[index]
            print(f"{c.YELLOW}Invalid selection.{c.RESET}")
            continue

        term = raw.lower()
        exact_match = next(
            (entry for entry in entries if entry.citekey.lower() == term), None
        )
        if exact_match:
            return exact_match

        matches = [
            entry
            for entry in entries
            if term in entry.citekey.lower() or term in entry.title.lower()
        ]
        if not matches:
            print(f"{c.YELLOW}No matches found. Try another search.{c.RESET}")
            continue
        current_list = matches[:10]


@dataclass(frozen=True)
class ReferenceContext:
    """Context for a reference: its directory and optional reference note."""

    directory: Path
    reference_note: Path | None
    entry: BibEntry


def _get_reference_paths(root: Path, entry: BibEntry) -> tuple[Path, Path]:
    """Calculate directory and reference note paths for a BibEntry."""
    year = entry.year or "unknown"
    base_key = _split_citekey_year(entry.citekey, year)
    slug_key = _sanitize_slug(base_key or entry.citekey)
    slug_title = _sanitize_slug(entry.title)

    directory_name = f"{slug_key}-{year}-{slug_title}"
    target_dir = root / "literature-notebook" / directory_name
    filename = f"{slug_key}-{year}-reference-note.md"
    note_path = target_dir / filename

    return target_dir, note_path


def _create_reference_note_for_entry(
    root: Path, entry: BibEntry
) -> tuple[Path, Path]:
    """Create reference note for a BibEntry. Returns (directory, note_path)."""
    target_dir, note_path = _get_reference_paths(root, entry)
    target_dir.mkdir(parents=True, exist_ok=True)

    c = _Colors
    if note_path.exists():
        print(f"{c.CYAN}i{c.RESET} Reference note already exists: {note_path}")
        return target_dir, note_path

    note_path.write_text(_render_reference_note(entry), encoding="utf-8")
    print(f"{c.BRIGHT_GREEN}v{c.RESET} Created reference note: {c.CYAN}{note_path}{c.RESET}")
    return target_dir, note_path


def _get_or_create_reference_context(
    root: Path, entries: list[BibEntry]
) -> ReferenceContext:
    """Select a reference and ensure its directory/note exist."""
    entry = _select_bib_entry(entries)
    target_dir, note_path = _get_reference_paths(root, entry)

    c = _Colors
    if target_dir.exists():
        # Directory exists, check for reference note
        existing_note = note_path if note_path.exists() else None
        if existing_note:
            print(f"{c.CYAN}i{c.RESET} Using existing reference: {c.BOLD}{target_dir.name}{c.RESET}")
        else:
            print(f"{c.YELLOW}!{c.RESET} Directory exists but no reference note: {target_dir.name}")
            if _prompt_yes_no("Create reference note?", default=True):
                _create_reference_note_for_entry(root, entry)
                existing_note = note_path
        return ReferenceContext(
            directory=target_dir, reference_note=existing_note, entry=entry
        )

    # Directory doesn't exist
    print(f"{c.CYAN}i{c.RESET} No existing directory for: {entry.title[:60]}...")
    if not _prompt_yes_no("Create reference note first?", default=True):
        print(f"{c.DIM}Cannot create subnote without reference directory.{c.RESET}")
        sys.exit(0)

    _create_reference_note_for_entry(root, entry)
    if not _prompt_yes_no("Continue to create subnote?", default=True):
        print(f"{c.BRIGHT_GREEN}v{c.RESET} Done.")
        sys.exit(0)

    return ReferenceContext(
        directory=target_dir, reference_note=note_path, entry=entry
    )


def _create_reference_note(root: Path) -> None:
    c = _Colors
    entries = _parse_bibtex_entries(_get_bibtex_path(root))
    entry = _select_bib_entry(entries)
    target_dir, note_path = _get_reference_paths(root, entry)

    if note_path.exists():
        print(f"{c.YELLOW}!{c.RESET} Reference note already exists: {note_path}", file=sys.stderr)
        sys.exit(1)

    target_dir.mkdir(parents=True, exist_ok=True)
    note_path.write_text(_render_reference_note(entry), encoding="utf-8")
    print(f"{c.BRIGHT_GREEN}v{c.RESET} Created reference note: {c.CYAN}{note_path}{c.RESET}")


def _select_note_in_directory(directory: Path, prompt: str) -> Path:
    notes = sorted(directory.glob("*.md"))
    if not notes:
        print(f"No notes found in {directory}", file=sys.stderr)
        sys.exit(1)

    labels = [note.stem for note in notes]
    index = _prompt_choice(prompt, labels)
    return notes[index]


def _find_chapter_note(directory: Path, chapter_num: str) -> Path | None:
    chapter_prefix = f"ch{chapter_num}"
    candidates = sorted(
        [note for note in directory.glob("ch*.md") if note.stem.startswith(chapter_prefix)]
    )
    return candidates[0] if candidates else None


def _create_chapter_note(
    directory: Path,
    chapter_num: str,
    chapter_title: str,
    created: str,
    tags_yaml: str,
) -> Path:
    slug_title = _sanitize_slug(chapter_title)
    display_title = f"ch{chapter_num} {chapter_title}"
    filename = f"ch{chapter_num}-{slug_title}.md"
    note_path = directory / filename

    if not note_path.exists():
        note_path.write_text(
            _render_chapter_section_note(display_title, created, tags_yaml),
            encoding="utf-8",
        )

    return note_path


def _create_subnote(root: Path) -> None:
    entries = _parse_bibtex_entries(_get_bibtex_path(root))
    reference_context = _get_or_create_reference_context(root, entries)
    note_types = ["chapter", "section", "concept"]
    note_type = note_types[_prompt_choice("Select sub-note type:", note_types)]

    created = datetime.now().strftime("%Y-%m-%d %H:%M")
    tags_yaml = _prompt_tags()

    if note_type == "chapter":
        chapter_num = _prompt_text("Chapter number (e.g., 1)")
        chapter_title = _prompt_text("Chapter title")
        note_path = _create_chapter_note(
            reference_context.directory,
            chapter_num,
            chapter_title,
            created,
            tags_yaml,
        )
        c = _Colors
        if reference_context.reference_note:
            _append_related_link(reference_context.reference_note, note_path.stem)
        print(f"{c.BRIGHT_GREEN}v{c.RESET} Created chapter note: {c.CYAN}{note_path}{c.RESET}")
        return

    if note_type == "section":
        c = _Colors
        section_num = _prompt_text("Section number (e.g., 2.5)")
        section_title = _prompt_text("Section title")
        section_id = section_num.replace(".", "_")
        slug_title = _sanitize_slug(section_title)
        display_title = f"sec{section_num} {section_title}"
        filename = f"sec{section_id}-{slug_title}.md"
        note_path = reference_context.directory / filename
        if note_path.exists():
            print(f"{c.YELLOW}!{c.RESET} File already exists: {note_path}", file=sys.stderr)
            sys.exit(1)

        note_path.write_text(
            _render_chapter_section_note(display_title, created, tags_yaml),
            encoding="utf-8",
        )
        chapter_num_match = re.match(r"\d+", section_num)
        chapter_num = chapter_num_match.group(0) if chapter_num_match else section_num
        chapter_note = _find_chapter_note(reference_context.directory, chapter_num)
        if not chapter_note:
            wants_create = _prompt_yes_no(
                f"No chapter found for ch{chapter_num}. Create one now (otherwise link to main reference note)?"
            )
            if wants_create:
                chapter_title = _prompt_text("Chapter title")
                chapter_note = _create_chapter_note(
                    reference_context.directory,
                    chapter_num,
                    chapter_title,
                    created,
                    tags_yaml,
                )
                if reference_context.reference_note:
                    _append_related_link(reference_context.reference_note, chapter_note.stem)
        if chapter_note:
            _append_related_link(chapter_note, note_path.stem)
        elif reference_context.reference_note:
            _append_related_link(reference_context.reference_note, note_path.stem)
        else:
            print(
                f"{c.YELLOW}!{c.RESET} No chapter or reference note found to link. Skipping link insertion.",
                file=sys.stderr,
            )
        print(f"{c.BRIGHT_GREEN}v{c.RESET} Created section note: {c.CYAN}{note_path}{c.RESET}")
        return

    if note_type == "concept":
        c = _Colors
        target_note = _select_note_in_directory(
            reference_context.directory, "Select a note to link:"
        )
        concept_title = _prompt_text("Concept title")
        filename = f"{_sanitize_slug(concept_title)}.md"
        note_path = reference_context.directory / filename
        if note_path.exists():
            print(f"{c.YELLOW}!{c.RESET} File already exists: {note_path}", file=sys.stderr)
            sys.exit(1)

        note_path.write_text(
            _render_concept_note(concept_title, created, tags_yaml),
            encoding="utf-8",
        )
        _append_related_link(target_note, note_path.stem)
        print(f"{c.BRIGHT_GREEN}v{c.RESET} Created concept note: {c.CYAN}{note_path}{c.RESET}")
        return


def main() -> None:
    # Register cleanup handlers for graceful terminal restoration
    atexit.register(_cleanup_terminal)
    signal.signal(signal.SIGINT, _cleanup_terminal)
    signal.signal(signal.SIGTERM, _cleanup_terminal)

    root = Path(__file__).resolve().parents[2]
    actions = ["create-reference", "create-subnote"]
    action = actions[_prompt_choice("Select action:", actions)]

    if action == "create-reference":
        _create_reference_note(root)
    elif action == "create-subnote":
        _create_subnote(root)
    else:
        print(f"Unsupported action: {action}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
