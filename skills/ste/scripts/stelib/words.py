"""Classify the words of a sentence with the dictionary and the project terms."""
from __future__ import annotations

from dataclasses import dataclass

from .dictionary import Dictionary, Entry, Reading
from .terms import TermMatcher
from .text import Sentence, Token, WORD

FUNCTION_WORD_POS = {"adv", "prep", "conj", "pron"}
VERB_CONTEXT = {"to", "can", "cannot", "must", "will", "do", "does", "did", "not", "should",
                "could", "would", "may", "might", "shall", "you", "we", "they", "i"}
DETERMINERS = {"the", "a", "an", "this", "that", "these", "those", "each", "every", "its",
               "their", "our", "your", "any", "no", "some", "all", "his", "her", "my"}

_UNITS = ("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen "
          "fifteen sixteen seventeen eighteen nineteen twenty thirty forty fifty sixty seventy "
          "eighty ninety hundred thousand million billion").split()
_ORDINALS = ("first second third fourth fifth sixth seventh eighth ninth tenth eleventh twelfth "
             "twentieth thirtieth hundredth thousandth").split()
NUMBER_WORDS = set(_UNITS) | set(_ORDINALS)

OK = "ok"
UNKNOWN = "unknown"
NOT_APPROVED = "not approved"  # only lowercase readings
FUNCTION_WORD = "function word"  # only lowercase adverb, preposition, conjunction, pronoun rows
WRONG_PART_OF_SPEECH = "wrong part of speech"  # approved in a different part of speech
UNLISTED_FORM = "unlisted form"  # a form that the dictionary does not give for an approved verb


def normalize(text: str) -> str:
    word = text.lower().replace("’", "'")
    if word.endswith("(s)"):
        word = word[:-3]
    for ending in ("'s", "'"):
        if word.endswith(ending):
            word = word[: -len(ending)]
    return word.strip("-")


def is_number_word(word: str) -> bool:
    """A number in words ("two", "twenty-one", "third"): a technical noun (rule 1.5)."""
    parts = [part for part in word.split("-") if part]
    return bool(parts) and all(part in NUMBER_WORDS for part in parts)


def is_acronym(text: str) -> bool:
    letters = [char for char in text if char.isalpha()]
    return len(letters) > 1 and all(char.isupper() for char in letters)


@dataclass
class Verdict:
    status: str
    readings: list[Reading]

    @property
    def lowercase_entries(self) -> list[Entry]:
        return unique_entries(r.entry for r in self.readings if not r.entry.approved)

    @property
    def approved_entries(self) -> list[Entry]:
        return unique_entries(r.entry for r in self.readings if r.approved)


def unique_entries(entries) -> list[Entry]:
    seen, result = set(), []
    for entry in entries:
        if id(entry) not in seen:
            seen.add(id(entry))
            result.append(entry)
    return result


