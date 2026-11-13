# The assessment method

Read this before you write an assessment prompt. Everything here goes into the prompt's method section, word for word where it defines a count, because two assessments are comparable only when their participants counted the same things the same way. When there are several candidate sets, write the method once and use it unchanged for every set.

## Contents

1. Goal questions
2. Reading shares
3. Defect register
4. Earlier-findings checklist
5. Change against base: corrections, losses, false additions
6. Entry point and routing probe
7. Consumers and generated sections
8. Scorecard M1–M8
9. Verdict and fix-before-merge rule
10. What a static review cannot show: the paired delivery run

## 1. Goal questions

Every assessment answers two questions, and presumes neither answer:

1. **How useful is the set to an AI agent working in this repository?** True against the source, complete enough, consistent with itself, and easy to route through.
2. **What can be said about the solutions an agent delivers with it, and what cannot be said without a run?** A static review shows which guides an agent would load and what they would tell it. It does not show what the agent then builds. Say so in the outcome, and name the run that would show it (§10).

For a single change against base, question 1 becomes "does the change improve on base?", with the answer improves / mixed / worse, backed by its three strongest pieces of evidence.

## 2. Reading shares

- Everyone reads the entry file (`AGENTS.md`) whole.
- Every guide is read in full by exactly one assigned reader, who checks each of its claims against the source. Split by folder, so a share is easy to state and nobody has to guess the boundary. Balance the shares by size, not by file count.
- Give the guides that describe code (architecture, components, patterns, styling) to the source-accuracy lens, the guides that change what an agent does (development, API, workflow) to the delivery lens, and the operational guides (project, quality gates, standards, security, testing, onboarding) plus the entry file to Claude. Adjust to the repository.
- Samples outside one's share are welcome. From round 2 on, everyone re-checks the others' rows.
- **The shares are identical for every candidate set.** A guide read by a different reader in each set produces a difference in the counts that has nothing to do with the sets.

## 3. Defect register

One row per defect:

| ID | Where | Defect | Kind | Severity | Origin | Found by | Reproduced by | Status |
|---|---|---|---|---|---|---|---|---|

- **ID:** in round 1 the finder's tag and a number (`GPT-07`). Claude renumbers agreed rows per set at consolidation (`A-07`).
- **Where:** `guide:line` in the set, every line that holds the defect.
- **Defect:** the statement, quoted exactly (keep its bold and backticks, never join two sentences with "…"), then what the source says, with `path:line` or the command that shows it.
- **Kind:** `false` (the source contradicts it), `contradiction` (two statements in the set cannot both be true; give both anchors), `broken` (a path, symbol, link or command that does not resolve), `structure` (a table, section or route that is malformed or misleading). A row with parts of several kinds takes the kind of its main statement.
- **Severity:** `major` when it would lead an agent to a wrong action: a file, symbol, script or command that does not exist; wrongly described behaviour; a rule the code contradicts; a route to the wrong guide. `minor` when it is inaccurate but unlikely to change an action. When participants disagree, ask the one question that decides it: would an agent following this text do something different from what the code needs? Name the consumer step.
- **Origin**, one of three values, so that both rules in §8 can be computed from the same register:
  - `run`: the run wrote the false, broken or malformed text;
  - `run-c`: the run wrote a true line that now contradicts old text it kept (the defect exists because the run added the line);
  - `inh`: the text was in base and the run left it.

  Decide by searching base for the line (`grep -n '<phrase>' base/<guide>`), and record the search. A shared defect that sits in base is still a defect of the set: inherited does not mean harmless.
- **Row unit:** one row per passage that states one wrong thing. Repeats of the same wrong statement in other guides go in the same row's Where. Don't split one defect into several rows, and don't merge two different wrong statements because they sit near each other.
- **Reproduction:** a defect enters the outcome only when a second participant has reproduced it. Record who found it and who reproduced it. A participant who cannot reproduce a row writes `not reproduced: <why>` with the command they ran.
- **Same text, same decision:** identical text gets the same kind and severity wherever it appears, including in another set.
- **A defect that looks like the generator's doing** is still counted as a defect of the set. Mark it and move on; causes are a separate deliverable (`evidence-review.md`).

`kit.py tally --board <board.md>` counts the agreed register and refuses values outside these lists. Quote its counts instead of counting by hand.

## 4. Earlier-findings checklist

When an earlier review of the same generator exists, turn its findings into a numbered checklist (`P-01` …) in its own file, and have every participant give each item one status for the set:

- `absent`: the defect is not in this set; say how you searched.
- `present`: give `path:line` and the source evidence.
- `changed`: a related defect exists in another form; describe it with anchors.

