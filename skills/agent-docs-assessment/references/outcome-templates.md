# Outcome documents

The board's Outcome section is the record, but nobody hands a board on. When a session closes, write a standalone `outcome.md` in its discussion folder without being asked, and give the user its path. Fill it from the closed board and `kit.py tally`, copying decisions as the board states them; add nothing the participants did not agree.

## Assessment outcome

```markdown
# Outcome: assessment of <set L | the change in <branch>>

**Status:** final, confirmed by <participants>; decision rule: <unanimity>. **Date:** <date>. **Record:** `<abs dir>/board.md` (decisions, topics, log) and `rounds/` (each participant's reasoning). **Method and agenda:** `<abs dir>/prompt.md`.
<After a comparison closes: **Identity:** set <L> = <branch> (<commit>, <how produced>).>

<Two sentences: what was assessed, against what. Every defect below was reproduced by at least two participants. Paths are relative to <guides folder>; line numbers are set lines. Tag letters: <C = Claude, …>.>

## Answers
**Goal question 1:** <answer, e.g. mixed against base; better in …>. Strongest evidence: (1) … (2) … (3) …
**Goal question 2:** <not shown>; what would show it: <the paired run, one line>.
**Verdict:** <usable as is | usable after named fixes | not usable>.

## Scorecard
| M | Measure | Value |
|---|---|---|
<M1–M8 as agreed>

## Decisions per agenda item
| Item | Decision | Category | Accepted by | Dissent | No response |
|---|---|---|---|---|---|

## Fix before merge
### Major defects (<n>)
| ID | Where | Defect | Kind | Origin |
|---|---|---|---|---|
### Run-made minor defects (<n>)
<same table>

## Owner decisions
<Rows still disputed, each stance by tag.>

## Corrections against base (M3)
<Numbered list.>

## Can wait
<Inherited minor rows: ID, where, one line each.>

## Routing probe
| Task | Row | Guide(s) | Verdict (strict / lenient) |
|---|---|---|---|

## Outside the agenda
<Each entry with its owner, or why it was dropped.>
```

## Comparison outcome

```markdown
# Comparison of <sets>: outcome

Final, confirmed by <participants> (rounds 1–<n>, <rule>). Full record: `board.md` and `rounds/`. Inputs: the assessment outcomes and `facts.md`.

**Identity (revealed after confirmation; the comparison was blind):** <label = branch (commit, how produced)>, …

## Answers
1. **Which set is more useful:** <set>, on <measures>; <other set> on <measures>, <material or not>; no material difference on <measures>.
2. **Which to keep:** <set>, fixed, with <n> named passages from <other set>; fix cost <n> blocking rows (<other> would need <n>).
3. **Common to all sets:** <n> shared major families and the shared minors; they belong to base or the generator (follow-ups).

**Decision for the owner:** <which set to keep>.

## Scorecard
| M | <A> | <B> | Better | Reason |
|---|---|---|---|---|

## Why <set>
<Accuracy (set-only majors and what they do), what each run added and removed, routing, consumers: four short paragraphs.>

## Fix list for <set>
<Blocking rows by ID; passages to take from another set with file:line; what can wait.>

## Generator follow-ups
Owner: <generator maintainers>. Trigger: before the next regeneration.
<Numbered defect families common to all sets.>

## Paired delivery run
<When, tasks, setup, records, pass rule, owner, trigger.>

## Other agreed points
<Reclassifications recorded here, not in the closed assessments; outside-the-agenda items.>
```

Keep both files free of positions that the board does not record. When the user asks for a shorter version, cut detail, never a decision or a dissent.
