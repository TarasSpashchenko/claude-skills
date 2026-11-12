---
tags: [skill-creator]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Our team writes all docs in ASD-STE100 Simplified Technical English. Write a short runbook section, rotate-api-key.md, that tells the on-call engineer how to rotate the API key of the payments service: generate a new key in the admin console, put it in Vault at secret/payments/api-key, restart the payments deployment with kubectl, check that the /health endpoint returns 200, and then revoke the old key in the admin console. Save it as rotate-api-key.md.
