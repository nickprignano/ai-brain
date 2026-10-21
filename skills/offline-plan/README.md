# offline-plan: stay on top of things while Claude is out

A Claude skill for the days the owner can't use Claude (a usage cap, travel). It gathers the facts first:
- open pull requests, with their merge state read twice, because GitHub computes it lazily
- running threads
- approved cloud runs with no result yet
- security steps that need the owner's hands

Then it builds two things:
- a private phone sheet: billing check, merge order, decisions, restart message
- optionally, a public live checklist that ticks itself off from GitHub's anonymous API

The skill itself is [SKILL.md](SKILL.md).

## Why two outputs

Personal specifics (the billing check, cloud runs, private repos) never go on a public page. The public
checklist holds only what anyone could read from GitHub anyway, so it can live in a public repo, and threads
can update it by pull request.

## Install

1. Copy [SKILL.md](SKILL.md) into a new skill in your Claude account.
2. Fill in the settings block: your public repos, the repo that hosts the live checklist (if you want one),
   the private repo that tracks cloud runs, your monthly spend cap and your approval phrase.
3. For a live checklist, start from a page that reads a data file and asks only `api.github.com`. The avd-ops
   repo's `site/checklist.html`, `site/checklist.json` and `site/assets/checklist-core.js` (MIT) are one
   example, with offline tests.
