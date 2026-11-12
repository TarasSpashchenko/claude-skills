"""Read the dictionary of ASD-STE100 Issue 9 from the local page files.

Column 1 of the word list gives the word, its part of speech and its approved
forms. An UPPERCASE word is approved, a lowercase word is not approved.
Column 2 gives the meaning (approved word) or the alternatives (not approved).
Columns 3 and 4 give an STE example and a non-STE example.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from .standard import TECHNICAL_VERB_PAGES, WORD_LIST_PAGES, read_page_lines

HELP_MARK = "**Help:**"
PART_OF_SPEECH_LABELS = ("n", "v", "adj", "adv", "prep", "conj", "pron", "art", "prefix")
ROW_CELLS = 4
GAP_MARK = "..."

_POS_LABEL = re.compile(r"\((" + "|".join(PART_OF_SPEECH_LABELS) + r")\)")
_HEAD_WITH_NOTE = re.compile(r"^(.*?)\s*\((.*?)\)\s*$")
_HYPHEN_AT_LINE_BREAK = re.compile(r"-\*\*<br>\*\*(?=[A-Za-z])")
_CATEGORY_TITLE = re.compile(r"\*\*(\d)\.\s+<u>")
_MARKED_LIST = re.compile(r"<mark>(.*?)(?:</mark>|$)")
_SPACES = re.compile(r"\s+")


@dataclass
class Entry:
    """One dictionary entry: a column-1 row and its continuation rows."""

    headword: str
    pos: str
    approved: bool
    forms: tuple[str, ...]
    page: int
    line: int
    meaning: list[str] = field(default_factory=list)
    help: list[str] = field(default_factory=list)
    ste_examples: list[str] = field(default_factory=list)
    non_ste_examples: list[str] = field(default_factory=list)

    @property
    def key(self) -> str:
        return self.headword.lower()

    @property
    def label(self) -> str:
        return f"{self.headword} ({self.pos})" if self.pos else self.headword

    @property
    def alternatives(self) -> str:
        """Column 2 as one line: the meaning or the approved alternatives.
        Some rows give only a help text in column 2."""
        return "; ".join(self.meaning) or " ".join(self.help)

    @property
    def noun_is_technical(self) -> bool:
        """A verb row that tells that the noun of the same word is a technical noun,
        for example "file (v)" with the alternative "FILE (TN)"."""
        if self.pos != "v":
            return False
        marker = re.compile(rf"\b{re.escape(self.headword.upper())}\b[^;]*?[(\[]TN[)\]]")
        return bool(marker.search(" ".join(self.meaning))) or any(
            "technical noun" in text.lower() for text in self.help)


@dataclass(frozen=True)
class Reading:
    """How a word of a text agrees with one dictionary entry."""

    entry: Entry
    how: str  # "exact", "plural", "verb form" (of a lowercase verb), "unlisted form"

    @property
    def approved(self) -> bool:
        return self.entry.approved and self.how != "unlisted form"


def clean_cell(cell: str) -> str:
    cell = _HYPHEN_AT_LINE_BREAK.sub("", cell).replace("-<br>", "-")
    for markup in ("<br>", "**", "<u>", "</u>"):
        cell = cell.replace(markup, " " if markup == "<br>" else "")
    return _SPACES.sub(" ", cell).strip()


def split_help(cell: str) -> tuple[str, str]:
    """Return the cell without its help text, and the help text."""
    if HELP_MARK not in cell:
        return cell, ""
    head, help_text = cell.split(HELP_MARK, 1)
    return head, clean_cell(help_text)


def _headword_and_spellings(head: str) -> tuple[str, list[str]]:
    """Read forms such as "case (in case of)", "prevent (from)", "MATT (or MATTE)"."""
    match = _HEAD_WITH_NOTE.match(head)
    if not match:
        return head.strip(), []
    base, note = match.group(1).strip(), match.group(2).strip()
    if note.lower().startswith("or "):
        return base, [note[3:].strip()]
    if any(word.startswith(base.lower()) for word in note.lower().split()):
        return note, []
    return f"{base} {note}", []


def _listed_forms(rest: str, headword: str) -> list[str]:
    """Read the forms after the part of speech, for example ", REMOVES, REMOVED"."""
    forms = []
    for piece in rest.split(","):
        piece = piece.replace("(", " ").replace(")", " ").strip()
        piece = re.sub(r"^also\s+", "", piece, flags=re.IGNORECASE)
        if not piece:
            continue
        if " " in piece and " " not in headword:
            forms.extend(piece.split())  # a row without commas between its forms
        else:
            forms.append(piece)
    return forms


def parse_head_cell(cell: str) -> tuple[str, str, list[str], str] | None:
    """Return (headword, part of speech, forms, help) or None for a continuation row."""
    head, help_text = split_help(cell)
    text = clean_cell(head)
    if not text:
        return None
    label = _POS_LABEL.search(text)
    pos = label.group(1) if label else ""
    head_part = text[: label.start()] if label else text
    rest = text[label.end():] if label else ""
    headword, spellings = _headword_and_spellings(head_part)
    forms = [headword, *spellings, *_listed_forms(rest, headword)]
    return headword, pos, forms, help_text


def _is_uppercase(text: str) -> bool:
    letters = [char for char in text if char.isalpha()]
    return bool(letters) and all(char.isupper() for char in letters)


def _table_rows(lines: list[str]):
    for number, line in enumerate(lines, 1):
        if not line.startswith("|") or line.startswith("|---") or "**Word**" in line:
            continue
        cells = line.rstrip().split("|")[1:-1]
        if len(cells) == ROW_CELLS:
            yield number, cells


def _add_text(target: list[str], cell: str) -> str:
    """Append the cell text to target and return its help text."""
    body, help_text = split_help(cell)
    text = clean_cell(body)
    if text:
        target.append(text)
    return help_text


def read_entries(standard_dir: Path) -> list[Entry]:
    entries: list[Entry] = []
    for page in WORD_LIST_PAGES:
        for line, cells in _table_rows(read_page_lines(standard_dir, page)):
            head = parse_head_cell(cells[0])
            if head is None and entries:
                continuation_help = split_help(cells[0])[1]
                if continuation_help:
                    entries[-1].help.append(continuation_help)
            if head:
                headword, pos, forms, help_text = head
                entries.append(Entry(
                    headword=headword, pos=pos, approved=_is_uppercase(headword),
                    forms=tuple(dict.fromkeys(form.lower() for form in forms)),
                    page=page, line=line,
                    help=[help_text] if help_text else []))
            if not entries:
                continue
            entry = entries[-1]
            for help_text in (_add_text(entry.meaning, cells[1]),
                              _add_text(entry.ste_examples, cells[2]),
                              _add_text(entry.non_ste_examples, cells[3])):
                if help_text:
                    entry.help.append(help_text)
    return entries


def read_technical_verbs(standard_dir: Path) -> dict[int, set[str]]:
    """Read the example verbs of the technical verb categories (rule 1.12)."""
    categories: dict[int, set[str]] = {}
    current = None
    for page in TECHNICAL_VERB_PAGES:
        for line in read_page_lines(standard_dir, page):
            title = _CATEGORY_TITLE.search(line)
            if title:
                current = int(title.group(1))
                continue
            marked = _MARKED_LIST.search(line)
            if current is None or not marked or ":" in marked.group(1):
                continue  # text with a colon is an example sentence, not a list
            for item in marked.group(1).split(","):
                verb = re.sub(r"\(.*?\)", "", item).strip().lower()
                if verb:
                    categories.setdefault(current, set()).add(verb)
    return categories


VOWELS = "aeiou"
SIBILANT_ENDINGS = ("s", "x", "z", "ch", "sh")


# Irregular forms that the dictionary does not list for the approved verbs
# BE, DO, GO and GET. The parser uses them only to find the base verb.
# It also maps frequent irregular forms of other verbs to their base, so that a form of
# a verb that is not approved ("took" of "take") finds its row.
IRREGULAR_BASES = {
    "been": "be", "being": "be", "done": "do", "doing": "do", "gone": "go", "going": "go",
    "gotten": "get", "getting": "get", "took": "take", "taken": "take", "ran": "run",
    "chose": "choose", "chosen": "choose", "built": "build", "wrote": "write", "written": "write",
    "broke": "break", "broken": "break", "began": "begin", "begun": "begin", "gave": "give",
    "given": "give", "sent": "send", "found": "find", "held": "hold", "kept": "keep",
    "left": "leave", "lost": "lose", "paid": "pay", "said": "say", "sold": "sell",
    "spent": "spend", "stood": "stand", "told": "tell", "thought": "think", "brought": "bring",
    "bought": "buy", "caught": "catch", "knew": "know", "known": "know", "shown": "show",
    "saw": "see", "seen": "see", "drew": "draw", "drawn": "draw", "rose": "rise", "risen": "rise",
    "meant": "mean", "met": "meet", "led": "lead", "fell": "fall", "fallen": "fall",
    "felt": "feel", "fed": "feed", "hid": "hide", "hidden": "hide", "spoke": "speak",
    "spoken": "speak", "understood": "understand", "forgot": "forget", "forgotten": "forget",
}


def base_candidates(word: str) -> list[tuple[str, str]]:
    """Possible (base, ending) pairs of an inflected English word."""
    candidates = [(IRREGULAR_BASES[word], "ed")] if word in IRREGULAR_BASES else []
    if len(word) > 4 and word.endswith("ies"):
        candidates.append((word[:-3] + "y", "s"))
    if len(word) > 3 and word.endswith("es") and word[:-2].endswith(SIBILANT_ENDINGS + ("o",)):
        candidates.append((word[:-2], "s"))
    if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
        candidates.append((word[:-1], "s"))
    if len(word) > 4 and word.endswith("ied"):
        candidates.append((word[:-3] + "y", "ed"))
    if len(word) > 4 and word.endswith("ed"):
        stem = word[:-2]
        candidates += [(stem, "ed"), (word[:-1], "ed")]
        if len(stem) > 2 and stem[-1] == stem[-2]:
            candidates.append((stem[:-1], "ed"))
    if len(word) > 5 and word.endswith("ing"):
        stem = word[:-3]
        candidates += [(stem, "ing"), (stem + "e", "ing")]
        if len(stem) > 2 and stem[-1] == stem[-2]:
            candidates.append((stem[:-1], "ing"))
    return candidates


def _doubles_last_consonant(word: str) -> bool:
    """A short consonant-vowel-consonant end, as in "stop" and "debug"."""
    return (len(word) > 2 and word[-1] not in VOWELS + "wxy"
            and word[-2] in VOWELS and word[-3] not in VOWELS)


def plurals(noun: str) -> set[str]:
    """The noun and its regular plural."""
    if len(noun) > 1 and noun.endswith("y") and noun[-2] not in VOWELS:
        return {noun, noun[:-1] + "ies"}
    return {noun, noun + ("es" if noun.endswith(SIBILANT_ENDINGS) else "s")}


def inflections(word: str) -> set[str]:
    """Regular forms of a word: plural or third person, past, and "-ing"."""
    if len(word) > 1 and word.endswith("y") and word[-2] not in VOWELS:
        return {word, word[:-1] + "ies", word[:-1] + "ied", word + "ing"}
    forms = {word, word + ("es" if word.endswith(SIBILANT_ENDINGS) else "s")}
    if word.endswith("e"):
        return forms | {word + "d", word[:-1] + "ing"}
    forms |= {word + "ed", word + "ing"}
    if _doubles_last_consonant(word):
        forms |= {word + word[-1] + "ed", word + word[-1] + "ing"}
    return forms


class Dictionary:
    """The word list, indexed by surface form, with the technical verb lists."""

    def __init__(self, entries: list[Entry], technical_verbs: dict[int, set[str]]):
        self.entries = entries
        self.technical_verbs = technical_verbs
        self._by_form: dict[str, list[Entry]] = {}
        self._phrases: dict[str, list[tuple[tuple[str, ...], Entry]]] = {}
        for entry in entries:
            for form in entry.forms:
                if GAP_MARK in form or form.endswith("-"):
                    continue
                words = tuple(form.split())
                if len(words) == 1:
                    self._by_form.setdefault(form, []).append(entry)
                else:
                    self._phrases.setdefault(words[0], []).append((words, entry))
        for options in self._phrases.values():
            options.sort(key=lambda option: -len(option[0]))

    @classmethod
    def load(cls, standard_dir: Path) -> "Dictionary":
        return cls(read_entries(standard_dir), read_technical_verbs(standard_dir))

    def exact(self, word: str) -> list[Entry]:
        return self._by_form.get(word, [])

    def phrases_from(self, first_word: str) -> list[tuple[tuple[str, ...], Entry]]:
        """Multi-word entries that start with the word, longest first."""
        return self._phrases.get(first_word, [])

    def readings(self, word: str) -> list[Reading]:
        """All the ways the word agrees with the dictionary. Empty if unknown."""
        exact = self.exact(word)
        if exact:
            return [Reading(entry, "exact") for entry in exact]
        found: dict[int, Reading] = {}
        for base, ending in base_candidates(word):
            for entry in self.exact(base):
                if entry.key != base:
                    continue
                if ending == "s" and entry.pos == "n":
                    found.setdefault(id(entry), Reading(entry, "plural"))
                elif entry.pos == "v":
                    how = "unlisted form" if entry.approved else "verb form"
                    found.setdefault(id(entry), Reading(entry, how))
        return list(found.values())

    def related(self, word: str) -> list[Reading]:
        """Readings of the base forms of a word, also when the word has its own entry,
        for example "running" (an adjective) and "run" (a verb)."""
        exact = {id(entry) for entry in self.exact(word)}
        found: dict[int, Reading] = {}
        for base, _ in base_candidates(word):
            for entry in self.exact(base):
                if entry.key == base and id(entry) not in exact and entry.pos in ("v", "n"):
                    how = "unlisted form" if entry.approved and entry.pos == "v" else "form"
                    found.setdefault(id(entry), Reading(entry, how))
        return list(found.values())

    def approved_ing_words(self) -> set[str]:
        return {form for entry in self.entries if entry.approved
                for form in entry.forms if form.endswith("ing")}

    def lookup(self, query: str) -> list[Reading]:
        """Readings of a word or of a group of words."""
        words = query.lower().split()
        if len(words) > 1:
            return [Reading(entry, "exact") for phrase, entry in self.phrases_from(words[0])
                    if list(phrase) == words]
        return self.readings(words[0]) if words else []
