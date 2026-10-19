---
title: "Prompt: Research how a project could use a set of tools"
summary: "Research-and-proposal only: evaluates candidate tools against a project's real architecture and threat model and returns a ranked recommendation"
topic: prompting
status: verified
last_reviewed: 2026-10-19
---

# Prompt: Research how a project could use a set of tools

**Use when** a survey (often one from this KB) turned up tools or techniques, and a specific
project should work out which of them fit its own architecture before anyone installs anything.

**Paste into** the project that would use the tools, or send it as a handoff issue.

**Run so far:** not yet as written; a close earlier version was handed to a sibling project (2026-10-19).

## Placeholders

| Placeholder | What goes in | Example |
|---|---|---|
| `{{PROJECTS}}` | The systems to evaluate for | the build agents and the deploy pipeline |
| `{{GOAL}}` | What the tools should achieve, in a sentence | defend the agents from prompt injection and give operators better signal |
| `{{SURVEY}}` | Where the survey is, as a link | this KB's privacy-and-safety page, "Open-source AI tools for fighting bad actors" |
| `{{CANDIDATES}}` | Numbered areas, each with the candidates and what's already known about them (licences, costs, preview status, roles) | 1. Prompt-injection defense: tool A as the main control, tool B as a tripwire (GPL-3.0, so the idea, not the code) |
| `{{CONTEXT}}` | What to evaluate against | our architecture, threat model and open red-team findings |
| `{{HARD_RULES}}` | Constraints that rule options out | keyless auth only, no new AI vendor, least-privilege roles |

## The prompt

```text
Look into how {{PROJECTS}} could use these tools to {{GOAL}}. This is research and a proposal
only: no installs, and no changes to any account, subscription, deployment or spend setting.
Anything you propose goes in as a pull request or a design doc for my yes.

Source survey: {{SURVEY}}. Read it first and link to it rather than copying it.

Evaluate these against {{CONTEXT}}:

{{CANDIDATES}}

For each one, say where it would sit in our system, what it would have caught or prevented in our
own findings, and what it needs: roles, licences, data it must see, and what it costs where it
bills. Say plainly when something is only realistic for some of our deployments, and why.

Hard rules: {{HARD_RULES}}. Check every tool's licence before proposing to use its code; for
code with no licence or a copyleft one we can't meet, take the idea, not the code. No employer,
customer or tenant names in any repo, KB, commit or PR.

Deliver: a short ranked recommendation (adopt, pilot or skip, and why), the role and licence needs
of each, a rough cost note where it bills, and the first pull request you would open. Record what
you learn in this project's KB, and link to the survey instead of copying it.
```

## Notes

- **Carry the known facts into `{{CANDIDATES}}`.** Licence traps, preview status, billing and the
  roles a tool needs were found once in the survey; restating them in the prompt saves the
  receiver from rediscovering them, or missing them.
- **"Research and a proposal only" up front.** It stops a capable agent from installing a tool to
  try it.
- **Ask what each option would have caught in your own findings.** It turns a feature list into
  a ranking.
- Generalized from a prompt that took a 2026-10-19 security-tooling survey into a sibling
  project.
