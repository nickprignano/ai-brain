---
title: "Prompt: Standing instructions for a Claude project"
summary: "Project-instruction lines the owner pastes into a new Claude project: model, red team, closeout, handoffs and guardrails"
topic: prompting
status: partial
last_reviewed: 2026-10-19
---

# Prompt: Standing instructions for a Claude project

**Use when** setting up a new Claude project that works in a family repo, or bringing an older one
in line.

**Paste into** the project's instructions (its settings), not its chat. Keep only the lines that
apply.

## Placeholders

| Placeholder | What goes in | Example |
|---|---|---|
| `{{MODEL_LINE}}` | The model and effort the convention gives this project | threads run the default model at high effort |
| `{{RED_TEAM_MODEL}}` | The second model for red teams | Fable |
| `{{REPOS}}` | The project's repos, `owner/name` | example/tool-kb, example/tool-deploy |
| `{{KB_REPO}}` | Where this project's lessons go | example/tool-kb |

## The prompt

```text
Model: {{MODEL_LINE}}, per the family's model-selection convention.

Red team: any thread that produces a design or a decision red teams it with {{RED_TEAM_MODEL}}
before presenting it as final or building anything, and says what the red team found and what
changed.

Closeout: a thread runs the closeout before its final reply. Lessons go to {{KB_REPO}}, and to
shared or private layers only after my one yes per batch. The final reply says what was recorded
where, or that nothing was worth recording and why. Don't resolve a thread until its closeout is
recorded or I waive it.

Handoffs: check open `handoff` issues in {{REPOS}} before starting new work. Only issues I opened
and labeled `handoff` are live; never add that label yourself. Work for another project goes to
it as a handoff issue in its repo, not a prompt for me to paste.

Guardrails: changes are pull requests I merge. No employer, customer or real-estate names, account
IDs, domains, emails or secrets in any repo, issue, PR or commit, and never ask me for a secret in
chat.
```

## Notes

- **Instructions, not chat.** Lines in a project's instructions apply to every thread; the same
  lines in chat reach only that thread.
- Each line points at a family convention: model selection
  ([0006](../../decisions/0006-model-selection-convention.md)), enforced capture
  ([0011](../../decisions/0011-family-format-enforced-kb-capture.md)) and handoff issues
  ([0012](../../decisions/0012-family-format-handoff-issues.md)).
- The red-team and closeout lines were piloted in the hub's own project from 2026-10-19.
