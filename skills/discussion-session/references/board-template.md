# Board template

Create `board.md` from the skeleton below. It starts with **no marker line**: the side that opens adds the first one. Mention markers in prose only inline, never alone on a line, so a whole-line match can never fire by mistake. Add the `## Edit register` section only when the outcome is edits to files (`edit-outcomes.md`). In relay mode, drop the `board.py` mentions from rule 4.

---

```markdown
# <Topic>: discussion board

Participants: **<TAG>** (<counterpart role>) and **CLAUDE** (<Claude's role>). Prompt, agenda and scope: `prompt.md` in this folder.

## Board rules

1. An editable board, not a log. On your turn, edit any part; fold settled points into topic entries and delete superseded text. Keep topic IDs, decisions, owners and both positions on anything open, each in a sentence or two, not as competing full drafts. No turn transcripts.
2. Turns alternate (<opener> first), with no fixed count<, and at most N turns: the user's ceiling, not a schedule — include only if the user set one>. Each turn ends with a close-out check (ready to close yes/no; still open: …). CLAUDE writes the Outcome as soon as both sides say ready, or every item is agreed or routed to an owner, or a full round changes no position. The other side then confirms or disputes each row. Edit only on your own turn.
3. The board ends with one marker line (format `END-OF-TURN <N> NEXT=<who>`), replaced on each publish; `DISCUSSION-CLOSED` ends the session.
4. Publish atomically with `python3 board.py publish` (or write `.board.tmp` in this folder and rename it over `board.md`); wait with `python3 board.py wait`.
5. Scope: <one-line guardrail summary>. Every point names the agenda item or new fact it answers; anything else goes to "Outside the agenda". Facts carry their source and how they were established (read, run, inferred). Items only an owner can decide go to that owner, not to more turns.

## Status

| Item | Status | Owner | Left |
|---|---|---|---|

## Topics

<!-- One "### D-xx <title>: <status>" entry per agenda item, added as the discussion proceeds. -->

## Outside the agenda

<!-- One line per issue raised that doesn't answer an agenda item: what, proposed owner, proposed routing (follow-up, parked or drop). The Outcome routes every line. -->

## Edit register

<!-- Only for edit outcomes; format in edit-outcomes.md. Otherwise delete this section. -->

## Questions

## Outcome

<!-- Written by CLAUDE at its outcome turn, in the shape the user asked for; confirmed row by row by <TAG>. -->

## Log
```

## Group variant

Use this skeleton in group mode (`group-mode.md`). Keep the `Roster:` and `Round:` lines exactly in this form, with no Markdown formatting on them: `board.py` reads them. Only CLAUDE publishes this board, and each round's long form lives in `rounds/<R>/`.

```markdown
# <Topic>: group discussion board

Roster: CLAUDE <TAG> <TAG> …
Round: 1 discussion, deadline not-started

Participants: **CLAUDE** (<role>; also coordinates and publishes this board), **<TAG>** (<role>), … Prompt, agenda and scope: `prompt.md` in this folder. Submissions: `rounds/<R>/<TAG>.md`.

## Board rules

1. Only CLAUDE publishes this board. Every participant, CLAUDE included, stores its own submission each round with `board.py submit`. Submissions are never changed.
2. Round R is open while the board ends with `END-OF-TURN R NEXT=ALL`. The `Round:` line gives its purpose and deadline. A late submission is refused and not counted, and a missed round is recorded, never treated as agreement.
3. Each topic holds the proposal and one line per distinct stance with its holders. A stance stands until its holder changes it. Corrections of your own stance go in your next submission.
4. Agreement: <decision rule; default: every participant explicitly accepts the current decision; one dissent or missing acceptance → needs-decision for <owner>>. CLAUDE writes the Outcome as soon as every latest check says ready, every item is agreed or routed, or a full round changes no stance. The next round confirms it.
5. Scope: <one-line guardrail summary>. Every point names the agenda item or new fact it answers. Facts carry their source and how they were established (read, run, inferred).

## Status

| Item | Status | Owner | Left |
|---|---|---|---|

## Topics

<!-- "### D-xx <title>: <status>", then Proposal, Support/Counter lines with holders, Missing. -->

## Outside the agenda

## Questions

<!-- Numbered, each naming its addressee; answered in the addressee's next submission. -->

## Outcome

<!-- Written by CLAUDE at the outcome synthesis: Item | Decision | Category | Accepted by | Dissent (tag: reason) | No response. -->

## Log

<!-- One line per round: "Round R: accepted <tags>; missing <tags>; late <tags>". -->
```
