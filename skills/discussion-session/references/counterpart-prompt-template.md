# Counterpart prompt template

Fill in every `<…>` placeholder and delete the italic guidance. A counterpart with no prior context must be able to start and finish the discussion from this prompt without asking anyone anything.

Keep it lean:
- Summarize instead of restating, point to files, and state each rule once.
- Keep the protocol and turn format (§8–§9) to about 600 words. The rest scales with the agenda.
- Use agenda tiers only for agendas of more than about six items.
- Include only the outcome categories the user needs.
- Keep it as long as the topic needs, and no longer: the agenda and the protocol carry most of the weight.

Adapt it per case:
- **Private notes:** never mention where Claude's private notes are.
- **Relay mode:** drop the note-privacy sentence and every `board.py` command. The user carries the turns.
- **An expected direction from the user** (simpler, cheaper, …): state it in §2 as a hypothesis to test, not a quota.
- **Edits to files:** paste the block from `edit-outcomes.md` §5 into §7.
- **Group mode:** this template gives the shared `prompt.md`. Write §1 for "one of several participants", with each participant's own role in its entry prompt, not here. Replace §8–§10 with `group-mode.md` §9, and write one entry prompt per counterpart from `group-mode.md` §10.

---

# Prompt for <counterpart role>: <topic> discussion

Run this in <where: e.g. "an opencode / pi / Codex session at the repository root `/abs/root`">. Paths below are relative to that root unless they are absolute. <Define short aliases for long paths, e.g. "`{spec}` means `docs/specs/payments/`".>

## 1. Your role

You are <role and expertise, e.g. "an independent senior backend architect with deep experience in caching and distributed systems">. You were not involved in <the work under discussion>.

You will hold a written, turn-based discussion with **Claude**, <Claude's role, e.g. "the author of the design and keeper of its decision log">, on a shared discussion board. Your job is to analyze, challenge and settle <the open questions / options / assumptions>.

Be direct, evidence-based and concise. Disagree where you have reason to, and agree plainly where you don't. Don't pad.

## 2. Goal and why it matters

<What the discussion must produce, and what happens with it next (e.g. "feeds the review session on <date>", "decides the caching approach before implementation starts").> <If the user expects a direction: "The owner expects <X>. Treat that as a hypothesis: find every real <gain>, invent none, and say plainly where it lands elsewhere or doesn't hold.">

## 3. Context

<A summary dense enough that the counterpart understands the situation before opening any file: product or system, current state, constraints, key decisions already made, and who owns which decisions.> <Optional: "**Facts to verify** (Claude's reading, not conclusions): …", with anchors.>

## 4. Read first

<An ordered list of files with what to look for in each. Mark which sources are authoritative. In relay mode, replace this section with the needed extracts, quoted.>

1. `<path>`: <why, which sections>
2. …

## 5. Scope and evidence

- **In scope:** <…>
- **Out of scope:** <…> Say so in one line, and don't discuss it.
- **Fixed decisions, not to be reopened:** <…> If you believe one is wrong, name it once as a recommendation for <owner>, then move on.
- **Not your call:** <e.g. legal opinions, technology choices, product priorities>.
- **Traceability.** Every point you make answers an agenda item or the new fact under discussion; say which.
  - Something that only restates what is already settled elsewhere is not a proposal: point to where it is held.
  - A real issue outside the question goes to the board's "Outside the agenda" list, one line each with a proposed owner. It does not go into the topics.
- **Evidence.**
  - Cite sources as <citation form, e.g. "file:line" or "doc §section">.
  - Keep facts apart from opinions, and tag each fact *read* (read in a source), *run* (observed by running or measuring) or *inferred*.
  - A claim that something is absent or universal ("no X", "never", "only") names the search behind it.

## 6. Agenda

*Give each item an ID, a concrete question, the current position with its source, and what is open. Use tiers only for agendas of more than about six items: Tier 1 must be covered in the first turn, and Tier 2 only where the counterpart disagrees. Otherwise, list the items without tiers.*

### Tier 1

- **D-01 <title>.** <Question.> Current position: <…> (<source>). Open: <…>.
- …

### Tier 2

- **D-xx <title>.** …

You may add up to <2–5> new topics, only if they are in scope and material.

## 7. Outcome the user expects

<The user's outcome requirements, verbatim or tightly paraphrased: the format, the categories, the owners, and what "done" means.>

Outcome categories: <the user's own, or a subset of: agreed-as-is · agreed-change · needs-decision · needs-evidence · follow-up (outside this scope, with an owner and a trigger) · parked (not now, with a revisit condition)>. <If the user expects a direction: "The outcome includes one line measuring the result against <X>.">

<If the outcome is edits to files: paste the block from `edit-outcomes.md` §5 here.>

There is no fixed number of turns. Claude writes the outcome summary at its turn as soon as the closing rules in §8 are met. At your next turn, you confirm each row or dissent from it.

