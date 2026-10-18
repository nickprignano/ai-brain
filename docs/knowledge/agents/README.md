---
title: "Agents and Claude Code"
summary: "Claude Code, cloud sessions, MCP servers, skills, sub-agents and guardrails for agents that act"
topic: agents
status: partial
last_reviewed: 2026-10-17
sources:
  - https://www.sourcepulse.org/projects/28283027
  - https://lobehub.com/mcp/administrativetrick-obsidian-mcp
  - https://pypi.org/project/obsidian-mnemo/
  - https://www.verdent.ai/guides/obsidian-mcp-server
---

# Agents and Claude Code

How we run agents: Claude Code locally and in cloud sessions, MCP servers and integrations, skills,
sub-agents, and the guardrails that keep an agent that can act from doing harm.

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
