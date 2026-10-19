---
title: "Prompt: Survey a tool landscape for the KB"
summary: "Has Claude survey open-source and vendor tools in an area, check licences and dates, red team the result and add it to the KB"
topic: prompting
status: verified
last_reviewed: 2026-10-19
---

# Prompt: Survey a tool landscape for the KB

**Use when** you want to know what already exists in an area before building or adopting
something, and want the answer to stay in the KB.

**Paste into** the project that owns the KB the survey belongs in.

**Run so far:** a close earlier version, for the privacy-and-safety survey of AI tools against bad actors (2026-10-19).

## Placeholders

| Placeholder | What goes in | Example |
|---|---|---|
| `{{AREA}}` | The area, in a sentence | open-source AI tools that help defenders against attackers |
| `{{ANGLES}}` | The questions the survey must answer, one per line | which are maintained; which run locally; which need a paid service |
| `{{FOR_WHOM}}` | Who or what will use the result | our own agents and the projects that run them |
| `{{KB_PAGE}}` | The topic page the result goes on | privacy-and-safety |
| `{{RED_TEAM_MODEL}}` | The second model that checks it | a model other than the author's, as your model convention picks |

## The prompt

```text
Survey {{AREA}}, for {{FOR_WHOM}}. First run the prior-art check
(python3 scripts/kb/prior_art.py "{{AREA}}") and read what the KB already says.

Answer:
{{ANGLES}}

For every tool: link its primary source (repo, docs or vendor page), its licence, its last release
or commit date, what it needs to run (local, cloud, paid, keys), and what it's good and bad at.
Mark anything you couldn't confirm from a primary source as unverified. Prefer tools with a clear
licence and recent activity, and say which ones fail that.

Then red team the survey with {{RED_TEAM_MODEL}}: wrong facts, missing well-known tools, licence
or billing traps, and claims stronger than their source. Fix what it finds.

Put the result on the {{KB_PAGE}} page of the KB as a new section, linking to sources rather than
copying them, and open it as a pull request for my review. In your reply, say what the red team
found and what changed, and suggest which projects should evaluate which tools next.
```

## Notes

- **Dates and licences are the parts that rot and trap.** Asking for them per tool caught a
  copyleft licence and a red-team tool whose default mode sends data to a third-party cloud.
- **Red team before the PR, not after.** A second model reliably finds overstated claims and at
  least one missing tool.
- Follow up with [Research how a project could use a set of tools](research-proposal.md) for each
  project that should act on the survey.
