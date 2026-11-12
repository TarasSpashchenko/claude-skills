"""Find the technical nouns and technical verbs of a project in a text."""
from __future__ import annotations

from .dictionary import inflections, plurals


def _verb_forms(verb: str) -> set[str]:
    """The regular forms of a technical verb, without "-ing": rule 3.5 also applies to it."""
    return {form for form in inflections(verb) if not form.endswith("ing")}


class TermMatcher:
    """Matches terms of one or more words: nouns with their plural, verbs with their forms."""

    def __init__(self, nouns=(), verbs=(), extra_forms=()):
        self._phrases: dict[str, set[tuple[str, ...]]] = {}
        for noun in nouns:
            words = noun.lower().split()
            if words:
                for form in plurals(words[-1]):
                    self._add((*words[:-1], form))
        for verb in verbs:
            words = verb.lower().split()
            if words:
                for form in _verb_forms(words[0]):
                    self._add((form, *words[1:]))
        for form in extra_forms:
            self._add(tuple(form.lower().split()))

    def _add(self, phrase: tuple[str, ...]) -> None:
        if phrase:
            self._phrases.setdefault(phrase[0], set()).add(phrase)

    def match_length(self, words: list[str], index: int) -> int:
        """Number of words of the longest term that starts at index, or 0."""
        best = 0
        for phrase in self._phrases.get(words[index], ()):
            end = index + len(phrase)
            if len(phrase) > best and tuple(words[index:end]) == phrase:
                best = len(phrase)
        return best
