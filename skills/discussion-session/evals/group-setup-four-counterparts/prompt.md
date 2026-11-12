---
tags: [skill-creator, group-mode]
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

I want you, Codex, Gemini CLI, opencode and pi to discuss our catalog API caching design together, as a group. All four run on this machine and can read and write files and run shell commands. The material is design.md and decisions.md in this folder. Redis is already decided (ADR-014); don't let it be relitigated. What I need at the end: one decision record per open question (OQ-1 to OQ-5) with the chosen option, rationale, risks, and who follows up. Prepare everything; I'll start the four agents and tell you when to go.

Input files: decisions.md, design.md
