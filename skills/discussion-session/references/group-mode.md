# Group mode

Read this when the discussion has two to four counterparts, so three to five participants in all. Everything in SKILL.md still holds unless this file says otherwise: intake, agenda, evidence, outcome categories, private notes, and never starting a participant yourself. This file covers only what changes when more than two take part.

## Contents

1. Who you are in a group
2. The cap
3. Intake additions
4. Files
5. How a round runs
6. Board shape
7. Closing, agreement and confirmation
8. Missing, late and relayed participants
9. Shared prompt: the protocol section
10. Entry prompt for each participant

## 1. Who you are in a group

You are two things at once, and the discussion only works if you keep them apart:

- **A full participant.** You submit your own positions every round, exactly like the others, and your acceptance or dissent counts the same as theirs, no more.
- **The coordinator.** You are the only one who publishes the board. You fold every submission into it, including your own, and keep the record honest.

The coordinator role carries a temptation: you write the summary, so you can tilt it. Guard against it the way the protocol is built. Write your own submission before you read anyone else's for that round. List your stance by tag like any other. Apply a participant's corrections to how the board describes them, and leave everyone's submissions on disk as the record anyone can check.

## 2. The cap

At most **5 participants in total, you included**: you plus up to four counterparts. This is the user's limit, and `board.py` enforces it on the roster. If the user asks for more, ask which participants to keep. Don't silently drop anyone, and don't split the discussion into two panels unless the user asks for that.

## 3. Intake additions

Ask these in the same single batch as the rest of Phase 1, inferring what you can:

- **The roster.** For each counterpart: its harness or app, a unique uppercase tag, and its role. Roles are lenses taken from the topic, such as correctness, operations, cost, user impact or a skeptic's view. They are not stereotypes of the harness. Anyone may still challenge any item. Distinct lenses are why more participants add value; four copies of one reviewer only add noise. The same lens twice makes sense only when the user wants a comparison between models.
- **Access, per participant.** Direct means it can read and write the shared folder and run `board.py`. Relay means the user carries its turns. Mixing them is fine. Say what relay costs: the user pastes in and out for that participant every round.
- **Timing.** A round window (default 60 minutes) and each participant's wait budget (default 120 minutes, the window plus 60). The budget must exceed the window plus your consolidation time, or a fast participant gives up before the next round opens. For a human participant, offer a longer window.
- **Decision rule.** The default is unanimity: a row is agreed only when every participant explicitly accepts it. Another rule (majority, or a named owner who decides) applies only if the user chooses it now, before the discussion. Never infer a majority rule from the number of participants.
- **A ceiling,** if the user sets one, counts opened rounds, including the confirmation round.

Write the roster into your private notes with each participant's tag, role, access, harness and start line.

## 4. Files

In the discussion folder:

- `prompt.md`: the shared prompt. It holds the context, the reading list, the agenda, the scope, the evidence standard, the outcome requirements and the group protocol (§9). Build §1–§7 from `counterpart-prompt-template.md`, written for "one of several participants", with no single role in it, then use §9 below in place of the template's §8–§10.
- `prompt-<TAG>.md`: one short entry prompt per counterpart (§10). It is the file the user pastes into that participant's session.
- `board.md`: from the group variant in `board-template.md`. It starts with the `Roster:` and `Round:` lines.
- `board.py`: a copy of `scripts/board.py`. Delete it when the discussion closes.
- `rounds/<R>/<TAG>.md`: the submissions, created by `board.py submit`. They are never edited or overwritten, and they stay as the record.

Your private notes stay outside the folder, as in pair mode.

## 5. How a round runs

Round R is open when the board ends with `END-OF-TURN R NEXT=ALL`. `ALL` is a reserved tag that addresses everyone. Every participant answers the same board, and only you move it forward.

1. **Open round 1 at setup.** Publish the agenda board with `Round: 1 discussion, deadline not-started` and the marker `END-OF-TURN 1 NEXT=ALL` (`--expect-last none`). A participant can submit the moment the user starts it.
2. **Submit your own opening** right away, before any other round-1 file exists: `board.py submit --round 1 --tag CLAUDE --from <draft>`. That keeps your first view as independent as everyone else's. Cover every Tier 1 item. Independence rests on a cooperative rule: every participant can read the folder, and only its prompt asks it not to read others' submissions early. Never tell the user that others cannot see a submission.
3. **Hand off.** Give the user one paste line per counterpart (`Read and follow <abs>/prompt-<TAG>.md`), plus any access flag from `harnesses.md`. Then stop, as in pair mode.
4. **Start the clock at the user's go.** When the user says the participants are started, or simply "go", publish the same board again with the deadline as a clock time: `Round: 1 discussion, deadline <now + window, ISO 8601 with offset>`, using `--expect-last 'END-OF-TURN 1 NEXT=ALL' --marker 'END-OF-TURN 1 NEXT=ALL'`. Round 1 runs whether or not everyone has started. Otherwise a participant that never starts would hold everyone hostage.
5. **Collect** in the background, like the pair-mode watcher (`run_in_background: true`, `timeout: 7200000`):

   ```bash
   python3 <skill>/scripts/board.py collect --board /abs/path/board.md --round 1 --timeout 7100
   ```

   It exits 0 when every rostered participant has submitted, 4 when the deadline passed with some missing, and 124 when this call's own timeout ended first. Run it again after a 124. The deadline is the one on the board, so a repeat or a resume never extends it.
