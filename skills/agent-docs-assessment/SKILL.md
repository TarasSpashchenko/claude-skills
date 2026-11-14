---
name: agent-docs-assessment
description: >-
  Assess AI-agent documentation (AGENTS.md, CLAUDE.md, .ai-run/guides and similar guide trees),
  especially docs a generator such as sdlc-factory's knowledge-foundation regenerated in a branch or
  MR, with reviewing agents (e.g. GPT in Codex, Gemini) on top of the discussion-session skill. It
  builds a blind review kit, runs identical, comparable assessments (reproduced defect register,
  routing probe, consumer analysis, scorecard), compares candidate sets, writes outcomes and
  developer feedback, and evidence-checks claims about causes. Use it whenever the user wants to
  know if regenerated or rewritten agent guides are better, usable or mergeable; to compare versions
  of the guides (e.g. produced by different models or generator revisions); to tell a developer
  what is still wrong in them; or to verify a feedback document's claims "with evidence", even if
  they never say "assessment". Not for writing or fixing the guides, reviewing application code, or
  a quick one-file proofread.
---

# Agent docs assessment

You assess documentation written for AI agents: the entry file an agent loads in every session (`AGENTS.md`, `CLAUDE.md`) and the guides it routes to. The question is always practical: does an agent that follows these documents take the right action in this repository, and is this version better than the one before, or than the other candidate?

This skill sits on **discussion-session**. Load that skill first and follow its group mode for everything about the board: `board.py`, rounds, deadlines, independence, private notes, consolidation, confirmation, closing, and never starting a counterpart yourself. This skill adds what an assessment needs on top: the review kit, a method that makes assessments comparable, the prompts, the comparison, the outcome documents and the evidence standard for feedback.

Why it is built this way. Each rule below answers a failure seen in real assessments:
- **Two assessments that counted differently cannot be compared.** The method fixes every unit and rule before round 1, and the comparison normalises what still differs.
- **A reviewer who knows which model or team produced a set judges the label.** Sets get blind labels and are checked for leaks.
- **Claims checked against the wrong source give false defects.** Each set is exported with the exact source it was generated from, outside the user's repository.
- **One unsearched "none found" or "the only" sinks a report.** Absence and universal claims name their search, and a defect counts only when a second participant reproduced it.
- **A plausible cause written as fact discredits the true ones.** Causes meet a strict standard, or go to "Not established".
- **An outcome buried in a board is lost.** Every closed session gets a standalone `outcome.md`.

## Workflows

| The user wants | Run | Read |
|---|---|---|
| To know whether one branch or MR that regenerates the docs should merge | Assess one change: kit → one assessment → outcome → feedback for the developer if asked | `review-kit.md`, `method.md`, `prompts.md`, `outcome-templates.md` |
| To compare two or more candidate versions | Blind kit → one identical assessment per set → comparison → reveal | the above, plus `comparison.md` |
| Feedback for the developer, or a check that its claims hold | Feedback document → self-audit → evidence-review session | `evidence-review.md` |
| Any of these on docs from sdlc-factory | The same, with the profile | `profiles/sdlc-factory.md` |

