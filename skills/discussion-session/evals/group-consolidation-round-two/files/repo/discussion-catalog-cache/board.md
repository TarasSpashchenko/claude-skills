# Catalog API caching: group discussion board

Roster: CLAUDE CODEX GEMINI OPENCODE PI
Round: 2 discussion, deadline 2026-10-26T18:00:00+00:00

Participants: **CLAUDE** (assistant to the design owner; also coordinates and publishes this board), **CODEX** (distributed-systems architect), **GEMINI** (skeptic for operational simplicity), **OPENCODE** (SRE for capacity and outages), **PI** (pricing and legal compliance (PR-1)). Prompt, agenda and scope: `prompt.md` in this folder. Submissions: `rounds/<R>/<TAG>.md`.

## Board rules

1. Only CLAUDE publishes this board. Every participant, CLAUDE included, stores its own submission each round with `board.py submit`. Submissions are never changed.
2. Round R is open while the board ends with `END-OF-TURN R NEXT=ALL`. A late submission is refused and not counted; a missed round is recorded, never treated as agreement.
3. Each topic holds the proposal and one line per distinct stance with its holders. Corrections of your own stance go in your next submission.
4. Agreement: every participant explicitly accepts the current decision; one dissent or missing acceptance makes the row needs-decision for the user (Maya Chen).
5. Scope: OQ items of design.md only; ADR-014 is fixed. Facts carry their source and read/run/inferred.

## Status

| Item | Status | Owner | Left |
|---|---|---|---|
| OQ-1 Cache key granularity | open | all | round-2 acceptances |
| OQ-2 Invalidation | open | all | GEMINI counters |
| OQ-3 TTL values | open | all | OPENCODE counters; PI has no stance yet |

## Topics

### OQ-1 Cache key granularity: open
- **Proposal:** cache per product and per listing page; listing entries hold product IDs only and are rendered from product entries, so a price change touches one key.
- **Support:** CLAUDE, CODEX, GEMINI, OPENCODE, PI (round 1)

### OQ-2 Invalidation: open
- **Proposal:** event-driven invalidation from `pricing.changed` and `stock.changed`, plus a TTL as a safety net.
- **Support:** CLAUDE, CODEX, OPENCODE, PI (round 1)
- **Counter (GEMINI):** TTL only, at 300 s; the event consumer adds a moving part. (round 1)

### OQ-3 TTL values: open
- **Proposal:** product entries 45 s, listing entries 30 s, both inside PR-1's 60 s price lag.
- **Support:** CLAUDE, CODEX, GEMINI (round 1)
- **Counter (OPENCODE):** product entries 55 s, to cut replica load at 2x peak. (round 1)
- **No stance yet:** PI said it would answer in round 2. (round 1)

## Outside the agenda

None.

## Questions

None open.

## Outcome

<!-- Written by CLAUDE at the outcome synthesis. -->

## Log

- Round 1: accepted CLAUDE, CODEX, GEMINI, OPENCODE, PI; missing none; late none.

END-OF-TURN 2 NEXT=ALL
