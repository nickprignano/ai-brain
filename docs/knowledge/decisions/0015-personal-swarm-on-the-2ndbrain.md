---
status: proposed
date: 2026-10-19
decision-makers: [maintainer]
---

# 0015. A personal swarm on the 2ndbrain, built from the roles that already run

## Context and Problem Statement

The owner's work already runs through several agents: a coordinator and thread sessions in each
Claude project, a weekday open-work routine, handoff routines, token-free KB workflows and scoped
Fable red teams. Each was added on its own, so nothing lists them, says what each may do without
asking, or stops all of them at once. The cloud swarm designs (the AVD swarm and the AWS
first-principles design) worked out how agents should act safely, but for a cloud estate with
identities, plan stores and observers. What should a personal swarm on the 2ndbrain be, and how
much of the cloud design does it need?

## Considered Options

- Keep adding agents one at a time, with no shared spec
- Port the cloud swarm design: per-agent identities, a plan store, observers, a judge
- A thin spec over what already runs: named roles, action tiers, an owner queue cap, one stop
  switch and a registry, with new roles added one at a time behind an eval

## Decision Outcome

Chosen option: "A thin spec over what already runs", because the owner's attention, not agent
time, is the bottleneck, and the cloud design's machinery costs more than it catches at one
owner's volume. The full spec lives in the swarm's own private repo, which public text
doesn't name, the same rule as the private layer's (2ndbrain spec section 8). In short:

- Roles: coordinator, builder, red teamer, finisher, courier, curator exist; a digest worker and a
  second reviewer are designed, not scheduled.
- Four action tiers: free, lands itself (the low-risk auto-merge class), the owner's yes, the
  owner runs it. Unknown means the last.
- The owner's queue is capped at one 30-minute sitting of estimated review time, counted live from
  GitHub; one active build per project.
- One stop switch: an owner-closed `swarm-stop` issue in this hub that any role can open,
  checked by this hub's `directives.py gate` and `handoffs.py session-start`, plus pause directives,
  auto-merge disarm, per-repo pause variables and spend walls.
- A `swarm.yaml` registry in the swarm's repo, validated, listing every role, its trigger, tier
  ceiling, data classes, provider, heartbeat and stop.
- Phase 0 writes the registry; phase 1 adds the stop issue, the cap and four numbers in the
  weekday pass; phase 2 a machine GitHub identity. Everything after phase 1 is designed, not
  scheduled.

### What this hub would change, in its own PRs, once accepted

- `schema/directive.schema.json`: add `swarm` and `kb-auto-merge` to the `pause` enum (a family
  format change, so it ships with the next format bump), and the private layer template's
  `pausable` list in `hub.toml` to match.
- `scripts/kb/directives.py` and `scripts/kb/handoffs.py`: read the stop issue.
- A `swarm-stop` label here, with no issue template that applies it. The stop issue lives in this
  public hub, not the swarm's private repo, so every repo's workflows and sessions can read it with
  no token.

### Consequences

- Good, because phases 0 and 1 build nothing new to run: a file, a check, an issue and a few rules.
- Good, because every role has one written stop that any role can throw in seconds.
- Bad, because until the machine identity exists, tier C rests on rules Claude keeps: agents act as
  the owner's GitHub account, so GitHub can't tell them apart.
- Bad, because the stop reaches routines and sessions only when they start new work, not mid-turn.

## More Information

- Red-teamed 2026-10-19 (Opus, then a scoped Fable pass: eight findings, two spot-checked); the
  table is in the spec's section 12.
- Builds on [0006](0006-model-selection-convention.md), [0008](0008-family-format-maintainer-directives-and-pause-switch.md),
  [0009](0009-second-model-family.md), [0011](0011-family-format-enforced-kb-capture.md),
  [0012](0012-family-format-handoff-issues.md) and [0014](0014-family-format-auto-merge-low-risk-prs.md)
  (GitHub work conventions).
- Revisit after phase 1 has run for two weeks, or on 2027-01-19, whichever is first.