For another generator, the method stays the same: work out its equivalents of the profile (where the docs live, the entry file's loading rule, the generated sections, the checker, the consumers) at intake, and write them in your notes.

## Phase 1: Intake

Infer what you can from the conversation and the repository, then ask once, in one batch, for what is missing:

1. **Candidates.** The branches, commits or MRs, and the repository. Fetch them if needed, and say so.
2. **Base.** The revision the run started from, usually the merge-base with the target branch. Not the user's current checkout, which is often ahead.
3. **Generator.** What produced the docs, at which revision, and whether it has a checker. Use the profile if one fits.
4. **Consumers.** Which agents read the docs, and which revision of them is in use. The consumers often run from a different branch than the generator; ask when unclear.
5. **Earlier review.** If one exists, its findings become a checklist (`method.md` §4).
6. **Team.** By default, Claude plus two counterparts with distinct lenses (`prompts.md` §3): a delivery-agent lens and a source-accuracy lens. The user starts them.
7. **Deliverables.** Always an `outcome.md` per session. For one change, offer feedback for the developer. For several candidates, a comparison and a recommendation.
8. **Blind.** On by default for two or more candidates.

Then give the user a short plan before you build anything: the sessions, what makes them comparable, the choices you made (blind labels, the review root outside the repository), and what they will be asked to start.

## Phase 2: Build the review kit

Follow `references/review-kit.md`. In short:

1. `kit.py setup` exports base, each candidate (random labels when blind), the generator and the consumers into a review root next to the repository. The label mapping goes to your private notes folder, never under the root.
2. `kit.py leaks` with the model, tool, author and branch names. Neutralise every revealing hit, and run it again until it reports none.
3. `kit.py seal` makes each set a git repo with one clean commit. It runs the same check and refuses while a leak is left: a word committed before you remove it stays in the history.
4. `kit.py facts`, `routes` and `paths`, plus the generator's checker per set, into `facts/`.
5. Write `prior-findings.md` if there is an earlier review.

## Phase 3: Prepare each assessment

One discussion folder per set (`assess-<L>/`), set up as discussion-session group mode describes, with these additions:

1. **Method.** Write the method section from `references/method.md`: the reading shares, the register with its kinds, severity test, origin values (`run`, `run-c`, `inh`) and row unit, the reproduction rule, the checklist statuses, the units of M3–M5, the eight probe tasks with the strict and lenient rule, and the fix-before-merge rule. Fix all of them now; a rule settled in round 3 of one assessment differs from the rule in another.
2. **Prompts.** Shared prompt and entry prompts from `references/prompts.md`. With several sets, render all prompts from one template and diff them after swapping the labels: only measured facts may differ.
3. **Your round-1 submission.** Gather your share's evidence with background subagents, verify their main claims, count with `kit.py tally`, and store your submission right after publishing the round-1 board (`prompts.md` §5). Do this for every set before the user starts anyone.
4. **Hand off.** One start line per agent per set, each a fresh session started in the review root, so no agent sees two sets. Then stop until the user says go (discussion-session group mode §5).

## Phase 4: Run the rounds

Follow discussion-session group mode §5–§8. What an assessment adds at each consolidation:

- **Verify before you fold.** Re-run the key command of every new row and of every counter-claim, and check that each cited file is under the review root. A reviewer once reported a whole checklist from another checkout of the same repository; the reproduction rule caught it only because someone checked. Mark rows that fail as `not reproduced`, with the command.
- **The register is the board's centre.** Keep one table per set with the columns of `method.md` §3, each row with who found it and who reproduced it. Admit a row only when a second participant reproduced it. Settle severity with the one question in `method.md` §3, and give identical text the same decision.
- **Count with the script.** Run `kit.py tally` on the board before you publish a scorecard. Hand counts drift: a "9 major" that was 8, a checker count that included its summary line.
- **Concede on evidence, quickly.** When a counterpart shows your row is wrong, say so in your next submission and fix the board. Your earlier submission stays as stored.
- **Probe:** record each participant's verdict per task. Agree strict and lenient separately.
- **Keep your notes current** with a "RESUME HERE" block: these sessions are long, and the user may compact your context between rounds.

## Phase 5: Close and write the outcome

At close, as discussion-session describes, and then without being asked:

1. Write `outcome.md` in the discussion folder from `references/outcome-templates.md`, using the board's decisions, `kit.py tally` for the counts, and nothing the participants did not agree.
2. Tell the user in a few lines: the verdict, the scorecard highlights, what needs their decision, and the paths.
3. If the user wants feedback for the developer, follow `references/evidence-review.md`.

## Phase 6: Compare (two or more sets)

When every assessment is closed, follow `references/comparison.md`: write `compare/facts.md` (scorecards side by side, every counting difference, every register row against the other set), run the comparison discussion with the C-01 to C-07 agenda, and write its outcome. Then reveal the mapping (`comparison.md` §6): add the identity lines, change no decision, and tell the user which label was which.

## Phase 7: Feedback and evidence review

`references/evidence-review.md` gives the feedback document's sections, the claim standard for causes, the self-audit, and the evidence-review session with an edit outcome. Write the document, self-audit it, and deliver it; a request for "facts only" is met by the audit. Offer the team review in one line, and set it up only when the user asks for it or questions a claim after reading: one weak claim usually has siblings. Every command in the document uses tools the developer has, never `kit.py`.

## Things that go wrong, and what to do

- **The user's checkout is ahead of the candidates.** Check against the exports, never the checkout.
- **The generator's checker is a later revision than the one that ran.** Say which revision you ran, and call the producing revision inferred unless you can show it.
- **A counterpart is missing at a deadline.** Follow group mode: record it as missing, never as assent, and tell the user.
- **A fact in your own stored submission is wrong.** Correct it in your next submission and on the board; never edit a stored submission.
- **A later discussion changes how a closed one classified a row.** Record the change in the later outcome. Don't edit the closed record.
- **The repository forbids report documents.** Keep every kit, board and outcome in the review root outside it.

## Files in this skill

- `references/review-kit.md`: the review root, its layout, `kit.py` commands, blind labels, facts to verify, the checklist file. Read in Phase 2.
- `references/method.md`: reading shares, defect register, checklist, M3–M5, routing probe, consumers, scorecard, verdict and fix rule, the paired delivery run. Read in Phase 3.
- `references/prompts.md`: the shared prompt template, lenses, entry-prompt additions, your round-1 submission. Read in Phase 3.
- `references/outcome-templates.md`: `outcome.md` for an assessment and for a comparison. Read in Phase 5.
- `references/comparison.md`: facts for the comparison, normalisation rules, agenda C-01 to C-07, outcome, reveal. Read in Phase 6.
- `references/evidence-review.md`: the developer feedback, the claim standard, the self-audit, the evidence-review session. Read in Phase 7.
- `references/profiles/sdlc-factory.md`: knowledge-foundation output, its contract, `sdlc-guides check`, the factory's consumers, defect families seen before. Read at intake when the docs come from sdlc-factory.
- `scripts/kit.py` (Python 3, standard library): `setup`, `leaks`, `seal`, `facts`, `routes`, `paths`, `tally`. Run `python3 <skill>/scripts/kit.py <command> --help`. It is your tool: never cite it in a document someone else must check.
