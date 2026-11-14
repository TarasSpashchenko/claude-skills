# The review kit

Read this when you set up an assessment. The kit is a folder that holds everything the participants read: the sets, base, the generator and the consumers, and the measured facts. Build it before you write any prompt, because the prompt's facts and paths come from it.

## Contents

1. Where the kit lives, and why
2. Layout
3. Building it with `kit.py`
4. Blind labels
5. Facts to verify
6. The earlier-findings checklist file

## 1. Where the kit lives, and why

Put the review root **outside the repository**, next to it (for example `../<repo>-docs-review/`):

- Each set is checked against the exact source it was generated from. The user's working checkout is often ahead of the branches, so reading claims against it gives false defects.
- Copies inside the repository end up in the user's index, search and code-intelligence tools, and an agent may edit them by mistake.
- Agents can be started in the root, which gives them read access to everything they need and write access to the discussion folders only.

Ask before writing anywhere inside the user's repository. A `git fetch` to get the candidate branches is fine; say that you did it.

## 2. Layout

```
<root>/
├── set-A/  set-B/ …        full export of each candidate (standalone git repo, branch "review")
├── base/                   the docs as they were before the run (entry file, its imports, docs folder)
├── generator/              the generator at the revision whose checker you run (optional)
├── consumers/              the consuming package at the revision in use (optional)
├── prior-findings.md       the earlier review's findings as a checklist (optional)
├── facts/                  sizes.md, checker output per set, diffs base → set, any other measurement
├── assess-A/  assess-B/ …  one discussion folder per set (discussion-session group mode)
└── compare/                the comparison discussion, when there are two or more sets
```

With one candidate, use `set-A` all the same: the prompts, facts and scripts stay the same shape.

## 3. Building it with `kit.py`

`kit.py` is in this skill's `scripts/` folder. Run it with Python 3.

```bash
# Exports: random labels, the mapping outside the root
python3 <skill>/scripts/kit.py setup --repo <repo> --root <root> \
  --base <merge-base revision> --candidate <branch-1> --candidate <branch-2> \
  --docs AGENTS.md CLAUDE.md .ai-run \
  --mapping ~/.claude/discussion-notes/<slug>-mapping.txt \
  --tool generator=<generator repo>@<rev>:<package subdir> \
  --tool consumers=<consumer repo>@<rev>:<package subdir>

# Words that would reveal a set's origin; neutralise every revealing hit (§4), run it again
python3 <skill>/scripts/kit.py leaks --root <root> --mapping <mapping file> --term <model-1> --term <model-2>

# Only when leaks reports 0 revealing hits: make each set a git repo with one clean commit
python3 <skill>/scripts/kit.py seal --root <root> --mapping <mapping file> --term <model-1> --term <model-2>

# Sizes, section headings, caps; diffs base → set into facts/
python3 <skill>/scripts/kit.py facts --root <root> --docs-dir .ai-run --entry AGENTS.md --guides .ai-run/guides

# Per set: routing tables of the entry file, and paths in the docs that do not resolve
python3 <skill>/scripts/kit.py routes --set <root>/set-A
python3 <skill>/scripts/kit.py paths --set <root>/set-A --prefix src/
```

- **Base** is the revision the run started from: usually `git merge-base <target> <candidate>`. When several candidates exist, check they share it; if not, export one base per candidate and say so in the facts.
- **The generator.** If the profile has a checker, run it from each set's root and save the full output as `facts/check-<L>.txt`. Run the newest generator revision's checker, and record which revision produced the set if you can tell (the profile says how). Counts of diagnostic lines exclude the summary lines: count with `grep -c '^<prefix>:'`, not by eye.
- **The consumers.** Export the revision the delivery agents actually run. Ask the user when unclear; it is often the main branch, not the generator's branch.
- `seal` makes each set a standalone git repo, so reviewers can use `git grep`, and a stray edit shows in `git status`. It runs the leak check first and refuses while a revealing hit is left, because a commit made before you neutralise a word keeps that word in the history, where a text search does not see it. Never `git init` a set by hand.

## 4. Blind labels

Use blind labels whenever there are two or more candidates. A reviewer who knows which set came from which model, team or tool judges it differently, and the comparison then measures the reputation, not the set.

- `setup` shuffles the candidates and writes the mapping to a private file. The tool refuses a mapping path inside the root. Keep the mapping in your private notes folder, never in a file a participant can read.
- Run `leaks` with the model names, tool names, author names and the mapping, before anyone reads the root. A hit in a file that is identical in every set reveals nothing (the tool says so). A hit in a file that differs between sets is a leak:
  - in a file the reviewers do not assess, such as a generator manifest, a config file or a changelog: remove the field or replace the word with the same neutral value in every set's export (`set-A`, `set-B` would itself be a mapping: use one value for all), record it in the facts as "neutralised in every set", and tell the user;
  - in the guide text under review: tell the user before you go on, because neutralising it changes what is assessed.
- Then run `leaks` again, and `seal` only when it reports 0 revealing hits. `leaks` also searches the history of any set that is already a git repo; if it finds a hit there, delete that set's `.git` folder and seal again.
- Name nothing after the candidates: no folder, file, heading or commit message under the root mentions a branch, model or commit id. Check again after you write the prompts (`leaks` on the root).
- Each counterpart session sees one set only. Ask the user to start a fresh session per agent per set, and write in the prompt which folders of the root it must not open.
- You are not blind: you set up the export. Say so to the user, and keep your positions to evidence.
- Reveal the mapping only after the comparison outcome is confirmed (`comparison.md` §6).

## 5. Facts to verify

The prompt carries measurements as *facts to verify*, each with a command a participant can run with standard tools (`wc`, `grep -c`, `find`, `diff`, the generator's own checker). Participants cannot run `kit.py`: it lives with this skill, next to your private notes, so give the plain command that reproduces its number. The facts are: sizes from `facts/sizes.md`, checker status and counters, headings per section, the routing-table findings, where the consumers name the docs. They save every participant the same search, and the label keeps each check independent.

Keep them to measurements. A count you derived from a judgement (how many defects, which guide is better) is a position, and it would anchor the others before they form their own view. Positions go in your own round-1 submission.

## 6. The earlier-findings checklist file

When an earlier review of the same generator exists, write `<root>/prior-findings.md`:

- one line on where the findings come from, and a warning that their line numbers are from the earlier output;
- the three statuses and what each needs as evidence (`method.md` §4);
- one table per family of findings (false or broken content, new text contradicting old text, entry-file defects, …) with `ID | Where (earlier output) | Finding`, each finding stated so that it can be searched for in a new set.

Reuse the same file for every set.