6. **Consolidate.** Read every received submission, and check factual claims against the sources as in pair mode. Fold the round into the board (§6). Answer the questions addressed to you in your own submission for the next round, not in the synthesis. Add the round's log line: `Round R: accepted <tags>; missing <tags>; late <tags>`. That line is the acceptance record. Until you publish it, a collection is tentative, and you may repeat it after a crash.
7. **Open the next round.** Publish with `Round: R+1 <discussion|confirmation>, deadline <now + window>` and the marker `END-OF-TURN R+1 NEXT=ALL`. Then submit your own round R+1 file at once, before you read anyone else's. After a round closes, everyone may read all of its submissions, so nobody has less information than the coordinator.
8. **Tell the user** after each round, in a line or two: what settled, what is open, and who was missing.

To resume after a compaction, read your notes, then run `board.py status`. It shows the open round, its deadline and who has submitted. Run `collect` again for that round. There is no other state to recover.

## 6. Board shape

Each topic entry holds the current proposal and one line per distinct stance, with its holders:

```markdown
### D-03 Retry policy: open
- **Proposal:** exponential backoff, at most 5 attempts, then a dead-letter queue.
- **Support:** CLAUDE, CODEX, PI
- **Counter (GEMINI):** 5 attempts hides outages; cap at 3 and alert. (round 2)
- **Missing:** OPENCODE gave no stance in rounds 2–3.
```

- Group identical stances. Keep every minority stance, however small, in one sentence with its reason.
- A stance stands until its holder changes it. Your synthesis is never anyone's approval.
- A participant's correction of how the board describes it is applied as written. A factual claim inside a position stays attributed to its holder, and is not promoted to verified fact unless someone checked it.
- No transcripts. The submissions are the long form, and the board is the short one.

## 7. Closing, agreement and confirmation

**When to write the outcome.** Write it at the synthesis where any of these holds:
- every participant's latest close-out check says ready. A missing participant's check is not a ready;
- every item is agreed, or routed to an owner or to evidence-gathering;
- a complete round, responses plus synthesis, changed no substantive stance. A timeout is not a stall vote.

**What counts as agreed** (default rule, unanimity):
- A row is agreed only when every rostered participant, you included, has explicitly accepted its current decision. An earlier explicit acceptance of the same, unchanged decision counts. Silence never does.
- One dissent, or one missing acceptance, makes the row `needs-decision` for the user, with each stance named. It stays in the record. It just isn't agreement.
- If the user chose another rule at intake, apply that rule instead, and say in the outcome which rule applied.

Each outcome row records, besides the usual columns:

| Item | Decision | Category | Accepted by | Dissent (tag: reason) | No response |
|---|---|---|---|---|---|

**The confirmation round.** Publish the outcome with `Round: R confirmation, deadline …`. Each participant confirms that each row records the discussion faithfully, or dissents. Confirming the record is not the same as accepting a decision: a participant can confirm that its dissent is recorded correctly.
- A substantive amendment invalidates the confirmations of the rows it touches.
- Amended rows get one more confirmation round, and only those rows. Then finalize, labeling whatever is still unconfirmed. Don't keep re-asking.
- A missing confirmation is labeled as such. It neither adds nor removes agreement.

**Closing.** Mark the outcome final, publish with `DISCUSSION-CLOSED`, delete the `board.py` copy, and summarize for the user as in pair mode. Name the rows that need their decision first.

**If every counterpart is missing** at a deadline, write an outcome marked **incomplete**: it claims no agreement, and names who was missing in which round. Close, and tell the user.

## 8. Missing, late and relayed participants

- **Missing.** A participant with no submission at the deadline is recorded as missing for that round, and you tell the user. Never treat a miss as assent. Don't drop the participant either: only the user changes the roster. A roster change gets a reason in the log and takes effect at the next round.
- **Late.** `submit` refuses once the next round is open, or once the deadline has passed. A file written by hand after you collected is not part of that round. Note it in the log as late, and its author raises the points again in the current round. A late file never reopens a round.
- **Skipped rounds.** A participant that comes back after missing rounds waits with `board.py wait --after-round <its last round>`. That wakes it on whatever round is current, and it answers that round. It never replays the rounds it missed.
- **Relayed participants.** When the user pastes a relayed participant's reply, check that it names its tag and round. If the attribution is unclear, ask; don't guess. Store it with `board.py submit --tag <TAG>`, with `Relayed by user.` as its first line. The packet you give the user to paste back holds the round, the deadline, the changed topics and the questions for that participant, not the whole board. The relay burden is no reason to drop anyone; only the user decides that.

