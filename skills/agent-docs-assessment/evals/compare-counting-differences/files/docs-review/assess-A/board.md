# Assessment of set A: group discussion board

Roster: CLAUDE GPT GEMINI
Round: closed

Participants: **CLAUDE** (structure, routing, internal consistency; coordinates), **GPT** (delivery-agent lens), **GEMINI** (source-accuracy lens). Prompt: `prompt.md`. Submissions: `rounds/<R>/<TAG>.md`.

## Status

| Item | Status |
|---|---|
| D-01 to D-06 | final |

## Defect register

| ID | Where | Defect | Kind | Severity | Origin | Found by | Reproduced by | Status |
|---|---|---|---|---|---|---|---|---|
| A-01 | `AGENTS.md:27`, `:22` | "extract this constant" sits in the old Development row (P0 `api.md`) and the new Constants row (P0 `constants.md`) | structure | major | run-c | C | P,G | agreed |
| A-02 | `components/components.md:4` | "Every component folder exposes an `index.ts`": `src/components/Button/` has no `index.ts` (`ls src/components/Button`) | false | minor | inh | G | C | needs-decision (GPT: a convention, not a defect) |
| A-03 | `development/constants.md:14` vs `:5` | "Flags are booleans: `if (FEATURE_FLAGS.WISHLIST)`" against the Overview "string keys"; `src/constants/featureFlags.ts:2-3` | contradiction | major | run-c | P | C,G | agreed |
| A-04 | `testing/testing.md:4` | "Run them with `npm run test:unit`": `package.json:10` has `test`, no `test:unit` | broken | major | inh | C | G | agreed |
| A-05 | `development/api.md:18` | "`apiStream(url)` returns a `ReadableStream`; call `getReader()` on it": it returns the reader (`src/api/client.ts:17,23-24`) | false | major | run | P | G | agreed |
| A-06 | `standards/git-workflow.md:11` vs `:10` | the example subject is 80 characters, against the guide's own "under 72 characters" | contradiction | minor | run | C | P | agreed |

## Routing probe

| Task | Row | Guide | Verdict (strict / lenient) |
|---|---|---|---|
| R1 list of guides | Index (guide table) | `README.md` | correct / correct |
| R2 extract this constant | Development and Constants | `api.md` or `constants.md` | wrong / correct |
| R3 call an endpoint, own error message | API | `api.md` | correct / correct |
| R4 write a unit test | Testing | `testing.md` | wrong / wrong |

## Outcome

Status: **final**. Confirmed by CLAUDE, GPT and GEMINI in round 3. Decision rule: unanimity.

**Scorecard**

| M | Measure | Value |
|---|---|---|
| M1 | defects | 5 agreed: 4 major, 1 minor; plus A-02 (minor, needs-decision). Origin of the 5: run 2 (A-05, A-06), run-c 2 (A-01, A-03), inh 1 (A-04) |
| M3 | corrections against base | 3 |
| M4 | content lost | 0 |
| M5 | false statements added | 1 (A-05) |
| M6 | routing probe | strict 2/4, lenient 3/4 |
| M8 | size | see `../facts/sizes.md` |

**M3 list:** 1 `apiGet` "never throws, returns `{ data, error }`" → rejects with the `Response`; 2 every route page in `lazy()` → static imports; 3 constants: `FEATURE_FLAGS` from the barrel and `limits.json` → the real modules.

**Fix before merge (every major and every run-made minor):** A-01, A-03, A-04, A-05, A-06. **Owner decision:** A-02. **Verdict:** usable after named fixes.

**Goal question 2:** not shown; a paired delivery run after the fixes would show it.

## Log

- Round 1: accepted CLAUDE, GPT, GEMINI; missing none; late none.
- Round 2: accepted CLAUDE, GPT, GEMINI; missing none; late none.
- Round 3 (confirmation): accepted CLAUDE, GPT, GEMINI; missing none; late none. Outcome final.

DISCUSSION-CLOSED
