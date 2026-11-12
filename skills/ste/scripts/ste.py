#!/usr/bin/env python3
"""ASD-STE100 Issue 9 (Simplified Technical English): dictionary lookup and text check.

  ste.py lookup WORD ["GROUP OF WORDS" ...]
  ste.py check FILE [FILE ...] [--since HEAD]

The standard is not part of this tool. Put the page files of the standard in
~/.local/share/ste/ASD-STE100_ISSUE9/, or give the folder with STE_STANDARD_DIR
or --standard-dir.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from stelib.changes import ChangesError, changed_sentences, sentence_count, text_at_revision  # noqa: E402
from stelib.checks import Checker  # noqa: E402
from stelib.config import (FILE_KINDS, SPECIFICATION, Config, ConfigError, find_config,  # noqa: E402
                           load_config)
from stelib.dictionary import Dictionary  # noqa: E402
from stelib.document import build_units  # noqa: E402
from stelib.lookup import format_lookup, look_up, lookup_json  # noqa: E402
from stelib.markdown import read_blocks  # noqa: E402
from stelib.report import EXIT_INCOMPLETE, FileReport, exit_code, format_json, format_text  # noqa: E402
from stelib.standard import StandardNotFound, find_standard  # noqa: E402
from stelib.terms import TermMatcher  # noqa: E402

STDIN = "-"
LAW_AND_REGULATIONS = 4


def build_terms(config: Config, dictionary: Dictionary | None, kind: str) -> TermMatcher:
    """Project nouns and verbs, glossary terms, and the technical verbs of the
    configured categories. Specifications also get the verbs of category 4."""
    verbs = list(config.verbs)
    if dictionary:
        categories = set(config.verb_categories)
        if kind == SPECIFICATION:
            categories.add(LAW_AND_REGULATIONS)
        for category in categories:
            verbs += [verb for verb in sorted(dictionary.technical_verbs.get(category, ()))
                      if not _has_lowercase_row(dictionary, verb)]
    extra_forms = [form for forms in config.verb_forms.values() for form in forms]
    return TermMatcher([*config.nouns, *config.glossary_terms()], verbs, extra_forms)


def _has_lowercase_row(dictionary: Dictionary, verb: str) -> bool:
    """A category verb that the dictionary does not approve ("copy") is correct only in
    the context of its category (rule 1.12). The check asks about it, with a hint."""
    return any(not entry.approved for entry in dictionary.exact(verb.split()[0]))


def _config_for(args, start: Path) -> Config:
    if args.no_config:
        return Config()
    return load_config(Path(args.config) if args.config else find_config(start))


def _read_text(name: str) -> str:
    return sys.stdin.read() if name == STDIN else Path(name).read_text(encoding="utf-8-sig")


def check_file(name: str, args, dictionary: Dictionary | None, missing: str | None) -> FileReport:
    report = FileReport(name)
    if missing:
        report.complete = False
        report.notes.append(missing)
    path = Path.cwd() if name == STDIN else Path(name)
    try:
        text = _read_text(name)
        config = _config_for(args, path)
        report.config = str(config.path) if config.path else None
        kind, sections = config.document_kind(path)
        report.kind = args.kind or kind
        terms = build_terms(config, dictionary, report.kind)
        units = build_units(read_blocks(text, config.front_matter_keys), report.kind, sections)
        selected = None
        if args.since and name != STDIN:
            old_text = text_at_revision(path, args.since)
            old_units = build_units(read_blocks(old_text, config.front_matter_keys), report.kind, sections)
            selected = changed_sentences(units, old_units)
            report.scope = (f"new and changed sentences since {args.since} "
                            f"({len(selected)} of {sentence_count(units)})")
        report.findings = Checker(dictionary, terms).check(units, selected)
    except (OSError, UnicodeDecodeError, ConfigError, ChangesError) as error:
        report.complete = False
        report.notes.append(str(error))
    return report


def _load_dictionary(option: str | None) -> tuple[Dictionary | None, str | None]:
    try:
        return Dictionary.load(find_standard(option)), None
    except StandardNotFound as error:
        return None, f"{error} Only the checks without the dictionary were done."


def run_check(args) -> int:
    dictionary, missing = _load_dictionary(args.standard_dir)
    reports = [check_file(name, args, dictionary, missing) for name in args.files]
    print(format_json(reports) if args.json else format_text(reports))
    return exit_code(reports)


def run_lookup(args) -> int:
    dictionary, missing = _load_dictionary(args.standard_dir)
    if dictionary is None:
        print(missing, file=sys.stderr)
        return EXIT_INCOMPLETE
    try:
        config = _config_for(args, Path.cwd())
        terms = build_terms(config, None, config.default_kind)
    except (OSError, UnicodeDecodeError, ConfigError) as error:
        print(f"warning: {error}", file=sys.stderr)
        terms = TermMatcher()
    results = [look_up(dictionary, query, lambda q: _is_term(terms, q)) for query in args.words]
    if args.json:
        print(json.dumps([lookup_json(result) for result in results], indent=2, ensure_ascii=False))
    else:
        print("\n\n".join(format_lookup(result) for result in results))
    return 0


def _is_term(terms: TermMatcher, query: str) -> bool:
    words = query.lower().split()
    return bool(words) and terms.match_length(words, 0) == len(words)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--standard-dir", help="folder with the page files of the standard")
    common.add_argument("--config", help="use this .ste.toml (default: the nearest one)")
    common.add_argument("--no-config", action="store_true", help="do not read a .ste.toml")
    common.add_argument("--json", action="store_true", help="write JSON")
    commands = parser.add_subparsers(dest="command", required=True)

    lookup = commands.add_parser("lookup", parents=[common], help="find words in the dictionary")
    lookup.add_argument("words", nargs="+", help='a word, or a group of words in quotes')
    lookup.set_defaults(handler=run_lookup)

    check = commands.add_parser("check", parents=[common], help="examine Markdown or text files")
    check.add_argument("files", nargs="+", help='files to examine; "-" reads the standard input')
    check.add_argument("--since", metavar="REV",
                       help="examine only the sentences that are new or changed since this git revision")
    check.add_argument("--kind", choices=FILE_KINDS, help="the text kind (default: from .ste.toml, "
                       "else descriptive)")
    check.set_defaults(handler=run_check)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    sys.exit(main())
