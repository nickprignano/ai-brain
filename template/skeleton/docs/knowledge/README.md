---
title: "Knowledge base"
summary: "What this knowledge base is, how it's organised, and how to add to it safely"
topic: overview
status: partial
last_reviewed: 2026-10-18
---

# Knowledge base

What this project has learned: research findings, gotchas, fixes with versions, and the decisions
behind them. It's written for people, tools and LLM agents alike. When something new is learned,
add it to the topic page it belongs to instead of starting a new file.

## Index

<!-- BEGIN GENERATED: kb-index (from front matter; run scripts/kb/build.py) -->
<!-- END GENERATED: kb-index -->

## Related knowledge bases

<!-- BEGIN GENERATED: family (from family.yaml; run scripts/kb/build.py) -->
<!-- END GENERATED: family -->

When a fact belongs to a sibling's topic, link to their page instead of copying it. See
[curation.md](curation.md#staying-aligned-with-the-family).

## Before you build something

Every change follows the [guardrails](../guardrails.md). Run the prior-art check first
(`python3 scripts/kb/prior_art.py "<topic>"`, see
[curation.md](curation.md#prior-art-check-kb-prior-art)).

## How to add to it

- **Without editing files:** open a **Knowledge base feedback**, **Known error** or **Suggest an
  expert to follow** issue. When a maintainer labels it `kb-accepted`, a workflow turns it into a
  pull request.
- **With a pull request:** add a bullet to the matching topic page, say what happened, the fix and
  the versions it applies to, and mark anything you haven't confirmed as *unverified*. Known errors
  go in [troubleshooting/known-errors.yaml](troubleshooting/known-errors.yaml). Decisions are a copy
  of [decisions/template.md](decisions/template.md) at the next number, `proposed` until the
  maintainer says yes. Run `python3 scripts/kb/build.py` and `python3 scripts/kb/validate.py`
  before pushing.

## Format

Page front matter (`title`, `summary`, `topic`, `status`, `last_reviewed`) is checked against
[schema/page.schema.json](schema/page.schema.json). Decisions are
[MADR 4](https://adr.github.io/madr/) records. The YAML data files each have a JSON Schema in
[schema/](schema/page.schema.json), and the Markdown tables and `llms.txt` are generated from them.
The full system is in the [2ndbrain spec](../2ndbrain/SPEC.md).
