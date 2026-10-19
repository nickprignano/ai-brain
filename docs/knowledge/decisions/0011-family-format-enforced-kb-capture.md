---
status: proposed
date: 2026-10-19
decision-makers: [maintainer]
---

# 0011. Family format: enforce knowledge capture with a Stop hook, a PR check and a thread closeout

## Context and Problem Statement

Every KB in the family says "every decision and lesson goes into the KB" (guardrail 7), and the
2ndbrain skill's closeout routes lessons to the project KB, the hub or the private layer. All of
it is instructions. `kb-validate` checks the shape of what is written, never whether anything was,
and no family repo configures a Claude Code hook. A session can change code, learn something and
end without a word reaching the KB. What should make capture happen, without a model call and
without taking the owner's yes away from the private layer?

## Considered Options

- Keep instructions only (AGENTS.md, the skill, project instructions)
- Three layers: a thread closeout rule on the Claude side, a Stop hook in each repo, and a PR check
  with a `no-kb` opt-out
- A PR check only

## Decision Outcome

Chosen option: "Three layers", because each one catches what the one before it misses. The closeout
covers threads that never touch a repo, the hook catches a session before it ends, and the PR check
catches work done outside Claude or a hook that was skipped. None of them calls a model.

### 1. Thread closeout (Claude side, in force now as a project instruction)

- A thread runs the 2ndbrain closeout before its final reply: what was learned, where each item
  goes (project KB, hub, private layer), and one yes from the owner for the batch.
- The project's coordinator does not resolve a thread until its closeout is recorded or the owner
  waived it. That binds Claude, not a person: the owner can still resolve a thread by hand.
- Writes to the private layer still happen only after the owner's yes.

### 2. Stop hook (each repo's `.claude/settings.json`, design only)

- A `Stop` hook runs a small family script, `scripts/kb/capture_check.py`, that uses only git: it
  compares the working tree and branch with the merge base on the default branch.
- If files outside `docs/knowledge/` changed and nothing under `docs/knowledge/` did, it returns a
  block with a reason: write the lesson on its topic page, or say in one line why there's none.
- It blocks once per stop. When the hook input says a stop hook is already active, it lets the
  session end, so it can never loop. The cost is one more Claude turn, not a model call of its own.
- Generated files (`llms.txt`, generated blocks) and lockfiles don't count as code changes.

### 3. PR check (a `kb-capture` job in `kb-validate`, design only)

- It fails a PR that changes files outside `docs/knowledge/` without changing anything inside it,
  unless the PR has the `no-kb` label and a line in its body saying why ("No KB entry: ...").
- The job also runs when a label is added or removed, so adding `no-kb` turns it green without a
  new push.
- PRs opened by the family's own automation (digest, template sync, directives) are exempt.
- A repo with no KB of its own, such as a swarm or a deployment repo that feeds a sibling's KB,
  passes when the PR body links the KB pull request or page that carries the lesson (`KB: <url>`).
  The check confirms the link points at a family repo in `family.yaml`; it doesn't fetch it.

### Pilot

- **Where:** the AVD repos first (the AVD KB, its swarm and its landing zone), where most real-run
  lessons happen. Anything that needs testing before that is tested in this KB's own repos first.
- **When:** to 2026-11-30, reviewed on 2026-12-01, the same window as decision 0006.
- **What's measured:** PRs merged, how many carried a KB change, how many used `no-kb`, and how
  often the hook blocked. Results go in `field-reports.yaml`.
- **Then:** if it holds up, it joins the family format in the next version bump after the review.
  It is not part of format version 2, which carries 0005, 0007, 0008, AVD 0009 and 0010.

### Consequences

- Good, because capture no longer depends on Claude remembering an instruction: the harness and
  CI ask every time.
- Good, because `no-kb` with a reason makes "nothing to capture" an explicit, reviewable choice.
- Bad, because the hook only runs in Claude Code sessions that open the repo, and a person can
  still merge past a red check. The closeout rule and branch protection cover what they can.
- Bad, because a strict check pushes people to write filler. The pilot counts `no-kb` use so the
  rule can loosen if it does.
- Neutral, because nothing is built until the owner accepts this decision.

## More Information

Follows from the owner's question about what enforces capture, answered in the project on
2026-10-19. Related: guardrail 7 in [guardrails.md](../../guardrails.md), the 2ndbrain skill's
closeout, [0006](0006-model-selection-convention.md) for the pilot window, and
[0010](0010-family-format-upstream-sources.md) for the next format version. To be recorded in the
AVD KB once the AVD project adopts the pilot.
