"""Read a Markdown file into text blocks: titles, paragraphs, list items, table cells.

The reader keeps, for each character of a block, its line and column in the
file. It does not return code (fenced or indented), HTML comments, HTML
blocks, or the keys of the front matter.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

TITLE = "title"
PARAGRAPH = "paragraph"
ITEM = "item"
CELL = "cell"
HEADER_CELL = "header cell"

TAB_WIDTH = 4
CODE_INDENT = 4
FRONT_MATTER_FENCE = "---"
BLOCK_SCALAR_MARKS = {"", ">", "|", ">-", "|-", ">+", "|+"}
BYTE_ORDER_MARK = "﻿"
RAW_HTML_TAGS = ("pre", "script", "style", "textarea")

_HEADING = re.compile(r"^ {0,3}(#{1,6})\s+(.*?)\s*#*\s*$")
_SETEXT = re.compile(r"^ {0,3}(=+|-+)\s*$")
_RULE = re.compile(r"^ {0,3}([-*_])(\s*\1){2,}\s*$")
_FENCE = re.compile(r"^\s*(`{3,}|~{3,})(.*)$")
_LIST_ITEM = re.compile(r"^(\s*)([-*+]|\d{1,9}[.)])(\s+)(\S.*)?$")
_TASK_BOX = re.compile(r"^\[[ xX]\]\s+")
_TABLE_SEPARATOR = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$")
_HTML_BLOCK = re.compile(r"^\s*</?[A-Za-z][^>]*>\s*$")
_RAW_HTML_START = re.compile(r"^\s*<(" + "|".join(RAW_HTML_TAGS) + r")\b", re.IGNORECASE)
_FRONT_MATTER_KEY = re.compile(r"^([A-Za-z_][\w-]*):\s*(.*)$")
_BLOCKQUOTE = re.compile(r"^(\s*>\s?)")


@dataclass
class ListInfo:
    ordered: bool
    depth: int
    lead: "Block | None"  # the paragraph directly before a top-level list
    items: list["Block"] = field(default_factory=list)


@dataclass
class Block:
    kind: str
    text: str = ""
    positions: list[tuple[int, int]] = field(default_factory=list)
    sections: tuple[str, ...] = ()  # titles of the sections that contain the block
    list: ListInfo | None = None
    front_matter: bool = False
    column: int = 0  # the column number of a table cell (0 = first)

    def add(self, line_number: int, line: str, column: int) -> None:
        """Append the part of a line that starts at column (0-based)."""
        if self.text:
            self.text += " "
            self.positions.append(self.positions[-1])
        piece = line[column:].rstrip()
        self.text += piece
        self.positions.extend((line_number, column + offset + 1) for offset in range(len(piece)))

    def position(self, offset: int) -> tuple[int, int]:
        if not self.positions:
            return (0, 0)
        return self.positions[max(0, min(offset, len(self.positions) - 1))]


@dataclass
class _OpenItem:
    block: Block
    marker_indent: int
    content_indent: int


def _indent(text: str) -> int:
    return len(text.expandtabs(TAB_WIDTH))


def _table_cells(line: str) -> list[tuple[int, int]]:
    """(start, end) columns of the cells of a table row. A "|" in code does not divide."""
    bounds, in_code, start = [], False, None
    for index, char in enumerate(line):
        if char == "`":
            in_code = not in_code
        if char == "|" and not in_code and (index == 0 or line[index - 1] != "\\"):
            if start is not None:
                bounds.append((start, index))
            start = index + 1
    if start is not None and line[start:].strip():
        bounds.append((start, len(line)))
    return bounds


def _blank_quote_marker(line: str) -> str:
    """The line without its blockquote marker; spaces keep the columns."""
    match = _BLOCKQUOTE.match(line)
    return " " * match.end() + line[match.end():] if match else line


class _Reader:
    def __init__(self, text: str, front_matter_keys: tuple[str, ...]):
        self.lines = text.lstrip(BYTE_ORDER_MARK).splitlines()
        self.front_matter_keys = front_matter_keys
        self.blocks: list[Block] = []
        self.sections: list[tuple[int, str]] = []
        self.paragraph: Block | None = None
        self.lead: Block | None = None  # a paragraph that can introduce a list
        self.items: list[_OpenItem] = []
        self.after_blank = True
        self.in_quote = False

    # -- helpers ---------------------------------------------------------
    def _new_block(self, kind: str, **values) -> Block:
        block = Block(kind, sections=tuple(title for _, title in self.sections), **values)
        self.blocks.append(block)
        return block

    def _close_paragraph(self) -> None:
        self.paragraph = None

    def _interrupt(self) -> None:
        """A block that is not a paragraph: no lead for a list that follows."""
        self._close_paragraph()
        self.lead = None

    def _close_all(self) -> None:
        self._interrupt()
        self.items = []

    # -- line kinds ------------------------------------------------------
    def read(self) -> list[Block]:
        index = self._read_front_matter()
        while index < len(self.lines):
            index = self._read_at(index)
        return self.blocks

    def _read_at(self, index: int) -> int:
        line = self.lines[index]
        fence = _FENCE.match(line)
        if fence and fence.group(1)[0] * 3 not in fence.group(2):
            return self._skip_fence(index, fence.group(1))
        if line.strip().startswith("<!--"):
            return self._skip_comment(index)
        if _RAW_HTML_START.match(line):
            return self._skip_raw_html(index)
        if not line.strip():
            self._close_paragraph()
            self.after_blank = True
            self.in_quote = False
            return index + 1
        if self._is_indented_code(line):
            self._interrupt()
            return index + 1
        if line.lstrip().startswith("|"):
            return self._read_table(index)
        self._read_line(index + 1, line)
        return index + 1

    def _is_indented_code(self, line: str) -> bool:
        return not self.items and self.paragraph is None and self.after_blank \
            and _indent(line[: len(line) - len(line.lstrip())]) >= CODE_INDENT

    def _read_line(self, number: int, line: str) -> None:
        is_quote = bool(_BLOCKQUOTE.match(line))
        if is_quote != self.in_quote:
            self._interrupt()  # the start or the end of a blockquote
            self.in_quote = is_quote
        if is_quote:
            inner = _blank_quote_marker(line)
            if not inner.strip():
                self._close_paragraph()
                self.after_blank = True
                return
            self.in_quote = False
            self._read_line(number, inner)
            self.in_quote = True
            self.lead = None  # a quote does not introduce a list after it
            return
        heading = _HEADING.match(line)
        setext = _SETEXT.match(line)
        item = _LIST_ITEM.match(line)
        if heading:
            self._read_heading(number, heading.start(2), heading.group(2), len(heading.group(1)))
        elif setext and self.paragraph is not None and not self.items:
            self._make_setext_title(setext.group(1))
        elif _RULE.match(line):
            self._close_all()
        elif item and item.group(4):
            self._read_item(number, line, item)
        elif _HTML_BLOCK.match(line):
            self._interrupt()
        else:
            self._read_text(number, line)
        self.after_blank = False

    def _end_sections(self, level: int) -> None:
        while self.sections and self.sections[-1][0] >= level:
            self.sections.pop()

    def _read_heading(self, number: int, column: int, title: str, level: int) -> None:
        self._close_all()
        self._end_sections(level)
        block = self._new_block(TITLE)
        block.add(number, self.lines[number - 1][: column + len(title)], column)
        self.sections.append((level, title.strip()))

    def _make_setext_title(self, underline: str) -> None:
        """Text followed by "===" or "---" is a title of level 1 or 2."""
        block = self.paragraph
        level = 1 if underline.startswith("=") else 2
        self._close_all()
        self._end_sections(level)
        block.kind = TITLE
        block.sections = tuple(title for _, title in self.sections)
        self.sections.append((level, block.text.strip()))

    def _read_item(self, number: int, line: str, match: re.Match) -> None:
        marker_indent = _indent(match.group(1))
        content_indent = _indent(line[: match.start(4)])
        while self.items and self.items[-1].marker_indent > marker_indent:
            self.items.pop()
        ordered = match.group(2)[0].isdigit()
        sibling = self.items and self.items[-1].marker_indent == marker_indent \
            and self.items[-1].block.list.ordered == ordered
        if sibling:
            info = self.items.pop().block.list
        elif self.items and marker_indent > self.items[-1].marker_indent:
            info = ListInfo(ordered, self.items[-1].block.list.depth + 1, None)
        else:
            self.items = []
            info = ListInfo(ordered, 0, self.lead)
        self._interrupt()
        block = self._new_block(ITEM, list=info)
        info.items.append(block)
        start = match.start(4)
        box = _TASK_BOX.match(line[start:])
        block.add(number, line, start + (box.end() if box else 0))
        self.items.append(_OpenItem(block, marker_indent, content_indent))

    def _read_text(self, number: int, line: str) -> None:
        column = len(line) - len(line.lstrip())
        if self.items:
            current = self.items[-1]
            continues = _indent(line[:column]) >= current.content_indent or not self.after_blank
            if continues and self.paragraph is None and not self.after_blank:
                current.block.add(number, line, column)
                return
            if not continues:
                self.items = []
            # else: a new paragraph in the item, after a blank line or a code block
        if self.paragraph is None:
            self.paragraph = self._new_block(PARAGRAPH)
            self.lead = self.paragraph if not self.items else None
        self.paragraph.add(number, line, column)

    def _read_table(self, index: int) -> int:
        self._close_all()
        rows = []
        while index < len(self.lines) and self.lines[index].lstrip().startswith("|"):
            rows.append(index)
            index += 1
        header = rows[0] if len(rows) > 1 and _TABLE_SEPARATOR.match(self.lines[rows[1]]) else None
        for row in rows:
            line = self.lines[row]
            if _TABLE_SEPARATOR.match(line):
                continue
            kind = HEADER_CELL if row == header else CELL
            for column, (start, end) in enumerate(_table_cells(line)):
                if line[start:end].strip():
                    block = self._new_block(kind, column=column)
                    lead = len(line[start:end]) - len(line[start:end].lstrip())
                    block.add(row + 1, line[:end], start + lead)
        self.after_blank = False
        return index

    def _skip_fence(self, index: int, opening: str) -> int:
        """Skip a fenced code block. Only a line of the same marks closes it."""
        self._interrupt()
        closing = re.compile(rf"^\s*{re.escape(opening[0])}{{{len(opening)},}}\s*$")
        index += 1
        while index < len(self.lines) and not closing.match(self.lines[index]):
            index += 1
        return index + 1

    def _skip_comment(self, index: int) -> int:
        self._interrupt()
        first = self.lines[index]
        if "-->" in first[first.index("<!--") + 4:]:
            return index + 1
        index += 1
        while index < len(self.lines) and "-->" not in self.lines[index]:
            index += 1
        return index + 1

    def _skip_raw_html(self, index: int) -> int:
        self._interrupt()
        tag = _RAW_HTML_START.match(self.lines[index]).group(1).lower()
        while index < len(self.lines) and f"</{tag}" not in self.lines[index].lower():
            index += 1
        return index + 1

    def _read_front_matter(self) -> int:
        if not self.lines or self.lines[0].strip() != FRONT_MATTER_FENCE:
            return 0
        end = next((i for i in range(1, len(self.lines))
                    if self.lines[i].strip() == FRONT_MATTER_FENCE), None)
        if end is None:
            return 0
        index = 1
        while index < end:
            match = _FRONT_MATTER_KEY.match(self.lines[index])
            index += 1
            if not match or match.group(1) not in self.front_matter_keys:
                continue
            block = self._new_block(PARAGRAPH, front_matter=True)
            value = match.group(2).strip()
            if value not in BLOCK_SCALAR_MARKS:
                quote = value[0] if value[:1] in "\"'" and value.endswith(value[0]) else ""
                block.add(index, self.lines[index - 1], match.start(2) + len(quote))
                if quote:
                    block.text = block.text[: -1]
                    block.positions = block.positions[: -1]
                continue
            while index < end and self.lines[index][:1] in (" ", "\t"):
                line = self.lines[index]
                block.add(index + 1, line, len(line) - len(line.lstrip()))
                index += 1
        return end + 1


def read_blocks(text: str, front_matter_keys: tuple[str, ...] = ()) -> list[Block]:
    return _Reader(text, front_matter_keys).read()
