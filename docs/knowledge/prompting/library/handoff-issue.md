---
title: "Prompt: Draft a handoff issue for another project"
summary: "Has the sending project turn an ask into a decision-0012 handoff issue in the receiving repo, waiting for the owner's label"
topic: prompting
status: verified
last_reviewed: 2026-10-19
---

# Prompt: Draft a handoff issue for another project

**Use when** work decided in one Claude project has to be done by another project, in a repo
that project owns.

**Paste into** the sending project, the one where the work was decided.

**Run so far:** yes, to open decision 0011's rollout issues in five sibling repos (2026-10-19).

## Placeholders

| Placeholder | What goes in | Example |
|---|---|---|
| `{{ASK}}` | What the other project should do, in a sentence or a prompt from this library | adopt decision 0042 with the link check in block mode |
| `{{TO_PROJECT}}` | The receiving project's name | Tool project |
| `{{TO_REPOS}}` | The receiving repo or repos, `owner/name` | example/tool-kb, example/tool-deploy |
| `{{WAITS_ON}}` | PRs or issues that must merge or close first, or "nothing" | https://github.com/example/hub/pull/42 |
| `{{LABEL}}` | Optional: a label grouping a rollout | 0042 |

## The prompt

```text
Hand this to the {{TO_PROJECT}} project as decision-0012 handoff issues, one per repo:
{{TO_REPOS}}.

The ask: {{ASK}}

For each repo:
1. Use the repo's handoff issue template (.github/ISSUE_TEMPLATE/handoff.md). Title it
   "Handoff: <a few words>".
2. Fill in From (this project and its repo; from a private project, only "a private project"),
   To, The ask, Waits on ({{WAITS_ON}}) and Report back.
3. Write The ask to stand alone: the receiver reads only that issue, so include every link,
   rule and step it needs, and nothing that only makes sense in this conversation.
4. Label it `handoff-proposed`. [optional: Also label it {{LABEL}}.] Never add `handoff`: that
   label is my approval, and I add it by hand.
5. Don't open the issue yourself if this project is private, or a repo isn't one this environment
   can reach, or it's missing the template or the labels. Give me the full issue text to open by
   hand instead, and say why.

These issues are public: no employer, customer or private-project names, no account IDs, domains
or emails. Then give me the issue links and tell me which ones need my `handoff`
label.
```

## Notes

- **The `handoff` label is the owner's approval.** Claude projects act on GitHub as the owner's
  account, so nothing can tell a project's label from the owner's; the rule only holds if Claude
  never adds it. See [decision 0012](../../decisions/0012-family-format-handoff-issues.md).
- **A private project never opens the issue.** Decision 0012 has the owner open a handoff from a
  private project, and any handoff to a repo the sender can't reach, by hand.
- **One issue per repo.** A shared issue across repos can't be picked up and closed cleanly by
  one project.
- **Name the PR in Waits on when its merge is what matters.** A handoff issue closes when its
  PRs are opened, not merged.
- First used 2026-10-19 to roll out decision 0011 to five sibling repos.
