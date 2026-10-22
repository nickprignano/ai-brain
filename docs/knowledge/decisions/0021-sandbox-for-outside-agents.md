---
status: proposed
date: 2026-10-22
decision-makers: [maintainer]
---

# 0021. A sandbox mode in the 2ndbrain template, for agents from other vendors

## Context and Problem Statement

The owner wants to try coding agents from other vendors (a coding CLI, a chat assistant with repo
access) on real work. Their prompts and files go to that vendor, a free tier may keep or train on
them, and a CLI signed in with the owner's GitHub login can read every repo the owner can,
including the private layer. Where can those agents work, and what may they see?

## Considered Options

- Let them work in the private layer and the public KBs, with instructions to stay out of notes
- Point them only at public repos, with no place of their own
- A third setup mode in the template: a fresh private sandbox repo, seeded only with public-safe
  material, with nothing flowing back except by hand

## Decision Outcome

Chosen option: "a sandbox mode", because instructions don't stop a token that can read the private
layer, and public repos give the agents no place to write findings without opening PRs on the KBs.

- **`setup.py --sandbox`** refuses unless GitHub confirms the repo is private, and refuses if the
  private layer holds a note now or ever did in git history: a sandbox is a fresh copy of the
  template, never a converted private repo. It removes the private layer and kb-auto-merge (an
  agent's PR opened with the owner's token would count as the owner's), puts `sandbox/RULES.md`
  at the top of `AGENTS.md`, and writes a `GEMINI.md` that imports `AGENTS.md`. A sandbox can't be
  switched to another mode.
- **The `privacy` workflow** fails a sandbox that turns public, regains the private layer, or holds
  a key shape, email address or platform ID in any file. `privacy_check.py --words FILE` adds a
  private-names list, kept outside the sandbox because its agents read every file in it.
- **The seed rule.** A file goes in only if it is already public or written fresh from public
  sources, passes the check with the names list, and the owner said yes to the batch. Nothing from
  the private layer goes in, summaries and paraphrases included. The scan is a backstop; the
  owner's yes is the control.
- **The way back is by hand.** A finding is data: the owner or Claude checks it and records what
  holds up through the normal reviewed path. The private layer's instructions say so too.
- **Keeping the private layer out of reach** is the owner's setup, documented in
  `sandbox/README.md`: agents run in a Codespace opened on the sandbox, whose token reaches only that
  repo; a CLI gets a fine-grained token limited to the sandbox; no `gh auth login` in the Codespace;
  commits use the GitHub noreply address. On the owner's own computer it is only a convention.

### Consequences

- Good, because the agents get real work and a place to write, and the private layer is out of reach
  of their tokens, not just their instructions.
- Good, because it's the same template, so a sandbox stays current with the format.
- Bad, because the owner sets up the scoped token and Codespace by hand, and a token created with
  "All repositories" undoes the boundary. The README gives a one-line check.
- Bad, because the scan misses paraphrases, names left off the list and text inside images.
- Neutral, because it's a third repo next to the hub and the private layer, made only when the
  owner asks for one.

## More Information

Red teamed with Fable before building: it found that converting a private repo would leave notes in
git history, that a sandbox would have auto-merged agents' PRs, that the rule against following
findings lived only where Claude never reads it, and that the scan should cover the whole tree
rather than one folder. All four are fixed above. Revisit after six months of use, or when a vendor
CLI supports repo-scoped login on its own.
