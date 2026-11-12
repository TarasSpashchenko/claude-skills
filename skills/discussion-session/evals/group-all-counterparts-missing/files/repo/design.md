# Catalog API caching — design draft v0.3

Owner: Platform team (Maya Chen). Status: five open questions remain.

## Context

The catalog API serves product listings and product detail pages. Traffic is read-heavy: about 4,800 requests per second at peak, writes about 40 per second (price and stock updates). Today every read hits the Postgres read replicas, which have roughly 3,000 rps of headroom left at current peak (decisions.md, D-2). Black Friday is expected to double peak traffic.

## Proposal

Put a Redis cache (ADR-014) in front of catalog reads. Product detail and listing responses are cached; writes go to Postgres and publish change events on the existing `pricing.changed` and `stock.changed` topics.

## Open questions

- **OQ-1 Cache key granularity.** Cache per product, per listing page, or both?
- **OQ-2 Invalidation.** TTL only, or event-driven invalidation from `pricing.changed` / `stock.changed`, or both?
- **OQ-3 TTL values.** Which TTLs are safe given the price-lag rule (decisions.md, PR-1)?
- **OQ-4 Stampede protection.** Request coalescing, probabilistic early expiry, or locks?
- **OQ-5 Redis outage behavior.** Fail open to the replicas, serve stale, or shed load?
