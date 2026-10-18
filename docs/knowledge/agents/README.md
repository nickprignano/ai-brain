---
title: "Agents and Claude Code"
summary: "Claude Code, cloud sessions, MCP servers, skills, sub-agents and guardrails for agents that act"
topic: agents
status: partial
last_reviewed: 2026-10-18
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
  design or decision record, or it is a long run nobody will watch. Fable 5.1 only after Opus
  5.5 at `high` failed the same task twice.
- **Down** (`low`, or Sonnet 5.5): mechanical edits, renames, formatting, lookups, and summaries
  of text you supply.
- On Opus 5.5, Sonnet 5.5 and Haiku 5.5, thinking can't be turned off; lower the effort instead.
- Switch at a task boundary, not mid-task. Prompt caches are per model, so a model switch makes
  the next request re-read the whole conversation at full input price. *Unverified:* whether
  an effort change in Claude Code rebuilds the cache too (on the API, changing the top-level
  effort does).

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
- *Unverified:* whether commit attribution lines or pushes to workflow files behave differently.

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
- *Unverified* since 2026-10-17: whether an official connector now exists, whether the plugins
  above are still maintained and still need `mcp-remote`, and whether the web chat gained a
  local-file bridge.
