---
title: "Prompt: Add an AGENTS.md to a repo"
summary: "Has Claude give a repo an AGENTS.md with its guardrails and the four change rules, and make CLAUDE.md import it (decision 0019)"
topic: prompting
status: verified
last_reviewed: 2026-10-22
---

# Prompt: Add an AGENTS.md to a repo

**Use when** the repo audit reports `change-rules` for a repo: it has no `AGENTS.md`, its
`AGENTS.md` has no "How to make a change" section, or its `CLAUDE.md` doesn't import it. A repo
made from the 2ndbrain template already has all of this.

**Paste into** a Claude Code session or project thread that has the repo attached, or put it in a
handoff issue for the project that owns the repo.

**Run so far:** not yet as written.

## Placeholders

| Placeholder | What goes in | Example |
|---|---|---|
| `{{REPO}}` | The repo, `owner/name` | example/tool-web |
| `{{CHECKS}}` | The commands that prove a change works, or "none yet" | `npm test`, `npm run typecheck` |

## The prompt

````text
Give {{REPO}} an AGENTS.md that follows decision 0019 (every repo has one, with the four change
rules), as one change made the way the repo's rules say (a pull request unless they say otherwise).

1. Read the repo's existing CLAUDE.md, AGENTS.md, README and CONTRIBUTING, if any. Keep every rule
   they already state; the repo's own rules win where they're stricter or deliberately different.
2. AGENTS.md at the repo root holds, in this order: a title line, the repo's own rules (moved from
   CLAUDE.md if that's where they are), the guardrails below that apply, the "How to make a change"
   section below word for word, and a "Checks to run" section with {{CHECKS}}.
3. CLAUDE.md becomes the single line `@AGENTS.md`, and so does .claude/CLAUDE.md if it exists.
4. Don't change anything else. Say in the PR body what you moved and what you assumed.

Guardrails (keep the ones that apply, drop none that already exist; leave out the pull-request
line where the repo's own rules say commits go straight to the default branch):
- Never put API keys, account or tenant IDs, domains, IPs, emails, secrets, or employer, customer
  or private-project names in the repo, commits, issues or PR text.
- Never ask for, show or store a secret in chat. The owner runs the step that handles it.
- Propose changes as pull requests. Never change a real account, deployment or spend setting
  without the owner's explicit yes.

The section to copy:

## How to make a change

Four rules after the community "Karpathy guidelines" (MIT), reworded for agents that work unattended.

- Say what you assumed. When the ask leaves a detail open, pick the reasonable default, say which,
  and keep going. Stop to ask only when the choice changes the goal, something the owner will
  notice, or a step no one can undo; if no one is there to answer, do the reversible part and leave
  the question in the PR body. If a simpler way exists than the one asked for, say so.
- Write the least code that does the job: no features, options or abstractions nobody asked for,
  and no handling for cases that can't happen.
- Touch only what the task needs and match the style around it. Every changed line should trace
  back to the ask. Mention unrelated dead code instead of deleting it; remove only what your own
  change left unused.
- Before you start, name the check that proves the task is done (a failing test, the "Checks to
  run" below, an expected output), and don't call it done until it passes in front of you.
````

## Notes

- **Why `@AGENTS.md`.** Claude Code reads `AGENTS.md` on its own only when there's no `CLAUDE.md`,
  and only from v2.1.277 and in sessions that support it
  ([docs](https://code.claude.com/docs/en/memory#agents-md)). A `CLAUDE.md` that doesn't import
  it hides it from Claude. The one-line import works in every Claude Code session. A Claude
  project thread that reads the repo through a connector reads neither file; the change-rules line
  in its [project instructions](project-instructions.md) covers that.
- **Wording.** The section is the template's, minus its knowledge-base lines. Keep the heading
  exactly, and the first rule's opening words: the repo audit looks for `## How to make a change`
and "Say what you assumed".
- Decision: [0019](../../decisions/0019-agents-md-in-every-repo.md). For a repo that will also run
  the full conventions, use the [handoff issue](handoff-issue.md) and the 2ndbrain template instead.
