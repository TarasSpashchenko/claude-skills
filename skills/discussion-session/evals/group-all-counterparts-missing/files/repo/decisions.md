# Catalog decisions (authoritative)

- **ADR-014 (2026-08-12) Cache technology.** Redis 7 (managed) is the cache. Closed; not to be revisited.
- **PR-1 (Pricing/Legal) Price lag.** A displayed price may lag the source of truth by at most 60 seconds.
- **D-2 (2026-09-30) Replica capacity.** The read replicas have about 3,000 rps of headroom at current peak; beyond that, latency degrades sharply.
