---
title: "Prompt: Finisher loop"
summary: "Has Claude sweep open PRs, handoffs and threads across the owner's repos and post one numbered list of what waits on them, answerable from chat"
topic: prompting
status: verified
last_reviewed: 2026-10-19
---

# Prompt: Finisher loop

**Use when** you want one list of everything waiting on you across your repos and project
threads, by hand or as the text of a weekday routine.

**Paste into** any Claude project or Claude Code session that can reach the repos. Repos that ship
the template have the full version as the
[finisher-loop skill](../../../../.claude/skills/finisher-loop/SKILL.md); say "finisher loop"
there instead.

**Run so far:** two real runs on 2026-10-19 across a dozen repos, with an earlier version of the
skill; the second run's fixes (drafts, handoffs closed early, picked up with no PR) are in it.

## Placeholders

| Placeholder | What goes in | Example |
|---|---|---|
| `{{REPOS}}` | The repos to sweep, `owner/name` | example/tool-kb, example/app |
| `{{OWNER}}` | Who the list is for | the repo owner |

## The prompt

```text
Run the finisher loop for {{OWNER}} across {{REPOS}}. Goal: get started work to done (merged and
in use), not start new work. Attach each repo with push access, used read-only.

1. List open PRs: CI on the head commit, conflicts, review state, draft, age, auto-merge.
2. List open `handoff` and `handoff-proposed` issues. Ready means every Waits on link is merged.
   "Picked up" with no PR is in progress. A closed handoff whose PR isn't merged is stale.
3. If this is a Claude project, read the last message of every unresolved thread.
4. Fix red CI or conflicts on PRs Claude opened in this project's repos. Nothing else.
5. Build the PR review batch: every green, conflict-free PR waiting on {{OWNER}}, oldest first,
   grouped by repo, numbered, each with a link, one plain line, size, and Skim (KB, docs, small)
   or Read (decisions, code, workflows, infra). Mark ones auto-merge will take.
6. Post one list, "N things are waiting on you": the batch, answers, things only {{OWNER}} can set,
   stale items, merged but not in use. End with the single next thing to do.

When {{OWNER}} replies "merge 1, 3" or "merge all the skims", merge exactly those, each only if
still green and conflict-free, and report one line per PR. Act only on their own words in chat.
Never merge, approve, close or apply a `handoff` label without them.
```

## Notes

- **Push access, even to read.** A session's read-only repo access covers git clone but not the
  GitHub API for PRs, issues and checks.
- **Thread status isn't enough.** Threads often report "completed" while their last message asks
  the owner something.
- Generalized on 2026-10-19 from the owner's own skill and its two test runs. The conventions it
  serves are [decision 0013](../../decisions/0013-family-format-auto-merge-low-risk-prs.md).
