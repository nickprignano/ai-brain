---
status: proposed
date: 2026-10-21
decision-makers: [maintainer]
---

# 0019. Family format: this hub and the private layer are the default home for every domain

## Context and Problem Statement

The family grew one KB at a time, and each new domain raised the same question again: where do
its public facts go, and where do its private notes, roadmap and unreleased material go? The
answers so far have been a new public KB repo, a KB folder inside a product repo, or the
maintainer's private layer. Answering it per domain spreads knowledge over more repos than the
maintainer can keep current, and each new private repo needs its own guard. Should there be one
default home for every domain, including the maintainer's work outside this family, and when is a
separate KB worth breaking out?

## Considered Options

- One pair by default: this hub for public knowledge, the private layer for private material; a
  separate pair only when the maintainer asks or a break-out reason applies
- One public KB repo per domain, with private material in the private layer
- KBs inside each domain's product repo, with private notes wherever the domain's work happens

## Decision Outcome

Chosen option: "One pair by default", because two places are the most one person can keep
current, and [0002](0002-public-kb-separate-from-personal-notes.md) and
[0013](0013-one-2ndbrain-template-private-by-default.md) already set up both halves.

- **Public by default:** knowledge for any domain goes on a topic page in this hub, under the
  same guardrails and checks. A new domain gets a topic folder here, not a new repo.
- **Private by default:** private notes, roadmap and unreleased material for any domain go in that
  domain's own area of the private layer. The 2ndbrain routing rules apply as they are: the
  private layer may link here, never the other way.
- **Breaking out a separate pair** (a public `<domain>-kb` built from the
  [2ndbrain template](https://github.com/nickprignano/2ndbrain), listed in
  [family.yaml](../family.yaml)) happens only when the maintainer asks for it or one of these
  holds, recorded in a decision:
  - the domain has readers or contributors who should get it without the rest of the hub;
  - it needs a license, review rule or release cadence the hub can't share;
  - it would crowd the hub's checks, indexes or digests enough to slow the AI research down.
  A broken-out domain's private material still goes in its area of the private layer; a separate
  private repo needs its own reason, such as material shared with someone who can't see the
  private layer.
- **Product repos are not KBs.** Private product repos keep their own code, docs and lessons; they
  aren't family members and aren't named in public text.
- **Existing KBs stay put.** The AVD and Nerdio HCL KBs are already broken out and stay as they
  are. A KB that lives in a product repo today (the Liquidware KB) moves only by its own PR with
  the maintainer's yes, either here or to a broken-out pair.
- **Beyond the family.** The same default is kept in the maintainer's own assistant instructions,
  so a new project starts with it.

### Consequences

- Good, because a new domain needs no new repo and no new choice.
- Good, because there's no new private repo to secure, sync or keep out of public text.
- Bad, because this hub's scope grows past AI research; its `focus` line in family.yaml and its
  topic list change when the first non-AI domain lands here.
- Bad, because a busy domain may need breaking out later, which means moving pages and leaving
  redirects.

## More Information

Revisit by 2027-04-21, or when the hub carries a third non-AI domain. Checkable assumption: the
hub's validate and digest runs stay fast with every domain's pages in them.
