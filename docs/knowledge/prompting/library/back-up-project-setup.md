---
title: "Prompt: Back up a Claude project's setup as a note"
summary: "Has a Claude project describe its own setup (instructions, repos, model, scheduled tasks, connectors) as one linked note, with secrets, IDs and private data left out"
topic: prompting
status: verified
last_reviewed: 2026-10-21
---

# Prompt: Back up a Claude project's setup as a note

**Use when** you keep a readable backup of your Claude setup in a notes vault, and one of your
projects holds settings the vault's own project can't see: its instructions, scheduled tasks and
connectors.

**Paste into** the project being backed up. It returns the note in chat; paste the reply into the
project that owns the vault, which checks it and commits it. Don't run it in a project that holds
work or other people's data: list those projects in one generic line instead.

**Run so far:** not yet as written (drafted 2026-10-21 alongside a backup of the drafting project).

## Placeholders

| Placeholder | What goes in | Example |
|---|---|---|
| `{{HUB}}` | The vault's hub note, as a wikilink target | claude-setup |
| `{{RELATED}}` | The vault's other setup notes to link | preferences, repos, routines, connectors, skills |
| `{{OFF_LIMITS}}` | Extra kinds of data this owner never wants in the vault | children's data, health details |

## The prompt

```text
Write a backup note describing this Claude project's setup, and return it in chat as one
Markdown code block. Do not write files, open pull requests or touch any repo.

Format:
---
title: <project name> project
kind: project
created: <today>
updated: <today>
captured_from: <today>, this project's session context and tools
tags: [claude-setup, project]
status: active
related: ["[[{{HUB}}]]", plus a [[link]] for each of {{RELATED}}]
---

One line on what the project is for.
- Visibility, repos (names only), environment name, model and effort.
- Scheduled tasks in this project: name, schedule with timezone, one line on what each does.
- Connectors this project uses: product name and purpose only.
- Skills it relies on: names only.

## Project instructions (verbatim)
The project instructions copied exactly, in a ```text block.

Hard rules: no secret values, tokens, keys or env var values (name env vars by purpose only);
no IDs of any kind (account, org, project, environment, trigger, session, connector), no
emails, no IPs, no custom connector URLs; no employer or customer names or details; no
{{OFF_LIMITS}}; no dollar figures; no project memory content. Where the instructions or a
task prompt break a rule, replace that part with "[omitted: <reason>]". After the block, list
in one line anything you left out and why.
```

## Notes

- **Return text, don't write.** The backed-up project may hold context the vault must never see.
  Having it hand back text that the vault's own project checks keeps write access in one place.
- **Scrub before verbatim.** Scheduled-task prompts often carry the owner's address or personal
  senders. Copying them word for word is what makes a backup rebuildable, so check each one and
  summarize the ones that fail.
- **Run a pattern check before committing.** A small script that fails on key shapes, emails,
  IPs, prefixed IDs and UUIDs, plus a git-ignored list of names, catches what a model's summary
  misses.
- **Leave out memory.** Project memory is working state: rebuildable, and the most sensitive part.
- Came out of a red-teamed design for backing up a Claude setup into a private notes vault
  (2026-10-21).
