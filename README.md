# claude-skills

Agent skills for Claude Code.

| Skill | What it does |
|---|---|
| [`ste`](skills/ste/SKILL.md) | Writes and checks documentation in ASD-STE100 Simplified Technical English (Issue 9). |
| [`discussion-session`](skills/discussion-session/SKILL.md) | Runs a turn-based written discussion between Claude and other agents (Codex, Gemini CLI, opencode, pi, …) or human experts on a shared Markdown board, and closes with an agreed outcome. |

Both skills ship helper scripts that need Python 3 (standard library only).

`ste` also needs a local copy of the ASD-STE100 Issue 9 standard as Markdown, one file per PDF page (`page_001.md` …).
ASD owns its copyright, so this repository does not include it. Request the PDF from ASD, convert it, and put the pages in
`~/.local/share/ste/ASD-STE100_ISSUE9/` or set `STE_STANDARD_DIR`. See [configuration.md](skills/ste/references/configuration.md).

## Install

As a Claude Code plugin:

```
/plugin marketplace add <owner>/claude-skills
/plugin install ts-skills@ts-claude-skills
```

Or link one skill directly:

```
ln -s "$PWD/skills/ste" ~/.claude/skills/ste
```
