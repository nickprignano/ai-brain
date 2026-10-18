---
status: proposed
date: 2026-10-18
decision-makers: [maintainer]
---

# 0001. Adopt the family knowledge base format, version 1

## Context and Problem Statement

This project researches AI tooling that the maintainer's other projects use, and two of them call
the Claude API directly. Those projects each keep a knowledge base in the format of the
[nerdio-hcl reference](https://github.com/nickprignano/nerdio-hcl/blob/main/docs/knowledge/README.md). Should this one follow the same format, or keep its own?

## Considered Options

- Adopt the family format (version 1), copying the reference's scripts, schemas, workflows and issue forms
- A format of its own, tuned to this topic
- No in-repo knowledge base; keep notes elsewhere

## Decision Outcome

Chosen option: "Adopt the family format (version 1)", because the same checks and layout across
all the KBs let people, tools and agents move between them, and the siblings can watch and link to
each other.

### Consequences

- Good, because the tooling is already built and tested, and uses no LLM tokens or API keys to run.
- Good, because a change to the shared format happens once, as a "Family format" decision in every KB.
- Bad, because a few reference topics and guardrails are written for Azure and needed rewording here.
- Neutral, because topics and data differ by KB; only the format is shared.

## More Information

Listed in [family.yaml](../family.yaml). How the KBs stay aligned is in
[curation.md](../curation.md#staying-aligned-with-the-family).
