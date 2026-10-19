---
title: "Prompt: Apply red-team findings in another project"
summary: "Hands a red-team findings file to the project that owns the design, to fix, accept or dispute each finding through pull requests"
topic: prompting
status: verified
last_reviewed: 2026-10-19
---

# Prompt: Apply red-team findings in another project

**Use when** a red team ran in one project but the design it attacked, and so the fixes, live in
another project's repos.

**Paste into** the project that owns the design, or send it as a handoff issue. The findings must
be somewhere it can read, such as a public repo or the issue itself.

**Run so far:** a close earlier version (2026-10-19).

## Placeholders

| Placeholder | What goes in | Example |
|---|---|---|
| `{{FINDINGS}}` | The findings, as a link, or pasted in when the receiver can't read them | the red-team section of the design PR |
| `{{IDS}}` | Which findings to work, or "all" | RT-1 to RT-9, plus RT-16 and RT-17 |
| `{{REPOS}}` | The repos the fixes go into | example/agents, example/kb |
| `{{PRIORITY}}` | What goes first | anything rated High, then whatever blocks the next release |

## The prompt

```text
A red team found problems in our design: {{FINDINGS}}. Work findings {{IDS}} in {{REPOS}}.

For each finding:
1. Check it against the current code and docs. The red team may have read an older version, so
   say if it's already fixed or doesn't reproduce.
2. If it holds, make the change it names, or a better one, and say why yours is better.
3. If you disagree, say why with evidence, and leave the finding open for me.

Go in this order: {{PRIORITY}}. Open one pull request per repo, each listing the finding IDs it
fixes, and don't merge them. Record the lessons in this project's KB.

When you're done, give me a table: finding, status (fixed, already fixed, disputed, open) and the
PR. Don't paste the findings into any public repo or PR if they name real customers or
systems; refer to them by ID.
```

## Notes

- **Let the receiver dispute.** The owner of the design knows things the red team didn't; a
  prompt that only says "fix these" gets fixes for findings that don't hold.
- **Refer to findings by ID in public places.** The findings file can carry detail that shouldn't
  be in a public PR.
- Generalized from the fix and update prompts that took a 2026-10-19 red team of a sibling's agent
  design back to that project.
