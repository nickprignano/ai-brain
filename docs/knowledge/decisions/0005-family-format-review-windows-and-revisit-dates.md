---
status: proposed
date: 2026-10-18
decision-makers: [maintainer]
---

# 0005. Family format: per-page review windows and revisit dates on decisions

## Context and Problem Statement

The family format flags every page not reviewed in 90 days, and decisions have no date to look
back. Facts about fast-moving tools, such as model versions, go stale sooner than that, concept
pages last much longer, and decisions rest on assumptions that change. Should the shared format
carry its own review clocks?

## Considered Options

- Add an optional `review_after_days` to page front matter (default 90) and an optional
  `revisit_on` date to accepted decisions, both flagged by `kb-freshness`
- Keep the flat 90 days and no revisit dates
- Shorten the flat window for every page

## Decision Outcome

Chosen option: "Add an optional `review_after_days` and `revisit_on`", because the maintainer's
personal notes vault already runs these two clocks and they flag the right things: fast pages
early, slow pages rarely, and decisions when their assumptions can be tested.

### Consequences

- Good, because both fields are optional, so existing pages and records stay valid.
- Bad, because it's a shared format change: it lands in every KB, then `format_version` goes to 2.
- Neutral, because until all the KBs merge it, this KB stays on version 1.

## More Information

Proposed to the family per [curation.md](../curation.md#staying-aligned-with-the-family). Not built
yet: the schemas and `freshness.py` change only once all the KBs agree.
