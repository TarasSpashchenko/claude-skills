"""The STE rules that a script can examine, applied to the units of a document.

The class `error` is for a rule that the script can examine without grammar.
The class `question` is for an item that the writer (the model) must examine.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .config import PROCEDURAL, STRUCTURE
from .dictionary import Dictionary, Entry, base_candidates
from .document import Unit
from .markdown import CELL, HEADER_CELL, PARAGRAPH, TITLE, ListInfo
from .terms import TermMatcher
from .text import CODE, IDENT, LATIN, PUNCT, WORD, Sentence, count_words
from .words import (DETERMINERS, FUNCTION_WORD, NOT_APPROVED, UNKNOWN, UNLISTED_FORM,
                    WRONG_PART_OF_SPEECH, SentenceWords, is_number_word, normalize)

ERROR = "error"
QUESTION = "question"
UNKNOWN_WORD_RULE = "1.5"

PROCEDURE_SENTENCE_LIMIT = 20
SENTENCE_LIMIT = 25
PARAGRAPH_SENTENCE_LIMIT = 6
NOUN_GROUP_LIMIT = 3
MIN_ING_WORD_LENGTH = 5
TEXT_EXCERPT = 30

PRONOUNS = {"he", "she", "him", "her", "his", "hers", "himself", "herself"}
CONTRACTION_ENDINGS = ("n't", "'re", "'ve", "'ll", "'d", "'m")
CONTRACTED_WORDS = {"it's", "that's", "let's", "there's", "here's", "what's", "who's",
                    "where's", "how's", "he's", "she's"}
MAKE_SURE_VERBS = {"make", "makes", "made", "making"}
HAVE_FORMS = {"has", "have", "had"}
PASSIVE_BE_FORMS = {"is", "are", "was", "were"}
MODAL_BE = {("is", "to", "be"), ("are", "to", "be"), ("can", "be"), ("cannot", "be"),
            ("must", "be"), ("will", "be"), ("could", "be"), ("should", "be"),
            ("would", "be"), ("may", "be"), ("might", "be")}
IRREGULAR_PARTICIPLES = {
    "been", "begun", "bent", "bound", "broken", "brought", "built", "bought", "caught", "chosen",
    "done", "drawn", "driven", "eaten", "fallen", "felt", "found", "forgotten", "frozen", "given",
    "gone", "grown", "held", "hidden", "kept", "known", "laid", "led", "left", "lost", "made",
    "meant", "met", "paid", "proven", "ridden", "risen", "run", "said", "seen", "sent", "set",
    "shaken", "shown", "shut", "sold", "spent", "split", "spoken", "stolen", "struck", "stuck",
    "taken", "taught", "thrown", "told", "torn", "understood", "won", "worn", "written",
}
NOT_PARTICIPLES = {"need", "feed", "seed", "speed", "bleed", "breed", "shed", "embed", "red", "bed"}
NOT_ING_FORMS = {"ceiling", "morning", "evening", "nothing", "anything", "everything", "something",
                 "during", "awning", "herring"}
SENTENCE_END = (".", "?", "!")
CLOSING_MARKUP = "*_\"”’')"
CATEGORY_NAMES = {1: "manufacturing processes", 2: "computer processes", 3: "subject fields",
                  4: "law and regulations"}


@dataclass
class Finding:
    cls: str
    rule: str
    line: int
    column: int
    text: str
    message: str
    alternatives: str = ""
    page: int | None = None
    count: int = 1
    lines: list[int] = field(default_factory=list)  # all the lines of a grouped question


def _entry_hint(entries: list[Entry]) -> tuple[str, int | None]:
    """Alternatives and page of the lowercase rows."""
    if not entries:
        return "", None
    alternatives = "; ".join(f"{entry.label}: {entry.alternatives}" for entry in entries)
    return alternatives, entries[0].page


def _is_contraction(word: str) -> bool:
    return word in CONTRACTED_WORDS or word.endswith(CONTRACTION_ENDINGS)


def _has_style_error(text: str) -> bool:
    """Words that the style checks report: the word check does not report them again."""
    word = text.lower().replace("’", "'")
    return _is_contraction(word) or word in PRONOUNS


def _visible_end(text: str) -> str:
    """The text without closing emphasis marks, quotes and parentheses at its end."""
    return text.rstrip().rstrip(CLOSING_MARKUP)


class _GroupedQuestions:
    """One question for each word, with all the lines where it occurs."""

    def __init__(self):
        self._findings: dict[tuple[str, str], Finding] = {}

    def add(self, key: str, finding: Finding) -> None:
        existing = self._findings.get((finding.rule, key))
        if existing:
            existing.count += 1
            if finding.line not in existing.lines:
                existing.lines.append(finding.line)
        else:
            finding.lines = [finding.line]
            self._findings[(finding.rule, key)] = finding

    def findings(self) -> list[Finding]:
        return list(self._findings.values())


class Checker:
    def __init__(self, dictionary: Dictionary | None, terms: TermMatcher):
        self.dictionary = dictionary
        self.terms = terms
        self.approved_ing = dictionary.approved_ing_words() if dictionary else set()

    def check(self, units: list[Unit], selected: set[int] | None = None) -> list[Finding]:
        """Findings for the sentences in selected (ids), or for all sentences if None."""
        findings: list[Finding] = []
        grouped = _GroupedQuestions()
        for unit in units:
            chosen = [s for s in unit.sentences if selected is None or id(s) in selected]
            for sentence in chosen:
                findings += _SentenceCheck(self, unit, sentence, grouped).run()
            if chosen:
                findings += self._paragraph_findings(unit)
        findings += self._list_findings(units, selected)
        findings += grouped.findings()
        return sorted(findings, key=lambda f: (f.line, f.column, f.rule))

    def technical_verb_categories(self, word: str) -> list[int]:
        """Categories of rule 1.12 that list the word, or a base form of it, as an example."""
        if not self.dictionary:
            return []
        bases = {word, *(base for base, _ in base_candidates(word))}
        return sorted(category for category, verbs in self.dictionary.technical_verbs.items()
                      if bases & verbs)

    # -- rule 6.6 ---------------------------------------------------------
    def _paragraph_findings(self, unit: Unit) -> list[Finding]:
        if unit.block.kind != PARAGRAPH or unit.kind == PROCEDURAL:
            return []
        count = sum(1 for sentence in unit.sentences if not sentence.nested and not sentence.is_label)
        if count <= PARAGRAPH_SENTENCE_LIMIT:
            return []
        line, column = unit.block.position(0)
        return [Finding(ERROR, "6.6", line, column, f"{count} sentences",
                        f"paragraph has {count} sentences (maximum {PARAGRAPH_SENTENCE_LIMIT}): "
                        "divide it, or use a vertical list")]

    # -- rule 4.3 ---------------------------------------------------------
    def _list_findings(self, units: list[Unit], selected: set[int] | None) -> list[Finding]:
        unit_of = {id(unit.block): unit for unit in units}
        lists: dict[int, ListInfo] = {}
        for unit in units:
            if unit.block.list is not None:
                lists.setdefault(id(unit.block.list), unit.block.list)
        findings = []
        for info in lists.values():
            if unit_of[id(info.items[0])].kind != STRUCTURE:
                findings += _ListCheck(info, unit_of, selected).run()
        return findings


class _ListCheck:
    """Rule 4.3 for one list. With --since, only the changed parts give results."""

    def __init__(self, info: ListInfo, unit_of: dict[int, Unit], selected: set[int] | None):
        self.info = info
        self.unit_of = unit_of
        self.selected = selected

    def _changed(self, block) -> bool:
        return self.selected is None or any(id(s) in self.selected for s in self.unit_of[id(block)].sentences)

    def _error(self, block, offset: int, message: str) -> Finding:
        line, column = block.position(offset)
        return Finding(ERROR, "4.3", line, column, block.text[max(0, offset - TEXT_EXCERPT):offset + 1],
                       message)

    def run(self) -> list[Finding]:
        info, findings = self.info, []
        first, last = info.items[0], info.items[-1]
        if info.depth > 0 and self._changed(first):
            findings.append(self._error(first, 0, "list in an item of a different list: "
                                        "use one level of list"))
        lead = info.lead
        if info.depth == 0 and lead is not None and self._changed(lead) \
                and not _visible_end(lead.text).endswith(":"):
            findings.append(self._error(lead, len(lead.text.rstrip()) - 1,
                                        "text before a vertical list must end with a colon"))
        for item in info.items:
            if self._changed(item):
                findings += self._item_errors(item)
        end = _visible_end(last.text)
        if info.depth == 0 and end and self._changed(last) and not end.endswith(SENTENCE_END + (":",)):
            findings.append(self._error(last, len(last.text.rstrip()) - 1,
                                        "put a period after the last item of a vertical list"))
        return findings

    def _item_errors(self, item) -> list[Finding]:
        findings = []
        tokens = [t for s in self.unit_of[id(item)].sentences if not s.nested for t in s.tokens]
        if tokens and tokens[0].kind == WORD and tokens[0].text[:1].islower():
            findings.append(self._error(item, tokens[0].start, "start each list item with an "
                                        "uppercase letter"))
        if _visible_end(item.text).endswith(","):
            findings.append(self._error(item, len(item.text.rstrip()) - 1,
                                        "do not put a comma at the end of a list item"))
        return findings


class _SentenceCheck:
    """All the checks of one sentence."""

    def __init__(self, checker: Checker, unit: Unit, sentence: Sentence, grouped: _GroupedQuestions):
        self.checker = checker
        self.unit = unit
        self.sentence = sentence
        self.grouped = grouped
        self.is_title = unit.block.kind in (TITLE, HEADER_CELL) or sentence.is_label
        self.words = SentenceWords(sentence, checker.dictionary, checker.terms,
                                   imperative_possible=unit.block.kind not in (TITLE, HEADER_CELL, CELL))
        self.findings: list[Finding] = []

    def run(self) -> list[Finding]:
        self._punctuation_and_style()
        if self.checker.dictionary:
            self._word_approval()
            self._ing_words()
        if not self.is_title:
            self._make_sure_that()
            self._length()
            self._verb_constructions()
            if self.checker.dictionary:
                self._noun_groups()
        return self.findings

    # -- helpers ------------------------------------------------------------
    def _at(self, index: int) -> tuple[int, int]:
        return self.unit.block.position(self.sentence.tokens[index].start)

    def _add(self, cls: str, rule: str, index: int, message: str, **extra) -> None:
        line, column = self._at(index)
        self.findings.append(Finding(cls, rule, line, column, self.sentence.tokens[index].text,
                                     message, **extra))

    def _group(self, key: str, rule: str, index: int, message: str, **extra) -> None:
        line, column = self._at(index)
        self.grouped.add(key, Finding(QUESTION, rule, line, column, key, message, **extra))

    # -- rules 8.1, 4.2, GR-6, GR-3 ---------------------------------------------
    def _punctuation_and_style(self) -> None:
        for index, token in enumerate(self.sentence.tokens):
            word = token.text.lower().replace("’", "'")
            if token.kind == PUNCT and token.text == ";":
                self._add(ERROR, "8.1", index, "semicolon: write two sentences or use a vertical list")
            elif token.kind == LATIN:
                self._add(ERROR, "GR-6", index, 'Latin abbreviation, not an approved word: write '
                          '"for example", "that is", or give the full list')
            elif token.kind == WORD and _is_contraction(word):
                self._add(ERROR, "4.2", index, "contraction: write the full words")
            elif token.kind == WORD and word in PRONOUNS:
                self._add(ERROR, "GR-3", index, 'do not use "he" or "she" (GR-7): write the noun, '
                          'for example "the operator", or "you"')

    # -- GR-1 (a recommendation, thus a question) -----------------------------------
    def _make_sure_that(self) -> None:
        words = self.words.words
        for index in range(len(words) - 1):
            if words[index] in MAKE_SURE_VERBS and words[index + 1] == "sure":
                following = words[index + 2] if index + 2 < len(words) else None
                if following != "that":
                    self._add(QUESTION, "GR-1", index, 'write "that" after "make sure"')

    # -- rules 5.1, 5.5, 6.3 --------------------------------------------------------
    def _limit(self) -> tuple[int, str]:
        unit = self.unit
        if unit.is_note:
            return SENTENCE_LIMIT, "5.5"
        if unit.is_safety_instruction or unit.kind == PROCEDURAL:
            return PROCEDURE_SENTENCE_LIMIT, "5.1"
        return SENTENCE_LIMIT, "6.3"

    def _length(self) -> None:
        count = count_words(self.sentence, self.words.is_proper_noun)
        limit, rule = self._limit()
        if count > limit:
            self._add(ERROR, rule, 0, f"sentence has {count} words (maximum {limit})")
        elif count > PROCEDURE_SENTENCE_LIMIT and self.unit.is_numbered_item and not self.unit.is_note:
            self._add(QUESTION, "5.1", 0, f"numbered item has {count} words: if it is a procedure "
                      f"step, the maximum is {PROCEDURE_SENTENCE_LIMIT}")

    # -- rule 1.1 and rules 1.2, 1.5, 1.12, 3.1 ---------------------------------------
    def _word_approval(self) -> None:
        for start, (_, entry) in self.words.phrases.items():
            if not entry.approved:
                self._judge_phrase(start, entry)
        for index in self.words.checked_indexes():
            word = self.words.words[index]
            if self._is_ing_candidate(word) or _has_style_error(self.sentence.tokens[index].text):
                continue  # rule 3.5, or the style checks, examine it
            self._judge_word(index)

    def _judge_phrase(self, start: int, entry: Entry) -> None:
        """A group of words with a lowercase row. It can also be a sequence of words that
        are approved one by one ("close to"), a verb and a preposition ("turn on"), or,
        after an article, a noun ("the rear of"). Only a group that is not a verb group
        and has a word that is not approved alone is certain."""
        if self.words.previous_word(start) in DETERMINERS:
            return
        hint = dict(alternatives=f"{entry.label}: {entry.alternatives}", page=entry.page)
        words = entry.key.split()
        certain = entry.pos != "v" and any(  # a verb group can be a verb and a preposition
            not any(r.approved for r in self.checker.dictionary.readings(w)) for w in words)
        in_emphasis = self.sentence.tokens[start].group is not None
        if certain and not in_emphasis:
            self._add(ERROR, "1.1", start, f'"{entry.headword}" is not approved', **hint)
        else:
            self._group(entry.key, "1.1", start, f'"{entry.headword}" is not approved, unless the '
                        "words are not one group here", **hint)

    def _verb_hint(self, word: str) -> str:
        categories = self.checker.technical_verb_categories(word)
        if not categories:
            return ""
        names = ", ".join(f"{c} ({CATEGORY_NAMES[c]})" for c in categories)
        return (f". The standard lists it as a technical verb, category {names}: correct only "
                "for that process, and only as a verb (rules 1.12, 1.13)")

    def _judge_word(self, index: int) -> None:
        word = self.words.words[index]
        verdict = self.words.verdict(index)
        alternatives, page = _entry_hint(verdict.lowercase_entries)
        hint = dict(alternatives=alternatives, page=page)
        in_emphasis = self.sentence.tokens[index].group is not None
        if verdict.status == FUNCTION_WORD and not in_emphasis:
            self._add(ERROR, "1.1", index, f'"{word}" is not approved', **hint)
        elif verdict.status in (FUNCTION_WORD, NOT_APPROVED):
            self._group(word, "1.1", index, f'"{word}" is not approved, unless it is part of a '
                        f"technical noun or a technical verb{self._verb_hint(word)}", **hint)
        elif verdict.status == WRONG_PART_OF_SPEECH:
            approved = ", ".join(entry.label for entry in verdict.approved_entries)
            self._group(word, "1.2", index, f'"{word}" is approved only as {approved}: '
                        f"examine the part of speech here{self._verb_hint(word)}", **hint)
        elif verdict.status == UNLISTED_FORM:
            entry = verdict.readings[0].entry
            self._group(word, "3.1", index, f'the dictionary does not give the form "{word}" of '
                        f"{entry.label}: use a form that it gives", page=entry.page)
        elif verdict.status == UNKNOWN and not self.is_title:
            self._group(word, UNKNOWN_WORD_RULE, index, f'"{word}" is not in the dictionary')

    # -- rule 3.5 ------------------------------------------------------------------------
    def _is_ing_candidate(self, word: str) -> bool:
        if not word.endswith("ing") or len(word) < MIN_ING_WORD_LENGTH:
            return False
        stem = word[:-3]
        return (word not in self.checker.approved_ing and word not in NOT_ING_FORMS
                and any(vowel in stem for vowel in "aeiouy"))

    def _ing_words(self) -> None:
        """A title can have an "-ing" technical noun, but not a word that is not approved."""
        for index in self.words.checked_indexes():
            word = self.words.words[index]
            if not self._is_ing_candidate(word):
                continue
            verdict = self.words.verdict(index)
            if verdict.status in (NOT_APPROVED, FUNCTION_WORD):
                alternatives, page = _entry_hint(verdict.lowercase_entries)
                self._group(word, "1.1", index, f'"{word}" is a form of a word that is not approved',
                            alternatives=alternatives, page=page)
            elif not self.is_title:
                self._group(word, "3.5", index, f'"-ing" form "{word}": use it only in a technical '
                            "noun (for example a title) or as a modifier in a technical noun")

    # -- rules 3.4 and 3.6 -------------------------------------------------------------------
    def _is_participle(self, word: str | None) -> bool:
        if not word or word in NOT_PARTICIPLES:
            return False
        if not (word in IRREGULAR_PARTICIPLES or (word.endswith("ed") and len(word) > 3)):
            return False
        dictionary = self.checker.dictionary
        approved_adjective = dictionary and any(
            r.approved and r.entry.pos == "adj" for r in dictionary.readings(word))
        return not approved_adjective

    def _verb_constructions(self) -> None:
        words = self.words.words
        flagged: set[int] = set()
        for index, word in enumerate(words):
            for pattern in MODAL_BE:
                end = index + len(pattern)
                if tuple(words[index:end]) == pattern and end < len(words) and self._is_participle(words[end]):
                    self._add(QUESTION, "3.4", index, f'"{" ".join(pattern)} {words[end]}": '
                              'use the active voice, for example "you can do" or "the system does"')
                    flagged.update(range(index, end + 1))
            if word in HAVE_FORMS and index + 1 < len(words) and self._is_participle(words[index + 1]):
                self._add(QUESTION, "3.4", index, f'"{word} {words[index + 1]}": use the simple '
                          "past or the simple present, not a perfect tense")
                flagged.add(index)
        for index, word in enumerate(words):
            if word in PASSIVE_BE_FORMS and index not in flagged and index + 1 < len(words) \
                    and self._is_participle(words[index + 1]):
                self._add(QUESTION, "3.6", index, f'"{word} {words[index + 1]}": passive voice? Use '
                          "the active voice, unless the text is descriptive and the agent is unknown. "
                          "A past participle that shows a condition is an adjective (rule 3.3)")

    # -- rule 2.1 ---------------------------------------------------------------------------
    def _is_nominal(self, index: int) -> bool:
        token = self.sentence.tokens[index]
        if token.kind != WORD:
            return token.kind in (IDENT, CODE)
        word = normalize(token.text)
        if is_number_word(word):
            return False
        if index in self.words.in_term or self.words.is_proper_noun(token, index):
            return True
        readings = self.checker.dictionary.readings(word)
        # A word with only rows that are not approved can be a technical noun ("list", "file").
        return not any(r.approved for r in readings) or any(r.entry.pos == "n" for r in readings)

    def _noun_groups(self) -> None:
        run_start, run_length, previous_proper = 0, 0, False
        tokens = self.sentence.tokens
        for index in range(len(tokens) + 1):
            if index < len(tokens) and self._is_nominal(index):
                proper = self.words.is_proper_noun(tokens[index], index)
                run_start = index if run_length == 0 else run_start
                run_length += 0 if (proper and previous_proper) else 1  # a name counts as one word
                previous_proper = proper
                continue
            if run_length > NOUN_GROUP_LIMIT:
                group = " ".join(token.text for token in tokens[run_start:index])
                self._add(QUESTION, "2.1", run_start, f'"{group}" has {run_length} nouns together '
                          f"(maximum {NOUN_GROUP_LIMIT}): use a preposition or a different construction")
            run_length, previous_proper = 0, False
