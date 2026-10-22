---
status: proposed
date: 2026-10-22
decision-makers: [maintainer]
---

# 0019. Every repo Claude works in has an AGENTS.md with the four change rules

## Context and Problem Statement

The owner works with Claude across many repos and several Claude projects, not only the knowledge
bases in this family. The family's `AGENTS.md` already carries the rules agents follow, including
four rules for making a change, after the community "Karpathy guidelines"
([agents page](../agents/README.md#the-karpathy-guidelines)). App repos, sites and older repos
have no `AGENTS.md`, or keep their rules only in a `CLAUDE.md` that other agents don't read. So an
agent's habits depend on which repo it lands in. How do the same rules reach every repo the owner
works on with Claude?

## Considered Options

- Leave it to each repo
- Put the rules only in the owner's account-wide Claude preferences
- A standing convention: every repo has an `AGENTS.md` with the four rules, any `CLAUDE.md`
  imports it, and the repo audit flags the gap

## Decision Outcome

Chosen option: "A standing convention", because a file in the repo travels with it to every coding
agent that reads `AGENTS.md` and every Claude Code session, and the [repo audit](../../../scripts/kb/repo_audit.py) can check a file but can't
check a chat setting.

- **Scope: Claude-wide.** Every repo the owner works on with Claude, in any Claude project, family
  or not, public or private. A repo can opt out only with the audit's `no-conventions-audit` topic
  (for one Claude never touches) or by being archived; dormant repos get one or the other before
  the rollout, so the audit lists only real gaps. The audit sees repos the owner's account owns;
  repos in an organization are checked by hand. Only the root `AGENTS.md` and the root and
  `.claude/` `CLAUDE.md` count; nested ones and a `CLAUDE.md` in a parent folder on someone's disk
  are out of scope.
- **One file, read by everyone.** Rules live in `AGENTS.md` at the repo root, the file other coding
  agents read. Claude Code reads `AGENTS.md` itself, but only when the repo has no `CLAUDE.md`
  (and not in older versions or some sessions), so a repo keeps a `CLAUDE.md` that is the one line
  `@AGENTS.md` (or a symlink to it). A repo whose rules sit in `CLAUDE.md` today moves them into
  `AGENTS.md`.
- **What it holds, at least:** the guardrails that apply to the repo (no secrets, IDs or private
  names; changes as pull requests; the owner's yes for real accounts and spend), and a "How to make
  a change" section with the four rules: say what you assumed, write the least code that does the
  job, touch only what the task needs, and name the check that proves it's done. The family's own
  [AGENTS.md](../../../AGENTS.md) and the 2ndbrain template carry them already; any other repo
  starts from the [Add an AGENTS.md prompt](../prompting/library/add-agents-md.md).
- **The repo's own rules win** where they're stricter, or where the repo is deliberately different
  (a private notes repo that commits straight to its default branch says so in its `AGENTS.md`).
  The four rules are a floor, not a replacement for what a repo already says.
- **Rollout by handoff.** Repos the deciding project works in get a pull request each. Repos that
  belong to another Claude project get one handoff issue per project
  ([0012](0012-family-format-handoff-issues.md)), listing its repos, filed only after the owner's
  yes. An issue in a public repo names only public repos; one that covers private repos goes in a
  private repo of that project, or by hand.
- **Outside repos.** Claude projects with no repo get the rules as a line in their project
  instructions ([prompt](../prompting/library/project-instructions.md)). The owner may also paste
  a short version into the account's personal preferences; that's an owner step, not checked.
- **Checked.** `repo_audit.py` reports `change-rules` drift for any audited repo whose `AGENTS.md`
  lacks the section (its heading and the first rule's opening words), or that has a `CLAUDE.md`
  without an `@AGENTS.md` line or symlink, whether or not the repo has adopted
  the rest of the conventions.

### Consequences

- Good, because every agent in every repo reads the same four rules, and they're visible and
  editable in the repo instead of implied.
- Good, because the audit turns "every repo" into a list the owner can work through.
- Bad, because each repo gets a copy, and copies drift. The audit checks only that the section
  exists, not its wording; a reworded rule here reaches other repos by handoff, not by sync.
- Bad, because the rules trade a little speed for caution, which the source says too.

## More Information

- Source of the four rules: [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills)
  (MIT per its README), a distillation of [Andrej Karpathy's post of 2026-01-26](https://x.com/karpathy/status/2015883857489522876)
  on the mistakes LLMs make when coding. Our wording differs on purpose for unattended agents; see
  the [agents page](../agents/README.md#the-karpathy-guidelines).
- How Claude Code picks between the two files: [memory docs, "AGENTS.md"](https://code.claude.com/docs/en/memory#agents-md)
  (checked 2026-10-22: it reads `AGENTS.md` only with no `CLAUDE.md` present, from v2.1.277).
- Revisit if every session Claude runs in reads `AGENTS.md` reliably, so the one-line `CLAUDE.md`
  can go, or if the copies drift enough to need a sync.
