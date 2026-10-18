# 2ndbrain: capture and sync for a two-layer second brain

A Claude skill that captures what a chat or code session produced into a **public hub KB** (this
repo's format) or a **private layer** (a personal notes vault), and refuses anything that's unsafe
for the public side. It also syncs family projects through the hub. The skill itself is
[SKILL.md](SKILL.md).

## Why two layers

Lessons about AI tooling are useful to anyone, so they belong in a public KB where others can read
and correct them. Judgment, goals and disagreements are personal, so they belong in a private repo.
One entry point that routes between them means the person capturing doesn't have to decide, and
the public side gets a safety gate every time.

## How it routes

```
 thread ──▶ 2ndbrain ──┬─ public-safe AI knowledge ──▶ hub KB (PR) ──▶ read by the private layer
                       ├─ personal ────────────────────────────────────▶ private layer (direct)
                       └─ secrets, work material ──▶ refused
```

- **Hub:** AI-technical facts, gotchas, fixes, sources and decisions, added to the page or data
  file they belong on, by pull request.
- **Private layer:** decisions, goals, disagreements, root-cause analyses, procedures and personal
  lessons, committed directly.
- **Split:** when a thread produced both, the general part goes to the hub and only the personal
  takeaway goes to the private layer, linking out to the hub page.
- **No copies:** a hub capture is never also written to the private layer. The private layer reads
  the hub on its own (for example a weekly roll-up of the hub's digest issues).
- **Refused:** secrets of any kind, and work material (employer, customer or tenant specifics),
  which belongs in that work project's own KB.

Before anything reaches the hub it passes the [guardrails](../../docs/guardrails.md): no IDs,
domains, emails, IPs, private app names or user data. A draft that can be generalised is rewritten
and shown; one that can't goes to the private layer instead.

## The one setting that matters: `private_layer`

| | `hidden` (default) | `named` |
|---|---|---|
| Public text | Never mentions the private layer. | May say a private layer exists, reads the hub and is never linked from it. |
| Split captures | Two independent notes; the hub PR says nothing about the other half. | The hub PR may say the personal takeaway was filed privately. |
| Always private | Contents, note names, paths, links, reasoning. | The same. |
| Before switching | Nothing. | A hub decision record allowing it, since guardrails change only by decision. |

## Triggers

Captures are offered, not forced: at most one offer line at the end of a thread. Lessons and
decisions are offered when a thread produced them; root-cause analyses and procedures only when the
user asked for troubleshooting or steps; disagreements only when the user asks. The full table is in
[SKILL.md](SKILL.md#triggers).

## Sync: the hub as the channel between projects

Claude projects can't read each other's chats, so a family project learns what changed elsewhere
from the hub. At the start of work in a family project (or on "2ndbrain sync"), the skill reads
the hub's public `directives.yaml`, `decisions/` and `family.yaml`, and reports:

- the directives in scope for this project, quoted exactly, with any pause;
- the decisions added or changed since the last sync, flagging family-format ones not yet adopted;
- whether this project's format version matches the hub's.

On request it writes a **handoff block**: one self-contained Markdown block, dated and pinned to
a hub commit, that a person pastes into another project. It's built only from public hub files,
so it never carries chat content, private-layer material or secrets.

Sync only reads. It writes nothing to any repo; adoption PRs it points to go through the normal
flow with the user's yes. Directives follow
[decision 0008](../../docs/knowledge/decisions/0008-family-format-maintainer-directives-and-pause-switch.md)
(proposed) and never override the guardrails or the user's own word.

## Install

1. Copy [SKILL.md](SKILL.md) into a new skill in your Claude account (or your project's
   `.claude/skills/2ndbrain/`).
2. Fill in the settings block: your hub repo, your private repo, its capture-rules file,
   `private_layer`, and the two sync settings.
3. Give your sessions push access to both repos, or use it from a plain chat, where it drafts notes
   for you to file.
4. Turn off any older capture skill that covers the same triggers, so only one fires.

## Not in v1

Searching or answering from either layer, the private layer's roll-up and patterns, writing
directives (sync only reads them), and staleness reviews.
