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
| A-02 | `components/components.md:13` | "Every component folder exposes an `index.ts`": `src/components/Button/` has none | false | minor | inh | G | C,P | agreed |
| A-03 | `development/constants.md:14` vs `:5` | "Flags are booleans" against the new Overview "string keys" (`src/constants/featureFlags.ts:2-3`) | contradiction | major | run-c | P | C,G | agreed |
| A-04 | `testing/testing.md:4` | "Run them with `npm run test:unit`": no such script (`package.json:10`) | broken | major | inh | C | G | agreed |
| A-05 | `development/api.md:18` | "`apiStream(url)` returns a `ReadableStream`; call `getReader()` on it": it returns the reader (`src/api/client.ts:17,23-24`) | false | major | run | P | G | agreed |
| A-06 | `standards/git-workflow.md:11` vs `:10` | example subject of 80 characters under the guide's own 72-character rule | contradiction | minor | run | C | P | agreed |
| A-07 | `development/api.md:46` | the Examples fence for `uploadFile` stops after 20 lines, inside the function's last `if` block: the closing brace, `return result` and the function's end are missing (`src/api/upload.ts:28-30`) | structure | minor | run | G | C | agreed |
| A-08 | `components/components.md:9` | `src/components/button/Button.tsx`: the folder is `src/components/Button/` (resolves only on a case-insensitive file system) | broken | minor | run | G | P | agreed |

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
| M1 | defects | 8 agreed: 4 major, 4 minor. Origin: run 4 (A-05, A-06, A-07, A-08), run-c 2 (A-01, A-03), inh 2 (A-02, A-04) |
| M3 | corrections against base | 4 |
| M4 | content lost | 0 |
| M5 | false statements added | 1 (A-05) |
| M6 | routing probe | strict 2/4, lenient 3/4 |
| M7 | generator's checker (`generator/scripts/check.py`) | no problems reported |

**M3 list:** 1 `apiGet` "never throws, returns `{ data, error }`" → rejects with the `Response`; 2 every route page in `lazy()` → static imports; 3 constants: `FEATURE_FLAGS` barrel and `limits.json` → the real modules; 4 guide index `testing/tests.md` → `testing/testing.md`.

**Fix before merge (every major and every run-made minor):** A-01, A-03, A-04, A-05, A-06, A-07, A-08. **Can wait:** A-02. **Verdict:** usable after named fixes.

**Goal question 1:** improves on base in the guides the run rewrote (api, routing, constants, index); mixed overall, because the run added A-05 and left the old Development row and the boolean flag line.

**Generator follow-up (not verified in this discussion; owner: generator maintainers):** participants suggested these causes; nobody checked them against `generator/`:
- G1 (GPT): Examples are cut at 20 lines by the excerpt step.
- G2 (CLAUDE): the AGENTS.md merge keeps the old Development row because it only replaces rows with the same category.
- G3 (GEMINI): the checker never looks at paths inside tables, so the wrong-case path in A-08 passed.
- G4 (GPT): the run used an outdated template, which is why `components.md` kept the `index.ts` rule.

**Goal question 2:** not shown; a paired delivery run after the fixes would show it.

## Log

- Round 1: accepted CLAUDE, GPT, GEMINI; missing none; late none.
- Round 2: accepted CLAUDE, GPT, GEMINI; missing none; late none.
- Round 3 (confirmation): accepted CLAUDE, GPT, GEMINI; missing none; late none. Outcome final.

DISCUSSION-CLOSED
