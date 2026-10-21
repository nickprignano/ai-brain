---
title: "Agents and Claude Code"
summary: "Claude Code, cloud sessions, MCP servers, skills, sub-agents and guardrails for agents that act"
topic: agents
status: partial
last_reviewed: 2026-10-21
sources:
  - https://code.claude.com/docs/en/costs
  - https://code.claude.com/docs/en/model-config
  - https://support.claude.com/en/articles/9797557-usage-limit-best-practices
  - https://www.sourcepulse.org/projects/28283027
  - https://lobehub.com/mcp/administrativetrick-obsidian-mcp
  - https://pypi.org/project/obsidian-mnemo/
  - https://www.verdent.ai/guides/obsidian-mcp-server
  - https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/automatically-merging-a-pull-request
  - https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows
  - https://claude.com/docs/connectors/building/authentication
  - https://claude.com/docs/connectors/building/lazy-authentication
  - https://github.com/cloudflare/workers-oauth-provider
  - https://developers.cloudflare.com/cloudflare-one/access-controls/ai-controls/secure-mcp-servers/
  - https://docs.x.ai/developers/management-api-guide.md
  - https://docs.x.ai/console/billing.md
  - https://github.com/anthropics/skills
  - https://skills.sh/anthropics/skills
  - https://github.com/obra/superpowers
  - https://github.com/trailofbits/skills
  - https://github.com/forrestchang/andrej-karpathy-skills
  - https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets
  - https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/troubleshooting-rules
  - https://docs.github.com/en/rest/repos/rules
  - https://github.com/github-community-projects/safe-settings
  - https://github.com/repository-settings/app
  - https://github.com/BetaHuhn/repo-file-sync-action
  - https://cli.github.com/manual/gh_ruleset_check
  - https://github.com/timelinize/timelinize
  - https://github.com/AgriciDaniel/claude-obsidian
  - https://github.com/HKUDS/LightRAG
  - https://github.com/urchade/GLiNER
---

# Agents and Claude Code

How we run agents: Claude Code locally and in cloud sessions, MCP servers and integrations, skills,
sub-agents, and the guardrails that keep an agent that can act from doing harm.

## Working inside Claude: model, effort, context and fresh sessions

The standing convention for Claude chat, Projects and Claude Code sessions, from
[decision 0006](../decisions/0006-model-selection-convention.md) (Layer 1). The defaults are
there; this section covers how to work with them. Checked against Anthropic's Claude Code and
help-center docs on 2026-10-18.

### Start from the default

- Threads and coding sessions: Claude Opus 5.5 at `medium` effort.
- Project chat, quick questions and triage: Claude Sonnet 5.5 at `low`.
- Workers or subagents that read, search or summarize: Haiku 5.5 or Sonnet 5.5 at `low`.
  In Claude Code, set `model: haiku` in the subagent's definition, or `CLAUDE_CODE_SUBAGENT_MODEL`.

### Scale up or down

Change effort first, then the model, one step at a time.

- **Up** (`high`, then `xhigh`, then Claude Fable 5.1): the same mistake comes back after a
  correction, the work spans several files or repos, it touches auth, secrets or spend, it is a
  design or decision record, or it is a long run nobody will watch. Fable 5.1 only as below.
- **Down** (`low`, or Sonnet 5.5): mechanical edits, renames, formatting, lookups, and summaries
  of text you supply.
- On Opus 5.5, Sonnet 5.5 and Haiku 5.5, thinking can't be turned off; lower the effort instead.
- Switch at a task boundary, not mid-task. Prompt caches are per model, so a model switch makes
  the next request re-read the whole conversation at full input price. Changing effort keeps
  the cache on Opus 5.5, Sonnet 5.5, Haiku 5.5 and Fable 5.1 with an API key or a Claude
  subscription, but rebuilds it on other models, on Bedrock and Google Cloud, and through the
  Claude apps gateway, so effort is the cheap lever mid-session on the current models.

### When to reach for Fable

Reach for Claude Fable 5.1 as a scoped worker, with the user's yes, in three cases:

1. **An Opus pass names a question it can't settle by reading,** and the answer changes a design
   decision: quantitative or probabilistic reasoning (false-alarm rates, sample sizes),
   re-identification and privacy inference, or adversarial reasoning across several documents.
