"""Regression tests for the findings of the independent review (own sentences only)."""
import tempfile
import unittest
from pathlib import Path

from support import check, needs_standard, rules
from stelib.checks import ERROR, QUESTION
from stelib.config import PROCEDURAL, STRUCTURE
from stelib.markdown import TITLE, read_blocks
from stelib.standard import StandardNotFound, find_standard
from stelib.terms import TermMatcher
from stelib.text import split_sentences
from test_cli_and_changes import git, run

SIX = " ".join(["The pump stops."] * 6)
WORDS_23 = " ".join(["the cable"] * 11) + " now"


def errors(text, **options):
    return rules(check(text, with_dictionary=False, **options), ERROR)


class MarkdownShapesTest(unittest.TestCase):
    def test_run_in_title_is_not_a_sentence_of_the_paragraph(self):
        self.assertEqual(errors(f"**Pump data.** {SIX}"), [])

    def test_blocks_between_the_paragraph_and_the_list(self):
        for between in ("---", "```\ncode;\n```", "<div>", "> A quote."):
            with self.subTest(between=between):
                text = f"The pump stops.\n\n{between}\n\n- The pump.\n- The valve.\n"
                self.assertEqual(errors(text), [])

    def test_setext_title(self):
        blocks = read_blocks("Parts\n=====\n\n- The pump.\n- The valve.\n")
        self.assertEqual(blocks[0].kind, TITLE)
        self.assertEqual(errors("Parts\n-----\n\n- The pump.\n- The valve.\n"), [])
        text = "Schema\n======\n\nThe items:\n\n- First item.\n  - **a:** b.\n- Last item.\n"
        self.assertEqual(errors(text, sections={"schema": STRUCTURE}), [])

    def test_markup_at_the_end_of_the_lead_and_the_last_item(self):
        self.assertEqual(errors('**The parts:**\n\n- The pump.\n- **The valve opens.**\n'), [])
        self.assertEqual(errors('The steps:\n\n- Open it.\n- Click "Stop."\n'), [])

    def test_html_entities_and_indented_code(self):
        self.assertEqual(errors("| `a` &#124; `b` | The pump&nbsp;stops. |\n|---|---|\n"), [])
        self.assertEqual(errors("The code follows.\n\n    x = 1; y = 2;\n\nThe end.\n"), [])

    def test_blockquote_lines_are_read_again(self):
        text = "> Note:\n>\n> - The pump stops.\n> - The valve opens.\n"
        self.assertNotIn("6.3", errors(text))

    def test_byte_order_mark_and_inline_fence(self):
        self.assertEqual(read_blocks("﻿# Title\n")[0].kind, TITLE)
        blocks = read_blocks("```ste.py``` reads the file.\n\nThe pump stops; now.\n")
        self.assertIn("The pump stops; now.", [b.text for b in blocks])

    def test_underscore_emphasis_closes(self):
        text = "Use _this_ mode. " + " ".join(["the cable"] * 13) + "."
        self.assertIn("6.3", errors(text))


class SentenceTest(unittest.TestCase):
    def test_period_in_quotes_and_abbreviation_with_number(self):
        self.assertEqual(len(split_sentences('Click "Save." Then close the window.')), 2)
        self.assertEqual(len(split_sentences("See Fig. 3 for the parts.")), 1)


class RuleFidelityTest(unittest.TestCase):
    def test_procedure_note_and_safety_limits(self):
        found = check(f"Connect {WORDS_23}.", kind=PROCEDURAL, with_dictionary=False)
        self.assertIn("maximum 20", found[0].message)
        self.assertEqual(errors(f"Note: {WORDS_23}.", kind=PROCEDURAL), [])
        self.assertEqual(errors(f"Note: {WORDS_23} {WORDS_23}.", kind=PROCEDURAL), ["5.5"])
        self.assertEqual(errors(f"WARNING: Connect {WORDS_23}."), ["5.1"])

    @needs_standard
    def test_will_be_and_number_words(self):
        self.assertIn("3.4", rules(check("The unit will be installed.")))
        self.assertNotIn("1.5", rules(check("Install two pumps.")))

    @needs_standard
    def test_groups_and_emphasis_are_not_sure(self):
        self.assertEqual(rules(check("The valves close to 50 percent."), ERROR), [])
        self.assertEqual(rules(check("Push **via** on the panel."), ERROR), [])

    def test_noun_terms_do_not_hide_verb_forms(self):
        terms = TermMatcher(nouns=["edit"], verbs=["revoke"])
        self.assertEqual(terms.match_length(["edits"], 0), 1)
        self.assertEqual(terms.match_length(["editing"], 0), 0)
        self.assertEqual(terms.match_length(["revoking"], 0), 0)


class RobustnessTest(unittest.TestCase):
    def test_wrong_config_types_give_code_2(self):
        for text in ("documents = []\n", "[documents]\nrules = [1]\n", "terms = 5\n",
                     "[terms]\nverb_forms = { build = [\"built\"] }\n"):
            with self.subTest(text=text), tempfile.TemporaryDirectory() as folder:
                Path(folder, ".ste.toml").write_text(text)
                Path(folder, "a.md").write_text("Stop.\n")
                self.assertEqual(run("check", "a.md", cwd=folder).returncode, 2)

    def test_lookup_with_a_missing_config_file_does_not_stop(self):
        result = run("lookup", "valve", "--config", "/nonexistent.toml")
        self.assertNotIn("Traceback", result.stderr)

    def test_incomplete_standard_folder(self):
        with tempfile.TemporaryDirectory() as folder:
            Path(folder, "page_149.md").write_text("")
            with self.assertRaises(StandardNotFound):
                find_standard(folder)


@needs_standard
class SinceScopeTest(unittest.TestCase):
    def test_old_lead_without_colon_is_not_reported(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder, "a.md")
            path.write_text("The parts\n\n- The pump.\n")
            git(folder, "init", "-q")
            git(folder, "add", ".")
            git(folder, "commit", "-q", "-m", "start")
            path.write_text("The parts\n\n- The pump.\n- The valve.\n")
            result = run("check", "a.md", "--since", "HEAD", "--no-config", cwd=folder)
            self.assertNotIn("colon", result.stdout)


if __name__ == "__main__":
    unittest.main()


class ItemParagraphTest(unittest.TestCase):
    def test_text_after_a_code_block_in_an_item_is_a_new_sentence(self):
        text = ("1. Enter this command:\n\n   ```sh\n   ls\n   ```\n\n"
                "   For the folder, use the name that you recorded in the first step of the task.\n")
        self.assertEqual(errors(text, kind=PROCEDURAL), [])
