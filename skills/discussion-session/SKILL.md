---
name: discussion-session
description: >-
  Run a focused, turn-based written discussion between Claude and one counterpart, or a group of up to
  four (five participants at most, Claude included): other AI agents or chat sessions (Codex, pi,
  opencode, Gemini CLI, Copilot CLI, Aider, another Claude Code instance, ChatGPT, ...) or human
  experts, on a shared Markdown board. Claude writes a self-contained prompt for each participant,
  runs turns or rounds on the board, and closes with an agreed outcome. Use it whenever the user wants
  to discuss, debate, challenge, pre-review, negotiate, settle open questions or agree document
  changes WITH other agents, models, tool sessions or experts, e.g. "discuss this with the agent in
  opencode", "prepare a prompt so the SME can go through the open questions with you", "review my
  changes with Codex", "get Codex, Gemini and pi to debate this with you", even if they never say
  "discussion board". Not for chatting with the user alone, party-mode persona simulations, or
  parallel subagent reviews.
---

# Discussion session

You run a written discussion with a **counterpart** through a shared Markdown **board**. The counterpart can be any agent harness (pi, opencode, Codex, Gemini CLI, Aider, another Claude Code session, …), a chat app, or a person; nothing here depends on a particular tool. The user brings the topic, all their material, and their expectations for the outcome. You prepare a prompt that lets the counterpart work without any further help. The user starts the counterpart and tells you when it is ready. Then the two of you take turns on the board until you agree an outcome.

With two to four counterparts at once, the discussion runs in **group mode** (`references/group-mode.md`): everyone answers each round in parallel, you take part as a full participant, and you also coordinate the board. Everything below describes pair mode, which group mode builds on.

Why it works this way:
- **A file board.** It persists, the user can watch it live, and it survives a compaction of your context.
- **End-of-turn markers.** Each side can wait for the other with no human relaying messages.
- **Consolidation.** Folding settled text into short topic entries keeps the board readable instead of letting it grow into a transcript.
- **A confirmed outcome.** The final summary is something both sides signed off on, not your private conclusion.

Four phases follow. Each ends at a clear hand-off point.

## Phase 1 — Intake

Collect what you need, inferring as much as you can from the conversation first. Ask once, in a single batch, for whatever is still missing:

1. **Topic and goal.** What should the discussion decide, settle or clarify, and why now?
2. **Material.** Everything the user has: file paths, pasted text, links, earlier decisions. Ask which sources are authoritative.
3. **Counterpart.**
   - How many. One counterpart is pair mode, which the rest of this file describes. Two to four is group mode: read `references/group-mode.md` now, because it adds intake questions about the roster, roles, timing and the decision rule. The cap is five participants in total, you included. If the user names more, ask which to keep.
   - Who or what it is: the harness or app (pi, opencode, Codex, Gemini CLI, Aider, Claude Code, a chat web app, or a human), and the role or expertise it should take.
   - Where it runs, and whether it can read and write files in a folder you share.
   - Whether it can run shell commands, ideally with Python 3 for `board.py`.
   - A short uppercase tag for markers, such as `SME`, `CODEX` or `REVIEWER`. Your own tag is `CLAUDE`.
4. **Outcome requirements.** What the user wants at the end:
   - the shape of the result: a decision record, a resolution table, a ranked list, edits to apply, questions for a decision-maker;
   - the outcome categories;
   - who owns which decisions.

   If the user names none, propose a default from the Phase 4 outcome table. Don't add categories or fields beyond what the user asked for unless the outcome really needs them; every extra field lengthens the prompt and the outcome.

   Two cases need more:
   - **An expected direction.** The user may expect the result to go one way: simpler, cheaper, shorter, fewer steps. Treat that as a hypothesis to test, not a target. The prompt states it and asks for real gains only, and the outcome reports how far it held, with a measure where one exists. A target invites both sides to manufacture gains; a measured line keeps the report honest even when the answer disappoints.
   - **Edits to files.** If the result is changes to documents or other files, read `references/edit-outcomes.md` now. Its register format, checks and apply step prevent rework and transcription drift. Other discussions don't need it.
5. **Scope guardrails.**
   - What is in and out of scope.
   - Which decisions are fixed and must not be reopened.
   - Who has authority over what.
   - Forbidden areas, for example legal advice or technology choices.