class SentenceWords:
    """The words of one sentence, the terms in it, and the dictionary verdicts."""

    def __init__(self, sentence: Sentence, dictionary: Dictionary | None, terms: TermMatcher,
                 imperative_possible: bool = True):
        self.tokens = sentence.tokens
        self.imperative_possible = imperative_possible  # False for titles and table cells
        self.dictionary = dictionary
        self.words = [normalize(token.text) if token.kind == WORD else None for token in self.tokens]
        self.label_end = sentence.label_length()  # "**Note:**", "WARNING:" are labels, not text
        self.first_word = next((i for i, token in enumerate(self.tokens)
                                if token.kind == WORD and i >= self.label_end), -1)
        self.in_term: set[int] = set()
        self.phrases: dict[int, tuple[int, Entry]] = {}  # start index -> (length, entry)
        self._mark_terms(terms)
        if dictionary:
            self._mark_dictionary_phrases()

    def _mark_terms(self, terms: TermMatcher) -> None:
        index = 0
        while index < len(self.words):
            length = terms.match_length(self.words, index) if self.words[index] else 0
            self.in_term.update(range(index, index + length))
            index += max(length, 1)

    def _mark_dictionary_phrases(self) -> None:
        index = 0
        while index < len(self.words):
            length, entry = self._phrase_at(index)
            if entry and not self.in_term.intersection(range(index, index + length)):
                self.phrases[index] = (length, entry)
                index += length
            else:
                index += 1

    def _phrase_at(self, index: int) -> tuple[int, Entry | None]:
        word = self.words[index]
        if not word:
            return 0, None
        for phrase, entry in self.dictionary.phrases_from(word):
            if tuple(self.words[index:index + len(phrase)]) == phrase:
                return len(phrase), entry
        return 0, None

    def covered_by_phrase(self, index: int) -> bool:
        return any(start <= index < start + length for start, (length, _) in self.phrases.items())

    def is_proper_noun(self, token: Token, index: int) -> bool:
        """A name: an acronym, or a capitalized word that is not the first word,
        or a first word that the dictionary does not know."""
        if token.kind != WORD or not token.text[:1].isupper():
            return False
        if is_acronym(token.text):
            return True
        if index != self.first_word:
            return True
        return not (self.dictionary and self.dictionary.readings(normalize(token.text)))

    def checked_indexes(self) -> list[int]:
        """Word tokens that the dictionary check examines."""
        return [i for i, token in enumerate(self.tokens)
                if token.kind == WORD and i >= self.label_end and i not in self.in_term
                and not self.covered_by_phrase(i) and not self.is_proper_noun(token, i)
                and self.words[i] and not is_number_word(self.words[i])]

    def previous_word(self, index: int) -> str | None:
        return self.words[index - 1] if index > 0 else None

    def next_is_word(self, index: int) -> bool:
        return index + 1 < len(self.tokens) and self.tokens[index + 1].kind == WORD

    def verdict(self, index: int) -> Verdict:
        word = self.words[index]
        readings = self.dictionary.readings(word)
        if not readings and "-" in word:
            return self._hyphenated_verdict(word)
        status = classify(readings, self._suspects(readings, index))
        if status == NOT_APPROVED and self._technical_noun_use(readings, word):
            status = NOT_APPROVED if self._verb_context(index) else OK
        return Verdict(status, readings)

    def _technical_noun_use(self, readings: list[Reading], word: str) -> bool:
        """The dictionary marks the noun of this verb as a technical noun, and the
        word has no verb ending. Then only a verb context shows a wrong use."""
        lowercase = [r.entry for r in readings if not r.entry.approved]
        return all(entry.noun_is_technical for entry in lowercase) and not word.endswith(("ed", "ing"))

    def _verb_context(self, index: int) -> bool:
        return self.previous_word(index) in VERB_CONTEXT or (
            index == self.first_word and self.imperative_possible)

    def _hyphenated_verdict(self, word: str) -> Verdict:
        """A hyphenated word that the dictionary does not know: examine its parts.
        A part that is not approved gives a question, never an error."""
        part_readings = [(part, self.dictionary.readings(part)) for part in word.split("-") if part]
        for _, readings in part_readings:
            status = classify(readings, wrong_use=False)
            if status in (NOT_APPROVED, FUNCTION_WORD):
                return Verdict(NOT_APPROVED, readings)
        if any(not readings for _, readings in part_readings):
            return Verdict(UNKNOWN, [])
        return Verdict(OK, [])

    def _suspects(self, readings: list[Reading], index: int) -> bool:
        """For a word that has approved and lowercase rows: does the context show
        the part of speech that is not approved?"""
        lowercase = {r.entry.pos for r in readings if not r.entry.approved}
        approved = {r.entry.pos for r in readings if r.approved}
        before = self.previous_word(index)
        if "v" in lowercase - approved and self._verb_context(index):
            return True
        if "n" in lowercase - approved and before in DETERMINERS:
            return True
        return "adj" in lowercase - approved and before in DETERMINERS and self.next_is_word(index)


def classify(readings: list[Reading], wrong_use: bool) -> str:
    if not readings:
        return UNKNOWN
    approved = [r for r in readings if r.approved]
    lowercase = [r for r in readings if not r.entry.approved]
    if approved and lowercase:
        return WRONG_PART_OF_SPEECH if wrong_use else OK
    if approved:
        return OK
    if lowercase:
        exact_function_words = all(r.how == "exact" and r.entry.pos in FUNCTION_WORD_POS for r in lowercase)
        return FUNCTION_WORD if exact_function_words else NOT_APPROVED
    return UNLISTED_FORM
