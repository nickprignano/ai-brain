---
title: "Agents and Claude Code"
summary: "Claude Code, cloud sessions, MCP servers, skills, sub-agents and guardrails for agents that act"
topic: agents
status: partial
last_reviewed: 2026-10-19
sources:
  - https://code.claude.com/docs/en/costs
  - https://code.claude.com/docs/en/model-config
  - https://support.claude.com/en/articles/9797557-usage-limit-best-practices
  - https://www.sourcepulse.org/projects/28283027
  - https://lobehub.com/mcp/administrativetrick-obsidian-mcp
  - https://pypi.org/project/obsidian-mnemo/
  - https://www.verdent.ai/guides/obsidian-mcp-server
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

Reach for Claude Fable 5.1 as a scoped worker, with the user's yes, in two cases:

1. **An Opus pass names a question it can't settle by reading,** and the answer changes a design
   decision: quantitative or probabilistic reasoning (false-alarm rates, sample sizes),
   re-identification and privacy inference, or adversarial reasoning across several documents.
2. **Opus 5.5 at `high` has failed the same task twice.**

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
  uncached input on every turn, so check the `/usage` cache line first. *Unverified:* whether
  Headroom forwards both.

### Check it's working

- Claude Code `/usage`: session tokens and cost, a prompt-cache line (share of input served from
  cache, misses and their likely cause), and on a plan, what share went to subagents, skills or
  MCP servers, with flags for long context or cache misses.
- `/insights`: a report on friction such as misunderstood requests.
- Claude chat: Settings > Usage shows the session and weekly limits.
- For the pilot, count per project: threads that needed a bump, sessions restarted because
  quality slipped, and the cache share from `/usage`.

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
- *Unverified* since 2026-10-17: whether an official connector now exists, and whether the web
  chat gained a local-file bridge.
