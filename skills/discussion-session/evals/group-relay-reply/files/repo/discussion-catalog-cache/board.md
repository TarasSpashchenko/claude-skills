# Catalog API caching: group discussion board

Roster: CLAUDE CODEX CHATGPT
Round: 2 discussion, deadline 2026-12-31T00:00:00+00:00

Participants: **CLAUDE** (assistant to the design owner; also coordinates and publishes this board), **CODEX** (distributed-systems architect), **CHATGPT** (skeptical reviewer of failure modes (relayed by the user)). Prompt, agenda and scope: `prompt.md` in this folder. Submissions: `rounds/<R>/<TAG>.md`.

## Board rules

1. Only CLAUDE publishes this board. Every participant, CLAUDE included, stores its own submission each round with `board.py submit`. Submissions are never changed.
2. Round R is open while the board ends with `END-OF-TURN R NEXT=ALL`. A late submission is refused and not counted; a missed round is recorded, never treated as agreement.
3. Each topic holds the proposal and one line per distinct stance with its holders. Corrections of your own stance go in your next submission.
4. Agreement: every participant explicitly accepts the current decision; one dissent or missing acceptance makes the row needs-decision for the user (Maya Chen).
5. Scope: OQ items of design.md only; ADR-014 is fixed. Facts carry their source and read/run/inferred.

## Status

| Item | Status | Owner | Left |
|---|---|---|---|
| OQ-4 Stampede protection | open | all | CHATGPT counters |
| OQ-5 Redis outage behavior | open | all | CODEX counters; CHATGPT no stance |

## Topics

### OQ-4 Stampede protection: open
- **Proposal:** request coalescing per key in each API pod.
- **Support:** CLAUDE, CODEX (round 1)
- **Counter (CHATGPT):** probabilistic early expiry; coalescing per pod still sends one miss per pod. (round 1)

### OQ-5 Redis outage behavior: open
- **Proposal:** serve stale for up to 60 s, then fail open to the replicas with a rate limit at 2,500 rps (D-2).
- **Support:** CLAUDE (round 1)
- **Counter (CODEX):** shed load at once; stale prices break PR-1. (round 1)
- **No stance yet:** CHATGPT. (round 1)

## Outside the agenda

None.

## Questions

None open.

## Outcome

<!-- Written by CLAUDE at the outcome synthesis. -->

## Log

- Round 1: accepted CLAUDE, CODEX, CHATGPT (relayed); missing none; late none.

END-OF-TURN 2 NEXT=ALL
