"""Shared helpers of the unit tests. The tests use only sentences that we wrote."""
from __future__ import annotations

import sys
import unittest
from functools import lru_cache
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from stelib.checks import Checker, Finding  # noqa: E402
from stelib.config import DESCRIPTIVE  # noqa: E402
from stelib.dictionary import Dictionary  # noqa: E402
from stelib.document import build_units  # noqa: E402
from stelib.markdown import read_blocks  # noqa: E402
from stelib.standard import StandardNotFound, find_standard  # noqa: E402
from stelib.terms import TermMatcher  # noqa: E402


@lru_cache(maxsize=1)
def dictionary() -> Dictionary | None:
    try:
        return Dictionary.load(find_standard())
    except StandardNotFound:
        return None


needs_standard = unittest.skipIf(dictionary() is None, "the local standard is not installed")


def check(text: str, kind: str = DESCRIPTIVE, sections: dict | None = None,
          terms: TermMatcher | None = None, with_dictionary: bool = True) -> list[Finding]:
    units = build_units(read_blocks(text), kind, sections or {})
    return Checker(dictionary() if with_dictionary else None, terms or TermMatcher()).check(units)


def rules(findings: list[Finding], cls: str | None = None) -> list[str]:
    return [finding.rule for finding in findings if cls is None or finding.cls == cls]
