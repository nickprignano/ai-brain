---
title: "Prompt: Adopt a hub decision in a sibling project"
summary: "Asks a sibling project to record a hub decision as its own copy, install the machinery from the hub's export and pilot it"
topic: prompting
status: partial
last_reviewed: 2026-10-19
---

# Prompt: Adopt a hub decision in a sibling project

**Use when** the hub has accepted a family decision that every sibling has to carry out in its own
repos, such as a new check, hook or convention.

**Paste into** the sibling's project, one prompt per project. Better: send it as a `handoff`
issue in the sibling's repo with [Draft a handoff issue](handoff-issue.md), one issue per repo.

## Placeholders

| Placeholder | What goes in | Example |
|---|---|---|
| `{{DECISION}}` | The hub decision's number and a few words on it | 0042 (enforce a weekly link check) |
| `{{DECISION_URL}}` | The decision record's URL on the hub's main branch | https://github.com/example/hub/blob/main/docs/knowledge/decisions/0042-link-check.md |
| `{{HUB_REPO}}` | The hub's repo, `owner/name` | example/hub |
| `{{KB_REPO}}` | The sibling's KB repo | example/tool-kb |
| `{{OTHER_REPOS}}` | The sibling's repos with no KB of their own, or "none" | example/tool-deploy |
| `{{MODE}}` | How strict this sibling starts, and why | warn, because this repo is the reference implementation |
| `{{PILOT_END}}` / `{{REVIEW_DATE}}` | When the pilot ends and is reviewed | 2026-11-30 / 2026-12-01 |
| `{{STEPS}}` | What installing it means here, one numbered line each | turn on the link-check job; create the `no-links` label |
| `{{METRICS}}` | What each checkpoint's field report counts | PRs merged, how many the check failed, how many were waived |

## The prompt

```text
The family accepted {{HUB_REPO}} decision {{DECISION}}. Read it first:
{{DECISION_URL}}

This project is a pilot through {{PILOT_END}}, counted from when the change goes live here, with a
review on {{REVIEW_DATE}}. It starts in {{MODE}} mode. Please do this:

1. Record the decision in {{KB_REPO}} as this KB's own copy ("Also recorded in"
   {{HUB_REPO}} {{DECISION}}), status accepted, with the pilot dates and the mode.
2. Install the machinery from {{HUB_REPO}}'s template export (`python3 scripts/kb/export_template.py
   <empty folder>` on its main branch), not from memory and not by copying a sibling. The family
   scripts stay identical to the hub's apart from kb.toml.
3. {{STEPS}}
4. Repos with no KB of their own ({{OTHER_REPOS}}): install the same pieces there, pointing at
   {{KB_REPO}} as the KB they feed.
5. Exempt the family's own automation pull requests (digest, template sync, directives).
6. Open one pull request per repo. Don't merge them; I'll review.

Keep the guardrails: no employer, customer or real-estate specifics in a KB entry, a PR body, a
label reason or a commit. At each pilot checkpoint, add one field report to {{HUB_REPO}}:
{{METRICS}}. When you're done, tell me the steps only I can do.
```

## Notes

- **Install from the hub's export, every time.** Copying from a sibling or from memory is how
  family scripts drift apart. The template repo can lag the hub by a sync, so the hub's export is
  the safe source.
- **Pick the mode per sibling.** The reference implementation started in warn mode, the rest in
  block mode. Say why in `{{MODE}}`, so the receiver doesn't second-guess it.
- **A dated demo or deadline comes first.** When a sibling has one, add a line that nothing in the
  deadline work may wait on the new check, and how to waive it meanwhile.
- First used for [decision 0011](../../decisions/0011-family-format-enforced-kb-capture.md)
  (enforced KB capture) across three sibling projects, 2026-10-19.
