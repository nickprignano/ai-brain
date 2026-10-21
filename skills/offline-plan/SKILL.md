---
name: offline-plan
description: Use when the owner will be away from Claude (a usage cap, travel) and needs a phone plan: nothing billing, what to merge, what waits, and how to restart.
---

# offline-plan: stay on top of things while Claude is out

When the owner can't use Claude for a few days, they still need to:
- know nothing is billing
- merge what is ready from a phone
- see what waits for them
- restart cleanly afterwards

This skill makes them two things they can use without Claude:

1. **A private sheet** (a Claude artifact) with their personal specifics: the billing check, the exact merge
   list, their decisions and the restart message.
2. **A public live checklist** (optional), a static page plus a data file in a public repo. It ticks pull
   requests and repo settings off by itself from GitHub's anonymous API. The owner's manual steps are checkboxes
   stored in their browser only.

Do not start anything billable. Never ask for, show or store a secret.

## Settings

Fill these in when you install the skill.

```yaml
owner: <name>                              # who the plan is for
public_repos: [<owner>/<repo>, ...]        # repos whose PRs and settings the plan covers
checklist_repo: <owner>/<repo>             # optional: where the live checklist page and its data file live
checklist_data: site/checklist.json        # the data file threads edit by PR
sandbox_queue: <owner>/<private-repo>      # optional: where approved cloud runs are tracked (issues)
spend_cap: <amount per month>              # the budget the billing check compares against
approval_phrase: "go batch <id> $<total>"  # the only words that approve a cloud run; a bare "go" never does
brand: <repo with brand/profile.json>      # optional: use the brand-profile skill for the sheet
```

## 1. Gather from primary sources, not memory

- **Threads or sessions still running:** for each, note what it waits on. Everything stops when usage ends,
  and nothing should run in the cloud on its own.
- **Open pull requests** in `public_repos`: read `mergeable_state` from
  `https://api.github.com/repos/<owner>/<repo>/pulls/<n>`, and **read it twice**. GitHub computes it lazily, so
  the first read after a push says `unknown`.
  - `clean` and `has_hooks` mean ready; `dirty` is a conflict; `unstable` means a check is failing or still
    running.
  - Mark pairs that must merge together, and hold both halves if either one has a conflict.
  - Mark ordering dependencies, for example a data source before the page that renders it.
  - Mark PRs opened in the last hour as "read first".
- **Cloud runs:** open run issues in `sandbox_queue`. Note which are approved but have no recorded result.
- **Security:** if an audit is running, ask it for only the steps that need the owner's own hands, with no
  secret values.
- Ask whoever owns each conflicted PR to rebase it before usage runs out.

## 2. The private sheet (artifact)

Make it phone-first, with a copy button on every command block. Sections, in this order:

1. **If you do only three things.**
2. **Security clicks**, with direct settings links. Say that GitHub settings pages need a browser (with the
   desktop site on a tablet), because the GitHub app can't change them.
3. **Nothing billing:**
   - what could still be running, and the expected still-billing list (domains, alerts)
   - `spend_cap` and month-to-date spend, with portal links
   - one read-only, shell-neutral Cloud Shell block (`pwsh -NoLogo -Command '...'`) that lists resource
     groups, VM power states and resources billed by the hour, and runs a Cost Management month-to-date query
     that prints the full HTTP error if it fails
4. **Pending merges:** the ready list in order, then read first, hold, and needs a rebase. Private repos are
   named only generically.
5. **What waits for them,** in priority order: tags, release blocks, DNS, decision cards.
6. **Safe to ignore.**
7. **Where to look:** the live checklist, PR and issue searches, boards, Actions, the security overview,
   cost.
8. **Threads:** a state for each and what it waits on.
9. **Restart:** a copyable first message for when Claude is back. It covers which security clicks were done,
   cloud run results, PRs merged while out (so their owners re-pin and record closeouts), rebases, then
   decisions.

No credentials, tenant or subscription IDs, emails or private-repo contents, because the sheet may be shared.
Republish to the same URL on every change.

## 3. The public live checklist (optional)

- Edit only `checklist_data`, by pull request.
  - Line kinds: `pr` (one pull request, or a pair), `ruleset` (deletion, non_fast_forward and pull_request
    rules on the default branch), `pvr` (private vulnerability reporting) and `manual`.
  - Public repos only, and nothing private.
  - Drop lines that are already done.
- Keep a full check under the anonymous limit: 60 requests an hour per network, one per open PR plus one per
  repo for each setting line.
- Run the repo's tests, run a code review, open the PR and give the owner its "merge N". After the merge,
  check the page answers 200.

## 4. Close out

Record what was learned where the project keeps its closeouts, update project memory for this offline
window, and leave the thread open for updates until the owner says done.

## Rules that always hold

- **Cloud runs:** only `approval_phrase` approves a cloud run, and the sheet says to approve none while the
  owner is out.
- **Data:** never delete the last copy of anything. Stop VMs rather than deleting them, so teardown keeps its
  evidence.
- **Results** always carry a word, never color alone.
