---
title: "Claude API"
summary: "Models and model choice, prompt caching, rate limits, spend and keys per app, refusals and fallbacks"
topic: claude-api
status: verified
last_reviewed: 2026-10-29
sources:
  - https://platform.claude.com/docs/en/about-claude/models/overview
  - https://platform.claude.com/docs/en/about-claude/pricing
  - https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry
  - https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/claude-models-quotas-limits
  - https://code.claude.com/docs/en/model-config
  - https://docs.x.ai/developers/models.md
  - https://docs.x.ai/developers/faq/security
  - https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/models-sold-directly-by-azure-region-availability
  - https://ai.google.dev/gemini-api/terms
  - https://dev.meta.ai/legal/terms-of-service
  - https://developers.openai.com/api/docs/guides/safety-checks/under-18-api-guidance
  - https://developers.cloudflare.com/workers-ai/platform/data-usage/
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
  docs on 2026-10-29: spend and rate limits are set per workspace (the docs name no per-key
  limit), can't be higher than the organization's, and a spend limit can't be set on the Default
  Workspace. Token usage can be filtered and grouped by API key, but the cost report groups only
  by workspace or description, so a workspace per app is still the way to see and cap each app's
  spend. Prompt caches are per workspace on the Claude API and Foundry (per organization on
  Bedrock and Google Cloud).
- The Python SDK went to 2.0.0 on 2026-10-21 for API version `2026-10-21`, its one breaking
  change; 2.2.0 added usage and cost reports by dimension
  ([changelog](https://github.com/anthropics/anthropic-sdk-python/blob/main/CHANGELOG.md)). Pin
  the SDK's major version and read the changelog before a major bump.

## Choosing a model

The family's defaults per kind of job, the override rule and the fallbacks are in
[decision 0006](../decisions/0006-model-selection-convention.md). This section holds the facts
they rest on. Checked against Anthropic's [models](https://platform.claude.com/docs/en/about-claude/models/overview),
[pricing](https://platform.claude.com/docs/en/about-claude/pricing) and
[deprecations](https://platform.claude.com/docs/en/about-claude/model-deprecations) pages on
2026-10-29; re-check before relying on a price.

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
2026-10-29.

- **Prices** are Anthropic's standard rates, billed on the Azure bill in Claude Consumption
  Units, metered hourly and invoiced monthly in arrears; CCUs aren't prepaid credits. The CCU
  price is on Anthropic's separate Foundry pricing page.
- **Two hostings.** Hosted on Azure offers Opus 5.5, Opus 5, Opus 4.8, Sonnet 5.5, Sonnet 5,
  Haiku 5.5 and Haiku 4.5, in Global Standard or US Data Zone Standard. Hosted on Anthropic
  offers every model on Foundry, Fable 5.1 included (Mythos models are limited availability), in
  Global Standard only. Sonnet 5.5 is Global Standard
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
  `https://ai.azure.com/.default` with `AnthropicFoundry`. Anthropic's page names Foundry User
  (formerly Azure AI User) or Cognitive Services User. Use
  Foundry User on the Foundry resource: Microsoft's Foundry RBAC page calls it the
  least-privilege role and advises against roles starting with "Cognitive Services" for Foundry
  ([Foundry RBAC](https://learn.microsoft.com/en-us/azure/foundry/concepts/rbac-foundry), checked
  2026-10-18). Anthropic's page gives the two roles as examples ("such as") and says a 403 means
  the account "might lack" permissions.
- **Claude Code on Foundry:** its `opus`, `sonnet` and `haiku` aliases point at Opus 4.6,
  Sonnet 4.5 and Haiku 4.5 there (Bedrock and Google Cloud: Opus 5.5, Sonnet 4.5, Haiku 4.5;
  [model config](https://code.claude.com/docs/en/model-config), checked 2026-10-29). Set
  `ANTHROPIC_DEFAULT_OPUS_MODEL` and its siblings to full IDs.

## Other model families

Which second family the apps use, and for what, is
[decision 0009](../decisions/0009-second-model-family.md). These are the facts behind it, checked on
the providers' own pages on 2026-10-19; re-check before relying on them.

- **What Claude doesn't do.** It reads images and PDFs but can't create or edit images, takes no
  video or audio, and has no embedding model (Anthropic points to Voyage).
- **xAI.** Text models `grok-4.7` ($2/$6 per MTok; also `grok-4.6` and `grok-4.5` at that price)
  and `grok-4.3` ($1.25/$2.50), each doubling for prompts of 200K tokens or more (checked
  2026-10-29); image, video
  and speech models on the same API. No training on API data; requests kept 30 days by default,
  with a zero-retention switch. Chat Completions is marked legacy in favour of the Responses API.
- **Grok on Azure.** Foundry sells `grok-4.3`, `grok-4.6`, `grok-4.7` and `grok-4.20` (Global
  Standard in US, Canada and Brazil regions; Data Zone in US regions). Text only: no Grok Imagine.
- **Ruled out for apps children use, by terms.** The Gemini API and Meta's own Model API (now
  serving Meta's Muse models) both require users to be 18 and bar products aimed at or likely used
  by under-18s. ElevenLabs requires 18. OpenAI bars personal data of under-13s without zero
  retention, which needs sales approval. Mistral bars personal data of under-13s.
- **Retired lately.** OpenAI's Sora 2 and Videos API (2026-09-24); Imagen 4 on the Gemini API
  (2026-08-17); the Gemini API's Veo 3.1 previews (2026-10-22). Check deprecation pages first.
- **Cloudflare Workers AI** doesn't train on or keep request data unless AI Gateway logging is on,
  and hosts Llama Guard 3, FLUX image models and Whisper.

## Measuring a model choice

Log, per request, the model, effort, `usage` (input, output, cache read and cache write tokens),
`stop_reason` and latency, in the logs the app already has. Then track per kind of job:

- tokens and dollars per completed task, counting retries and extra turns
- failure rate: `refusal`, `max_tokens`, tool errors and user retries, over all tasks
- cache hit rate: cache read tokens over all input tokens
- p95 latency, for anything a person waits on

Compare candidates on the app's own eval set (see [evals](../evals/README.md)), the same tasks at
the same and one lower effort, before changing a default.
