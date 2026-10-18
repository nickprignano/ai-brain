---
status: proposed
date: 2026-10-18
decision-makers: [maintainer]
---

# 0006. One model-selection convention, piloted on the family, with per-project overrides

## Context and Problem Statement

The four projects in the family each pick Claude models on their own: in Claude project sessions
(the project chat and its threads), in apps that call the Claude API, and on Microsoft Foundry
when that's the path. The picks drift, nobody measures whether they're right, and a missing
Foundry quota has already forced one app onto a different path
([nerdio-hcl 0020](https://github.com/nickprignano/nerdio-hcl/blob/main/docs/knowledge/decisions/0020-claude-api-federation-for-the-chat.md)).
What should each layer default to, how does a project override it, how do we know a choice is
right, and what happens when quota or access is missing?

## Considered Options

- One convention with a default per kind of job, piloted on the four family projects, then
  promoted to every Claude project, with overrides recorded per project
- The most capable model everywhere, so nobody has to choose
- Each project chooses its own models with no shared default
- The cheapest model that works, chosen per request by a router

## Decision Outcome

Chosen option: "One convention with a default per kind of job, piloted first", because one
model at one effort can't be right for routing a chat message and for writing a Terraform module,
a per-project free-for-all is what we have now, and a router adds code and splits the prompt
cache (caches are per model) before we have numbers that say it pays. The facts behind the
defaults (model IDs, prices, Foundry availability and quota) are on the
[Claude API page](../claude-api/README.md#choosing-a-model), checked against Anthropic's and
Microsoft's docs on 2026-10-18.

Three rules hold in every layer:

- **Effort before model.** Change `effort` first, then the model. Lower effort on a stronger
  model often beats a weaker model at higher effort, and one model keeps one prompt cache.
- **Pin full model IDs in config, never aliases.** Aliases move under you, and not the same way
  on every provider (in Claude Code on Foundry, `opus` resolved to Opus 4.6 when Anthropic's API
  resolved it to Opus 5.5).
- **Keyless and least-privilege.** Apps sign in with a managed identity: workload identity
  federation to the Claude API, Entra ID to Foundry. No API key is stored, shown or pasted.

### Layer 1: Claude project sessions

| Role | Default | Why |
|---|---|---|
| Project chat (routing, short answers, memory) | Claude Sonnet 5.5, effort `low` | Answers in seconds and costs half of Opus; routing is cheap to get wrong, because a misrouted ask is corrected in one message |
| Threads (code, research, specs) | Claude Opus 5.5, effort `medium` | Anthropic's recommended default for agentic coding and knowledge work; `medium` is its default effort |
| Workers a thread starts for bulk reading or search | Claude Haiku 5.5 or Sonnet 5.5, effort `low` | Reading-heavy fan-out where the thread does the judging |

Bump a thread up one step at a time, effort first:

- To `high`: changes across several files or repos, anything that touches auth, secrets or
  spend, a decision record, or a second failed attempt at the same task.
- To `xhigh`: long autonomous runs and hard debugging, after `high` failed.
- To Claude Fable 5.1: only when Opus 5.5 at `high` has failed the same task twice, or for
  long-horizon research the user asks for by name. It costs 2.5 times Opus 5.5.

Move a thread down to Sonnet 5.5 at `low` for doc edits, link fixes, triage and lookups.

The user sets the defaults in each project's instructions (one line, for example "Start threads
on claude-opus-5-5 at medium effort"), because a Claude session changes its model or effort only
when the user asks for it. Inside a repo, `.claude/settings.json` (`model`, `effortLevel`) pins
Claude Code sessions for that repo.

### Layer 2: apps that call the Claude API

| Kind of job | Default | Why |
|---|---|---|
| Agent with tools that changes things (setup chat, deploy helpers) | Claude Opus 5.5, `medium` | Wrong tool calls are the costly failure; quality first |
| Chat or Q&A over given documents | Claude Sonnet 5.5, `low` | Latency is what people notice; quality holds at `low` for chat |
| Classify, extract, route, high volume | Claude Haiku 5.5, `low` | A twentieth of Sonnet's price. Keep prompts under 100,000 tokens, where its price goes up five times |
| Offline bulk work (nightly summaries, eval runs) | Sonnet 5.5 or Haiku 5.5 on the Batch API | Half price when nobody is waiting. The Claude API only: Foundry has no Batch API |
| Grading in evals (LLM as judge) | Sonnet 5.5, `low` | Rubric checks are narrow; spot-check 20 grades by hand before trusting it |

How to override: every app reads `<APP>_MODEL`, `<APP>_EFFORT` and `<APP>_MODEL_PROVIDER`
(`claude-api` or `foundry`) from its environment, with the table's defaults in code, and its
infrastructure code sets them as variables. On Foundry the model value is the deployment name, so
keep deployment names equal to the model ID.

When to switch an app's model:

- A new model comes out, or a price changes: run the app's eval set on the candidate at the same
  and one lower effort. Switch when the pass rate holds and the cost per completed task drops.
- A model's retirement date comes within six months (Opus 5.5 is "not sooner than
  2027-09-22").
- The measures below go bad two weeks in a row.

Handle `stop_reason: "refusal"` everywhere. On the Claude API, turn on server-side fallbacks
(`fallbacks: "default"`); Foundry doesn't support them, so use the SDK's client-side fallback
there.

### Layer 3: Microsoft Foundry and other paths

The primary provider is a per-app choice in config, and fallbacks follow these rules:

1. **Foundry quota missing or denied** (Claude Fable models start at zero quota; Opus, Sonnet
   and Haiku 5.5 start at 40 requests a minute on pay-as-you-go): use the Claude API with
   workload identity federation, as nerdio-hcl 0020 does.
2. **Foundry returns 429 under load:** back off and retry (the SDK retries twice by default),
   then send jobs marked as degradable (chat, Q&A) to the next model down. Jobs that change
   things never step down; they fail with a clear message.
3. **The Claude API can't be set up yet** (no Anthropic organization admin to create the
   federation rule): use Foundry if it has quota; otherwise the app reports it isn't connected.
   A stored API key is never the fallback unless a new decision record says why.
4. **A feature Foundry lacks** (Batch API, server-side fallbacks, Models API; on deployments
   hosted on Azure also code execution, Files API, Agent Skills and the newer web tools): use a
   deployment hosted on Anthropic, or the Claude API.
5. **Data must stay in the US:** a US Data Zone deployment on Foundry, or `inference_geo: "us"`
   on the Claude API, both at 1.1 times the price. Sonnet 5.5 has no Data Zone deployment yet.
6. **Claude Code on Foundry:** pin `ANTHROPIC_DEFAULT_OPUS_MODEL`, `ANTHROPIC_DEFAULT_SONNET_MODEL`
   and `ANTHROPIC_DEFAULT_HAIKU_MODEL` to full IDs, because its aliases there point at older models.

Other clouds (Amazon Bedrock, Google Cloud) are out of scope: the family uses no paid service
beyond Microsoft, Nerdio and Anthropic. Because provider and model are config, adding one later
is a config change and a new client class, not new app logic.

Least privilege on each path: on the Claude API, one federation rule per app that matches the
identity's exact object ID, with only the `workspace:inference` scope, in the app's own workspace
([0003](0003-claude-api-as-model-provider.md)). On Foundry, the app's managed identity gets one of
the roles Anthropic's docs name (Foundry User or Cognitive Services User) on the Foundry resource
only, and key-based (local) auth is turned off on the resource.

### Measuring whether the choice is right

Each app logs, per request, the model, effort, `usage` (input, output, cache read and cache write
tokens), `stop_reason` and latency, to the logs it already has. No new tool. From those:

- **Tokens and dollars per completed task**, not per request: a cheaper call that needs a retry
  isn't cheaper.
- **Failure rate:** tasks ending in `refusal`, `max_tokens`, a tool error or a user retry.
- **Cache hit rate:** cache read tokens over all input tokens. Near zero means something is
  breaking the cache.
- **p95 latency** for chat jobs.

For project sessions, the measure is the bump rate: the share of threads that had to move up a
model or effort, or needed the user to redo work. Anthropic's Console reports spend per workspace.

### Pilot, overrides and promotion

- **Pilot:** the four family projects (AI, Nerdio, AVD and Liquidware) from 2026-10-18 to
  2026-11-30.
- **Overrides:** a project that needs a different model for a kind of job writes a decision in
  its own KB titled "Model override: (job)" with the model, effort, the measure that justified it
  and a revisit date, and sets its config to match. The default here doesn't change for one
  project.
- **Reporting:** each project files its pilot numbers as a knowledge base feedback issue on this
  repo against the Claude API page, so results land in [field-reports.yaml](../field-reports.yaml)
  in one place. The maintainer's private notes read from there; nothing private flows back.
- **Success:** in at least three of the four projects, every app logs usage per task; the app
  failure rate is under 2% of tasks; jobs moved to a smaller model keep their eval pass rate at
  the same or lower cost per task; and fewer than one thread in five needs a bump.
- **Promotion:** at the review on 2026-12-01, if the success measures hold, the maintainer marks
  this decision accepted for every current and future Claude project, and the Layer 1 line goes
  into each project's instructions. If they don't, this record is revised with what the numbers
  showed.

### Consequences

- Good, because every project starts from the same defaults and changes them with evidence.
- Good, because the measures come from data each app already gets back from the API.
- Bad, because Sonnet in the project chat may misroute more than Opus would; the bump rate
  shows it, and the fix is one line in the project instructions.
- Bad, because apps gain three config values each.
- Neutral, because prices and IDs change; the facts live on one page with a review date, and
  this record changes only when a default does.

## More Information

Sources, checked 2026-10-18: Anthropic's
[models overview](https://platform.claude.com/docs/en/about-claude/models/overview),
[pricing](https://platform.claude.com/docs/en/about-claude/pricing),
[Claude in Microsoft Foundry](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry)
and [Claude Code model configuration](https://code.claude.com/docs/en/model-config), and
Microsoft's [Claude quotas and limits in Foundry](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/claude-models-quotas-limits).

*Unverified:* which of the two Foundry roles is the narrower one for inference only, and whether
a project chat's own model can be set from project settings rather than through its
instructions. Re-check both during the pilot.

A cross-project decision: recorded here as the source of truth
([0004](0004-source-of-truth-for-claude-api-topics.md)), with "Also recorded in" pointers in each
sibling's decisions. Revisit on 2026-12-01.
