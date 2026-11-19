---
status: proposed
date: 2026-11-18
decision-makers: [maintainers]
---

# 0022. Unlink sibling repositories from ai-brain

## Context and Problem Statement

`ai-brain` previously tracked three sibling knowledge bases (`nerdio-hcl`, `avd`, and
`liquidware`) in [family.yaml](../family.yaml) and watched their commits in
[sources.toml](../sources.toml). The maintainer wants `ai-brain` separated from those sibling
repositories while keeping the KB/2ndbrain tooling and the `private-layer` observer intact. Should
we strip all family machinery or unlink the sibling repositories?

## Considered Options

- **Unlink sibling repositories only** — remove `nerdio-hcl`, `avd`, and `liquidware` from
  `family.yaml` and `sources.toml`, keep `ai` (`self: true`) and `private-layer` (`observer`), and
  keep the KB/2ndbrain schemas, scripts, and template export intact.
- **Remove all family machinery** — delete `family.yaml`, `family.schema.json`, `check_family()`,
  and related workflows/scripts.

## Decision Outcome

Chosen option: **"Unlink sibling repositories only"**, because it cleanly separates `ai-brain` from
the sibling repos without breaking the `2ndbrain` template export, validation schemas, or the
`private-layer` directives workflow.

### Consequences

- Good, because `ai-brain` no longer pulls, indexes, or links to `nerdio-hcl`, `avd`, or
  `liquidware`.
- Good, because `private-layer` (`directives.yaml`) and the `2ndbrain` template export continue to
  work without changes.
- Neutral, because historical decisions (`0001`–`0019`) and Apache-2.0 `NOTICE` attributions remain
  unchanged as historical records.
