"""Divide the text of one Markdown block into tokens and sentences.

The tokens keep their offsets in the block text, so that each result can give
its line and column. Inline code, quoted text, URLs and identifiers become one
token each, because the STE word count counts each of them as one word
(rules 8.6 and 8.7). Text in parentheses becomes one token of the outer
sentence and a sentence of its own (rule 8.5).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

WORD = "word"
IDENT = "ident"
NUMBER = "number"
CODE = "code"
QUOTE = "quote"
URL = "url"
PAREN = "paren"
LATIN = "latin"
PUNCT = "punct"

SENTENCE_ENDS = ".!?"
UNITS = {
    "ms", "s", "sec", "min", "h", "hr", "d", "kb", "mb", "gb", "tb", "kib", "mib", "gib",
    "b", "px", "pt", "em", "rem", "mm", "cm", "m", "km", "kg", "g", "v", "a", "w", "hz",
    "khz", "mhz", "ghz", "bps", "kbps", "mbps", "rpm", "°c", "°f", "percent",
}
QUOTE_PAIRS = {'"': '"', "“": "”"}
SHORT_SUFFIX_IN_PARENS = 3  # "file(s)" is one word, not a parenthetical sentence
MAX_ABBREVIATION_LENGTH = 4  # "Fig. 3", "No. 5": not the end of a sentence
MIN_WORD_BEFORE_LOWERCASE_START = 4  # "... the build. npm ..." ends a sentence
LABEL_WORDS = {"note", "notes", "warning", "caution", "danger", "notice"}

_LATIN = re.compile(r"(?i)(e\.g\.|i\.e\.|etc\.|viz\.|cf\.)")
_URL = re.compile(r"(?:https?://|www\.)[^\s<>()\[\]]*[^\s<>()\[\].,;:!?'\"]")
_AUTOLINK = re.compile(r"<(?:https?://|mailto:)[^>]+>")
_HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)
_HTML_TAG = re.compile(r"</?[A-Za-z][^>]*>")
_HTML_ENTITY = re.compile(r"&(?:#\d+|#[xX][0-9A-Fa-f]+|[A-Za-z][A-Za-z0-9]*);")
_NUMBER = re.compile(r"\d+(?:[.,]\d+)*%?")
_WORDISH = re.compile(
    r"[A-Za-z0-9](?:[A-Za-z0-9'’\-]|_(?=[A-Za-z0-9])|[./\\:@#+](?=[A-Za-z0-9_]))*")
_IDENTIFIER = re.compile(r"^[A-Z][A-Z0-9]*-\d")
_EMPHASIS = re.compile(r"\*\*|__|\*|_")


@dataclass
class Token:
    kind: str
    text: str
    start: int
    end: int
    group: int | None = None  # tokens of one emphasis span count as one word

    @property
    def is_word(self) -> bool:
        return self.kind == WORD


@dataclass
class Sentence:
    tokens: list[Token]
    nested: bool = False  # the text was in parentheses
    key: str = ""  # whitespace-normalized text, set by split_sentences

    @property
    def is_label(self) -> bool:
        """A run-in title such as "**Activation tab.**": all words in one emphasis span."""
        groups = {token.group for token in self.tokens if token.kind != PUNCT}
        return len(groups) == 1 and None not in groups

    def label_length(self) -> int:
        """Number of tokens of a label at the start: "**Note:**", "WARNING:", "Note:"."""
        first = self.tokens[0]
        if first.group is not None:
            in_group = 0
            while in_group < len(self.tokens) and self.tokens[in_group].group == first.group:
                in_group += 1
            if any(token.text == ":" for token in self.tokens[:in_group]):
                return in_group
            if in_group < len(self.tokens) and self.tokens[in_group].text == ":":
                return in_group + 1
            return 0
        if first.is_word and first.text.lower() in LABEL_WORDS and len(self.tokens) > 1 \
                and self.tokens[1].text == ":":
            return 2
        return 0


@dataclass
class _Scan:
    text: str
    tokens: list[Token] = field(default_factory=list)
    inner: list[tuple[int, int]] = field(default_factory=list)  # parenthetical spans
    group: int | None = None
    next_group: int = 0


def _matching_bracket(text: str, start: int, opening: str, closing: str) -> int:
    depth = 0
    for index in range(start, len(text)):
        if text[index] == opening:
            depth += 1
        elif text[index] == closing:
            depth -= 1
            if depth == 0:
                return index
    return -1


def _link_end(text: str, label_end: int) -> int:
    """Offset after the target of "[label](target)" or "[label][ref]"; -1 if no link."""
    after = label_end + 1
    if after < len(text) and text[after] in "([":
        closing = ")" if text[after] == "(" else "]"
        end = _matching_bracket(text, after, text[after], closing)
        return end + 1 if end >= 0 else -1
    return -1


def _emit(scan: _Scan, kind: str, start: int, end: int) -> None:
    scan.tokens.append(Token(kind, scan.text[start:end], start, end, scan.group))


def _word_kind(text: str) -> str:
    if any(char.isdigit() for char in text) or any(char in "./\\:@#+_" for char in text):
        return IDENT
    if _IDENTIFIER.match(text):
        return IDENT
    return WORD


def _emphasis_toggles(text: str, index: int, marker: str) -> bool:
    """An emphasis marker, not an underscore inside a name such as snake_case."""
    before = text[index - 1] if index > 0 else " "
    after = text[index + len(marker)] if index + len(marker) < len(text) else " "
    if marker.startswith("_"):
        return not (before.isalnum() and after.isalnum())
    return not (before.isspace() and after.isspace())


def _skip_markup(text: str, index: int) -> int | None:
    """End of an HTML comment, tag or character reference at index, or None."""
    if _AUTOLINK.match(text, index):
        return None
    for pattern in (_HTML_COMMENT, _HTML_TAG, _HTML_ENTITY):
        match = pattern.match(text, index)
        if match:
            return match.end()
    return None


def _scan_special(scan: _Scan, index: int) -> int | None:
    """Read one markup item at index. Return the next index, or None."""
    text = scan.text
    skipped = _skip_markup(text, index)
    if skipped is not None:
        return skipped
    autolink = _AUTOLINK.match(text, index)
    if autolink:
        _emit(scan, URL, index, autolink.end())
        return autolink.end()
    char = text[index]
    if char == "`":
        run = len(text[index:]) - len(text[index:].lstrip("`"))
        close = text.find("`" * run, index + run)
        if close >= 0:
            _emit(scan, CODE, index, close + run)
            return close + run
    if text.startswith("![", index) or char == "[":
        opening = index + 1 if char == "!" else index
        label_end = _matching_bracket(text, opening, "[", "]")
        end = _link_end(text, label_end) if label_end >= 0 else -1
        if end >= 0:
            if char == "[":
                _scan_into(scan, index + 1, label_end)
            return end
    if char in QUOTE_PAIRS:
        close = text.find(QUOTE_PAIRS[char], index + 1)
        if close > index + 1:
            _emit(scan, QUOTE, index, close + 1)
            return close + 1
    if char == "(":
        return _scan_parenthesis(scan, index)
    return None


def _scan_parenthesis(scan: _Scan, index: int) -> int | None:
    text = scan.text
    close = _matching_bracket(text, index, "(", ")")
    if close < 0:
        return None
    attached = index > 0 and text[index - 1].isalnum()
    if attached and close - index - 1 <= SHORT_SUFFIX_IN_PARENS:
        if scan.tokens and scan.tokens[-1].end == index:
            scan.tokens[-1].end = close + 1
            scan.tokens[-1].text = text[scan.tokens[-1].start: close + 1]
        return close + 1
    _emit(scan, PAREN, index, close + 1)
    scan.inner.append((index + 1, close))
    return close + 1


def _scan_into(scan: _Scan, start: int, end: int) -> None:
    index = start
    text = scan.text
    while index < end:
        if text[index].isspace():
            index += 1
            continue
        special = _scan_special(scan, index)
        if special is not None:
            index = special
            continue
        emphasis = _EMPHASIS.match(text, index)
        if emphasis and _emphasis_toggles(text, index, emphasis.group()) and (
                scan.group is not None or text.find(emphasis.group(), emphasis.end(), end) >= 0):
            if scan.group is None:
                scan.group, scan.next_group = scan.next_group, scan.next_group + 1
            else:
                scan.group = None
            index = emphasis.end()
            continue
        index = _scan_plain(scan, index)


def _scan_plain(scan: _Scan, index: int) -> int:
    text = scan.text
    for pattern, kind in ((_URL, URL), (_LATIN, LATIN)):
        match = pattern.match(text, index)
        if match:
            _emit(scan, kind, index, match.end())
            return match.end()
    number = _NUMBER.match(text, index)
    word = _WORDISH.match(text, index)
    if number and (word is None or number.end() >= word.end()):
        return _scan_number(scan, index, number.end())
    if word:
        _emit(scan, _word_kind(word.group()), index, word.end())
        return word.end()
    _emit(scan, PUNCT, index, index + 1)
    return index + 1


def _scan_number(scan: _Scan, index: int, end: int) -> int:
    """A number, with its unit when one follows (rule 8.6: one word)."""
    unit = re.match(r"\s?([A-Za-z°%]+)\b", scan.text[end:])
    if unit and unit.group(1).lower() in UNITS:
        end += unit.end()
    _emit(scan, NUMBER, index, end)
    return end


def tokenize(text: str, start: int = 0, end: int | None = None) -> tuple[list[Token], list[tuple[int, int]]]:
    """Tokens of text[start:end], and the spans of the parenthetical texts."""
    end = len(text) if end is None else end
    scan = _Scan(text=text[:end])
    _scan_into(scan, start, end)
    return scan.tokens, scan.inner


def _quote_ends_sentence(token: Token, following: Token | None) -> bool:
    """American punctuation puts the period in the quotes: click "Save." Then ..."""
    return token.kind == QUOTE and token.text[-2:-1] in tuple(SENTENCE_ENDS) and (
        following is None or following.text[:1].isupper())


def _sentence_ends_at(tokens: list[Token], index: int) -> bool:
    token = tokens[index]
    following = tokens[index + 1] if index + 1 < len(tokens) else None
    if _quote_ends_sentence(token, following):
        return True
    if token.kind != PUNCT or token.text not in SENTENCE_ENDS:
        return False
    if following is None:
        return True
    previous = tokens[index - 1] if index > 0 else None
    if previous is not None and previous.is_word and previous.text[:1].isupper() \
            and len(previous.text) <= MAX_ABBREVIATION_LENGTH and following.kind == NUMBER:
        return False  # "Fig. 3", "No. 5"
    if following.text[:1].islower():
        return following.is_word and previous is not None and previous.is_word \
            and len(previous.text) >= MIN_WORD_BEFORE_LOWERCASE_START
    return True


def _normalized(text: str, sentence_tokens: list[Token]) -> str:
    return " ".join(text[sentence_tokens[0].start:sentence_tokens[-1].end].split())


def split_sentences(text: str, start: int = 0, end: int | None = None,
                    nested: bool = False) -> list[Sentence]:
    """Sentences of a block text. Parenthetical texts follow as nested sentences."""
    tokens, inner_spans = tokenize(text, start, end)
    sentences: list[Sentence] = []
    current: list[Token] = []
    for index, token in enumerate(tokens):
        current.append(token)
        if _sentence_ends_at(tokens, index):
            sentences.append(Sentence(current, nested))
            current = []
    if current:
        sentences.append(Sentence(current, nested))
    sentences = [sentence for sentence in sentences
                 if any(token.kind != PUNCT for token in sentence.tokens)]
    for sentence in sentences:
        sentence.key = _normalized(text, sentence.tokens)
    for inner_start, inner_end in inner_spans:
        sentences.extend(split_sentences(text, inner_start, inner_end, nested=True))
    return sentences


def count_words(sentence: Sentence, is_proper_noun) -> int:
    """The STE word count of a sentence (rules 8.4 to 8.7).

    Each token counts as one word, except punctuation and a label at the start
    ("**Note:**", "WARNING:"). All the tokens of one emphasis span count as one
    word (text in a different font), and a group of proper-noun words counts as
    one word.
    """
    count = 0
    counted_groups: set[int] = set()
    previous_proper = False
    label = sentence.label_length()
    for position, token in enumerate(sentence.tokens[label:], start=label):
        if token.kind == PUNCT:
            previous_proper = False
            continue
        if token.group is not None:
            if token.group not in counted_groups:
                counted_groups.add(token.group)
                count += 1
            previous_proper = False
            continue
        proper = token.is_word and is_proper_noun(token, position)
        if not (proper and previous_proper):
            count += 1
        previous_proper = proper
    return count