6. **Opener and length.**
   - The counterpart opens by default, so its first view is independent of yours.
   - Don't fix the number of turns in advance. The discussion lasts as long as turns still settle things, and ends by the closing rules in Phase 3.
   - If the user states a maximum, treat it as a ceiling, not a target or a schedule.
     - The closing rules still decide when the outcome is written; the maximum only says "at the latest".
     - Never present the ceiling as the plan ("Claude writes the outcome at Turn 3").
     - If you reach it while a disagreement that another turn could settle is still open, ask the user whether to continue.
7. **Mode.**
   - **Automatic:** both sides watch the board file. Use it when the counterpart shares the folder and can poll.
   - **Relay:** the user carries turns between you. Use it when the counterpart cannot reach the files, such as a web chat.
8. **Location.**
   - Default: a `discussion-<slug>/` folder next to the main material, or else `./discussions/<slug>/`.
   - Use absolute paths in the prompt when the counterpart runs elsewhere.

## Phase 2 — Prepare

1. **Study the material.** For large documents, send subagents to extract what matters rather than loading everything into your context. If earlier discussions on the same material exist, point the prompt at their outcome files instead of summarizing them again.
2. **Build the agenda.**
   - Give each item a stable ID (`D-01`, `D-02`, …) and state it as a concrete question, with the current position and what is fixed versus open.
   - Agenda items are the questions the discussion must settle, not sections of the deliverable. A ranking, a list of questions for an owner or a table of contents is assembled from the items' answers in the outcome. Slots that restate the deliverable crowd out the substantive questions, such as whether a premise holds, which data is missing, or what an option really costs.
   - Split the items into tiers only when the agenda is long (more than about six items). Then Tier 1 items must be covered, and Tier 2 items are covered only if the counterpart disagrees.
   - Facts you have already established, such as where the topic touches the material or what the sources say, can go into the prompt as *facts to verify*, with their anchors. They save the counterpart a search, and labelling them "to verify" keeps its check independent. Keep them to what the sources say. A figure you derived, or a reading that implies an answer, is a position, and it would anchor the counterpart before it forms its own view.
   - Note your own positions privately, including what you would concede. Positions stay out of the prompt even when facts go in.
3. **Create the files.**
   - In the discussion folder, which the counterpart shares:
     - `prompt.md`: the counterpart prompt. Follow `references/counterpart-prompt-template.md`.
     - `board.md`: the discussion board. Follow `references/board-template.md`. It starts with no marker line.
     - In automatic mode, `board.py`: a copy of `scripts/board.py`. The counterpart publishes and waits with it, so neither side hand-builds polling loops. The copy also keeps the prompt from pointing at this skill's folder, which sits next to your private notes. Delete the copy when the discussion closes.
   - Outside the discussion folder: your private notes, at `~/.claude/discussion-notes/<slug>.md`.
     - Keep them out of the counterpart's view. They hold your positions, and a counterpart that read them would lose the independent view you brought it in for.
     - When the counterpart has file access, the prompt also tells it not to look for them, in case it can browse that far. In relay mode the counterpart can't see files, so leave the sentence out.
     - Never say where they are, and never describe the folders around the discussion folder; that would point the counterpart at them.
     - The notes hold:
     - the mode, the tags and the marker for each turn;
     - your exact watcher command;
     - your per-item positions, separating what is fixed from what you can concede;
     - the outcome requirements;
     - the current turn state and the closing check;
     - the paths to the board and the prompt.

     If your context gets compacted, this file is how you resume, so keep it current every turn.
4. **Hold the prompt to this bar: self-contained and self-sufficient.** A counterpart with zero prior context should be able to do excellent work from it alone. That means it states:
   - the role;
   - the goal and why it matters;
   - a context summary;
   - the files to read, in order and with what to look for. In relay mode, embed the extracts instead, because the counterpart cannot open files.
   - the agenda;
   - the scope guardrails and who decides what, including the rule that every point traces to an agenda item or to a new fact the discussion is about; anything else goes to the board's "Outside the agenda" list;
   - the evidence standard:
     - cite sources, and separate facts from opinions;
     - tag how each fact was established: read in a source, observed by running or measuring something, or inferred;
     - a claim that something is absent or universal ("no X", "never", "only") names the search behind it. A single counterexample sinks such a claim, so it needs the most support.
   - the user's outcome requirements;
   - the full board protocol;
   - the turn format;
   - exactly how to start.

   Self-contained doesn't mean long:
   - Summarize the context, and point to files instead of restating them.
   - State each rule once.
   - Cut anything the counterpart doesn't need to act.

   As a rough guide:
   - The protocol and turn format should take no more than about 600 words.
   - The rest scales with the agenda.
   - A short topic usually needs 1,000 to 1,500 words in all.
   - Relay prompts should be more compact still, because the user pastes them by hand.

   Then reread the prompt *as the counterpart*. Could you begin without asking anything? Fill every gap you find, then trim whatever repeats.
