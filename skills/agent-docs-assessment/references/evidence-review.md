# Developer feedback, and the evidence review of its claims

Read this when the user wants the assessment turned into feedback for the people who own the docs or the generator, and especially when the feedback explains causes ("why did the generator do this?"). Causes are where a confident text goes wrong: a plausible mechanism written as fact, a quotation tidied up, a line number from another revision. Users notice, and one wrong cause discredits the true ones beside it.

## Contents

1. The feedback document
2. The claim standard
3. Self-audit before anyone else reads it
4. The evidence-review session
5. Applying the result

## 1. The feedback document

Write it in the review root (or wherever the user says), never into the repository under review unless asked. Sections:

1. **Verdict** in one paragraph: the decision (merge, merge after named fixes, don't merge) and the answers to the goal questions.
2. **What is better than before**, with the strongest evidence.
3. **Fix before merge**: the run-made defects first, then the inherited majors, then the entry file; each with `guide:line`, the wrong statement, what the source says, and the fix in one line.
4. **Still wrong, but the same as before**: inherited defects that can wait.
5. **Usefulness of each generated section**: what an agent gains from it and what it doesn't.
6. **Not shown**: what the review cannot say about delivered solutions, and the run that would show it (`method.md` §10).
7. **Generator behaviour related to the defects, with evidence**: only claims that meet §2.
8. **Not established**: one line per open question, saying what is unknown and which artifact would settle it.

Sections 1–6 come from the closed assessment and need no new evidence; cite the register IDs. Section 7 is new material and needs §2–§4.

## 2. The claim standard

A statement stays in section 7 only if it meets all of these:

1. It is a fact about a source that exists: the text of a file at a named revision, the output of a command, or what a piece of code does when traced line by line.
2. **Quotations match character for character**: bold markers, backticks and punctuation kept; `…` joins parts of one line only, never two sentences.
3. **Line numbers hold at the named revision.** Generators change fast: say which revision every line is from (the revision that produced the docs, the current tip), and whether it changed between them.
4. **A *run* statement gives the exact command**, with every variable defined in the text, so a reader can paste it. No placeholders such as `<run snapshot>`. Use only tools the reader has: the shell, `git`, `grep`, `sed`, `diff`, or `python3` with the code inside the command. Never cite `kit.py` or a helper script you wrote and did not ship with the document: the developer cannot run it, so the claim cannot be checked.
5. **Code behaviour is traced through the code.** A comment or a commit subject is evidence of what its author wrote, not of what the code does.
6. **The actor is named correctly**: a script, an agent following instructions, or the user's approval step. "The generator did X" hides which.
7. **Absence and universal words** ("no", "none", "only", "nothing", "always", "every") name the search and its scope. One counterexample removes the statement.
8. **A causal link is its own claim.** "Mechanism M produced defect S in this run" is a fact only if you reproduce it, or if the code leaves no other path to S. Otherwise it is not a fact, however likely: it goes to "Not established", or is cut.
9. **Tags are honest**: *read* or *run* only for what was read or run; an inferred link tagged *read* is a false claim.
10. **No suggestions.** A proposal for how to fix the generator is not a fact; cut it from this section.
11. **A heading says no more than the rows under it show.**

To check line numbers in the generator, snapshot each revision you cite into the root (`git archive <rev>:<package dir>`), and state a command that compares the snapshot with git file by file and prints nothing. Then every *read* citation can be checked without trusting you.

## 3. Self-audit before anyone else reads it

Before you show the section to the user, or open a review session:

1. Number every claim in a copy of the section: `[C-nn · 7.x]` in front of each statement, with the file line number.
2. Check each claim against §2 yourself, with subagents for heavy traces. Mark keep / reword / cut / not established.
3. Expect to find errors. In one self-audit about a third of the first draft's claims held as written; the rest named the wrong actor, assumed what the code did, claimed "the only check" without searching, or tagged an inference as read.

Then deliver: the self-audited document, with every claim you could not settle moved to "Not established". A request for "facts only, no make-ups" is met by this audit; it is not a request for a session. Offer the team review of §4 in one line, and set it up only when the user asks for it, or when they question a claim after reading: one questioned claim usually means others share its flaw.

## 4. The evidence-review session

When the user asks for it: a discussion-session group discussion with an edit outcome (discussion-session `references/edit-outcomes.md`). The same team as the assessment works well: they know the material.

- **Files:** the numbered copy of the section, the generator snapshots, the feedback file.
- **Agenda:** one item per subsection, each listing its claim IDs. The question per item is the same: which claims hold as written, which are wrong, which say more than their evidence, and does the heading follow from what is left?
- **Scope:** only this section. Other sections, the merge decision and how to fix the generator are out of scope.
- **Rules in the prompt:** the §2 standard verbatim; no generator command that writes may be run; a participant may add a statement only to replace a wrong one, with its evidence, and another participant must verify it in the next round.
- **Agreement:** a claim is kept or reworded only when every participant accepts that exact text as verified. A claim one participant cannot verify, and another round does not settle, is cut and listed with each stance.
- **Edit register:** one entry per subsection (`E-00` preamble, `E-01` …) replacing its whole text, so the register stays small. `board.py edits check` before each publish; quote its `net:` line.
- **Outcome:** the disposition of every original claim (kept as written, reworded, cut, moved to "Not established"), with counts, and the net word change.

## 5. Applying the result

1. Back up the feedback file.
2. `board.py edits apply`, then `edits verify` (discussion-session `edit-outcomes.md` §4).
3. Check that the sections outside the review are byte-identical to the backup.
4. Search the new section for the words the review removed (old symbol names, "only", "always", the cut causes). Each hit is intended, and you say why, or a missed edit.
5. Tell the user the disposition counts, the net change, and where the file is.
