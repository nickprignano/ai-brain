---
status: proposed
date: 2026-10-18
decision-makers: [maintainer]
---

# 0003. The Claude API is the model provider, with a separate workspace per app

## Context and Problem Statement

The guardrails say a paid third-party service needs a decision saying why free options fell short.
Several of the maintainer's apps and sibling projects call a hosted model. Which provider do they
use, and how is spend kept apart between apps?

## Considered Options

- The Claude API, with one Console workspace per app
- The Claude API, with one shared workspace and a key per app
- Open-weight models self-hosted, to avoid a paid API
- Several providers behind an abstraction layer

## Decision Outcome

Chosen option: "The Claude API, with one Console workspace per app", because the apps depend on
capabilities the free and self-hosted options didn't match for this work, and workspaces carry
their own spend limits, rate limits and cost reports, while keys in one workspace share them.

### Consequences

- Good, because one app can't use up another's budget or rate limit.
- Good, because each app reads its own key variable, so a key can't be shared by accident.
- Bad, because it's a paid dependency; spend is watched per workspace.
- Neutral, because the KB's own tooling never calls the API.

## More Information

*Unverified:* whether cost reports can now be grouped by key as well as by workspace. Re-check
against Anthropic's Console docs. Related: [nerdio-hcl 0020](https://github.com/nickprignano/nerdio-hcl/blob/main/docs/knowledge/decisions/0020-claude-api-federation-for-the-chat.md).
