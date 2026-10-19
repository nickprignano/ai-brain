---
title: "Prompt library"
summary: "Reusable, generalized prompts for the work and research we do: paste one, fill its placeholders, run it"
topic: prompting
status: verified
last_reviewed: 2026-10-19
---

# Prompt library

Prompts that Claude wrote for real work in this family and that are worth using again, each
generalized: the specifics are replaced by `{{PLACEHOLDERS}}`. Copy the fenced block from a page,
fill in the placeholders and paste it where the page says. The rest of the
[prompting](../README.md) page holds the lessons; this folder holds the prompts themselves.

Unlike topic pages, each prompt has its own file, so a prompt can be linked, copied and revised on
its own. Each page's **Run so far** line says whether the prompt has been used in a real run as written,
only as a close earlier version, or not yet. `status` keeps its usual meaning: the page's facts
(the decisions and rules it cites) have been checked.

## Prompts

<!-- BEGIN GENERATED: folder-index (from front matter; run scripts/kb/build.py) -->
| Page | What's in it | Status |
|---|---|---|
| [Prompt: Adopt a hub decision in a sibling project](adopt-family-decision.md) | Asks a sibling project to record a hub decision as its own copy, install the machinery from the hub's export and pilot it | verified |
| [Prompt: Apply red-team findings in another project](apply-red-team-fixes.md) | Hands a red-team findings file to the project that owns the design, to fix, accept or dispute each finding through pull requests | verified |
| [Prompt: Draft a handoff issue for another project](handoff-issue.md) | Has the sending project turn an ask into a decision-0012 handoff issue in the receiving repo, waiting for the owner's label | verified |
| [Prompt: Survey a tool landscape for the KB](landscape-survey.md) | Has Claude survey open-source and vendor tools in an area, check licences and dates, red team the result and add it to the KB | verified |
| [Prompt: Standing instructions for a Claude project](project-instructions.md) | Project-instruction lines the owner pastes into a new Claude project: model, red team, closeout, handoffs and guardrails | verified |
| [Prompt: Red team a design or decision](red-team.md) | Has a second model attack a design, spec or decision record, returning numbered findings with severity, a fix and what's acceptable as is | verified |
| [Prompt: Research how a project could use a set of tools](research-proposal.md) | Research-and-proposal only: evaluates candidate tools against a project's real architecture and threat model and returns a ranked recommendation | verified |
| [Prompt: Thread closeout](thread-closeout.md) | The closeout a thread runs before its final reply: lessons to the project KB, and to shared or private layers only after the owner's yes | verified |
| [Prompt: Work the handoffs](work-the-handoffs.md) | Has a receiving project check its repos' handoff issues and pick up the live ones, following decision 0012's pickup rules | verified |
<!-- END GENERATED: folder-index -->

Elsewhere in this repo: [Adding a KB to this family](../../../2ndbrain/new-family-kb.md) has the
prompt that sets up a new family KB. It stays there, next to the steps it belongs to.

## Using a prompt

- **Fill every placeholder.** A `{{NAME}}` left in a pasted prompt is a bug. Optional lines are
  marked `[optional: ...]`; delete them or fill them in.
- **Across projects, send it as a handoff issue.** When the prompt is for another Claude project,
  put it in the "The ask" section of a `handoff` issue in that project's repo
  ([decision 0012](../../decisions/0012-family-format-handoff-issues.md)) instead of pasting it
  into its chat. [Draft a handoff issue](handoff-issue.md) does the wrapping.
- **The output is public when the repo is.** The [guardrails](../../../guardrails.md) apply to
  what goes in a placeholder: no employer, customer or private-project names, and nothing from a
  private app or a real user.

## Adding a prompt

When a thread writes a prompt that will be useful again, add a generalized copy here in the same
pull request as the work, or the next one:

1. Make it stand alone: the reader has only this prompt, not the conversation that produced it.
2. Replace every specific with a `{{PLACEHOLDER}}` in capitals, and keep the shape of the ask:
   the goal, the hard rules, what to deliver and where it goes. Drop dates and numbers that only
   mattered once.
3. Copy the layout of an existing page: front matter (`topic: prompting`), **Use when**,
   **Paste into**, **Run so far**, a placeholder table with a made-up example per row, the prompt
   in a ` ```text ` block, and notes on what made it work.
4. Check it against the [guardrails](../../../guardrails.md): no employer, customer or
   private-project names, no account IDs, domains or emails, no secrets, and nothing from a
   private app, a real user or a private layer.
5. Run `build.py` so the table above picks it up, then `validate.py`.

If a prompt already here covers the job, improve that page instead of adding a near copy.
