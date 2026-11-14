# Prompts for an assessment session

Read this when you write the files of an assessment discussion. It gives the shared prompt (`prompt.md`), the entry prompts (`prompt-<TAG>.md`), and the lenses. The protocol part comes from discussion-session's `group-mode.md` §9; this file adds what an assessment needs on top.

## Contents

1. One template, rendered per set
2. Shared prompt template
3. Lenses
4. Entry prompt additions
5. Claude's round-1 submission

## 1. One template, rendered per set

When there are several sets, write the shared prompt once as a template, with the label, the set's paths and the set's measured facts as the only variables, and render one copy per set. Then check: `diff` the two rendered prompts after replacing one label with the other. Only the measured facts may differ. A sentence added to one prompt and not the other is a difference in method, and the comparison inherits it.

Aliases keep the prompt short. Define them in the first line and write full paths in every command.

## 2. Shared prompt template

Fill every `<…>`. Keep §6 exactly as `method.md` defines the counts.

```markdown
# Shared prompt: assessment of <set label | the change in <branch>>

Aliases, used in this prompt only (write full paths in commands): `{root}` = `<abs root>`, `{set}` = `{root}/set-<L>` (the repository snapshot under assessment), `{base}` = `{root}/base`, `{dir}` = `{root}/assess-<L>` (this discussion). Guide paths are relative to `{set}/<guides folder>/`; source paths are relative to `{set}`.

## 1. Your role

You are one of <N> participants in a written, round-based discussion; your entry prompt gives your lens. You did not produce the documents. Be direct, evidence-based and concise. Disagree where you have reason to, agree plainly where you don't, and don't pad.

## 2. Goal and why it matters

<Who decides what, and why now: e.g. "The repository owner must decide which regenerated set of AI-agent documentation to keep." / "… whether to merge this regeneration.">
<For several sets: "This discussion assesses set <L> only; each other set gets its own discussion with the same agenda, and a later discussion compares the results.">
The assessment must answer:
1. <Goal question 1, method.md §1>
2. <Goal question 2, method.md §1>

Neither answer is presumed. Report real strengths and real defects, invent neither. <Several sets: "The comparison is only as good as the assessments are alike, so follow the method in §6 exactly and count what it asks you to count.">

<Blind: "**The labels are deliberate.** Judge only what is in `{set}`. Do not try to find out how the set was produced, and do not open <the other sets' folders, their discussion folders, the comparison folder, facts files named for another set>.">

## 3. Context

<The repository in two sentences. The docs: entry file, how it routes, how many guides.>
<The generator and the consumers in two sentences: what produces the docs, what reads them.>
<What base is. That the source is the same before and after. The earlier review and its checklist, if any.>

**Facts to verify** (Claude's measurements, not conclusions), each with its command:
- Size: <from facts/sizes.md>.
- Section headings: <counts per section, base → set>.
- Generator's checker: <status, exit code, counters; full output in `{root}/facts/check-<L>.txt`; which revision>.
- The generator's contract for sections and caps: <file:line>.
- Consumers: <the files that name the docs, with the line that shows what they read>.

## 4. Read first

1. **The set**: `{set}/<entry file>` whole, then the guides of your reading share (§6) whole, then samples of the rest.
2. **The source** (authoritative for whether a statement is true): <source folders and config files>.
3. **The change**: `{root}/facts/diff-base-<L>-docs.patch` and `…-entry.patch`.
4. **The checklist**: `{root}/prior-findings.md` <if any>.
5. **The consumers**: `{root}/consumers` <the files named in §3, plus the flows that call them>. Look for which file is read, how much of it, and at which step.
6. **The generator's contract**, when you judge a section against what it was meant to hold.

Everything under `{root}` is read-only for you except `{dir}`.

## 5. Scope and evidence

- **In scope:** <entry file, its imports and the guides> of this set, judged against the source in `{set}`, against base, and against how the consumers use them.
- **Out of scope:** <other sets and any comparison>; how the set was produced; redesigning the generator or the consumers. A defect that looks like the generator's doing is still a defect of the set: mark it "generator" and move on.
- **Fixed, not to be reopened:** <e.g. where the guides live and how the entry file routes>; nobody edits a file under `{root}` outside `{dir}`.
- **Not your call:** <the decision>. You recommend; the owner decides.
- **Traceability.** Every point answers an agenda item or a new fact under discussion; say which. Anything else goes to the board's "Outside the agenda" list, one line with a proposed owner.
- **Evidence.**
  - Cite a document as `path:line` in the set and the source as `path:line`, or give the command you ran.
  - Quote a disputed statement exactly.
  - Keep facts apart from opinions, and tag each fact *read*, *run* or *inferred*.
  - A claim that something is absent or universal ("no X", "every guide", "nothing reads") names the search behind it.
  - A claim about what an agent would do is *inferred* unless you ran it; say which consumer step it rests on.
  - Check that every file you rely on is under `{root}`.
  - A defect enters the outcome only when a second participant has reproduced it.

## 6. Method (<the same in every assessment>)

<Paste from method.md: reading shares with the names of this team, the defect register with its columns, kinds, severity test, origin values and row unit, the checklist statuses, the M3/M4/M5 units, the probe procedure with the eight fixed tasks and the strict/lenient rule.>

## 7. Agenda

- **D-01 Accuracy.** Against the source in `{set}`: which statements are false, broken or contradictory? Defect register rows, counted by kind, severity and origin.
- **D-02 Earlier findings.** Status of P-01 to P-<n> in this set, each with its evidence. <Drop when there is no checklist.>
- **D-03 Change against base.** What did the run correct, what did it add that is true and useful, what false statement did it add, and what true and useful content did it remove without keeping it elsewhere?
- **D-04 Entry point and routing.** Is each table of the entry file consistent, is every guide reachable, what does the always-loaded file cost, and what does the routing probe show (strict and lenient, n of 8)?
- **D-05 Usefulness to the consumers.** For each consuming step that reads the documents, does the set give it what it needs? Which generated sections carry information an agent could not get as cheaply from the rest of the guide or the code, and which do not?
- **D-06 Verdict.** Answers to the goal questions, and one of: usable as is, usable after named fixes, not usable. Which rows must be fixed before merge (§6 rule)?

You may add up to 2 new topics, only if they are in scope and material.

## 8. Outcome the owner expects

- One row per agenda item: `Item | Decision | Category | Accepted by | Dissent (tag: reason) | No response`. Categories: agreed-as-is · agreed-change · needs-decision · needs-evidence (a test with its decision rule) · follow-up (with an owner and a trigger).
- A scorecard M1–M8 (method §8), each value backed by rows all participants accepted.
- The agreed defect register, in two groups: "fix before merge" and "can wait".
- The answers to the goal questions with their strongest evidence, and the verdict.

<§9–§11: the protocol from discussion-session group-mode.md §9 (sections 8–10 there), renumbered, with the submission format below.>
```

