---
status: proposed
date: 2026-10-18
decision-makers: [maintainer]
---

# 0004. This KB is the family's source of truth for Claude API topics

## Context and Problem Statement

More than one project in the family uses the Claude API, so the same facts (models, caching,
limits, auth) could end up written in several KBs and drift apart. Where should they live?

## Considered Options

- Here, with siblings linking to this KB's pages
- In each project's own KB, copied where needed
- In whichever KB learned it first

## Decision Outcome

Chosen option: "Here, with siblings linking to this KB's pages", because the family rule is that
the KB closest to a topic is its source of truth, and this KB's topic is AI tooling.

### Consequences

- Good, because a Claude API fact is fixed in one place.
- Bad, because a sibling must open an issue or PR here instead of editing its own page.
- Neutral, because project-specific choices (such as how one app authenticates) stay in that
  project's KB, linking here for the general facts.

## More Information

Also recorded in [nerdio-hcl 0021](https://github.com/nickprignano/nerdio-hcl/blob/main/docs/knowledge/decisions/0021-knowledge-base-family.md),
which names this KB the family's hub for AI knowledge.
