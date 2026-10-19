---
status: proposed
date: 2026-10-19
decision-makers: [maintainer]
---

# 0013. Family format: GitHub work conventions, with low-risk pull requests merging themselves on green

## Context and Problem Statement

Building is no longer the slow step; merging is. On 2026-10-19 about a dozen green PRs waited on
the owner, most of them knowledge base pages that only needed a skim. Every change still has to go
through a PR with green CI ([guardrails](../../guardrails.md) rule 3), and decisions, code and
anything that changes a real account still need the owner's yes. How do the low-risk PRs land
without the owner clicking merge on each one, without loosening review for the rest?

## Considered Options

- Keep merging every PR by hand
- Batch review only: one list of ready merges each morning
- Auto-merge for a fixed class of low-risk PRs, decided by a workflow from the changed paths
- Let threads merge their own PRs when they judge them low-risk

## Decision Outcome

Chosen option: "Auto-merge for a fixed class of low-risk PRs", because the class is checked by a
workflow from the files a PR changes, not judged by the thread that wrote it, and GitHub's own
auto-merge still waits for every required check. It comes with two habits, and the three together
are the convention for GitHub work in every one of the owner's repos, family or not:

- **Low-risk PRs merge themselves** (sections 1 to 5).
- **Everything else is batch-reviewed.** The weekday open-work list groups the PRs ready for the
  owner, so they're cleared in one sitting. A thread doesn't chase the owner for each one.
- **Fewer, larger PRs.** One PR per piece of work, not one per step, with a body the owner can
  skim: what changes for them first, then how. Don't split work into small PRs to make each review
  smaller.

### 1. What's low-risk

- A PR is low-risk when **every changed file** (renames under both names) matches the repo's
  `auto_merge_paths` and none matches a fixed deny list that settings can't widen.
- The default set is the knowledge base: `docs/knowledge/**` and `llms.txt`. A repo may widen it
  to its other docs (this one uses `docs/**`, `README.md` and `llms.txt`).
- **Never low-risk,** whatever the settings say: decision records, `directives.yaml`,
  `family.yaml`, `kb.toml`, the JSON schemas, `curation.md`, the guardrails, the family spec,
  `template/`, `scripts/`, `skills/`, `LICENSE`, `NOTICE`; agent instructions and repo settings at
  any depth (`.github/`, `.claude/`, `AGENTS.md`, `CLAUDE.md`, `SKILL.md`, `CODEOWNERS`, Cursor
  rules); and anything that looks like code, infrastructure, config or a web page (`*.py`, `*.ts`,
  `*.sh`, `*.ps1`, `*.bicep`, `*.tf`, `*.json`, `*.toml`, `*.html`, `*.svg`, Dockerfiles, Makefiles
  and similar), matched without regard to case. The list is in `scripts/kb/auto_merge.py`. A repo
  can keep more for the owner with `auto_merge_deny`.
- The repo owner's account opened it, from a branch of the same repo, into the default branch, and
  it isn't a draft.
- It doesn't carry the `no-auto-merge` label. Anyone, Claude included, adds that label to keep a
  PR for the owner.

### 2. How it works

- The `kb-auto-merge` workflow runs on every PR event. It runs from the base branch
  (`pull_request_target`), reads only the PR's list of changed files from the API and never checks
  out or runs the PR's code, so a PR can't change the rule it's judged by.
- Eligible: it turns on GitHub's auto-merge (merge commit, pinned to the head commit it judged).
  Not eligible: it turns auto-merge off if it was on. A push that adds a risky file turns it off.
- Anything it can't read makes the PR ineligible, and a failed run still turns auto-merge off. It
  never merges anything itself.
- Threads never turn on auto-merge themselves, by tool or by hand; the workflow is the only
  route. This is a rule Claude keeps, like the `handoff` label in
  [0012](0012-family-format-handoff-issues.md), because Claude acts as the owner's account.

### 3. What the owner sets, once per repo

In this order, because the workflow is live as soon as it merges:

1. Merge the workflow with `auto_merge = "off"` (the template ships it off).
2. Repo settings: **Allow auto-merge** on, and a branch ruleset on the default branch requiring
   the status checks the repo actually runs on every PR: `auto-merge` always, plus `validate`,
   `gitleaks` and `kb-capture` where they exist. A required check that never reports holds every
   PR, so a repo without a KB doesn't require `validate`. No required review, because the owner
   can't approve their own PRs. Add the repository admin role to the ruleset's bypass list, for
   pull requests only, so the owner can still merge PRs whose checks never run (below).
