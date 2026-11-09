---
title: "Learning AI"
summary: "Courses, docs, cookbooks and people worth following to learn how to build with AI"
topic: learning
status: verified
last_reviewed: 2026-10-29
---

# Learning AI

Where to learn: official courses and cookbooks, docs worth reading end to end, and the people the KB follows ([experts](../experts.md)). Only the first finds are written so far.

## Cookbooks

Anthropic's [cookbook repo](https://github.com/anthropics/claude-cookbooks) added two recipes in
October 2026 that match work in this family (from the 2026-10-19 digest):

- **Agent security review** for Managed Agents
  ([commit](https://github.com/anthropics/claude-cookbooks/commit/a162e0184e71b60290808a43961a6cbc8060123c)):
  compare with the red-team patterns on the [agents page](../agents/README.md#swarms-and-multi-agent-patterns).
- **OpenTelemetry tracing**
  ([commit](https://github.com/anthropics/claude-cookbooks/commit/b2b0aa1ff7d8980b005b225d3802969c87bedad5)):
  a way to get the per-request log that [measuring a model choice](../claude-api/README.md#measuring-a-model-choice)
  asks for.

In November 2026 (from the 2026-11-09 digest):

- **Latency optimization**
  ([commit](https://github.com/anthropics/claude-cookbooks/commit/41ce172f08f0f17783fb41d75267ff72fa8b33fc)):
  applies each latency setting on the Claude API to a mock agent, measures time to first and last
  token and accuracy, and picks the fastest setup that still meets an accuracy bar. Claude Code
  v2.1.319 adds `/claude-api latency-optimize`, which does the same against your own code and eval.
- The cookbooks now use Haiku 5.5 and the 2.0 SDK
  ([commit](https://github.com/anthropics/claude-cookbooks/commit/785d7a06457b3413727f386b9c470083feb23c49)).
