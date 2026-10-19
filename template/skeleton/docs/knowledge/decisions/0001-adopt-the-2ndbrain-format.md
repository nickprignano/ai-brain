---
status: proposed
date: 2026-10-18
decision-makers: [maintainers]
---

# 0001. Adopt the 2ndbrain knowledge base format, version 1

## Context and Problem Statement

This project needs a place for what it learns and decides, readable by people, tools and AI agents,
that stays current without manual sweeps. Should it use the shared 2ndbrain format, or its own?

## Considered Options

- Adopt the 2ndbrain format (version 1) from the 2ndbrain template
- A format of its own
- No in-repo knowledge base; keep notes elsewhere

## Decision Outcome

Chosen option: "Adopt the 2ndbrain format", because its checks, digest and freshness loops are
already built and tested, it uses no LLM tokens or API keys to run, and other KBs in the same
format can watch and link to this one.

### Consequences

- Good, because knowledge changes in the same PR as the code it describes.
- Good, because format changes arrive through the template and are adopted by PR.
- Neutral, because topics and data are this project's own; only the format is shared.

## More Information

The system is specified in [the 2ndbrain spec](../../2ndbrain/SPEC.md).
