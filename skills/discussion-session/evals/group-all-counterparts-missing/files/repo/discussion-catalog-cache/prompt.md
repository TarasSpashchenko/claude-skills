# Shared prompt: catalog API caching, group discussion

Run every command from this folder, `discussion-catalog-cache/`. The material is in its parent folder.

## 1. Your role
You are one of 4 participants. Your own role is in your entry prompt.

## 2. Goal
Settle the open questions of `design.md` so the platform team can implement the cache before Black Friday. Outcome: one decision record per item: chosen option, rationale, risks, follow-up owner.

## 3. Context
Read `../design.md` and `../decisions.md`. ADR-014 (Redis) is fixed. PR-1: a displayed price may lag the source of truth by at most 60 seconds. D-2: about 3,000 rps of replica headroom at current peak.

## 6. Agenda
- **OQ-1 Cache key granularity.** Cache per product, per listing page, or both?
- **OQ-2 Invalidation.** TTL only, event-driven invalidation, or both?
- **OQ-3 TTL values.** Which TTLs are safe given PR-1?

## 8. How the discussion works
**Participants.** **CLAUDE** (assistant to the design owner; also coordinates and publishes this board), **CODEX** (distributed-systems architect), **GEMINI** (skeptic for operational simplicity), **PI** (pricing and legal compliance (PR-1)). Claude is a full participant and the only one who publishes the board.
**Rounds.** Round R is open while `board.md` ends with `END-OF-TURN R NEXT=ALL`. Store your submission with `python3 board.py submit --board board.md --round <R> --tag <TAG> --from <temp file>`, then wait with `python3 board.py wait --board board.md --after-round <R> --timeout 540`.
**Agreement.** A row is agreed only when every participant, Claude included, explicitly accepts it. Silence never counts. One dissent or missing acceptance sends the row to the user (Maya Chen) as needs-decision, with each stance named.