Judge the defect the item names, in the place it names. A similar defect elsewhere is a new register row, not a reason to call the item `changed`. Otherwise two assessments give the same state two different statuses.

## 5. Change against base

Three counts, each with its list of items, so another participant can strike or add one:

- **M3 corrections:** a false claim about the code that base made and the set no longer makes. Unit: one distinct false claim. List them. To find them, walk the base guides' false claims (the diff `base → set` and every defect family the earlier review named) and grep each in the set. Don't stop at what the diff makes obvious: in one comparison a set's own list missed five corrections it had made.
- **M4 losses:** true and useful content in base that the set removed and keeps nowhere else. Check "nowhere else" with a grep over the whole set.
- **M5 false statements added:** statements the run wrote that the source contradicts (rows with origin `run` and kind `false`).

## 6. Entry point and routing probe

**Tables.** For each table in the entry file: are its rows consistent, does every guide appear where it should, does a guide path resolve, does one example phrase sit in two rows that route to different guides? `kit.py routes --set <set>` lists the mechanical part. Record the always-loaded cost: bytes and lines of the entry file against base.

**Probe.** Fix six user tasks and two analyst tasks before round 1, and use the same eight for every set:
- one task that needs the guide index;
- tasks that hit the main routing rows, including at least one where the needed guide is the second-priority one;
- one task in an area the run rewrote, and one in an area with a known defect family;
- one test-writing task;
- two analyst tasks ("plan the change: …") that a planning consumer would research.

Write each as the user would say it. For each task, start from the entry file only, apply the entry file's own loading rule (for example "load the P0 guide"), and record the row that matches, the guide or guides loaded, the action the guide leads to (files, symbols, commands), and whether that action is correct against the source. Verdict: `correct`, `wrong` (say what), or `unresolved` (no route, or a pointer that does not resolve).

When a task matches several rows, record two verdicts: **strict**, the worse of the matching routes, and **lenient**, the better. Report both (`strict 4/8, lenient 6/8`). The probe gives static routes, not observed agent success.

## 7. Consumers and generated sections

**Consumers.** Find every file of the consuming package that names the docs (grep for the guide folder and the main guide names). For each consuming step, record which file it reads, how much of it (whole guide, one section, a command line), and at which step. Then judge, per step, whether the set gives it what it needs. Effects on an agent are *inferred* unless you ran the step. A bounded search can show what a step's contract guarantees; it cannot show that a step never loads a guide.

Check which revision of the consumers is in use. The consuming package may run from a different branch than the generator. Ask the user when it isn't clear.

**Generated sections.** When the generator adds standard sections (the profile names them), count them per guide with `kit.py facts`, case-insensitive. For each section kind, judge whether it carries information an agent could not get as cheaply from the rest of the guide or the code: an example cut mid-body, or a quick reference that repeats the guide, is not useful however many guides have one. More sections are not more useful guidance.

## 8. Scorecard M1–M8

| M | Measure | Unit and rule |
|---|---|---|
| M1 | defects | agreed register rows by kind and severity; origin counts under rule a (`run`) and rule b (`run` + `run-c`) |
| M2 | earlier findings | absent / changed / present out of the checklist |
| M3 | corrections against base | count, with the list |
| M4 | true and useful content lost | count, with the list |
| M5 | false statements added by the run | count, with the row IDs |
| M6 | routing probe | strict n/8, lenient n/8 |
| M7 | the generator's checker | status, exit code and counters, from the revision named in the facts |
| M8 | size against base | bytes of the docs folder and of the entry file, with the change in percent |

Every number in the scorecard is backed by rows all participants accepted.

## 9. Verdict and fix-before-merge rule

- **Verdict:** usable as is · usable after named fixes · not usable.
- **Fix before merge**, stated in the prompt before round 1: every major row, plus every run-made row (rule b: `run` and `run-c`), whatever its severity. A run should not merge with damage it did itself. Inherited minors can wait.
- Owner decisions: a row that stays disputed goes to the owner as needs-decision with each stance; it is neither in nor out of the fix list until the owner decides.

## 10. What a static review cannot show: the paired delivery run

Record this in the outcome as a follow-up, not as something to run before the decision:

- **Stage A (read-only):** repeat the routing probe with an agent that actually loads the documents, and compare its loaded guides with the static probe.
- **Stage B (paired runs):** run the delivery flow on the same tasks with base and with the fixed set; same source, same model, same consumer revision, same task text. Record the guides loaded, the analysis, the plan, the diff, the gate results and the rework. Pass rule: no guide-caused wrong API, file or action. Pick the tasks where the static review found the largest differences.
- **Owner:** the repository owner. **Trigger:** the fixed set is frozen.

Without it, the outcome may say the set is more accurate or easier to route through. It may not say the set makes agents deliver better solutions.
