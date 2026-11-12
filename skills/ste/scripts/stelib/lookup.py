"""Describe what the dictionary says about a word or a group of words."""
from __future__ import annotations

from dataclasses import dataclass, field

from .dictionary import Dictionary, Reading, base_candidates
from .words import is_number_word

CATEGORY_NAMES = {
    1: "manufacturing processes",
    2: "computer processes and applications",
    3: "subject fields",
    4: "law and regulations (specifications)",
}
TECHNICAL_VERB_PAGE = 58


@dataclass
class LookupResult:
    query: str
    readings: list[Reading]
    verb_categories: list[int] = field(default_factory=list)
    project_term: bool = False


def technical_verb_categories(dictionary: Dictionary, query: str) -> list[int]:
    word = query.lower()
    bases = {word, *(base for base, _ in base_candidates(word))}
    return sorted(category for category, verbs in dictionary.technical_verbs.items()
                  if bases & verbs)


def look_up(dictionary: Dictionary, query: str, is_project_term) -> LookupResult:
    readings = dictionary.lookup(query)
    if " " not in query.strip() and readings and all(r.how == "exact" for r in readings):
        readings += dictionary.related(query.lower())
    return LookupResult(query, readings, technical_verb_categories(dictionary, query),
                        is_project_term(query))


def _describe(reading: Reading, query: str) -> list[str]:
    entry = reading.entry
    status = "APPROVED" if reading.approved else "NOT APPROVED"
    if reading.how == "exact":
        head = f"{entry.label}: {status}"
    elif reading.how == "form":
        head = f'"{query}" can be a form of {entry.label}: {status}'
    elif reading.how == "unlisted form":
        head = (f'"{query}" is a form of {entry.label} that the dictionary does not give: '
                "NOT APPROVED (rule 3.1)")
    else:
        head = f'"{query}" is a {reading.how} of {entry.label}: {status}'
    lines = [f"{head} (p. {entry.page}, line {entry.line})"]
    if len(entry.forms) > 1:
        lines.append(f"  forms: {', '.join(entry.forms)}")
    lines.append(f"  {'meaning' if entry.approved else 'use instead'}: {entry.alternatives}")
    lines += [f"  help: {text}" for text in entry.help]
    lines += [f"  STE example: {text}" for text in entry.ste_examples]
    lines += [f"  non-STE example: {text}" for text in entry.non_ste_examples]
    return lines


def format_lookup(result: LookupResult) -> str:
    lines = [f"## {result.query}"]
    for reading in result.readings:
        lines += _describe(reading, result.query)
    if not result.readings and is_number_word(result.query.lower()):
        lines.append("a number: a technical noun (rule 1.5). Write it as digits or as words")
    elif not result.readings:
        lines.append("not in the dictionary: use it only if it is a technical noun or a "
                     "technical verb (rules 1.5, 1.12). If it is a form of a verb, look up the base form")
    for category in result.verb_categories:
        lines.append(f"listed as a technical verb, category {category} "
                     f"({CATEGORY_NAMES[category]}), p. {TECHNICAL_VERB_PAGE}")
    if result.project_term:
        lines.append("project term (.ste.toml or a glossary)")
    return "\n".join(lines)


def lookup_json(result: LookupResult) -> dict:
    return {
        "query": result.query,
        "readings": [{
            "headword": reading.entry.headword, "pos": reading.entry.pos,
            "approved": reading.approved, "how": reading.how, "forms": list(reading.entry.forms),
            "meaning_or_alternatives": reading.entry.alternatives, "help": reading.entry.help,
            "ste_examples": reading.entry.ste_examples,
            "non_ste_examples": reading.entry.non_ste_examples,
            "page": reading.entry.page, "line": reading.entry.line,
        } for reading in result.readings],
        "technical_verb_categories": result.verb_categories,
        "project_term": result.project_term,
    }
