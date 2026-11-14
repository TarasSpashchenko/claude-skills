---
tags: [skill-creator, agent-docs-assessment]
max_turns: 150
timeout_seconds: 3600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Our developers regenerated the AI-agent docs of shopfront-ui (the repo is ./shopfront-ui) with our docs generator twice, once per model: branch `docs/regen-opus` and branch `docs/regen-sonnet`, both cut from `main`. We need the same quality assessment for both branches, so we know how useful each set of guides is, and then a comparison of the two. GPT (in Codex) and Gemini (in agy) will be your teammates; I start them myself. Please prepare everything for the two assessments and tell me what to start.

Input files: shopfront-ui/ (built by place-files.sh)