3. Then turn on `auto_merge = "on"` in `docs/knowledge/kb.toml` (or `.claude/kb-capture.toml` in a
   repo without a KB) with its own PR, which the owner merges.

`auto-merge` must be required: it re-runs on every push, so the PR can't merge on a new head
before the workflow has judged it. It only guarantees that; it passes even for a PR that isn't
low-risk, so it never blocks the owner's own merge.

### 4. Stopping it

- `KB_PAUSED` or a family directive pausing `kb-auto-merge` ([0008](0008-family-format-maintainer-directives-and-pause-switch.md))
  stops new auto-merges at once; PRs it already armed are turned off on their next event.
- `auto_merge = "off"` turns it off for a repo; switching off "Allow auto-merge" turns it off
  everywhere at once.

### 5. Rollout to the owner's other repos

- Every repo adopts through a `handoff` issue the owner approves
  ([0012](0012-family-format-handoff-issues.md)), and turns auto-merge on with its own PR.
- A KB repo takes the workflow and script from the template export. A repo without a KB (an app,
  a swarm, a deployment repo) copies `.github/workflows/kb-auto-merge.yml` and
  `scripts/kb/auto_merge.py`, sets its paths in `.claude/kb-capture.toml`, and adds the
  conventions line to its `AGENTS.md`.
- App repos auto-merge only their docs (for example `docs/**` and `README.md`), never code.
- Repos that hold an employer's or customer's infrastructure keep the default: only their KB
  paths, never code, infra or pipeline files.

### Consequences

- Good, because KB PRs land on green without the owner, and the owner's review goes to decisions
  and code.
- Good, because the class is fixed in code and checked from the base branch, not judged by the
  author.
- Bad, because a wrong fact on a KB page can land without a human read. Validation, leak patterns
  and gitleaks still run, and freshness and feedback catch errors afterwards.
- Bad, because GitHub can't tell the owner from Claude; "threads never arm auto-merge by hand" is a
  rule Claude keeps, not a check.
- Bad, because nothing stops a session from merging by hand or arming auto-merge itself, since it
  acts as the owner. The workflow only decides which PRs it arms, and turns off auto-merge on any PR
  that isn't low-risk, including one the owner armed in the web UI.
- Bad, because PRs the family's own workflows open with `GITHUB_TOKEN` (feedback appends) don't
  start other workflows, so their required checks never report. The owner merges them through the
  admin bypass, or closes and reopens them to run the checks.
- Neutral, because merges made by the workflow's token don't start push-triggered workflows on the
  default branch; the same checks already ran on the PR. A repo that deploys on push to its default
  branch only auto-merges paths that don't need a deploy.
- Neutral, because it uses merge commits; a repo that requires linear history changes `--merge` in
  its copy of the workflow.

## More Information

Asked for by the owner on 2026-10-19 ("agree with the first 2, im fine with skimming big changes so
theres fewer"), then for the AVD family of projects, then "as conventions for all gh work
across all of my projects". Built in `.github/workflows/kb-auto-merge.yml`
and `scripts/kb/auto_merge.py`, both in the template export. `kb-validate` lost its paths filter on
pull requests so it can be a required check.

Red teamed with Fable before review (2026-10-19). Changed as a result: agent-instruction files,
`CODEOWNERS` and settings folders are denied at any depth, not just the root; the deny list ignores
case (`Deploy.PS1`) and gained web pages and more languages; only PRs into the default branch
qualify; a failed run still turns auto-merge off; a missing script means ineligible; ai-brain ships
`"off"` and the setup order is written down; the bypass for bot PRs, the per-repo required-check
list and the limits of the identity check are stated. To confirm on the first real PR: that the
`auto-merge` check attaches to the PR's head commit, as `pull_request_target` checks normally do.

Options not chosen:

- **Merge everything by hand:** the bottleneck this fixes.
- **Batch review only:** kept for everything else, but on its own every KB page still waits.
- **Threads merge their own PRs:** the author would be judging its own risk, and nothing would stop
  a code change from being called low-risk.
