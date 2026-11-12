import unittest

from support import check, needs_standard, rules
from stelib.checks import ERROR, QUESTION
from stelib.config import PROCEDURAL, STRUCTURE
from stelib.terms import TermMatcher

LONG = " ".join(["the cable"] * 13)  # 26 words


class StyleRulesTest(unittest.TestCase):
    """Rules that do not use the dictionary."""

    def run_check(self, text, **options):
        return check(text, with_dictionary=False, **options)

    def test_semicolon(self):
        self.assertIn("8.1", rules(self.run_check("Stop the pump; then open the valve."), ERROR))

    def test_contraction_but_not_possessive(self):
        self.assertIn("4.2", rules(self.run_check("Don't open the valve."), ERROR))
        self.assertNotIn("4.2", rules(self.run_check("Open the user's folder.")))

    def test_latin_abbreviation_and_pronoun(self):
        found = rules(self.run_check("He opens a file, e.g. the log."), ERROR)
        self.assertIn("GR-6", found)
        self.assertIn("GR-3", found)

    def test_make_sure_that(self):
        self.assertIn("GR-1", rules(self.run_check("Make sure the cable is dry."), QUESTION))
        self.assertNotIn("GR-1", rules(self.run_check("Make sure that the cable is dry.")))

    def test_sentence_length(self):
        self.assertIn("6.3", rules(self.run_check(f"Connect {LONG}."), ERROR))
        step = "1. " + " ".join(["Connect the cable"] * 7) + "."  # 21 words
        self.assertIn("5.1", rules(self.run_check(step, kind=PROCEDURAL), ERROR))
        self.assertIn("5.1", rules(self.run_check(step), QUESTION))
        note = "Note: " + " ".join(["the cable"] * 11) + "."  # 22 words
        self.assertEqual(rules(self.run_check(note, kind=PROCEDURAL)), [])

    def test_paragraph_length(self):
        text = " ".join(["The pump stops."] * 7)
        self.assertIn("6.6", rules(self.run_check(text), ERROR))

    def test_list_rules(self):
        found = rules(self.run_check("The parts\n\n- the pump\n- The valve,\n- The cable\n"), ERROR)
        self.assertEqual(found.count("4.3"), 4)  # colon, lowercase, comma, last period

    def test_list_after_title_and_code_start(self):
        text = "# Parts\n\n- `pump` is the first part.\n- The valve is the second part.\n"
        self.assertEqual(rules(self.run_check(text), ERROR), [])

    def test_nested_list_and_structure_section(self):
        text = "# Schema\n\nThe items:\n\n- First item.\n  - **intent:** The aim.\n- Last item.\n"
        self.assertIn("4.3", rules(self.run_check(text), ERROR))
        self.assertEqual(rules(self.run_check(text, sections={"schema": STRUCTURE}), ERROR), [])


@needs_standard
class WordRulesTest(unittest.TestCase):
    def test_function_word_and_group_are_errors(self):
        found = rules(check("Send the data via the cable, according to the manual."), ERROR)
        self.assertEqual(found.count("1.1"), 2)

    def test_group_after_article_is_not_an_error(self):
        self.assertNotIn("1.1", rules(check("Install the unit at the rear of the panel.")))

    def test_verb_group_is_a_question(self):
        self.assertEqual(rules(check("Turn on the pump.")), ["1.1"])
        self.assertEqual(rules(check("Turn on the pump."), ERROR), [])

    def test_not_approved_words_are_questions(self):
        findings = check("The role allowed access to the backup.")
        self.assertEqual(rules(findings, ERROR), [])
        self.assertEqual([f.text for f in findings if f.rule == "1.1"], ["allowed", "backup"])

    def test_technical_noun_of_a_verb_row(self):
        self.assertNotIn("1.1", rules(check("Open the file.")))
        self.assertIn("1.1", rules(check("You must file the report.")))

    def test_unknown_word_and_project_terms(self):
        self.assertIn("1.5", rules(check("Open the dashboard.")))
        terms = TermMatcher(nouns=["dashboard", "access token"], verbs=["revoke"])
        self.assertEqual(rules(check("Revoke the access tokens of the dashboard.", terms=terms)), [])

    def test_wrong_part_of_speech(self):
        self.assertIn("1.2", rules(check("You can test the unit.")))
        self.assertNotIn("1.2", rules(check("Do the test of the unit.")))

    def test_ing_words(self):
        self.assertIn("3.5", rules(check("Stop the engine before connecting the cable.")))
        self.assertNotIn("3.5", rules(check("Open the valve during the test.")))
        self.assertNotIn("3.5", rules(check("# Opening and closing\n\nOpen the valve.\n")))

    def test_verb_constructions(self):
        self.assertIn("3.4", rules(check("The pump has stopped.")))
        self.assertIn("3.4", rules(check("The valve must be opened.")))
        self.assertIn("3.6", rules(check("The valve is opened by the system.")))
        self.assertNotIn("3.6", rules(check("The valve is damaged.")))

    def test_noun_group(self):
        self.assertIn("2.1", rules(check("Replace the engine fuel pump filter element.")))

    def test_unlisted_form_of_approved_verb(self):
        self.assertIn("3.1", rules(check("The system activated the alarm.")))


if __name__ == "__main__":
    unittest.main()
