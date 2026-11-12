# Release 2.4.0 (2026-11-02)

This release is mostly about stability; it also adds one feature that was requested by many customers.
The team has fixed several issues and the following changes were made

- fixed the login timeout that occurred when a user's session was idle for more than 30 minutes
- added a CSV export to the orders page, it allows the admin to download all orders via the Export button
- the v1 endpoint /api/v1/orders is deprecated, e.g. clients should migrate to /api/v2/orders before 2027-01-01

If a customer can't log in, he should clear the browser cache and try again.
