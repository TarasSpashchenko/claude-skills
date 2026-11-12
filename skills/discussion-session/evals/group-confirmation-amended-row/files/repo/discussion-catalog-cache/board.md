# Catalog API caching: group discussion board

Roster: CLAUDE CODEX GEMINI OPENCODE PI
Round: 3 confirmation, deadline 2026-10-26T18:00:00+00:00

Participants: **CLAUDE** (assistant to the design owner; also coordinates and publishes this board), **CODEX** (distributed-systems architect), **GEMINI** (skeptic for operational simplicity), **OPENCODE** (SRE for capacity and outages), **PI** (pricing and legal compliance (PR-1)). Prompt, agenda and scope: `prompt.md` in this folder. Submissions: `rounds/<R>/<TAG>.md`.

## Board rules

1. Only CLAUDE publishes this board. Every participant, CLAUDE included, stores its own submission each round with `board.py submit`. Submissions are never changed.
2. Round R is open while the board ends with `END-OF-TURN R NEXT=ALL`. A late submission is refused and not counted; a missed round is recorded, never treated as agreement.
3. Each topic holds the proposal and one line per distinct stance with its holders. Corrections of your own stance go in your next submission.
4. Agreement: every participant explicitly accepts the current decision; one dissent or missing acceptance makes the row needs-decision for the user (Maya Chen). At most 5 rounds, including confirmation: the user's ceiling.
5. Scope: OQ items of design.md only; ADR-014 is fixed. Facts carry their source and read/run/inferred.

## Status

| Item | Status | Owner | Left |
|---|---|---|---|
| OQ-1 Cache key granularity | agreed | all | confirmation |
| OQ-2 Invalidation | needs-decision | Maya Chen | confirmation |
| OQ-3 TTL values | agreed | all | confirmation |

## Topics

### OQ-1 Cache key granularity: agreed
- **Decision:** cache per product and per listing page; listing entries hold product IDs only.
- **Accepted by:** CLAUDE, CODEX, GEMINI, OPENCODE, PI (round 2)

### OQ-2 Invalidation: needs-decision
- **Proposal:** event-driven invalidation plus a 45 s TTL safety net counted from the write.
- **Support:** CLAUDE, CODEX, OPENCODE, PI (round 2)
- **Dissent (GEMINI):** TTL only, at 45 s; the consumer can lag, so the TTL is the real guarantee anyway. (round 2)

### OQ-3 TTL values: agreed
- **Decision:** product entries 45 s, listing entries 30 s.
- **Accepted by:** CLAUDE, CODEX, GEMINI, OPENCODE, PI (round 2)

## Outside the agenda

None.

## Questions

None open.

## Outcome

**Status: draft for the confirmation round (round 3).**

| Item | Decision | Category | Accepted by | Dissent (tag: reason) | No response |
|---|---|---|---|---|---|
| OQ-1 | Cache per product and per listing page; listing entries hold product IDs only | agreed-change | CLAUDE, CODEX, GEMINI, OPENCODE, PI | — | — |
| OQ-2 | Event-driven invalidation plus a 45 s TTL safety net from the write | needs-decision (Maya Chen) | CLAUDE, CODEX, OPENCODE, PI | GEMINI: TTL only at 45 s; the consumer can lag | — |
| OQ-3 | Product entries 45 s, listing entries 20 s | agreed-change | CLAUDE, CODEX, GEMINI, OPENCODE, PI | — | — |

## Log

- Round 1: accepted CLAUDE, CODEX, GEMINI, OPENCODE, PI; missing none; late none.
- Round 2: accepted CLAUDE, CODEX, GEMINI, OPENCODE, PI; missing none; late none.

END-OF-TURN 3 NEXT=ALL
