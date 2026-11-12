"""A document as units: one Markdown block, its text kind, and its sentences."""
from __future__ import annotations

import re
from dataclasses import dataclass

from .markdown import ITEM, Block
from .text import Sentence, split_sentences

_NOTE = re.compile(r"^[*_]{0,2}notes?[*_]{0,2}\s*:", re.IGNORECASE)
_SAFETY = re.compile(r"^[*_]{0,2}(warning|caution|danger)[*_]{0,2}\s*:", re.IGNORECASE)


@dataclass
class Unit:
    block: Block
    kind: str
    sentences: list[Sentence]

    @property
    def is_note(self) -> bool:
        return bool(_NOTE.match(self.block.text))

    @property
    def is_safety_instruction(self) -> bool:
        """A warning or a caution: 20 words at most in all text kinds (rule 5.1)."""
        return bool(_SAFETY.match(self.block.text))

    @property
    def is_numbered_item(self) -> bool:
        return self.block.kind == ITEM and self.block.list.ordered

    @property
    def category(self) -> str:
        """The block context of a sentence, for the comparison of two versions."""
        return f"{self.block.kind}/{self.kind}/{'numbered' if self.is_numbered_item else ''}"


def section_kind(block: Block, file_kind: str, sections: dict[str, str]) -> str:
    """The kind of the innermost section that the configuration names, or the file kind."""
    kind = file_kind
    for title in block.sections:
        kind = sections.get(title.strip().lower(), kind)
    return kind


def build_units(blocks: list[Block], file_kind: str, sections: dict[str, str]) -> list[Unit]:
    return [Unit(block, section_kind(block, file_kind, sections), split_sentences(block.text))
            for block in blocks]