2. **Opus 5.5 at `high` has failed the same task twice.**
3. **The user asks for it by name** for long multi-step research, a large refactor across several
   repos, or dense PDF and spreadsheet analysis. These are the areas Anthropic names for it:
   start on Opus 5.5 and use Fable 5.1 "for demanding reasoning and long-horizon agentic work, or
   when your evals on Claude Opus 5.5 at higher effort still fall short"
   ([what's new in Fable 5.1](https://platform.claude.com/docs/en/models/fable-5-1/whats-new-fable-5-1),
   checked 2026-10-19).

It costs 2.5 times Opus 5.5 per token, always thinks and defaults to `high` effort. On a Max plan
Fable can use up to half of the weekly limit; on Pro it's paid from usage credits
([Fable on your plan](https://support.claude.com/en/articles/15424964-claude-fable-models-on-your-plan),
checked 2026-10-19).

Not for unknowns that only a test can answer (what an API actually does when the docs are
silent: run a spike), not for breadth review (Opus finds more issues per token), and not for
mechanical work. Run the first pass at `high`, as design reviews already call for above, so
Fable only gets what `high` can't settle. Brief the worker with the named questions and the
files, ask for a verdict, the reasoning with numbers and the concrete changes, and have the Opus
thread recompute a sample of the numbers, boundary cases included, before recording them.

**Field note (2026-10-19).** Two design-stage red teams ran on Opus 5.5. The first (a family
assistant's retrieval design, 12 findings) needed no Fable: its open unknown was an API
behavior the docs don't state, sent to a spike. The second (two unbuilt agent-operations
designs, 15 findings) ended by naming two questions it couldn't settle: whether two
pseudonymized data feeds together re-identify people, and whether a judge-drift auditor's
thresholds can tell drift from noise at a one-operator volume. A Fable worker answered both in
about four minutes. What it added beyond the first pass:

- **A reframe.** The feeds don't expose the customer, but small groups expose a team, and a
  95th percentile over five users is one person's numbers.
- **A finding nobody asked for.** One key served both user and resource pseudonyms, so the
  yearly rotation meant to forget users also broke every resource trend line.
- **Numbers.** With 40 seeded faults, a healthy 97% judge trips the alarm 12% of the time and a
  drifted 90% judge is caught only 78% of the time; checked nightly on an overlapping window, a
  false alarm is near certain within weeks.
- **A logic flaw.** The rule for promoting a second judge counted only its wins, so it promotes
  an equally good judge about 99.8% of the time.

Cost: the Fable worker was about 30% of the thread's list-price cost, and the escalation as a
whole (Fable plus the Opus turns that briefed it and checked the answer) about two-thirds of the
cost of the 15-finding Opus pass, so roughly five times as much per finding. Worth it here,
because both answers changed the design.

What the run showed about the rule:

- **"Failed twice" never fires on design work.** A review has no failing test, so its failure is
  "can't settle this", which the Opus pass reported itself. The escalation that happened (Opus
  names the questions, the user says go, a Fable worker answers, Opus checks) is case 1 above.
- **The `high` step was skipped.** Both red teams ran at the thread default, `medium`, because
  the convention isn't in the project instructions yet. *Unverified:* whether Opus at `high`
  would have settled either question; no run tried it.
- **The spot check missed a boundary.** Recomputing the figures confirmed them, except "a judge
  at exactly 95% trips about half the time": that is 32 to 38% if the alarm fires below 95%, and
  56 to 60% at or below, so the threshold's comparison needs stating.

### Start a fresh session

Long context costs on every message: each request re-sends the whole conversation, so a one-line
question late in an all-day session pays for all of it. Start fresh when:

- **The next task is unrelated.** `/clear` costs nothing. `/compact` reads the whole
  conversation to summarize it, so it's a large request; use it only to carry on the same task,
  and say what to keep (`/compact Keep the failing test output and the files changed`).
- **Most of the context is dead weight:** long tool output, abandoned approaches, or a big
  course correction where the wrong attempts outweigh the right one.
- **Quality slips:** it repeats a fixed mistake, forgets a stated constraint, or contradicts an
  earlier decision.
- **You're back after a break** longer than the cache lifetime (an hour on a subscription, five
  minutes on an API key or once drawing on usage credits). The next message re-reads everything
  at full price anyway, so a fresh session with a short handoff is cheaper when the history is
  long.

Before starting fresh, write the handoff where the next session will find it: the state, the
decisions and the next step, in the repo, the KB or project memory. In Claude Code, `/rename`
the session first so `/resume` can find it. In a Project, a long thread hands off to a new
thread with that summary instead of carrying on.

### Keep the context small

- Keep `CLAUDE.md` and `AGENTS.md` under 200 lines. Move workflow detail into skills, which load
  only when used.
- Run `/context` to see what fills the window. Turn off MCP servers you aren't using (`/mcp`), and
  prefer a CLI (`gh`, `az`) to an MCP server when both exist.
- Send noisy work (test runs, logs, doc fetches, wide searches) to a subagent so only its summary
  comes back. A hook can filter test or log output to the failures before Claude reads it.
- Ask specific questions that name the file and function, and give a check to pass (a test, an
  expected output). Vague asks make Claude scan widely.
- Use plan mode for anything complex, and stop early (Escape, then `/rewind`) when it heads the
  wrong way.
- In Claude chat: put related questions in one message, refer back instead of restating, and put
  documents you reuse in project knowledge, where they're cached.

### Tools considered

- **Headroom** ([repo](https://github.com/chopratejas/headroom), Apache-2.0, free; a paid
  offering exists for organizations). A local proxy, library or MCP server that compresses tool
  output, logs, files and history before they reach the model, and claims 15 to 20% fewer tokens
  for coding agents. It runs locally, but fetches a model from Hugging Face and checks PyPI for
  updates (`HEADROOM_UPDATE_CHECK=off`). Not part of the convention (checked 2026-10-18, release
  0.41.0): it can't sit in front of Claude chat or cloud sessions, which is where most of the
  family's work runs; Claude Code already defers MCP tools and supports subagents, hooks and
  compaction for the same job; and a proxy sees every request and credential and rewrites
  prompts, so a quality drop would be hard to see. A project may trial it in local Claude Code or
  in its own app as a fit-for-purpose choice: pin the version, turn the update check off, and
  compare tokens per task and the `/usage` cache share with and without it. Claude Code supports a
  proxy set by `ANTHROPIC_BASE_URL` alone: the claude.ai login stays the credential, so the
  plan's limits still apply, as long as the proxy forwards the OAuth capability in the
  `anthropic-beta` header. A proxy that strips the cache markers bills the whole history as
  uncached input on every turn, so check the `/usage` cache line first. Headroom's docs (checked
  2026-10-20) say it merges the client's `anthropic-beta` tokens with its own, client tokens
  first, and by default re-adds any token the client drops later in a session
  (`HEADROOM_BETA_HEADER_STICKY`), and that it reads Claude Code's `cache_control` TTL. Its
  Unix-socket mode makes Claude Code treat the session as API-key auth, which fails a
  subscription login, so use `ANTHROPIC_BASE_URL`. *Unverified:* a real run with a claude.ai
  login.

### Check it's working

- Claude Code `/usage`: session tokens and cost, a prompt-cache line (share of input served from
  cache, misses and their likely cause), and on a plan, what share went to subagents, skills or
  MCP servers, with flags for long context or cache misses.
- `/insights`: a report on friction such as misunderstood requests.
- Claude chat: Settings > Usage shows the session and weekly limits.
- For the pilot, count per project: threads that needed a bump, sessions restarted because
  quality slipped, and the cache share from `/usage`.

## Swarms and multi-agent patterns

What we learned specifying a personal swarm ([0015](../decisions/0015-personal-swarm-on-the-2ndbrain.md);
the spec lives in the swarm's own private repo). Checked 2026-10-19.

**Claude Code's own multi-agent pieces.** Subagents report a result back to one session. Agent
teams are a lead plus teammates that share a task list and message each other; they're
experimental, off unless `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`, one team per session, no nested
teams, and in-process teammates don't come back after `/resume`. Teammates' permission prompts
surface in the lead, and a teammate can't approve a prompt for you
([agent teams](https://code.claude.com/docs/en/agent-teams)). Anthropic suggests three to five
teammates and says to try subagents or cross-session messaging first. None of these outlives a
session, so a swarm that runs for weeks is built from projects, routines and GitHub, with these
only inside one piece of work.

**For one owner, the bottleneck is review, not agents.**

- A cap on the owner's queue doesn't raise merges per owner minute; how fast the owner reviews
  sets that. With about 4 items a day needing the owner and one 30-minute sitting that clears
  about 6, the queue averages 2 (M/M/1, ρ = 4/6) and a cap never binds. At 8 a day the queue grows
  without bound and throughput is still 6. What a cap buys is age (Little's law: wait = queue /
  rate), which saves rebases and re-skims. *Inferred* from one day's numbers.
- Count the cap in owner-minutes, not items: eight skims and eight full reads differ fourfold.
- Count it from a live query (open, green, non-draft, needs the owner), not a morning list that also
  holds answers and stale items, or builders wait forever on items that will never clear.

**Agents acting as your own GitHub account defeat every "the owner opened it" check.** Author
filters on handoff issues, auto-merge and directives all pass for anything a session opens, so
one session that read a stranger's issue can relaunder it as yours. Provenance lines (what owner
message or whose issue an agent's issue or PR answers) make it visible; only a separate machine
identity makes it checkable.

**A stop switch needs a fast, take-away-only trip any agent can throw.** A pause that needs a PR
the owner merges takes hours. An open issue with a reserved label, which only the owner closes
and no issue template can apply, takes seconds and needs no credential. Also disarm auto-merge
that was armed before the stop, or green checks merge it anyway. In this hub, directives' `pause`
enum accepts only `all` and four `kb-*` names today, so a new pause target is a schema change.

**Red-team patterns for agents that act** (from a design-stage red team, 2026-10-19):

- **Guardrails move with the executor.** When the component that acts moves (from a playbook to a
  separate swarm, say), its safety rules ("never undo another operator's change", "unknown
  sessions count as busy") have to move with it, or the new executor runs without them.
- **Public repos show the plan.** Actions logs and job summaries in a public repo are readable by
  anyone, so a write path that logs its targets publishes them. Run it from a private fork.
- **Default-token PRs don't trigger checks.** A PR opened with `GITHUB_TOKEN` starts no other
  workflow, so an agent's PR can skip the guard check meant for it.
- **One maintainer can't review themselves.** CODEOWNERS and watchdog rules do nothing with a solo
  owner; a time-lock (a delay before a change takes effect) works instead.
- **A kill switch must stop every path that spends.** One that halts the main loop but not a
  fallback API call keeps spending, and a daily cost cap sees spend only hours later.

**Hard limits for agents that spend money.** A draft trading bot's guardrails had five bugs that
make a test checklist for any agent with a budget: the daily cap counted only open orders, the
loss breaker always returned 0, sells counted against the capital cap, negative amounts got past
the per-trade cap, and the trading day ran on UTC instead of market time. Each bot also gets its
own key variable and fails hard when it's missing, instead of falling back to a shared key.

**Field note: the second Fable red team (2026-10-19).** A scoped Fable worker took four questions
the Opus pass named (throughput, bypass, the stop switch, scope) and returned eight findings in
about four minutes, one Critical and three High; the two checked against the code held. As in the
first field note above, the gain was reframes with numbers (the cap buys age, not throughput) and
code-level checks the Opus pass hadn't run (the schema enum, the author filter).

## Cloud sessions can commit to your GitHub repos

A Claude session with GitHub tools can list your repos, attach one with push access, clone it,
write files, commit and push. That's enough to keep a notes repo or a knowledge base up to date
from a phone or a browser, with no desktop app. Observed working on 2026-10-17.

1. List the repos the session can reach and check `can_push`.
2. Attach the repo with push access (a confirm prompt may appear).
3. Clone, write files, commit, push.
4. Pull on your computer, or use a Git plugin in your notes app, to see the changes.

Trade-offs:

- Sync is pull-based, not real time.
- Merge conflicts are possible if you and the agent edit the same file. Keeping the agent's files
  in their own folder avoids most of them.
- A public repo exposes everything committed. Keep personal notes in a private repo.
- Pushes that add or change `.github/workflows/` files work from a cloud session, and commit
  trailers (co-author and session lines) come through as written (checked in a real run on
  2026-10-18).

What a cloud session can't do on GitHub (seen in real runs, 2026-10-19):

- **Create repos or delete remote branches.** Repo creation returns 403 and the git proxy refuses
  branch deletes, so merged branches stay until the owner deletes them.
- **Create a label on its own.** The tools apply labels to issues but have no "create label" call;
  applying a new label to an issue once creates it.
- **See repos added after it started.** Repos added in the project's settings reach new sessions
  only. A running session attaches them itself (`add_repo`), and only to that session.
- **Read PR state with read access.** Read access is a clone; mergeable state and check runs need
  the repo attached with push access.
- **Use connectors in a scheduled task** when the organization doesn't allow it. The task then
  relies on the environment's own GitHub access.
- **Search GitHub or call the API on a repo outside the session (checked 2026-10-20).** The
  session is bound to its configured repos, and the 403 says so: `/search/...` is refused
  ("sessions are bound to their configured repositories") and `/repos/<other>/...` is refused
  until the repo is attached. This holds with the environment's network access on Full, so
  don't blame or change the network setting. Raw files on `raw.githubusercontent.com` and web
  search still work, so for prior-art research check candidates one repo at a time.
- **Request the owner's review on its own PR.** The session's PRs are opened as the owner, so
  asking the owner to review fails ("Review cannot be requested from pull request author");
  assign the PR instead. The PR itself is still created (checked 2026-10-20).

**Check merge state before pushing more to a PR.** Three times in one day a PR merged a moment
before the next push, and the new commit was stranded on a merged branch and needed its own PR.
Related traps:

- GitHub runs no CI on a PR with a merge conflict, so a conflicted PR shows fewer checks, not red
  ones.
- Archiving a repo leaves comparison checks that read it silently green. Repoint anything that
  depends on it first.

## Outside review from another company's model

A second Claude model as red team still shares a company's training and habits with the author,
so a mistake both miss gets no flag. For the few items where a miss is expensive (secrets and
access, money, going public, things that can't be undone), the family adds one pass from another
company's assistant through a single file the owner pastes: [decision 0017](../decisions/0017-outside-review-for-high-stakes-work.md),
[prompt](../prompting/library/outside-review.md). What made it workable:

- **A file, not access.** The reviewer reads one self-contained file and never the repos, so the
  file must be safe to publish: free consumer assistants may keep what they're given.
- **Leave out your own red team's findings,** or the second pass anchors on the first.
- **Paste by hand before building a tool.** xAI's text API costs about two cents a review, but a
  tool means a new connector to red team, and Claude would then choose what the owner sees.

## What counts as the owner's yes

A decision, a merge or a write to a private layer waits for the owner's own words in chat, such
as "accept 0016" or "merge 1, 3". These don't count (field notes, 2026-10-18 and 2026-10-19):

- **A bare "go"** after a report approves the work, not the decisions inside it. Decision records
  stay `proposed` until the owner names them.
- **A relay.** A card tap or a message another session passes on is that session's account of
  what the owner said, not the owner's words. Ask, or read the owner's message yourself.
- **A widened decision.** When a red team adds rules the owner didn't agree to, the record stays
  `proposed` until the owner accepts the new version.

Handoff issues follow the same rule ([decision 0012](../decisions/0012-family-format-handoff-issues.md)).

## Letting agent PRs merge themselves

When agents open most of the PRs, the owner's merge click becomes the bottleneck. GitHub's
auto-merge can take the low-risk ones, if the class is decided by a workflow, not by the agent that
wrote the change. The family's version is [decision 0014](../decisions/0014-family-format-auto-merge-low-risk-prs.md).
What matters when building one (from GitHub's docs, 2026-10-19):

- **Judge from the base branch.** A `pull_request` workflow runs the PR's own copy of the workflow,
  so a PR could rewrite its own gate. `pull_request_target` runs the base branch's copy with a
  write token; that's safe only if it never checks out or runs the PR's code. Read the changed
  files from the API instead (`pulls/{n}/files`, up to 3,000 files; fail closed above that, by the
  PR's `changed_files` count, since renames listed under both names can hide a cut-off list).
- **Turn auto-merge off when turning it on fails.** An earlier head may have armed it; a failed or
  canceled enable step must fall through to the disable step, not leave the old arming in place.
- **Count renames twice.** The files API gives `previous_filename` for a rename; moving a file out
  of a denied path must count as touching it.
- **Auto-merge survives pushes** from anyone with write access. A later push that adds a risky file
  doesn't turn it off by itself, so the gate must re-run on every push and be a required check, or
  the PR can merge on the new head before the gate turns auto-merge off.
- **A required check that never reports blocks the PR forever.** Workflows with a `paths` filter
  can't be required checks unless every PR matches the filter.
- **Merges made with `GITHUB_TOKEN` don't trigger other workflows,** including `push` workflows on
  the default branch.
- **The agent is often the owner's account.** GitHub can't tell them apart, so "agents never arm
  auto-merge by hand" is a rule the agent keeps, not something GitHub enforces.

## Keeping all your repos on the same conventions

Once conventions like [decision 0014](../decisions/0014-family-format-auto-merge-low-risk-prs.md)
apply to every repo, they drift: a label never created, a ruleset missing a check, a workflow copy
left behind. [`scripts/kb/repo_audit.py`](../../../scripts/kb/repo_audit.py) lists the owner's
repos from the API, reports drift per repo with a stable id (`repo/check`), and with
`--fix repo/check,...` applies only the ids the owner names, using the owner's own `gh` login. It
never runs from a cloud session (the session proxy refuses the API outside attached repos), and
its full report names private repos, so only the `--summary` output goes into a chat.

Prior art (checked 2026-10-21; maintenance dates not compared):

- **[Safe Settings](https://github.com/github-community-projects/safe-settings)** (GitHub, ISC)
  is the full version: policy as code, rulesets, labels, reverting manual changes. It's built
  around an organization's `admin` repo, so it doesn't fit a personal account.
- **The [Repository Settings app](https://github.com/repository-settings/app)** works per repo
  on a personal account, but its README warns it gives anyone with push the admin role, and its
  ruleset support is "still under development".
- **The Terraform or OpenTofu GitHub provider** does real drift detection (`plan`) and supports
  user-owned repos, at the cost of a state backend, a stored admin token and importing every
  repo.
- **[repo-file-sync-action](https://github.com/BetaHuhn/repo-file-sync-action)** (MIT) and the
  label-sync tools fix one kind of drift each, and file sync needs a full `repo`-scope token.
- **OpenSSF Allstar and Scorecard** check security hygiene, not your own conventions.
- **[`gh ruleset check --default`](https://cli.github.com/manual/gh_ruleset_check)** shows one
  repo's effective rules with no code; fine for a single repo.

What the audit had to get right (red teamed with a second model, 2026-10-21):

- **On GitHub Free, private repos have no rulesets and no auto-merge.** Both are public-only on
  Free (and on Free for organizations); private repos need Pro, Team or Enterprise. So 0014's
  auto-merge and required checks only hold in public repos on Free, a free org changes nothing for
  private ones, and Pro on the personal account is the smallest step that makes them hold. The
  audit reads the plan and doesn't report or "fix" what GitHub won't enforce.
- **Require only checks that report on every PR.** A ruleset matches the check's job name (the
  job's `name:` if set), and a path-filtered or schedule-only workflow never reports on some PRs,
  which then wait forever. The audit takes the expected checks from what ran on recent merged PRs,
  not from workflow YAML.
- **Extend a ruleset by read, append, write back.** The update call replaces the whole ruleset, so
  anything not sent back (a rule added by hand) is lost. Keep `strict_required_status_checks_policy`
  off, or every merge makes the other armed PRs stale.
- **Classic branch protection still applies alongside rulesets.** A leftover "1 approving review"
  blocks a solo owner whatever the ruleset says.
- **In a Codespace, `GITHUB_TOKEN` is the Codespace's own token,** scoped to one repo. An audit run
  with it sees a fraction of the repos and looks clean; unset it and `gh auth login -w`.
- **Compare file copies by committed blob SHA** (`git rev-parse HEAD:<path>`), not by hashing the
  working tree, or Windows line endings show every file as changed.

## A capture skill for a two-layer second brain

[2ndbrain](../../../skills/2ndbrain/README.md) is a Claude skill that closes out a thread: it
reviews what the thread produced, proposes captures in one batch, and writes the approved ones to
the project's own KB or this KB (by PR, after a public-safety check) or to a private notes repo. It
refuses secrets and customer or tenant specifics. Its sync mode reads this KB's directives and
decisions at the start of work in a family project, and can write a handoff block to paste into
another project, since projects can't read each other's chats. One skill, not one per repo: two skills with
overlapping triggers both fire on "lessons learned", so the older one gets turned off when this
one is installed. A setting, `private_layer`, decides whether public text may say the private
layer exists; its contents stay private either way.

## A brand skill that reads one file per project

[brand-profile](../../../skills/brand-profile/README.md) makes pages, artifacts and images in a
project's look by reading the project's `brand/profile.json` (format in the skill's
`profile.schema.json`). A per-brand theme skill isn't needed on top of it: a profile's `starters`,
`required` lines and `rules` carry what such a skill would say, so one skill serves every brand and
none is the default. A profile is kept honest by a test in its own repo that checks it against
the schema and the brand's token stylesheet (checked 2026-10-21).

A skill the 2ndbrain template ships lives in this repo's `skills/` and is listed in
`template/manifest.toml`; the template's weekly `template-sync` exports it. Adding one straight to
the template repo doesn't last: the export replaces everything but `.git`, so the next sync deletes it.

## Skills that learn from use

A skill can't rewrite its own files. In a claude.ai Project or cloud session, the synced skill
files on disk are a read-only cache, and a saved skill proposal replaces the whole `SKILL.md`
(checked 2026-10-18). So a skill that is meant to improve over time, such as one holding a
writing-style profile, keeps its learned state inside `SKILL.md` and ends its learning step by
proposing the complete updated file for the user to save. Two things make that work:

- Gate every change on the user's yes, item by item, with the evidence for each, so a bad
  inference never lands silently.
- Bump a revision number and keep sample counts in the file, so the next session can tell how
  much the learned state rests on.

## Third-party skills worth adding

A survey of well-known Claude Code skills, checked 2026-10-20 against each repo's LICENSE files,
the [skills.sh](https://skills.sh/anthropics/skills) install counts and Anthropic's plugin
directory. Anthropic's
own set ([anthropics/skills](https://github.com/anthropics/skills), Apache-2.0 for most skills; the
document skills are proprietary) is
mostly built into claude.ai already: the document skills, skill-creator, mcp-builder,
theme-factory, canvas-design and web-artifacts-builder. Worth adding on top:

| Skill or plugin | Source and license | Why |
| --- | --- | --- |
| verification-before-completion | [obra/superpowers](https://github.com/obra/superpowers), MIT | Run the proving command and read its output before any "done" claim. |
| systematic-debugging | obra/superpowers, MIT | Reproduce and find the root cause before fixing; a failing test first. |
| frontend-design | anthropics/skills, Apache-2.0; also a one-skill plugin in Anthropic's plugin directory | The most-installed skill on skills.sh at the time of writing; steers UI work away from a generic look. |
| webapp-testing | anthropics/skills, Apache-2.0 | Drives a local web app with Python Playwright, with a helper that starts and stops the dev servers. |
| differential-review, supply-chain-risk-auditor, static-analysis (plugins; static-analysis bundles codeql, semgrep and sarif-parsing) | [trailofbits/skills](https://github.com/trailofbits/skills), CC-BY-SA-4.0 | Security review of a diff, a dependency tree, and CodeQL or Semgrep scans. |

Not yet reviewed, for the next pass: [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills)
(MIT, about 106k stars, 25 engineering-lifecycle skills, installs as a Claude Code plugin
marketplace; checked 2026-10-20).

What we learned getting them in:

- **A saved skill is one `SKILL.md`.** A claude.ai skill proposal carries no `scripts/` or
  reference files, and many popular skills lean on them (webapp-testing's server helper,
  systematic-debugging's three technique files, the three Trail of Bits plugins here). For a small skill,
  inline the extra files into `SKILL.md` and say where the rest lives upstream. A skill built
  around scripts belongs in a plugin instead: Trail of Bits publishes its repo as a Claude Code
  plugin marketplace (`/plugin marketplace add trailofbits/skills`, then install from the
  `/plugin` menu or with `/plugin install <name>@trailofbits`).
- **Take single skills, not whole methodology bundles.** Superpowers ships 15 skills and a
  SessionStart hook that steer every session through brainstorm, plan and subagent steps. That
  clashes with a setup that already has its own PR and closeout workflow, so we took the two
  skills that stand alone. Its plugin in Anthropic's directory installs all of them.
- **Adapting is allowed, so say so.** MIT and Apache-2.0 allow modified copies; keep the
  copyright line and a "changes" note at the top of the adapted `SKILL.md`. CC-BY-SA requires
  the same license on adaptations, so Trail of Bits skills are installed as published, not copied.
- **Skip:** the aggregator lists of 1,000 or more skills (unvetted, and a skill is text Claude
  follows), token-cutting style skills such as Caveman (they trade readable replies for tokens),
  and interview-style planning skills where a design red-team step already covers it
  ([When to reach for Fable](#when-to-reach-for-fable)).

### The "Karpathy guidelines"

[forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills)
(MIT per its README; no LICENSE file) is a community distillation of Andrej Karpathy's January
2026 post on LLM coding mistakes, not something he wrote. It is one CLAUDE.md with four rules:
think before coding, simplicity first, surgical changes, and goal-driven execution. Its own
caveat is that the rules trade speed for caution.

Three of the four hold as written. The first doesn't fit agents that work while the owner is
away: "if uncertain, ask" and "present interpretations, don't pick silently" park an
asynchronous thread until someone answers. We kept the half that matters, saying the assumption
out loud, and paired it with the rule threads already follow: pick the reasonable default, say
which, and ask only when the answer changes the goal, a visible result or an irreversible step.
The template's `AGENTS.md` now carries the four rules in that form, in our own words, under "How
to make a change"; siblings pick it up on their next template sync.

Much of this already lives in Claude Code's own instructions (match the surrounding style, act
when you have enough to act). Writing it into `AGENTS.md` still pays: other agents that read
`AGENTS.md` get it, and the rule is visible and editable in the repo instead of implied.

## Connecting an Obsidian vault

An Obsidian vault is just a folder of Markdown on your disk, so the web chat has no path to it.
Claude needs the desktop app, Claude Code, or a Git repo as the vault. There was no official
one-click Obsidian connector as of 2026-10-17; everything below is community tooling or plain
folder access. Simplest first:

1. **Connect the vault folder** through the desktop app. File access is enough.
2. **A community MCP server** in Claude Desktop, configured by editing its config with the vault
   path. These are third-party projects, so check maintenance and permissions first.
3. **An Obsidian plugin acting as an MCP server** (obsidian-claude-code-mcp): WebSocket for Claude
   Code, HTTP/SSE for Claude Desktop. Desktop needs Node.js and the `mcp-remote` bridge.
4. **Claude Code run inside the vault folder.** No plugin needed.
5. **A Git repo as the vault,** committed to from a cloud session (see the section above).

Constraints:

- A local MCP server must run on the same machine as the vault, so it doesn't work from a
  browser-only session or a phone.
- Anything connected gets read and write access to the vault. Keep history (Git, or Obsidian Sync)
  before letting an agent edit notes.
- obsidian-claude-code-mcp still needs `mcp-remote` for Claude Desktop, because it serves the
  older HTTP-with-SSE transport, and its last commit was on 2025-06-23 (checked 2026-10-18). Treat
  it as unmaintained and check for a fork before relying on it.
- No official connector as of 2026-10-20: Anthropic's connectors help page doesn't list one, and
  says custom connectors reach your MCP server from Anthropic's cloud, not your device, so the web
  chat still can't open a local vault. Third-party Obsidian MCP plugins exist; they aren't official.

### Building a graph of personal data

A prior-art survey on 2026-10-20 looked for tools that turn scattered personal data (cloud drives,
social exports, chat exports, notes) into one store with an Obsidian-style graph of files and of
people, places and topics. Stars and licences were read from GitHub that day.

- **No single tool does it.** Copying and dedupe are solved (rclone, czkawka, dupeGuru), a local
  timeline of people and places is close to solved
  ([timelinize/timelinize](https://github.com/timelinize/timelinize), AGPL-3.0, imports Takeout,
  Facebook, Instagram, messages and GPS, merges contacts across sources, but has no graph view and
  says upgrades can mean rebuilding), and the Obsidian graph over the data is the gap.
- **The popular "LLM wiki" vault tools send your content to a cloud model.**
  [AgriciDaniel/claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian) (MIT, about 15.7k
  stars), SamurAIGPT/llm-wiki-agent and Ar9av/obsidian-wiki file sources into linked pages through
  Claude or another hosted model. Fine for your own notes; wrong for other people's messages or
  children's data.
- **Fully local entity graphs need a strong GPU.**
  [HKUDS/LightRAG](https://github.com/HKUDS/LightRAG) (MIT, has a graph web UI) gives
  Qwen3-30B-A3B as its minimum for local extraction and warns slow models time out. A small
  named-entity model like [GLiNER](https://github.com/urchade/GLiNER) (Apache-2.0) runs on CPU but
  finds mentions only, with no merging of "Mom" and a full name, so over chat logs it makes a
  hairball. For chats, take people from sender and participant fields instead.
- **A vault of cards beats a card per item.** One Markdown note per folder or notable document, with
  front matter that Dataview and [ExcaliBrain](https://github.com/zsviczian/excalibrain) read, keeps
  Obsidian's graph usable; the global graph slows past roughly 10,000 to 20,000 notes (community
  reports, not measured here).
- **Keep a private vault off every sync path.** On Windows, Windows Backup can sync Desktop,
  Documents and Pictures to OneDrive, so a private vault belongs outside those folders. Allow only
  the plugins you need: [Smart Connections](https://github.com/brianpetro/obsidian-smart-connections)
  is source-available under its own licence, not open source, and bundles cloud chat features.
- **File names leak.** When an agent writes the indexing script, test it on a made-up folder and
  have the owner share counts, not logs, because paths carry family members' names.

## Giving Claude a paid media API through an MCP server

What we learned designing a server that lets Claude call another provider's image, video and
speech APIs (2026-10-19 and 20, checked against the docs in the front matter). The provider choice
itself is [decision 0009](../decisions/0009-second-model-family.md); key storage is
[decision 0016](../decisions/0016-secrets-handling.md).

**Check what exists first.** Community MCP servers for a big provider's media API are common and
MIT-licensed, but the ones we found had no spend cap, no limit on which files they send out, and
extra tools (code execution, file upload, chat) the job didn't need. A small server of your own is
often a few hundred lines; use theirs as a reference.

**Local server or connector decides everything else.**

- A local stdio server is set up per repo in `.mcp.json`, so *where it is installed* can be a
  guardrail (for example, never in a kids' app repo).
- A remote server added as a claude.ai custom connector belongs to the account and shows up in
  every project, chat and phone. Any rule that relied on where it's installed has to move into
  the server. Prompt injection can now reach it from any chat, and a per-call approval is one tap,
  or none once someone picks "always allow".
- For a paid tool on a connector, keep the paid tools switched off by default. The owner turns
  them on for a short window from a page only they can log into, and while off they refuse calls.
  Read-only tools can stay on.

**Spend: put the hard cap in the provider account, not the code.** Use a separate team or
project, prepaid credit with auto top-up off, and a key restricted to the media models. With xAI,
keys take `acls` such as `api-key:endpoint:image` and per-key `qps`/`qpm`, and a $0 invoiced limit
rejects requests once credit runs out. Caps in the server (per call, session, day, month) are a
brake on mistakes, and the prepaid balance is the cap no bug can pass. Never retry a request the
API has already accepted: async video jobs are billed even when cancelled.

**Claude's connector OAuth, in practice:**

- Sign-in starts only on an HTTP `401` with `WWW-Authenticate: Bearer resource_metadata="…"`. A `200`
  carrying a tool error never prompts.
- Claude uses a Client ID Metadata Document (CIMD) only when the authorization server metadata
  advertises `client_id_metadata_document_supported: true` and `none` in
  `token_endpoint_auth_methods_supported`; otherwise it falls back to dynamic client registration.
  Leaving registration off and allowing only CIMD clients from Claude's own origin closes the
  "anyone can register a client" hole.
- The hosted apps' redirect URI is `https://claude.ai/api/mcp/auth_callback`. Claude Code uses a
  loopback redirect on any port. Discovery and token endpoints get 10 seconds, and `/token` must accept
  form-encoded bodies. Connector traffic comes from Anthropic's published egress range, which a
  WAF rule can allowlist.
- The confused-deputy risk stays even then: someone can start a connect from their own Claude
  account and send you the consent link. Show the consent page every time, and only approve
  one you just started.

**Cloudflare Workers specifics.** Cloudflare's Access-plus-OAuth MCP template pins
`workers-oauth-provider` 0.8 and has open registration turned on. Version 1.2 (2026-10) ships
browser-bound consent and upstream sign-in helpers that replace the template's hand-written
cookie and CSRF code. It also requires the exact resource URL, which is every token's audience, and
CIMD needs the `global_fetch_strictly_public` compatibility flag. To keep a hostname out of an
open-source repo, build the provider from an environment variable on the first request. Turning
off `workers.dev` doesn't turn off preview URLs; both need to be off (see
[Cloudflare Access in front of a Worker](../platforms/README.md#cloudflare-access-in-front-of-a-worker)).

**Files.** The provider's result URLs expire, so store results yourself. Accept inputs only as ids
of files the server made or the owner uploaded on purpose, never as paths, URLs or base64, so a
chat can't push someone's photo or a document out. Serve downloads through short-lived signed links
of allowlisted media types (never SVG or HTML), with `attachment`, `nosniff` and a sandbox CSP. Links
pasted into a shared chat travel with it.

