---
title: "Claude API"
summary: "Models and model choice, prompt caching, rate limits, spend and keys per app, refusals and fallbacks"
topic: claude-api
status: partial
last_reviewed: 2026-10-18
sources:
  - https://platform.claude.com/docs/en/about-claude/models/overview
  - https://platform.claude.com/docs/en/about-claude/pricing
  - https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry
  - https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/claude-models-quotas-limits
  - https://code.claude.com/docs/en/model-config
---

# Claude API

What we've learned calling the Claude API from apps: choosing models, prompt caching, rate and
spend limits, keeping each app's spend apart, refusal handling and fallbacks. Asks that need an
Anthropic change go in [upstream asks](../anthropic/upstream-contributions.md).

## Spend and limits per app

When two apps both call the Claude API, give each its own Anthropic Console workspace.
Workspaces carry their own spend limits, rate limits and cost reporting. Separate API keys in one
workspace share all three, so keys alone don't stop one app from using up the other's budget
([decision 0003](../decisions/0003-claude-api-as-model-provider.md)).

- Have each app read its own environment variable for the key (for example
  `APPNAME_ANTHROPIC_API_KEY`), so a key can't be shared by accident.
- Checked against Anthropic's [workspaces](https://platform.claude.com/docs/en/build-with-claude/workspaces)
  and [Usage and Cost API](https://platform.claude.com/docs/en/build-with-claude/usage-cost-api)
  docs on 2026-10-18: spend limits and rate limits are set per workspace (never per key), can't be
  set on the Default Workspace, and can't exceed the organization's. Token usage can be filtered
  and grouped by API key, but the cost report groups by workspace, so a workspace per app is still
  the way to see and cap each app's spend. Prompt caches are also per workspace.

## Choosing a model

The family's defaults per kind of job, the override rule and the fallbacks are in
[decision 0006](../decisions/0006-model-selection-convention.md). This section holds the facts
they rest on. Checked against Anthropic's docs on 2026-10-18; re-check before relying on a price.

| Model | ID | Input $/MTok | Output $/MTok | Cache read $/MTok | Default effort | Latency |
|---|---|---|---|---|---|---|
| Claude Fable 5.1 | `claude-fable-5-1` | 10 | 50 | 0.25 | `high` | Slower |
| Claude Opus 5.5 | `claude-opus-5-5` | 4 | 20 | 0.20 | `medium` | Moderate |
| Claude Sonnet 5.5 | `claude-sonnet-5-5` | 2 | 10 | 0.10 | `high` | Fast |
| Claude Haiku 5.5 (prompt up to 100K tokens) | `claude-haiku-5-5` | 0.10 | 0.50 | 0.01 | `medium` | Fastest |
| Claude Haiku 5.5 (prompt over 100K tokens) | `claude-haiku-5-5` | 0.50 | 2.50 | 0.05 | `medium` | Fastest |

- All four have a 1M-token context window and 128K output tokens. Apart from Haiku 5.5, the
  whole window is billed at the standard rate.
- The Batch API is half price. A 5-minute cache write costs 1.25 times the input price.
- `inference_geo: "us"` costs 1.1 times the price.
- Every model ID is a pinned snapshot. Pin the full ID in config; aliases (in Claude Code, for
  example) move to newer models and don't move the same way on every provider.
- Opus 5.5 can't turn thinking off: lower `effort` instead. Sonnet 5.5 and Haiku 5.5 default to
  different efforts, so set `effort` explicitly when comparing them.
- Fable 5.1 needs 30-day data retention, so it isn't available under zero data retention.
- Retirement is "not sooner than" 2027-09-01 (Fable 5.1), 2027-09-22 (Opus 5.5), 2027-09-28
  (Sonnet 5.5) and 2027-10-07 (Haiku 5.5).

## Claude on Microsoft Foundry

Checked against Anthropic's Foundry page and Microsoft's quota page (updated 2026-09-22) on
2026-10-18.

- **Prices** are Anthropic's standard rates, billed through the Azure Marketplace in Claude
  Consumption Units (100 CCU is 1 USD), metered hourly and invoiced monthly.
- **Two hostings.** Hosted on Azure offers Opus 5.5, Opus 5, Opus 4.8, Sonnet 5.5, Sonnet 5,
  Haiku 5.5 and Haiku 4.5, in Global Standard or US Data Zone Standard. Hosted on Anthropic
  offers every model, Fable 5.1 included, in Global Standard only. Sonnet 5.5 is Global Standard
  only.
- **The model parameter is the deployment name.** It defaults to the model ID and can't be
  renamed later; keep it equal to the ID so config is the same on both paths.
- **Default quota on pay-as-you-go:** 40 requests, 40,000 input tokens and 8,000 output tokens a
  minute for Opus 5.5, Sonnet 5.5 and Haiku 5.5; zero for Fable 5 and 5.1. Quota is per
  subscription and model, shared by every Global Standard deployment across regions. Cache reads
  don't count toward the input limit. More quota goes through Microsoft's request form and isn't
  guaranteed: one trial tenant's requests were denied (nerdio-hcl 0020).
- **Missing on Foundry:** the Batch API, server-side fallbacks (use the SDK's client-side
  fallback), the Models API, the Admin API, Managed Agents and the advisor tool. Deployments
  hosted on Azure also lack code execution, the Files API, Agent Skills, programmatic tool
  calling and web tools newer than `web_search_20250305` and `web_fetch_20250910`; they return
  400.
- **Rate-limit headers:** Foundry doesn't send Anthropic's `anthropic-ratelimit-*` headers; use
  Azure Monitor.
- **Keyless sign-in:** turn on Entra ID for the resource and use a token provider for the scope
  `https://ai.azure.com/.default` with `AnthropicFoundry`. The identity needs Foundry User
  (formerly Azure AI User) or Cognitive Services User; without one, calls return 403.
  *Unverified:* which of the two is narrower for inference only.
- **Claude Code on Foundry:** its `opus`, `sonnet` and `haiku` aliases point at Opus 4.6,
  Sonnet 4.5 and Haiku 4.5 there. Set `ANTHROPIC_DEFAULT_OPUS_MODEL` and its siblings to full IDs.

## Measuring a model choice

Log, per request, the model, effort, `usage` (input, output, cache read and cache write tokens),
`stop_reason` and latency, in the logs the app already has. Then track per kind of job:

- tokens and dollars per completed task, counting retries and extra turns
- failure rate: `refusal`, `max_tokens`, tool errors and user retries, over all tasks
- cache hit rate: cache read tokens over all input tokens
- p95 latency, for anything a person waits on

Compare candidates on the app's own eval set (see [evals](../evals/README.md)), the same tasks at
the same and one lower effort, before changing a default.