5. **If you open,** write your Turn 1 now. Cover every Tier 1 item with your position and the questions you want answered, and publish it with `--expect-last none` and the marker `END-OF-TURN 1 NEXT=<TAG>`. Where you can, put your proposal in the shape of the outcome the user asked for, such as a draft table or list. The counterpart can then confirm or amend it row by row, which shortens the road to the outcome. The counterpart can start the moment it is launched.
6. **Check that the counterpart can run the protocol from where it starts.**
   - Agent sandboxes usually allow writes only inside the agent's own working directory.
   - When you can, put the discussion folder inside it.
   - Otherwise, tell the user how to grant access when starting the counterpart. `references/harnesses.md` lists the access flag and shell time limit of common harnesses (Codex, Claude Code, Copilot CLI, opencode, pi, Gemini CLI), as read in their docs. For another harness, or if a flag may have changed, check the installed tool's `--help` or docs before quoting it, or ask the user to start it inside the discussion folder.
   - Give every command in the prompt absolute paths. The counterpart may start in another folder.
   - Its shell tool may cut commands off before the 9-minute wait ends. Claude Code's Bash tool, for example, defaults to 2 minutes. Tell it to raise that limit, or set a shorter `--timeout`.
7. **Hand off to the user.**
   - Give the paths and a one-line instruction to paste into the counterpart's session, for example: `Read and follow /abs/path/discussion-x/prompt.md`. In group mode, give one such line per counterpart, each pointing at its own entry prompt.
   - Ask the user to tell you when the counterpart is ready, meaning it has written its first turn or is waiting for yours.
   - **Never start the counterpart yourself.** That includes headless modes (`codex exec`, `claude -p`, `opencode run`, …) and holds even when the user tells you to work autonomously.
     - The counterpart runs under the user's own account, sandbox and approvals, where they can watch and steer it.
     - Started from your shell, it inherits your permissions instead. When its own sandbox can't start inside yours, the only way to run it is to bypass that sandbox.
     - Autonomy covers your decisions inside the discussion. Starting the other side stays the user's step.
   - **Stop here.** Don't start the discussion or a watcher until the user says the counterpart is ready. They may want to adjust the prompt first.

## Phase 3 — Discuss

In group mode, Phases 3 and 4 run as rounds: follow `group-mode.md` §5–§8 instead of the turn mechanics below. Step 3's checks still apply: verify claims, answer questions, test proposals against the question.

When the user says the counterpart is ready:

1. **Check the board's state** with `python3 <skill>/scripts/board.py status --board <board.md>`.
   - If the counterpart's marker is already the last line, take your turn now.
   - Otherwise, including when your own Turn 1 is waiting for its reply, start the watcher.
2. **Start the watcher.** Run this Bash command with `run_in_background: true` and `timeout: 7200000`. It re-invokes you when it exits:

   ```bash
   python3 <skill>/scripts/board.py wait --board /abs/path/board.md \
     --marker 'END-OF-TURN 3 NEXT=CLAUDE' --timeout 7100 --settle 10
   ```

   - It exits 0 once the board ends with that marker or with `DISCUSSION-CLOSED`, and 124 on timeout.
   - The settle pause lets a writer that doesn't rename atomically finish.
   - If it times out, start it once more and tell the user.
   - Don't poll in the foreground; the background task notifies you.
