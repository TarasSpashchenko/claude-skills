"""Read the optional project file `.ste.toml`.

The file gives the technical nouns and technical verbs of the project, the
glossaries to read terms from, and the kind of each document or section.
"""
from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from .markdown import CELL, ITEM, TITLE, read_blocks

CONFIG_NAME = ".ste.toml"
DESCRIPTIVE = "descriptive"
PROCEDURAL = "procedural"
SPECIFICATION = "specification"
STRUCTURE = "structure"
FILE_KINDS = (DESCRIPTIVE, PROCEDURAL, SPECIFICATION)
SECTION_KINDS = FILE_KINDS + (STRUCTURE,)
SHAPES = ("item-lead", "table-first-column")
VERB_CATEGORIES = (1, 2, 3, 4)

_ALLOWED_KEYS = {
    "file": {"terms", "glossaries", "documents"},
    "terms": {"nouns", "verbs", "verb_forms", "verb_categories"},
    "documents": {"default_kind", "front_matter_keys", "rules"},
    "documents.rules": {"glob", "kind", "sections"},
    "sections": {"title", "kind"},
    "glossaries": {"path", "section", "shape"},
}
_ITEM_LEAD = re.compile(r"^\*\*(.+?)\*\*")
_TERM_ALTERNATIVES = re.compile(r"\s+/\s+")


class ConfigError(Exception):
    """The project file is not correct."""


@dataclass
class DocumentRule:
    glob: str
    kind: str
    sections: dict[str, str]
    pattern: re.Pattern


@dataclass
class Glossary:
    path: str
    section: str
    shape: str


@dataclass
class Config:
    path: Path | None = None
    nouns: list[str] = field(default_factory=list)
    verbs: list[str] = field(default_factory=list)
    verb_forms: dict[str, list[str]] = field(default_factory=dict)
    verb_categories: list[int] = field(default_factory=list)
    glossaries: list[Glossary] = field(default_factory=list)
    default_kind: str = DESCRIPTIVE
    front_matter_keys: tuple[str, ...] = ()
    rules: list[DocumentRule] = field(default_factory=list)

    @property
    def root(self) -> Path | None:
        return self.path.parent if self.path else None

    def document_kind(self, file: Path) -> tuple[str, dict[str, str]]:
        """The kind of the file, and the kinds of its sections by title (lowercase)."""
        kind, sections = self.default_kind, {}
        relative = self._relative(file)
        if relative is None:
            return kind, sections
        for rule in self.rules:
            if rule.pattern.fullmatch(relative):
                kind = rule.kind
                sections.update(rule.sections)
        return kind, sections

    def _relative(self, file: Path) -> str | None:
        if self.root is None:
            return None
        try:
            return file.resolve().relative_to(self.root.resolve()).as_posix()
        except ValueError:
            return None

    def glossary_terms(self) -> set[str]:
        terms: set[str] = set()
        for glossary in self.glossaries:
            terms |= read_glossary(self.root or Path.cwd(), glossary)
        return terms


def glob_to_regex(glob: str) -> re.Pattern:
    """A glob with "**" for any folders, "*" and "?" in one path part."""
    parts, index = [], 0
    while index < len(glob):
        if glob.startswith("**/", index):
            parts.append("(?:.*/)?")
            index += 3
        elif glob.startswith("**", index):
            parts.append(".*")
            index += 2
        elif glob[index] == "*":
            parts.append("[^/]*")
            index += 1
        elif glob[index] == "?":
            parts.append("[^/]")
            index += 1
        else:
            parts.append(re.escape(glob[index]))
            index += 1
    return re.compile("".join(parts))


def _table(value, name: str) -> dict:
    if not isinstance(value, dict):
        raise ConfigError(f"{name} must be a table")
    return value


def _tables(value, name: str) -> list[dict]:
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise ConfigError(f"{name} must be an array of tables ([[{name}]])")
    return value


def _check_keys(table: dict, where: str) -> None:
    unknown = set(table) - _ALLOWED_KEYS[where]
    if unknown:
        raise ConfigError(f"unknown key(s) in [{where}]: {', '.join(sorted(unknown))}")


