---
title: "Claude API"
summary: "Models and model choice, prompt caching, rate limits, spend and keys per app, refusals and fallbacks"
topic: claude-api
status: partial
last_reviewed: 2026-10-17
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
- *Unverified:* this was a recommendation made while setting up a second app, not tested end to
  end. Re-check the Console docs on whether cost reports can now be grouped by key, and on
  per-workspace limits.