3. **Take your turn:**
   1. **Read the whole board.** Check the counterpart's factual claims against the sources before you agree with them, using subagents when a check is heavy. Agreeing with something false is the most expensive mistake in this process.
      - Check absence and universal claims hardest, yours included: one counterexample sinks them.
      - When a check settles a disputed fact, add it to the board as a fact with its anchor and how you established it (read, run or inferred), so the counterpart can check you back.
   2. **Respond to each item** with *accept*, *counter*, *answer* or *route to owner*.
      - Concede quickly and plainly when the counterpart is right.
      - Push back with evidence when it is not.
      - Answer every question it asked.
      - Give items that only an authority can settle (the user, a product owner, counsel, a playtest) to that owner instead of spending turns on them.
      - Test every proposal, the counterpart's and yours, against the question. A proposal that only restates something already settled elsewhere is dropped, with a pointer to where it is held. A real issue that predates the question or lies outside it goes to "Outside the agenda", with a proposed owner. Both are easy to mistake for thoroughness, and both make the outcome longer without answering anything.
   3. **Consolidate the board.**
      - Fold the counterpart's turn into the topic entries and delete superseded text.
      - Keep the IDs, decisions, owners and *both* positions on anything still open. "Both positions" means each side's position in a sentence or two, not two full drafts. When you counter a drafted text, replace it in place and keep a one-line note of what the other side had.
      - Settle substance before wording: don't draft exact text for a point whose substance is still open, because it will be rewritten.
      - Update the status table.
      - Answer the counterpart's questions where they belong.
      - Keep the log to one line per turn.
   4. **Publish atomically.** Write the full new board to a scratch file, then run:

      ```bash
      python3 <skill>/scripts/board.py publish --board <board.md> --from <draft.md> \
        --expect-last 'END-OF-TURN 1 NEXT=CLAUDE' --marker 'END-OF-TURN 2 NEXT=SME'
      ```

      The script refuses to publish if the board's last line is not the marker you expected, which means someone edited it concurrently. It writes through a temporary file in the same folder and a rename, and it ends the board with your marker. For an opening turn, use `--expect-last none`. If your turn changes an edit register, run `edits check` first (`references/edit-outcomes.md`).
   5. **End with a close-out check.** One line: ready to close yes or no, and what is still open that another turn could settle. The counterpart does the same every turn.
   6. **Update your notes,** then start the watcher for the counterpart's next marker, which is always the turn number you just published plus one.
4. **Stay focused.**
   - Raise no new topics beyond the agenda, unless they are in scope and few.
   - Don't argue for its own sake.
   - Don't relitigate fixed decisions.
   - When the user tells you to stay focused, take that as license to close items rather than polish them.
5. **Decide when to close, as you go.** There is no fixed count; turns continue while they make progress. Write the outcome (Phase 4) at your turn as soon as any of these holds:
   - both sides' latest close-out checks say ready;
   - every item is agreed, or has been given to an owner or to evidence-gathering;
   - a full round passed with no position changing. That is a stall: another turn won't help, so record the remaining dissent.

   The counterpart may propose closing at any turn. Markers simply keep counting (`END-OF-TURN 6 NEXT=SME`, `END-OF-TURN 7 NEXT=CLAUDE`, …).
6. **Keep the user informed.** After each of your turns, tell the user in a line or two where things stand: what got settled, and what is still open.

## Phase 4 — Outcome and close

1. **Write the outcome at the turn where the closing rules are met** (Phase 3). Put it in the board's **Outcome** section, shaped by the user's requirements. If they gave none, use one row per agenda item:

   | Item | Outcome | Owner | Action |
   |---|---|---|---|

   Use these outcome categories unless the user defined their own:

   | Category | Meaning |
   |---|---|
   | agreed-as-is | No change |
   | agreed-change | The exact text or decision to apply is spelled out |
   | needs-decision | The owner is named, and both positions are recorded |
   | needs-evidence | A test or measure, with its decision rule |
   | follow-up | Real work outside this discussion's scope, with an owner and a trigger for when it is picked up |
   | parked | Deliberately not pursued now, with a reason and a revisit condition |

   - Put exact texts to apply, and any new decisions, under the table. For edits to files, the edit register is that list; run `edits check` and write the outcome only when it reports 0 problems.
   - Route every "Outside the agenda" entry to a row, as `follow-up`, `parked` or dropped with a reason, so nothing raised is silently lost.
   - If the user expected a direction (Phase 1), add one line measuring the result against it, such as words, steps, cost or risks added versus removed. Say plainly when the expectation held only partly.
   - Ask the counterpart to confirm each row or dissent at its next turn.
   - If the outcome is long, also write it to a separate `outcome.md` the user can hand on, and keep the board's copy short.
2. **After the counterpart's confirmation turn:**
   1. Adopt any correction you accept.
      - If the counterpart raises a disagreement that another turn could settle, the discussion continues and you rewrite the outcome later.
      - Otherwise, record it as dissent with both positions.
   2. Mark the outcome final. If the confirmation turn changed nothing you object to, this is the whole job: flip the status, add a log line, and close. Don't rewrite the board.
   3. Publish the board with the marker `DISCUSSION-CLOSED`, so the counterpart's polling stops cleanly. Then delete the copied `board.py` from the discussion folder, and record the close in your notes.
   4. Summarize for the user, measured against their outcome requirements:
      - what was agreed;
      - what needs their decision;
      - remaining dissent;
      - the measured line, if they expected a direction;
      - next steps.

      Offer to apply the agreed changes, or apply them now if the user already asked for that.
