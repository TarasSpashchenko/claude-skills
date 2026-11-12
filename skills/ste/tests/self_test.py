#!/usr/bin/env python3
"""Self-test of the `ste` checker on the local copy of ASD-STE100 Issue 9.

The test reads the standard at run time and keeps nothing on disk:
1. Status: a short, independent read of column 1 must agree with the status
   that the parser gives to each entry (approved or not approved).
2. STE examples (column 3): the class `error` must give no result. The test
   uses only the checks that operate on a sentence, without project terms.
3. Non-STE examples (column 4): the test counts the examples that get an
   `error`. There is no limit, because many of them break a rule that only
   the model can examine.

Exit code 0 if parts 1 and 2 give no failure, else 1. Use --show to print the
STE examples that get an error.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from stelib.checks import ERROR, Checker  # noqa: E402
from stelib.config import DESCRIPTIVE  # noqa: E402
from stelib.dictionary import Dictionary, clean_cell, split_help  # noqa: E402
from stelib.document import build_units  # noqa: E402
from stelib.markdown import read_blocks  # noqa: E402
from stelib.standard import WORD_LIST_PAGES, find_standard, read_page_lines  # noqa: E402
from stelib.terms import TermMatcher  # noqa: E402

_FIRST_BOLD = re.compile(r"\*\*(.*?)\*\*")


def independent_status(standard: Path) -> dict[tuple[int, int], bool]:
    """(page, line) -> approved, from the letters of the first bold text of column 1."""
    status = {}
    for page in WORD_LIST_PAGES:
        for line, text in enumerate(read_page_lines(standard, page), 1):
            if not text.startswith("|") or text.startswith("|---") or "**Word**" in text:
                continue
            first_cell = text.split("|")[1]
            bold = _FIRST_BOLD.search(first_cell)
            word = re.sub(r"\(.*?(\)|$)", "", bold.group(1) if bold else "")
            letters = [c for c in word if c.isalpha()]
            if letters:
                status[(page, line)] = all(c.isupper() for c in letters)
    return status


def sentence_case(example: str) -> str:
    """The examples are in uppercase letters: write them as normal text."""
    lower = example.lower()
    return re.sub(r"(^|[.!?]\s+)([a-z])", lambda m: m.group(1) + m.group(2).upper(), lower)


def errors_in(checker: Checker, text: str) -> list:
    units = build_units(read_blocks(text), DESCRIPTIVE, {})
    return [finding for finding in checker.check(units) if finding.cls == ERROR]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--standard-dir")
    parser.add_argument("--show", action="store_true", help="print the STE examples that get an error")
    args = parser.parse_args()
    standard = find_standard(args.standard_dir)
    dictionary = Dictionary.load(standard)
    checker = Checker(dictionary, TermMatcher())

    expected = independent_status(standard)
    mismatches = [(e.page, e.line, e.headword) for e in dictionary.entries
                  if expected.get((e.page, e.line)) is not e.approved]
    print(f"status: {len(dictionary.entries)} entries, {len(mismatches)} differ from the independent read")
    for page, line, headword in mismatches:
        print(f"  status differs: p. {page}, line {line}: {headword}")

    ste_failures, non_ste_total, non_ste_with_error = [], 0, 0
    for entry in dictionary.entries:
        for example in entry.ste_examples:
            errors = errors_in(checker, sentence_case(split_help(example)[0]))
            if errors:
                ste_failures.append((entry, example, errors))
        for example in entry.non_ste_examples:
            non_ste_total += 1
            non_ste_with_error += bool(errors_in(checker, clean_cell(example)))
    ste_total = sum(len(entry.ste_examples) for entry in dictionary.entries)
    print(f"STE examples: {ste_total}, with an error: {len(ste_failures)} (required: 0)")
    print(f"non-STE examples: {non_ste_total}, with an error: {non_ste_with_error} "
          f"({100 * non_ste_with_error // max(non_ste_total, 1)}%)")
    rules: dict[str, int] = {}
    for _, _, errors in ste_failures:
        for error in errors:
            rules[error.rule] = rules.get(error.rule, 0) + 1
    if rules:
        print("errors on STE examples by rule: " + ", ".join(f"{r} {n}" for r, n in sorted(rules.items())))
    if args.show:
        for entry, example, errors in ste_failures:
            causes = "; ".join(f"{e.rule} {e.message}" for e in errors)
            print(f"  p. {entry.page} {entry.label}: {example}\n    -> {causes}")
    return 0 if not mismatches and not ste_failures else 1


if __name__ == "__main__":
    sys.exit(main())
