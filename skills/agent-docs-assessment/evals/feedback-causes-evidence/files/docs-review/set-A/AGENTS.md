# AGENTS.md

Entry point for AI agents working in shopfront-ui. Match the task to a Task Routing row and load its P0 guide before you search.

## Guides

| Guide | Path | Purpose |
|---|---|---|
| Index | `.ai-run/guides/README.md` | Which guide answers which question |
| API | `.ai-run/guides/development/api.md` | Backend calls and errors |
| Constants | `.ai-run/guides/development/constants.md` | Shared constants and feature flags |
| Routing | `.ai-run/guides/architecture/routing.md` | Routes and pages |
| Components | `.ai-run/guides/components/components.md` | Building components |
| Testing | `.ai-run/guides/testing/testing.md` | Unit tests |
| Git | `.ai-run/guides/standards/git-workflow.md` | Branches, commits, MRs |

## Task Routing

| Category | Example Requests | P0 Guide | P1 Guide |
|---|---|---|---|
| API | call an endpoint; handle a failed request | `.ai-run/guides/development/api.md` | - |
| Constants | extract this constant; add a feature flag | `.ai-run/guides/development/constants.md` | - |
| Routing | add a page; change a route | `.ai-run/guides/architecture/routing.md` | `.ai-run/guides/development/constants.md` |
| Components | new component; reuse a button | `.ai-run/guides/components/components.md` | - |
| Testing | write tests; fix a failing test | `.ai-run/guides/testing/testing.md` | - |
| Git | commit; open an MR | `.ai-run/guides/standards/git-workflow.md` | - |
| Development | call an endpoint; extract this constant; add a feature flag | `.ai-run/guides/development/api.md` | `.ai-run/guides/development/constants.md` |

## Critical Rules

| Rule | Trigger | Action |
|---|---|---|
| Check Guides First | Any task | Load the P0 guide of the matching row |
| Testing | "write tests" | Only when the user asks |
