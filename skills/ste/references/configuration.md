# Project configuration: `.ste.toml`

`STE check` and `STE lookup` read the nearest `.ste.toml` in the folder of the file or in a parent folder. The file is optional. Without it, each document is descriptive text and each project term is a question (rule 1.5). Use `--config PATH` for a different file and `--no-config` to read none. A wrong key or value stops the check with exit code 2, so that a typing error does not hide a problem.

## Keys

```toml
[terms]
# Technical nouns (rule 1.5). The tool also accepts their plurals.
nouns = ["access token", "dashboard", "pull request"]
# Technical verbs (rule 1.12). The tool also accepts their regular forms.
verbs = ["deploy", "grant", "rebuild", "revoke"]
# Irregular forms of the technical verbs above. Each key must also be in verbs.
verb_forms = { rebuild = ["rebuilt"] }
# Accept the example verbs of these categories of rule 1.12 (pages 57 and 58 of the standard):
# 1 manufacturing processes, 2 computer processes and applications, 3 subject fields,
# 4 law and regulations. Category 2 is useful for software documentation.
# A listed verb that the dictionary does not approve ("copy") still gets a question with a
# hint: it is correct only for that process and only as a verb (rules 1.12, 1.13).
verb_categories = [2]

# Read terms from a glossary section of a project document. Repeat the table for each glossary.
[[glossaries]]
path = "docs/prd.md"            # relative to the folder of .ste.toml
section = "3. Glossary"          # the title text of the section, without the "#" marks
shape = "item-lead"              # "- **Term** - definition" items
# shape = "table-first-column"   # the first column of each table row in the section

[documents]
default_kind = "descriptive"     # descriptive, procedural or specification
front_matter_keys = ["description"]   # front matter values to examine as text

# The kind of the files that a glob selects. The last rule that matches wins.
[[documents.rules]]
glob = "docs/runbooks/**/*.md"
kind = "procedural"

[[documents.rules]]
glob = "specs/*.md"
kind = "specification"           # descriptive rules, and the verbs of category 4 of rule 1.12
# The kind of a section by its title. "structure" is for schema lists: no list format
# checks there (rule 4.3), but the words and sentences are examined.
sections = [{ title = "Procedure", kind = "procedural" }, { title = "Capabilities", kind = "structure" }]
```

Globs use `/` between folders, `**` for any number of folders, and `*` and `?` in one name. They are relative to the folder of `.ste.toml`.

## When to add a term

Add a word to `terms` only when it is a technical noun or a technical verb of the project, and no approved word gives the same meaning (rules 1.5 and 1.12). Do not add an ordinary word to stop a question: "currently" or "simple" are not terms. If the project has a glossary, refer to it with `[[glossaries]]`, so that the terms have one source.

## Tell agents that the project uses STE

Put a short rule in the project instruction file (`AGENTS.md`, `CLAUDE.md`, or both), for example:

```markdown
## Documentation language

Write all documentation in ASD-STE100 Simplified Technical English, Issue 9: use the `ste` skill.
Write in STE the new text and each sentence that you change.
Before you complete the task, do the check
`python3 ~/.claude/skills/ste/scripts/ste.py check <file> --since HEAD`.
Correct each error, and examine each question.
```

## The standard

The tool reads the page files of the standard (`page_NNN.md`, one file for each page of the PDF) from `--standard-dir`, from `STE_STANDARD_DIR`, or from `~/.local/share/ste/ASD-STE100_ISSUE9/`. ASD owns the copyright: keep the files outside of git, and do not copy their text into project files. If a project needs the pages in its own folder, use a symlink and add its path to `.gitignore` without a trailing `/`, because git does not treat a symlink as a folder.
