---
status: proposed
date: 2026-10-18
decision-makers: [maintainer]
---

# 0007. Family format: this KB is the source of truth for the format, and templates are generated from it

## Context and Problem Statement

The family format began in nerdio-hcl, which is marked as its reference implementation. Since then,
the family code, the model convention and the alignment rules have been built here first and
copied out. That makes two places that can claim the format, and siblings drift when they copy from
whichever they saw last: the AVD KB's `family.yaml` already uses an older layout. Other people also
want to start their own knowledge base the same way. Which repo owns the format, and how does it
reach the siblings and new adopters?

## Considered Options

- This KB owns the format: siblings track it and adopt its changes by PR, and a public template
  repository is generated from it
- nerdio-hcl stays the reference, and this KB stays the hub for AI knowledge only
- No owner: each format change is negotiated across all four KBs

## Decision Outcome

Chosen option: "This KB owns the format", because the family's shared AI tooling and conventions
already live here, one owner removes the "which copy is right" question, and a template generated
from a working KB can't drift from it.

- **Roles.** In every `family.yaml`, this KB becomes `reference` (it owns the format) and also
  stays the hub for AI knowledge. nerdio-hcl becomes a `member`. The schema's role description
  changes to match, and a new `observer` role is added for private layers that read the family
  but aren't watched (no `repo`, skipped by the source check).
- **Tracking.** Each sibling adds `github_commits` sources on this repo's
  `docs/knowledge/schema`, `scripts/kb` and `.github/workflows`, beside the decisions and KB
  sources it already has. The freshness check already flags a sibling on a different
  `format_version`.
- **Changing the format.** A "Family format: ..." decision is written here first. Each sibling then
  adopts it by PR, and `format_version` goes up here once every sibling has merged it.
- **Templates.** `template/manifest.yaml` and `scripts/kb/export_template.py` build a clean copy
  of the machinery (scripts, schemas, workflows, issue forms, guardrails, the 2ndbrain spec and
  skill) with an empty KB skeleton and none of this KB's content. A public template repository,
  `2ndbrain-public`, pulls that export weekly with its own token and opens a PR in itself. This
  repo never writes to it.

### Consequences

- Good, because one place owns the format, and both the siblings and the template follow it by PR.
- Good, because new adopters start on the family's current version.
- Bad, because every KB changes its `family.yaml` roles once.
- Neutral, because nerdio-hcl's decisions and history stay where they are; only the role label moves.

## More Information

Also to be recorded in each sibling as a pointer decision once accepted. Supersedes nothing: nerdio-hcl
0021 set up the family, and this record changes who owns its format. Revisit on 2027-04-01, or when
a second person adopts the template.
