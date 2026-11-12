---
type: llm
focus: trace
weight: 1
---

rotate-api-key.md gives the five actions as numbered steps, in this sequence: new key in the admin console, Vault at secret/payments/api-key, kubectl restart of the payments deployment, /health returns 200, revoke the old key.