def _string_list(value, name: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ConfigError(f"{name} must be a list of strings")
    return value


def _kind(value, allowed: tuple[str, ...], name: str) -> str:
    if value not in allowed:
        raise ConfigError(f"{name} must be one of: {', '.join(allowed)}")
    return value


def _read_rule(table: dict) -> DocumentRule:
    _check_keys(table, "documents.rules")
    if not isinstance(table.get("glob"), str):
        raise ConfigError("each [[documents.rules]] needs a glob")
    sections = {}
    for section in _tables(table.get("sections", []), "sections"):
        _check_keys(section, "sections")
        title = section.get("title")
        if not isinstance(title, str):
            raise ConfigError("each section needs a title")
        sections[title.strip().lower()] = _kind(section.get("kind"), SECTION_KINDS, "section kind")
    kind = _kind(table.get("kind", DESCRIPTIVE), FILE_KINDS, "rule kind")
    return DocumentRule(table["glob"], kind, sections, glob_to_regex(table["glob"]))


def _read_glossary(table: dict) -> Glossary:
    _check_keys(table, "glossaries")
    if not isinstance(table.get("path"), str) or not isinstance(table.get("section"), str):
        raise ConfigError("each [[glossaries]] needs a path and a section")
    return Glossary(table["path"], table["section"], _kind(table.get("shape"), SHAPES, "glossary shape"))


def parse_config(data: dict, path: Path | None = None) -> Config:
    _check_keys(data, "file")
    terms = _table(data.get("terms", {}), "terms")
    _check_keys(terms, "terms")
    documents = _table(data.get("documents", {}), "documents")
    _check_keys(documents, "documents")
    verbs = _string_list(terms.get("verbs", []), "terms.verbs")
    verb_forms = _table(terms.get("verb_forms", {}), "terms.verb_forms")
    unknown_verbs = set(verb_forms) - set(verbs)
    if unknown_verbs:
        raise ConfigError(f"terms.verb_forms gives forms of verbs that are not in terms.verbs: "
                          f"{', '.join(sorted(unknown_verbs))}")
    categories = terms.get("verb_categories", [])
    if not isinstance(categories, list) or any(item not in VERB_CATEGORIES for item in categories):
        raise ConfigError("terms.verb_categories must be a list of numbers from 1 to 4")
    return Config(
        path=path,
        nouns=_string_list(terms.get("nouns", []), "terms.nouns"),
        verbs=verbs,
        verb_forms={verb: _string_list(forms, f"terms.verb_forms.{verb}")
                    for verb, forms in verb_forms.items()},
        verb_categories=categories,
        glossaries=[_read_glossary(table) for table in _tables(data.get("glossaries", []), "glossaries")],
        default_kind=_kind(documents.get("default_kind", DESCRIPTIVE), FILE_KINDS, "default_kind"),
        front_matter_keys=tuple(_string_list(documents.get("front_matter_keys", []),
                                             "documents.front_matter_keys")),
        rules=[_read_rule(table) for table in _tables(documents.get("rules", []), "documents.rules")],
    )


def find_config(start: Path) -> Path | None:
    """The nearest `.ste.toml` in the folder of start or in a parent folder."""
    folder = start.resolve()
    folder = folder if folder.is_dir() else folder.parent
    for candidate in (folder, *folder.parents):
        if (candidate / CONFIG_NAME).is_file():
            return candidate / CONFIG_NAME
    return None


def load_config(path: Path | None) -> Config:
    if path is None:
        return Config()
    try:
        with open(path, "rb") as file:
            return parse_config(tomllib.load(file), path)
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise ConfigError(f"{path}: {error}") from error
    except ConfigError as error:
        raise ConfigError(f"{path}: {error}") from error


def _clean_term(text: str) -> str:
    return text.replace("**", "").replace("`", "").strip().rstrip(":").strip().lower()


def _split_alternatives(term: str) -> set[str]:
    """ "restricted / open mode" gives two terms."""
    return {part.strip() for part in _TERM_ALTERNATIVES.split(term) if part.strip()}


def read_glossary(root: Path, glossary: Glossary) -> set[str]:
    """Terms of a glossary section: the text in "**" at the start of each list item,
    or the first column of each table."""
    path = root / glossary.path
    try:
        blocks = read_blocks(path.read_text(encoding="utf-8-sig"))
    except OSError as error:
        raise ConfigError(f"glossary file not found: {path}") from error
    wanted = glossary.section.strip().lower()
    if not any(block.kind == TITLE and block.text.strip().lower() == wanted for block in blocks):
        raise ConfigError(f'{path}: section "{glossary.section}" not found')
    in_section = [block for block in blocks
                  if any(title.strip().lower() == wanted for title in block.sections)]
    terms: set[str] = set()
    for block in in_section:
        if glossary.shape == "item-lead" and block.kind == ITEM:
            match = _ITEM_LEAD.match(block.text)
            if match:
                terms |= _split_alternatives(_clean_term(match.group(1)))
        elif glossary.shape == "table-first-column" and block.kind == CELL and block.column == 0:
            terms |= _split_alternatives(_clean_term(block.text))
    return {term for term in terms if term}