**Submission format for an assessment** (replaces the generic one in the protocol):

```markdown
    # <TAG>, round <R>
    ### D-xx <title>
    Stance: accept | counter | dissent | answer. <Position, rationale, sources with read/run/inferred.>
    ### Defect register
    <Rows as §6 describes; from round 2 on, also `reproduced` or `not reproduced: <why>` for other participants' rows.>
    ### Earlier findings
    <One line per checklist item of your share and of the entry file: status and evidence.>
    ### Routing probe
    <One line per task: row, guide(s), action, verdict; strict and lenient where they differ.>
    ### Corrections to the board
    <How the board misstates your position, if it does; Claude applies these as written.>
    ### Questions
    <Numbered, each naming its addressee.>
    Close-out check (<TAG>, round <R>): ready to close yes/no; still open: …

Cover every item the round asks for; skip none silently. In round 1 no proposal exists yet, so give your own position on every item, your defect rows, the checklist status for your share, and the routing probe. In a confirmation round, write one line per outcome row: `confirm` or `dissent: <reason>`.
```

## 3. Lenses

The default team is three participants. Lenses are taken from the question, not from the harness, and each lens says why it matters:

| Tag | Lens | Why it matters |
|---|---|---|
| GPT (or any delivery-minded agent) | **Delivery agent.** Judges the documents as the consuming agents would: which step reads which guide, what each step does with it, where a statement changes the code, the plan or the review an agent produces. | A guide that is accurate but never reaches the step that needs it is worth little, so this lens decides how much each defect matters. |
| GEMINI (or any source-checking agent) | **Source accuracy.** Judges the documents against the code: which statements are true, which are false, which point at something that does not exist. | A guide that reads well but misdescribes the code makes an agent's output worse, so this check carries the verdict. |
| CLAUDE | **Structure, routing and internal consistency** (in a comparison: also the comparability of the counts). | Defects in the entry file and in contradictions between guides reach every task, whatever the guide content. |

Every lens may challenge any item.

## 4. Entry prompt additions

Use discussion-session's entry-prompt template (`group-mode.md` §10), with these additions:

- **A third capability check** that the participant can read the review: `ls {set}/<guides folder> {root}/consumers/<a folder>` (in a comparison: both sets and both assessment boards). The failure message names the start command that fixes it (the review root as working folder).
- **A path check** for every agent, and twice over for one that has another checkout of the same repository in its workspace: "Make sure every file you read is under `<root>`: check the path of each file before you rely on it. Another checkout of the same repository may be open in your workspace; it is not part of this review." One reviewer once reported defects from a different checkout; this sentence and the reproduction rule catch it.
- The harness notes from discussion-session's `harnesses.md` (wait timeouts, write-access flags).

Start lines for the user: one per agent per set, each a fresh session, started in the review root.

## 5. Claude's round-1 submission

You are a participant first. Write your round-1 submission before any counterpart starts, and store it with `board.py submit` right after you publish the round-1 board:

- Gather the evidence for your share with background subagents, one per guide group, each told to quote exactly, give `path:line` for the set and the source, and name the search behind any "absent" claim. Check their main claims yourself before you use them: a subagent's error becomes your error once stored.
- Count with the scripts (`kit.py tally` on a draft register, `grep -c`), not by eye. A stored submission cannot be changed, so a wrong count costs you a correction round.
- Cover all six items, your defect rows, the checklist for your share and the entry file, and the probe.
- With several sets, write each set's submission from that set's evidence only. Don't let what you saw in one set fill a gap in the other.
