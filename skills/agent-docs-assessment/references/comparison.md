# Comparing two or more assessed sets

Read this when every assessment is closed and the user wants to know which set to keep. The comparison is its own discussion (`<root>/compare/`, discussion-session group mode), with the same team, still blind.

## Contents

1. Why a separate comparison, and why normalise first
2. facts.md: what to prepare
3. Normalisation rules
4. Agenda
5. Outcome
6. Revealing the mapping
7. More than two sets

## 1. Why a separate comparison, and why normalise first

Two discussions with the same method still count differently. In one comparison, two assessments run in parallel by the same team differed in nine ways: identical text decided two ways, two origin rules, two fix rules, shared defects registered on one side only, one defect split into two rows, the same defect at two severities, narrower rows on one side, a different granularity for corrections, and section headings counted with and without case. Ranking the raw totals would have measured those differences, not the sets.

So the comparison starts from facts that put the two results on one basis, and its first agenda item decides how to normalise. Only then does it rank.

## 2. facts.md: what to prepare

Write `<root>/compare/facts.md`, labelled "facts to verify", with the commands that produced them. It holds data, not positions: no "better", no recommendation.

1. **The scorecards side by side**, as each assessment closed them, plus each discussion's fix-before-merge list and the section-heading counts.
2. **Where the discussions counted differently.** Walk this list and record every case with the row IDs and a grep in both sets:
   - identical text with a different decision (kind, severity, agreed versus disputed);
   - a different origin rule (a run-created contradiction called inherited on one side): search base for the new line;
   - a different fix rule;
   - a defect present in both sets but registered in one register only;
   - one defect split into several rows on one side;
   - the same defect at a different severity or kind: check whether the files really differ;
   - narrower rows on one side (fewer of the lines that hold the defect);
   - a different unit for corrections (one item on one side, two on the other), and corrections a set made but did not list (grep the other set's defects in this set);
   - checklist items in the same state with different statuses;
   - section counts with and without case.
3. **Every register row against the other set.** For each row of each register, find whether the defect is in the other set: `shared` (with the anchor there), `partly` (what differs), or `only here` (with the search that shows it absent). This is the heaviest step: give each register to a subagent, one row at a time, with the rule "quote the other set's line or name the grep that found nothing", and spot-check its answers.
4. **Totals:** shared / partly / only here per register, and the major defects present in one set only.

## 3. Normalisation rules

Propose these in your round-1 submission; the discussion settles them.

- **M1, coverage-completed.** Count defects present in each set, not rows registered: add to each set the shared defects only the other register recorded, and give identical text the same classification in both. Label the result "coverage-completed; unequal row units", because the row units still differ.
- **The robust discriminator** is the list of **major defects present in one set only**. It is insensitive to row units and registration gaps, and it is what an agent meets differently in the two sets.
- **Origin:** apply one rule to both sets, and report both rules (`run` only, and `run` + `run-c`).
- **M3:** one granularity for both, and add the corrections a set made but did not list. Give the numbers at both granularities if the participants differ.
- **M2:** the same state gets the same status.
- **Section counts:** case-insensitive, with the exact-case count beside it.
- **Fix cost:** one rule for both sets (every major present plus every run-made row), with the other rules' numbers beside it (rule a; major-only). Fix counts are row actions, not hours.
- **Noise:** when a difference between the sets is smaller than the counting differences in §2, say "no material difference".

## 4. Agenda

- **C-01 Comparability.** For each measure M1–M8, the counting differences and the normalised values, or "cannot be compared".
- **C-02 Accuracy.** With shared defects set aside: which major defects exist in one set only, what each does to an agent (inferred, with the consumer step), and which set is more accurate.
- **C-03 What each run added and removed.** Corrections, losses, false additions, run-made rows, checker result and size: which run did more good and less damage?
- **C-04 Entry point and routing.** Differences in the entry file (tables, rows, conflicts, cost) and in the probe, task by task.
- **C-05 Usefulness to the consumers.** For each consuming step, does one set serve it better? The generated sections set against set.
- **C-06 Fix cost.** Blocking rows of each set under one rule, how many are shared, and which named parts of one set could fix the other.
- **C-07 Recommendation.** Keep one set, keep neither, or keep one with named files or passages from another; its fix list; and the generator follow-ups (defects common to all sets).

Goal questions for the prompt: which set is more useful to an agent, measure by measure and overall; which to keep and at what fix cost; which defects are common to all sets and so belong to base or the generator.

**Taking parts from one set into another.** Check every proposed graft by diff, and check what the graft would drop: a whole-file swap can remove true, source-backed rules the receiving set added. Prefer "this set's structure, that set's content" when both have something true. Name the file and the lines.

## 5. Outcome

- One row per agenda item, plus rows for the generator follow-ups (`follow-up`, owner: the generator's maintainers, trigger: before the next regeneration) and the paired delivery run (`follow-up`, owner: the repository owner, trigger: the fixed set is frozen; `method.md` §10).
- A comparison scorecard: one row per measure, with each set's value (normalised where C-01 says), the better set or "no material difference", and the reason.
- The recommendation with its fix list: the blocking rows of the kept set, the passages taken from another set, and what can wait.
- Answers to the three goal questions.
- If the comparison reclassifies a row of a closed assessment, record that in the comparison outcome. Don't edit the closed assessment's decisions: its record, dissent included, stays as it was.

## 6. Revealing the mapping

After the comparison outcome is confirmed, and before you summarise for the user:

1. Add an **Identity** section to the closed comparison board: each label with its branch, commit and what produced it, and the sentence "The comparison was made blind; this changes no row."
2. Add one identity line to each assessment's `outcome.md` and to the comparison's `outcome.md`. Change nothing else in them.
3. Tell the user in the summary which label was which.

## 7. More than two sets

Use one comparison discussion for all sets, with one column per set in the facts and the scorecard. The overlap table becomes one row per defect with a column per set (present / partly / absent). The discriminator becomes "major defects absent from the best set but present in another" and vice versa. Keep the number of participants within discussion-session's cap; sets are not participants.
