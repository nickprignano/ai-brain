---
title: "Knowledge base"
summary: "What this knowledge base is, how it's organised, and how to add to it safely"
topic: overview
status: verified
last_reviewed: 2026-10-18
---

# Knowledge base

What we've learned building with the Claude API, agents and AI tooling: research findings,
gotchas, fixes with versions, and the decisions behind them. It's written for people, tools and
LLM agents alike, and it's the family's source of truth for these topics
([decision 0004](decisions/0004-source-of-truth-for-claude-api-topics.md)).

This is a living document set. When something new is learned, add it to the topic page it
belongs to instead of starting a new file.

## Index

<!-- BEGIN GENERATED: kb-index (from front matter; run scripts/kb/build.py) -->
| Page | What's in it | Status |
|---|---|---|
| [anthropic/upstream-contributions.md](anthropic/upstream-contributions.md) | Gaps, API asks and doc fixes we could raise with Anthropic, with evidence | verified |
| [claude-api/](claude-api/README.md) | Models and model choice, prompt caching, rate limits, spend and keys per app, refusals and fallbacks | partial |
| [agents/](agents/README.md) | Claude Code, cloud sessions, MCP servers, skills, sub-agents and guardrails for agents that act | partial |
| [prompting/](prompting/README.md) | System prompts, audience-specific prompts and structured output that held up in real apps | partial |
| [evals/](evals/README.md) | Testing features built on LLMs: unit tests for guardrails, LLM-as-judge and regression checks | plan |
| [privacy-and-safety/](privacy-and-safety/README.md) | Keys and secrets, prompt injection, local-only designs and building AI features for kids | plan |
| [platforms/](platforms/README.md) | Hosting AI apps: serverless workers, databases, sign-in inside app wrappers, calling GitHub's API | verified |
| [learning/](learning/README.md) | Courses, docs, cookbooks and people worth following to learn how to build with AI | plan |
| [troubleshooting/](troubleshooting/README.md) | Errors hit with the Claude API, SDKs, agents and AI tooling: symptom, cause, fix and source | verified |
| [curation.md](curation.md) | How the KB stays current: the weekly digest, the prior-art check, the feedback loop, the freshness check and family alignment | verified |
| [experts.md](experts.md) | How we choose which people on the Claude API, agents and AI tooling the KB follows: the method, the scores and the list | verified |
| [decisions/](decisions/README.md) | Decision records (MADR): what was decided and why |  |
<!-- END GENERATED: kb-index -->

## Related knowledge bases

<!-- BEGIN GENERATED: family (from family.yaml; run scripts/kb/build.py) -->
| Knowledge base | Role | Focus | Source of truth for |
|---|---|---|---|
| [Nerdio HCL kit](https://github.com/nickprignano/nerdio-hcl/tree/main/docs/knowledge) | member | Nerdio Manager on Azure Virtual Desktop, deployed with Terraform and Packer | Nerdio Manager; the nerdio/nme provider; this kit's Terraform and Packer |
| AVD (repo not linked yet) | member | Azure Virtual Desktop itself | Azure Virtual Desktop platform; FSLogix; session host images in general |
| Liquidware (repo not linked yet) | member | Liquidware products on virtual desktops | Liquidware products |
| Private layer (repo not linked yet) | observer | The maintainer's private wisdom layer. It reads the family through this hub and sends directives here as pull requests; its contents stay private | Directives to the family; through docs/knowledge/directives.yaml |
<!-- END GENERATED: family -->

When a fact belongs to a sibling's topic, link to their page instead of copying it. When we learn
something they need, open an issue or PR on their repo with the evidence. See
[curation.md](curation.md#staying-aligned-with-the-family).

## Before you build something

Every change follows the [guardrails](../guardrails.md): no leaks, no secrets in chat, pull
requests only, and license rules.

Run the prior-art check first (`python3 scripts/kb/prior_art.py "<topic>"`, see
[curation.md](curation.md#prior-art-check-kb-prior-art)). It searches this KB, the sibling KBs and
GitHub, so you don't spend time on problems someone has already solved.

## How to add to it

Two ways in, both reviewed before anything merges:

- **Without editing files:** open a **Knowledge base feedback** issue (what worked, broke, went
  out of date or is missing), a **Known error** issue, or a **Suggest an expert to follow** issue.
  When a maintainer labels it `kb-accepted`, a workflow turns it into a pull request. See
  [curation.md](curation.md#feedback-loop-kb-feedback).
- **With a pull request:**
  - **A fact or gotcha:** add a bullet to the matching topic page. Say what happened, the fix,
    and the versions it applies to. Mark anything you haven't confirmed as *unverified*.
  - **A known error or an upstream ask:** add an entry to
    [troubleshooting/known-errors.yaml](troubleshooting/known-errors.yaml) or
    [anthropic/upstream.yaml](anthropic/upstream.yaml), not to the Markdown table.
  - **A decision:** copy [decisions/template.md](decisions/template.md) to the next number. A
    decision stays `proposed` until the maintainer says yes. If a decision is reversed, write a new
    record and set the old one's status to `superseded by NNNN`. Refer to a sibling's decision as
    `<project> 0012`, with a link.
  - **A new topic:** only when it doesn't fit an existing page. Give it front matter like the
    other pages; the index above picks it up.
  - When you change or re-check a page, update `last_reviewed` in its front matter, and `status`
    if it changed.
  - Run `python3 scripts/kb/build.py` and `python3 scripts/kb/validate.py` before pushing (see
    [Format](#format) for setup). CI runs both.

## Format

The KB uses open, common formats so people, tools and LLM agents can all read it. The format is
shared by every KB in the family, and this KB follows family format version 1.

- **Page front matter (YAML)** on every page: `title` (the same as the H1), `summary`, `topic`,
  `status` (`verified`, `partial`, `unverified` or `plan`) and `last_reviewed`, validated against
  [schema/page.schema.json](schema/page.schema.json).
- **Decision records in [MADR 4](https://adr.github.io/madr/) format,** with `status`, `date` and
  `decision-makers` in front matter ([schema/decision.schema.json](schema/decision.schema.json)).
- **Structured YAML** for the [known errors](troubleshooting/known-errors.yaml),
  [upstream asks](anthropic/upstream.yaml), [field reports](field-reports.yaml),
  [experts](experts.yaml) and the [family](family.yaml), each with a JSON Schema in
  [schema/](schema/page.schema.json). The Markdown tables are generated from them.
- **[`llms.txt`](../../llms.txt)** at the repo root, the [llms.txt](https://llmstxt.org) index that
  tells LLMs and agents what's here. It's generated too.

Generated parts sit between `BEGIN GENERATED` / `END GENERATED` comments; edit the source, not
the output. The scripts need Python 3.11+ with PyYAML and jsonschema:

```bash
pip install --user -r scripts/kb/requirements.txt
python3 scripts/kb/build.py && python3 scripts/kb/validate.py
```

## Keep it public-safe

This repo is public, so nothing here may identify a real account or project. Before committing,
check that your change has none of the following:

- API keys, tokens, or account, org, workspace or project IDs
- Domain names, email addresses, internal hostnames or URLs
- IP ranges from a real network (use RFC 5737 documentation ranges or `10.x` examples)
- Prompts, transcripts or data from a private app or a real user
- Employer, customer or private-project names

Use placeholders such as `<api-key>`, `<workspace-id>` and `example.com`. Write lessons as general
advice, not as a story about a specific app or account. Published identifiers that are the same for
everyone, such as model IDs and API versions, are fine.
