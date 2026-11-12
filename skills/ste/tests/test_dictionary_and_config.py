import re
import tempfile
import unittest
from pathlib import Path

from support import dictionary, needs_standard
from stelib.config import ConfigError, Glossary, glob_to_regex, parse_config, read_glossary

ERRORS_FILE = Path(__file__).resolve().parents[1] / "references" / "frequent-errors.md"
ALTERNATIVE = re.compile(r"([A-Z][A-Z' -]*[A-Z])\s*\((?:n|v|adj|adv|prep|conj|pron|TN)\)")


@needs_standard
class DictionaryTest(unittest.TestCase):
    def labels(self, word):
        return [(r.entry.label, r.approved, r.how) for r in dictionary().readings(word)]

    def test_help_text_is_not_a_word(self):
        self.assertTrue(all("BE" not in label for label, _, _ in self.labels("other")))

    def test_hyphen_at_a_line_break(self):
        self.assertEqual(self.labels("counterclockwise")[0][1], True)

    def test_plurals_and_verb_forms(self):
        self.assertEqual(self.labels("units"), [("UNIT (n)", True, "plural")])
        self.assertEqual(self.labels("allows"), [("allow (v)", False, "verb form")])
        self.assertEqual(self.labels("activated"), [("ACTIVATE (v)", False, "unlisted form")])

    def test_rows_without_part_of_speech_and_spellings(self):
        self.assertTrue(dictionary().lookup("for example")[0].approved)
        self.assertFalse(dictionary().lookup("such as")[0].approved)
        self.assertEqual(self.labels("matte")[0][0], "MATT (adj)")

    def test_counts_and_technical_verbs(self):
        entries = dictionary().entries
        self.assertEqual(sum(e.approved for e in entries), 879)
        self.assertEqual(sum(not e.approved for e in entries), 1319)
        self.assertIn("click", dictionary().technical_verbs[2])
        self.assertIn("comply with", dictionary().technical_verbs[4])

    def test_frequent_errors_agree_with_the_dictionary(self):
        rows = [line.split("|")[1:-1] for line in ERRORS_FILE.read_text().splitlines()
                if re.match(r"^\| [a-z]", line)]
        self.assertGreater(len(rows), 20)
        for word, pos, _example, use_instead, page in (map(str.strip, row) for row in rows):
            with self.subTest(word=word):
                entries = [r.entry for r in dictionary().lookup(word)
                           if r.entry.pos == pos and not r.entry.approved]
                self.assertTrue(entries, f"{word} ({pos}) is not a lowercase entry")
                self.assertEqual(entries[0].page, int(page))
                column_2 = " ".join(" ".join(e.meaning) for e in entries).upper()
                for alternative in ALTERNATIVE.findall(use_instead):
                    self.assertIn(alternative, column_2)


class ConfigTest(unittest.TestCase):
    def test_glob(self):
        pattern = glob_to_regex("docs/**/*.md")
        self.assertTrue(pattern.fullmatch("docs/a.md"))
        self.assertTrue(pattern.fullmatch("docs/x/y/.memlog.md"))
        self.assertFalse(pattern.fullmatch("src/a.md"))

    def test_kinds_and_sections(self):
        with tempfile.TemporaryDirectory() as folder:
            config = parse_config({"documents": {"rules": [
                {"glob": "spec/*.md", "kind": "specification",
                 "sections": [{"title": "Steps", "kind": "procedural"}]}]}},
                Path(folder) / ".ste.toml")
            kind, sections = config.document_kind(Path(folder) / "spec" / "a.md")
            self.assertEqual((kind, sections), ("specification", {"steps": "procedural"}))
            self.assertEqual(config.document_kind(Path(folder) / "b.md")[0], "descriptive")

    def test_wrong_values(self):
        for data in ({"term": {}}, {"documents": {"default_kind": "poem"}},
                     {"terms": {"verb_categories": [7]}}):
            with self.subTest(data=data), self.assertRaises(ConfigError):
                parse_config(data)

    def test_glossary_shapes(self):
        text = ("# Glossary\n\n- **Access token** - a key.\n- **Role:** a set.\n\n"
                "# Types\n\n| Type | Use |\n|---|---|\n| Assistant | Chat |\n\n# End\n")
        with tempfile.TemporaryDirectory() as folder:
            Path(folder, "g.md").write_text(text)
            root = Path(folder)
            self.assertEqual(read_glossary(root, Glossary("g.md", "Glossary", "item-lead")),
                             {"access token", "role"})
            self.assertEqual(read_glossary(root, Glossary("g.md", "Types", "table-first-column")),
                             {"assistant"})
            with self.assertRaises(ConfigError):
                read_glossary(root, Glossary("g.md", "Missing", "item-lead"))


if __name__ == "__main__":
    unittest.main()
