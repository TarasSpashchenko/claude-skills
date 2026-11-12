# Edit outcomes

Load this only when the discussion's outcome includes concrete edits to files: a spec, a PRD, a handbook, a config, code comments. Discussions that end in decisions, rankings, recommendations or questions for an owner don't need it.

Why it exists: edit discussions fail in two predictable ways.
- **Rework and bloat.** An opening turn that drafts exact text for every idea produces long proposals, many of which are later dropped or rewritten, and the board fills with competing drafts.
- **Drift on the way into the file.** Hand-copying agreed text into the target introduces small differences, and an anchor that occurs twice lands in the wrong place.

The register below, plus `board.py edits`, removes both. Everything here works the same in relay mode, except that the counterpart cannot run the script: you run it for both sides.

## 1. Intent first, exact text second

- With more than about eight edits in play, first agree on **intents**: one line per edit, giving the location, what changes, and what it traces to. Draft exact text only for intents both sides accept. Short lists can go straight to exact text.
- Draft the smallest change that achieves the intent. When another passage already states a rule, point to it instead of restating it: a restatement is a second copy that will drift.

## 2. The edit register

The board gets a `## Edit register` section. When it grows long, the outcome moves it to `outcome.md`. Each entry looks like this:

````markdown
#### E-07 Remove the offline-mode bullet — agreed
File: `docs/spec.md`
Traces to: D-02 (offline mode dropped)
~~~current
- Offline mode lets users edit without a network (FR-3).
~~~
~~~new
~~~
````

- **Operations:**
  - **Replace:** a `~~~current` block plus a `~~~new` block.
  - **Delete:** an empty `~~~new` block. A deleted whole line takes its line break with it.
  - **Insert:** an `~~~after` block instead of `~~~current`. It names whole lines, and `~~~new` holds the lines to add after them. A blank first line inside `~~~new` adds a blank line.
- **Status:** the last word of the heading, one of `proposed`, `countered`, `agreed` or `dropped`.
  - To counter, replace the text in place and add one line, `Was: …`, summarizing the other side's version. Delete that line once the entry is agreed.
  - A dropped entry keeps its ID and gets a one-line reason; delete its blocks. IDs are never reused or renumbered.
- **Anchors:**
  - Copy them from the file exactly, whitespace included.
  - Make them long enough to occur exactly once, and still once after the earlier entries apply: entries apply in register order.
  - If the text itself contains `~~~`, use `~~~~` fences.
- **Traces to:** the agenda item or new fact that forces the edit. An edit with nothing to trace to belongs under "Outside the agenda", not in the register.

## 3. Checks while discussing

Before publishing a turn that adds or changes entries, either side runs:

```bash
python3 <discussion folder>/board.py edits check --register <discussion folder>/board.md --root <folder the File: paths are relative to>
```

The check confirms that every entry that isn't dropped has a file, an anchor that is unique in order, and the right blocks. Its last line is the net effect, in the form `net: -84 words (added 120, removed 204) across 2 file(s); 0 problem(s)`. Quote that line in the turn. The outcome is written only once the check reports 0 problems.

## 4. Applying and verifying, after the discussion closes

1. **Apply.** Run `python3 <skill>/scripts/board.py edits apply --register <board.md or outcome.md> --root <root>`. It applies agreed entries only, and only if every one of them still checks out; otherwise it writes nothing. If the project requires changes to go through its own workflow (a documentation workflow, a review tool), apply through that instead.
2. **Verify.** Run `edits verify` with the same arguments. It confirms that every agreed text landed exactly and every replaced text is gone, however the edits were applied. Run it before any later polish or rewording, because it compares against the agreed texts.
3. **Search for leftovers.** Search the target files for the terms the change was meant to remove: old names, flags, qualifiers. Each hit is either intended, and you say why, or a missed edit.
4. **Report the net effect.** Give the `net:` line, set against the user's expected direction if they gave one (Phase 4).

## 5. Block for the counterpart prompt

Paste this into the prompt's §7, adjusting the paths:

> **Edits.** Agreed changes are recorded in the board's `## Edit register`. With more than about eight edits, agree one-line intents (location, change, `Traces to:`) before drafting exact text. Each entry has a heading `#### E-xx <title> — <proposed|countered|agreed|dropped>`, a `File:` line, a `Traces to:` line, and fenced `~~~current` (or `~~~after`) and `~~~new` blocks with text copied exactly from the file. An anchor must occur exactly once. To counter, replace the text in place and add a one-line `Was: …` note. Before you publish entries, run `python3 <abs dir>/board.py edits check --register <abs dir>/board.md --root <abs root>` and quote its `net:` line. Propose the smallest change that achieves the intent, and point to existing text instead of restating it.