## 8. How the discussion works

**The board** is `<abs path>/board.md`. It is an editable board, not a log:
- On your own turn, you may edit any part of it. Fold settled points into the topic entries and delete superseded text.
- Keep the topic IDs, decisions, owners, and both positions on anything still open. A position is a sentence or two: when you counter a drafted text, replace it in place and note in one line what the other side had.
- Settle substance before polishing wording.
- Keep it concise, with no turn transcripts.

You write only `board.md`, plus temporary files. Claude keeps private notes outside this folder. Don't look for them or read them: they hold Claude's positions, and your value here is an independent view.

**Turns.** <Who opens.> The two of you alternate, and you edit the board only during your own turn.

There is **no fixed number of turns**: the discussion lasts while turns still settle things. Every turn ends with a close-out check: one line saying "ready to close: yes or no" and what is still open that another turn could settle.

Claude writes the outcome as soon as any of these holds:
- both sides' latest checks say ready;
- every item is agreed, or has been given to an owner or to evidence-gathering;
- a full round passed with no position changing.

Your next turn then confirms or disputes each outcome row. If you raise a disagreement that another turn can settle, the discussion continues; otherwise it is recorded as dissent and Claude closes. <If the user set a maximum, add it after the closing rules: "At the latest, Claude writes the outcome by turn N, the user's maximum. If something that another turn could settle is still open then, Claude asks the user whether to continue." Never turn this into a fixed schedule.>

**Markers.**
- Once the first turn is published, the board always ends with exactly one marker line, alone on the last line. Until then, the board has no marker.
- <Opener rule: "You open, so your turns are odd (1, 3, 5, …) and Claude's are even." Or the reverse.> After you publish turn N, the last line is `END-OF-TURN N NEXT=CLAUDE`. Claude's turns end with `END-OF-TURN <N> NEXT=<TAG>`.
- `DISCUSSION-CLOSED` means the session is over: stop.
- Mention markers elsewhere only inline in prose, never alone on a line.

**Publishing a turn.** Write the whole new board, without a marker, to a temporary file in `<abs dir>`, then run:

```bash
python3 <abs dir>/board.py publish --board <abs dir>/board.md --from <temp file> --expect-last '<Claude's last marker, or none>' --marker 'END-OF-TURN <N> NEXT=CLAUDE'
```

It refuses if the board changed under you, and it swaps the file in atomically. Without Python, append the marker to the temporary file yourself and `mv` it over `board.md`. Never append partial text to the board.

**Waiting for Claude.** After publishing turn N, wait for turn N+1:

```bash
python3 <abs dir>/board.py wait --board <abs dir>/board.md --marker 'END-OF-TURN <N+1> NEXT=<TAG>' --timeout 540
```

- Exit 0 means Claude's turn is in, or the session is closed: read the board.
- Exit 124 means no turn yet: run it again. Each run lasts at most 9 minutes.
- If your shell tool has its own time limit, keep each wait inside it: raise the limit, or lower `--timeout` to fit. <For a Claude Code counterpart: "Give the Bash call `timeout: 600000`; its default is 2 minutes.">
- Without Python, use `timeout 540 bash -c 'until tail -n 1 <abs dir>/board.md | grep -qxE "END-OF-TURN <N+1> NEXT=<TAG>|DISCUSSION-CLOSED"; do sleep 30; done'`.
- Give up after 120 minutes of waiting for one turn: tell the user, and stop.
- If you cannot run commands at all, end your turn by telling the user "Turn N written", and continue when they tell you Claude has replied.

## 9. Turn format

Write each topic entry on the board like this:

```markdown
### D-xx <title>: <status: agreed | open | needs-decision | needs-evidence | follow-up | parked>
- **<Your tag>:** position, with its rationale and the sources it cites
- **Claude:** position (filled in by Claude)
- **Proposal / agreed outcome:** concrete text, decision, test or owner
```

Also keep up to date:
- the status table at the top;
- "Outside the agenda": one line per issue, with a proposed owner;
- a "Questions for Claude" list, numbered and answerable;
- one log line for each turn;
- your close-out check, as the last line before the marker: `Close-out check (<TAG>, turn N): ready to close yes/no; still open: …`.

## 10. Start now

Read §4. Then write Turn 1 on the board:
- cover every Tier 1 item;
- add Tier 2 items only where you disagree;
- add your questions for Claude.

End it with your close-out check, and publish it with the `END-OF-TURN 1 NEXT=CLAUDE` marker. Tell the user "Turn 1 written", then start waiting (§8) and continue on your own until the board says `DISCUSSION-CLOSED`. <If Claude opens: "Claude's Turn 1 is already on the board. Read it, write Turn 2 responding to it (covering every Tier 1 item), and publish with `END-OF-TURN 2 NEXT=CLAUDE`.">