## 9. Shared prompt: the protocol section

Use this as §8–§10 of `prompt.md` in group mode. Fill every `<…>`, and keep it about this long.

```markdown
## 8. How the discussion works

**Participants.** <N> participants: <TAG (role), TAG (role), …> and **CLAUDE** (<role>). Claude is a full participant, and it also coordinates: it is the only one who publishes the board. Each of you writes your own submission every round.

**Rounds.** The board is `<abs dir>/board.md`. Round R is open while the board ends with `END-OF-TURN R NEXT=ALL`. Its `Round:` line gives the purpose (discussion or confirmation) and the deadline. In each open round:
1. Read the board and the `prompt.md` sections it needs.
2. Write your submission to a temporary file, and store it:
   `python3 <abs dir>/board.py submit --board <abs dir>/board.md --round <R> --tag <YOUR TAG> --from <temp file>`
   A submission is stored once and never changed. If you must add something, say it in the next round.
3. Wait for the next round:
   `python3 <abs dir>/board.py wait --board <abs dir>/board.md --after-round <R> --timeout 540`
   Exit 0 means a new round is open or the discussion is closed: read the board. Exit 124 means not yet: run it again. Keep each call inside your shell tool's own time limit. Give up after <budget> minutes of waiting in total: tell the user, and stop.

**Independence.** In round 1, don't read other participants' submissions before you have stored yours. Once a round has closed (the board shows a later round), all of its submissions in `<abs dir>/rounds/` are open to everyone.

**Deadlines.** A submission after the deadline, or after the next round opens, is refused and not counted. A missed round is recorded as missing, never as agreement. If you miss rounds, answer the current one; don't replay old ones.

**Agreement.** <Default: "A row is agreed only when every participant, Claude included, explicitly accepts it. Silence never counts. One dissent or missing acceptance sends the row to <owner> as needs-decision, with each stance named." Or the user's own rule.> There is no fixed number of rounds<; at most N rounds, including confirmation, as the user's ceiling>. Claude writes the outcome as soon as every participant's latest check says ready, every item is agreed or routed, or a full round changes no stance. The next round is then a confirmation round: confirm that each row records the discussion faithfully, or dissent.

`DISCUSSION-CLOSED` at the end of the board means the session is over: stop. You write only your own submissions and temporary files. Claude keeps private notes outside this folder: don't look for them.

## 9. Submission format

    # <TAG>, round <R>
    ### D-xx <title>
    Stance: accept | counter | dissent | answer. <Position, rationale, sources with read/run/inferred.>
    ### Corrections to the board
    <How the board misstates your position, if it does; Claude applies these as written.>
    ### Questions
    <Numbered, each naming its addressee.>
    Close-out check (<TAG>, round <R>): ready to close yes/no; still open: …

Cover every item the round asks for; skip none silently. In a confirmation round, write one line per outcome row: `confirm` or `dissent: <reason>`.

## 10. Start now

Follow your entry prompt's first step, then answer round <the open round>.
```

## 10. Entry prompt for each participant

One file per counterpart, `prompt-<TAG>.md`. Keep it short: everything shared lives in `prompt.md`.

```markdown
# Entry prompt for <TAG>: <topic> discussion

You are **<TAG>**, <role: the lens you bring>, one of <N> participants in a written discussion. <One sentence on why this lens matters for the topic.> Challenge any item, not only those of your lens.

**First, check that you can take part.** Run:
1. `python3 <abs dir>/board.py status --board <abs dir>/board.md`
2. Create and then delete a temporary file in `<abs dir>`.

If either fails, tell the user: "<TAG> cannot <read the board | write to the discussion folder>. <Access instruction from harnesses.md, e.g. restart with `--add-dir <abs dir>`, or start the session inside <abs dir>.>" Then stop.

<Harness note when known, e.g. "Give each shell call a time limit above 540 seconds, or lower `--timeout` to fit.">

**Then read** `<abs dir>/prompt.md` in full. It holds the context, the agenda, the rules and the protocol. Your tag for every command is `<TAG>`, and your wait budget is <budget> minutes.

**Start** with the open round on the board, and continue on your own until it says `DISCUSSION-CLOSED`.
```

For a relayed participant, don't write an entry prompt. Write a relay prompt the user pastes once: it embeds the extracts it needs in place of the reading list, the agenda, the rules from §8 without the `board.py` commands, the submission format, and an instruction to start each reply with `<TAG>, round <R>`.
