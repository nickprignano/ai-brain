---
title: "Learning AI"
summary: "Courses, docs, cookbooks and people worth following to learn how to build with AI"
topic: learning
status: plan
last_reviewed: 2026-10-29
sources:
  - https://github.com/anthropics/claude-cookbooks
---

# Learning AI

Where to learn: official courses and cookbooks, docs worth reading end to end, and the people the KB follows ([experts](../experts.md)). Courses and docs aren't written up yet.

## Cookbooks worth running

From [anthropics/claude-cookbooks](https://github.com/anthropics/claude-cookbooks), picked from the
weekly digests and checked against the commits on 2026-10-29:

- **[Agent security review](https://github.com/anthropics/claude-cookbooks/commit/a162e0184e71b60290808a43961a6cbc8060123c)**
  (`managed_agents/CMA_agent_security_review.ipynb`, 2026-10-17): reviews finished agent sessions
  after the fact. It turns Managed Agents sessions, Messages API logs or Agent SDK logs into
  transcripts, flags suspicious actions with rules in code, and only then has Claude review each
  session. The first two parts run offline, so the rules can be tried on your own logs with no
  model calls. A good fit for the secrets-touch and red-team work in
  [privacy and safety](../privacy-and-safety/README.md).
- **[OpenTelemetry tracing](https://github.com/anthropics/claude-cookbooks/commit/b2b0aa1ff7d8980b005b225d3802969c87bedad5)**
  (`observability/opentelemetry_tracing.ipynb`, 2026-10-14): how the Python SDK and the API emit
  spans and join them into one trace with the `traceparent` header, across streaming, the tool
  runner and a Managed Agents session, with OTLP export. It is the way to collect the per-request
  numbers [Measuring a model choice](../claude-api/README.md#measuring-a-model-choice) asks for.
