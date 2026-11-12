"""Find the new and changed sentences of a file, compared with a git revision.

A sentence is new or changed if its text (spaces and line breaks ignored)
does not occur in the old version in the same block context. The comparison
counts occurrences: a second copy of an old sentence is new. A sentence that
goes into a different block context, for example from a description into a
procedure step, is changed.
"""
from __future__ import annotations

import subprocess
from collections import Counter
from pathlib import Path

from .document import Unit


class ChangesError(Exception):
    """git cannot give the old version."""


def _git(arguments: list[str], folder: Path) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(["git", *arguments], cwd=folder, capture_output=True, text=True)
    except OSError as error:
        raise ChangesError(f"cannot run git: {error}") from error


def text_at_revision(path: Path, revision: str) -> str:
    """The text of the file at the revision. Empty if the file is new."""
    folder = path.resolve().parent
    top = _git(["rev-parse", "--show-toplevel"], folder)
    if top.returncode != 0:
        raise ChangesError(f"{path} is not in a git repository")
    root = Path(top.stdout.strip())
    if _git(["rev-parse", "--verify", "--quiet", f"{revision}^{{commit}}"], root).returncode != 0:
        raise ChangesError(f"unknown git revision: {revision}")
    relative = path.resolve().relative_to(root.resolve()).as_posix()
    shown = _git(["show", f"{revision}:{relative}"], root)
    return shown.stdout if shown.returncode == 0 else ""


def changed_sentences(new_units: list[Unit], old_units: list[Unit]) -> set[int]:
    """The ids of the sentences of new_units that are new or changed."""
    old = Counter((sentence.key, unit.category) for unit in old_units for sentence in unit.sentences)
    changed = set()
    for unit in new_units:
        for sentence in unit.sentences:
            key = (sentence.key, unit.category)
            if old[key] > 0:
                old[key] -= 1
            else:
                changed.add(id(sentence))
    return changed


def sentence_count(units: list[Unit]) -> int:
    return sum(len(unit.sentences) for unit in units)
