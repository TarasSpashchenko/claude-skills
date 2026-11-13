---
type: llm
focus: trace
weight: 1
---

No file or folder name under the review folder contains `opus`, `sonnet` or a branch name, no file content there contains `opus` or `sonnet`, and neither does the git history of any repository under it (`git -C <set> log -p --all` for each set that is a git repo): the model names in the generated knowledge-manifest.json were removed, replaced or never copied, in the files and in every commit.
