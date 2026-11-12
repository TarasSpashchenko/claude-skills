import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from support import needs_standard

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "ste.py"


def run(*arguments, cwd=None, stdin=None):
    return subprocess.run([sys.executable, str(SCRIPT), *arguments], cwd=cwd, input=stdin,
                          capture_output=True, text=True)


def git(folder, *arguments):
    subprocess.run(["git", *arguments], cwd=folder, check=True, capture_output=True,
                   env={**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"})


class ExitCodeTest(unittest.TestCase):
    def test_missing_standard_gives_code_2(self):
        result = run("check", "-", "--standard-dir", "/nonexistent", "--no-config", stdin="Stop.\n")
        self.assertEqual(result.returncode, 2)
        self.assertIn("NOT COMPLETE", result.stdout)

    @needs_standard
    def test_codes_0_and_1_and_json(self):
        self.assertEqual(run("check", "-", "--no-config", stdin="Open the valve.\n").returncode, 0)
        result = run("check", "-", "--no-config", "--json", stdin="Stop; go.\n")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["files"][0]["findings"][0]["rule"], "8.1")

    def test_wrong_config_gives_code_2(self):
        with tempfile.TemporaryDirectory() as folder:
            Path(folder, ".ste.toml").write_text("[unknown]\n")
            Path(folder, "a.md").write_text("Open the valve.\n")
            self.assertEqual(run("check", "a.md", cwd=folder).returncode, 2)


@needs_standard
class ChangedSentencesTest(unittest.TestCase):
    OLD = "# Guide\n\nThe pump stops. The valve opens.\n\nThe cable is dry.\n"

    def changed(self, new_text):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder, "guide.md")
            path.write_text(self.OLD)
            git(folder, "init", "-q")
            git(folder, "add", ".")
            git(folder, "commit", "-q", "-m", "start")
            path.write_text(new_text)
            result = run("check", "guide.md", "--since", "HEAD", "--no-config", cwd=folder)
            return result.stdout.splitlines()[0]

    def test_unchanged_text_and_line_breaks(self):
        self.assertIn("(0 of 4)", self.changed("# Guide\n\nThe pump stops.\nThe valve opens.\n\nThe cable is dry.\n"))

    def test_changed_and_added_sentences(self):
        self.assertIn("(1 of 4)", self.changed(self.OLD.replace("valve opens", "valve closes")))
        self.assertIn("(1 of 5)", self.changed(self.OLD + "\nThe cable is dry.\n"))

    def test_sentence_that_goes_into_a_procedure_step(self):
        new = "# Guide\n\nThe pump stops. The valve opens.\n\n1. The cable is dry.\n"
        self.assertIn("(1 of 4)", self.changed(new))

    def test_unknown_revision_gives_code_2(self):
        with tempfile.TemporaryDirectory() as folder:
            Path(folder, "a.md").write_text("Stop.\n")
            git(folder, "init", "-q")
            result = run("check", "a.md", "--since", "nothing", "--no-config", cwd=folder)
            self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
