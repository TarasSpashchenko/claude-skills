import unittest

from support import check, rules  # noqa: F401  (support sets the import path)
from stelib.markdown import CELL, HEADER_CELL, ITEM, PARAGRAPH, TITLE, read_blocks
from stelib.text import CODE, PAREN, QUOTE, URL, count_words, split_sentences


def count(text: str) -> int:
    sentence = split_sentences(text)[0]
    return count_words(sentence, lambda token, index: False)


class WordCountTest(unittest.TestCase):
    def test_special_items_count_as_one_word(self):
        self.assertEqual(count("Run `make test --all` now."), 3)
        self.assertEqual(count('Push "Save all changes" now.'), 3)
        self.assertEqual(count("Wait 10 ms here."), 3)
        self.assertEqual(count("Read https://example.com/a/b now."), 3)
        self.assertEqual(count("Use the read-only mode."), 4)
        self.assertEqual(count("Set the **very important** flag."), 4)

    def test_parentheses_count_as_one_word_and_make_a_sentence(self):
        sentences = split_sentences("Stop the service (it takes two minutes).")
        self.assertEqual(len(sentences), 2)
        self.assertTrue(sentences[1].nested)
        self.assertEqual(count("Stop the service (it takes two minutes)."), 4)

    def test_label_at_the_start_does_not_count(self):
        self.assertEqual(count("**Note:** The cache is empty."), 4)

    def test_tokens(self):
        kinds = {t.text: t.kind for t in split_sentences('Run `a b` on "x y" (z) at https://a.io now.')[0].tokens}
        self.assertEqual(kinds["`a b`"], CODE)
        self.assertEqual(kinds['"x y"'], QUOTE)
        self.assertEqual(kinds["(z)"], PAREN)
        self.assertEqual(kinds["https://a.io"], URL)


class SentenceTest(unittest.TestCase):
    def test_split(self):
        text = "Open the file.md file. Then read it, e.g. the first line. Close it!"
        self.assertEqual(len(split_sentences(text)), 3)

    def test_lowercase_after_period_does_not_split(self):
        self.assertEqual(len(split_sentences("Use version 2. or later.")), 1)


class MarkdownTest(unittest.TestCase):
    TEXT = (
        "---\ntitle: Guide\ndescription: The guide tells how to start.\n---\n"
        "# Start\n\nThe steps are:\n\n1. Open the panel.\n   Then wait.\n2. Push the button.\n"
        "   - nested item\n\n```bash\nrm -rf /tmp/x\n```\n<!-- hidden; text -->\n"
        "| Name | Text |\n|---|---|\n| Cache | It keeps data. |\n"
    )

    def test_blocks(self):
        blocks = read_blocks(self.TEXT, ("description",))
        kinds = [b.kind for b in blocks]
        self.assertEqual(kinds, [PARAGRAPH, TITLE, PARAGRAPH, ITEM, ITEM, ITEM,
                                 HEADER_CELL, HEADER_CELL, CELL, CELL])
        self.assertTrue(blocks[0].front_matter)
        self.assertEqual(blocks[0].text, "The guide tells how to start.")
        self.assertEqual(blocks[3].text, "Open the panel. Then wait.")
        self.assertIs(blocks[3].list.lead, blocks[2])
        self.assertEqual(blocks[5].list.depth, 1)
        self.assertFalse(any("rm -rf" in b.text or "hidden" in b.text for b in blocks))

    def test_positions(self):
        blocks = read_blocks("# T\n\nOne two.\n  Three four.\n")
        paragraph = blocks[1]
        self.assertEqual(paragraph.position(0), (3, 1))
        self.assertEqual(paragraph.position(paragraph.text.index("Three")), (4, 3))


if __name__ == "__main__":
    unittest.main()