3. **Applying edits.** When the outcome is edits to files, apply and verify them as `references/edit-outcomes.md` §4 describes. In short:
   - apply only agreed entries, all or nothing;
   - verify that each text landed exactly;
   - search for leftovers of what the change removed;
   - report the net effect.

   If the project requires its own change workflow, apply through it, then verify.

## Board mechanics

These rules are for pair mode; group mode's are in `group-mode.md`. They are written into both the prompt and the board, so both sides follow the same rules:

- **Markers.**
  - Format: `END-OF-TURN <N> NEXT=<TAG>` in ASCII, alone on the board's last line, matched as a whole line (`grep -qx`).
  - The turn number makes each marker unique, so neither side can mistake an old turn for a new one.
  - Mention markers elsewhere only inline in prose, never alone on a line.
  - `DISCUSSION-CLOSED` ends the session.
- **One marker line,** at the end of the board, replaced every turn.
- **Atomic writes.** Write a full copy to a temporary file in the same folder, then rename it over `board.md`. The other side then never reads a half-written board. `board.py publish` does this, and checks the expected last marker too. The counterpart uses the copy in the discussion folder; a plain `mv` of a temporary file is the fallback when it has no Python.
- **Edit only on your own turn.** Either side may restructure the board then, but must keep IDs, decisions, owners and open dissent.
- **Counterpart polling.**
  - The counterpart waits with `python3 <abs dir>/board.py wait --board <abs dir>/board.md --marker '<next marker>' --timeout 540`, inside its shell tool's own time limit. Each wait lasts at most 9 minutes, because many agent sandboxes kill longer commands, and it repeats the wait while the result is exit 124. A shell `until grep` loop wrapped in `timeout 540` is the fallback.
  - It gives up after 120 minutes and tells the user.
  - If it cannot run shell commands at all, it ends its turn by telling the user "Turn N written" and waits to be told you have replied. That is a graceful fallback to relay.
- **No fixed length.** Each turn ends with a close-out check, and the closing rules decide when the outcome is written.
- **Write access.** The counterpart writes only `board.md`, plus temporary files. It doesn't look for Claude's private notes.

## Relay mode

In group mode, relay is set per participant (`group-mode.md` §8). For a pair discussion, use relay mode when the counterpart cannot reach the folder, for example a web chat:
- The prompt embeds all the context and the agenda. Each turn's text ends with its marker line, exactly as in automatic mode.
- The user pastes the counterpart's turn to you. You record it on the board, take your turn, and give the user your turn text to paste back. Never send the whole board, only the latest state of each topic.
- The board stays the single record, and the outcome works the same way.

## Resuming after a compaction

1. Read your notes at `~/.claude/discussion-notes/<slug>.md`. If you don't know the slug, list that folder.
2. Run `board.py status`.
3. If it is the counterpart's turn, restart the watcher. If it is yours, take it.

Never assume the counterpart has stopped: check the board.

## Files in this skill

- `references/counterpart-prompt-template.md`: the structure and wording of the counterpart prompt, with the publishing and waiting commands. Read it in Phase 2.
- `references/board-template.md`: the initial board skeleton and its rules. Read it in Phase 2.
- `references/edit-outcomes.md`: the edit register, its checks, and how to apply and verify edits. Read it only when the outcome is edits to files.
- `references/group-mode.md`: the group protocol for two to four counterparts, with the shared prompt's protocol section and the entry prompt per participant. Read it at intake when there is more than one counterpart.
- `references/harnesses.md`: access flags and shell limits of common agent harnesses. Read it in Phase 2 when a counterpart is an agent harness.
- `scripts/board.py`: standard library only.
  - `status`: whose turn it is; in group mode, also the round, its deadline and who has submitted.
  - `publish`: an atomic, marker-checked turn hand-off. In group mode it also checks the roster and the cap.
  - `wait`: a bounded wait for a marker, or with `--after-round R` for any later group round.
  - `submit`, `collect`: group mode only. They store a participant's round submission exactly once, and wait for every rostered submission or the deadline.
  - `edits check|apply|verify`: the edit register, for edit outcomes only.
