"""Find the local copy of ASD-STE100 Issue 9 and read its pages."""
from __future__ import annotations

import os
from pathlib import Path

ENV_VAR = "STE_STANDARD_DIR"
DEFAULT_DIR = Path.home() / ".local" / "share" / "ste" / "ASD-STE100_ISSUE9"
WORD_LIST_PAGES = range(149, 435)
TECHNICAL_VERB_PAGES = range(57, 59)


class StandardNotFound(Exception):
    """No folder with the page files was found."""

    def __init__(self, examined: list[Path], missing_pages: list[int] | None = None):
        self.examined = examined
        places = ", ".join(str(path) for path in examined)
        if missing_pages:
            pages = ", ".join(str(number) for number in missing_pages[:10])
            problem = f"the folder {places} is not complete (missing pages: {pages})"
        else:
            problem = f"ASD-STE100 Issue 9 not found (examined: {places})"
        super().__init__(f"{problem}. Put the page files there, set {ENV_VAR}, or use --standard-dir.")


def page_path(standard_dir: Path, number: int) -> Path:
    return standard_dir / f"page_{number:03d}.md"


def find_standard(option: str | None = None) -> Path:
    """Return the standard folder.

    The highest-precedence source that is set wins: the option, then the
    environment variable, then the default folder. A wrong explicit value is an
    error, not a silent fall-back, so that the user sees the mistake.
    """
    if option:
        candidate = Path(option).expanduser()
    elif os.environ.get(ENV_VAR):
        candidate = Path(os.environ[ENV_VAR]).expanduser()
    else:
        candidate = DEFAULT_DIR
    if not page_path(candidate, WORD_LIST_PAGES[0]).is_file():
        raise StandardNotFound([candidate])
    missing = [number for number in (*TECHNICAL_VERB_PAGES, *WORD_LIST_PAGES)
               if not page_path(candidate, number).is_file()]
    if missing:
        raise StandardNotFound([candidate], missing)
    return candidate


def read_page_lines(standard_dir: Path, number: int) -> list[str]:
    path = page_path(standard_dir, number)
    if not path.is_file():
        return []
    return path.read_text(encoding="utf-8").splitlines()
