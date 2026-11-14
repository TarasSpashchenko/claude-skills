# Assessment of set B: group discussion board

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
| B-01 | `AGENTS.md:27`, `:22` | "extract this constant" sits in the old Development row and the new Constants row | structure | major | run-c | C | P,G | agreed |
| B-02 | `components/components.md:4` | "Every component folder exposes an `index.ts`": `src/components/Button/` has none | false | minor | inh | G | C,P | agreed |
| B-03 | `development/constants.md:14` vs `:5` | "Flags are booleans" against the Overview "string keys" | contradiction | major | inh | P | C,G | agreed |
| B-04 | `architecture/routing.md:4` | "Every route page is wrapped in `lazy()`": `grep -c 'lazy(' src/router.tsx` gives 0 | false | major | inh | G | P | agreed |
| B-05 | `development/api.md:9` | "`apiGet<T>(url)` never throws: it returns `{ data, error }`": it rejects with the `Response` (`src/api/client.ts:10-13`) | false | major | inh | P | C,G | agreed |

## Routing probe

| Task | Row | Guide | Verdict (strict / lenient) |
|---|---|---|---|
| R1 list of guides | Index (guide table) | `README.md` | correct / correct |
| R2 extract this constant | Development and Constants | `api.md` or `constants.md` | wrong / correct |
| R3 call an endpoint, own error message | API | `api.md` | wrong / wrong |
| R4 write a unit test | Testing | `testing.md` | wrong / wrong |

## Outcome

Status: **final**. Confirmed by CLAUDE, GPT and GEMINI in round 3. Decision rule: unanimity.

**Scorecard**

| M | Measure | Value |
|---|---|---|
| M1 | defects | 5 agreed: 4 major, 1 minor. Origin: run-c 1 (B-01), inh 4 |
| M3 | corrections against base | 3 |
| M4 | content lost | 0 |
| M5 | false statements added | 0 |
| M6 | routing probe | strict 1/4, lenient 2/4 |
| M8 | size | see `../facts/sizes.md` |

**M3 list:** 1 `FEATURE_FLAGS` from the `@/constants` barrel → `@/constants/featureFlags`; 2 `src/constants/limits.json` → `limits.ts`; 3 guide index `testing/tests.md` → `testing/testing.md`.

**Fix before merge (every major):** B-01, B-03, B-04, B-05. **Can wait:** B-02. **Verdict:** usable after named fixes.

**Goal question 2:** not shown; a paired delivery run after the fixes would show it.

## Log

- Round 1: accepted CLAUDE, GPT, GEMINI; missing none; late none.
- Round 2: accepted CLAUDE, GPT, GEMINI; missing none; late none.
- Round 3 (confirmation): accepted CLAUDE, GPT, GEMINI; missing none; late none. Outcome final.

DISCUSSION-CLOSED
