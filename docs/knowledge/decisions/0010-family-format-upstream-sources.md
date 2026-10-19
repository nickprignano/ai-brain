---
status: proposed
date: 2026-10-19
decision-makers: [maintainer]
---

# 0010. Family format: link to upstream sources of truth, check against them, and give back

## Context and Problem Statement

Each KB in the family builds on someone else's documentation: vendor docs sites, product repos and
SDK repos. Those are the sources of truth for what a product is documented to do, and a KB that
paraphrases them goes stale the day they change, with nothing to say it did. The AVD KB found that
none of its topic pages linked the vendor docs they built on, that "verified" said a run happened
but not which documented behavior it confirmed or contradicted, and that its list of upstream asks
had no path from an ask to a filed issue and covered only one vendor. This KB has the same gaps:
its upstream asks live under `anthropic/`, and the family code points at a different folder in each
KB. How should the shared format link out to, check against and contribute to upstream sources?

## Considered Options

- Keep format v1; each KB links upstream as it sees fit
- A writing rule only, in each KB's curation page
- Writing rules now, plus a front matter field, a freshness check and a contribution path in
  format version 2

## Decision Outcome

Chosen option: "Writing rules now, plus a front matter field, a freshness check and a contribution
path in format version 2", because a rule nobody checks drifts, and the check needs no model and
no new service. The rules and the v2 proposal are written once in the
[family spec](../../2ndbrain/SPEC.md#5-upstream-sources), section 5.

### The writing rules (format v1, in force now, no code)

| Rule | This KB |
|---|---|
| **Link, don't restate.** A page says only what upstream doesn't (a gap, a contradiction found in a real run, how documented pieces combine) and links upstream for the rest. A sibling's topic still gets a link to the sibling. | Accept |
| **Who wins.** Upstream is the source of truth for what a product is documented to do; a real run is the source of truth for what it did. When they disagree, the page keeps the finding, links both, and the disagreement becomes an upstream ask. | Accept |
| **Verified means checked against the source.** A `verified` page's claims about documented behavior link the source they were checked against, not only say that a run happened. | Accept |
| **Giving back is a person's act.** Ask, then a reviewed draft, then a person files it under their own account and records the link. Drafts carry nothing from a real estate or account, follow the upstream's contributing rules, license and CLA, and link the public evidence. No agent opens an issue or PR upstream. | Change (C1) |
| **Default upstream set.** Microsoft Learn plus the repos in `sources.toml`. | Change (C2) |

### The format v2 proposal

| Item | This KB |
|---|---|
| Optional `upstream:` list of `https://` URLs in page front matter, shape checked by `validate.py` | Change (C3) |
| `freshness.py` warns, never fails, on `verified` pages with no `upstream`, and on pages whose upstream changed after `last_reviewed` (GitHub: last commit date; Microsoft Learn: `ms.date` or `updated_at`), in the monthly job only | Change (C4) |
| `upstream.yaml` covers any upstream: optional `target`, a `drafted` status between `candidate` and `raised`, an optional `draft` path | Change (C5) |
| The file and its page move from the vendor folder to `upstream/`, with `upstream/drafts/` beside them | Accept, with one more reason: the family code in `kblib.py` points at `anthropic/upstream.yaml` here and `microsoft/upstream.yaml` in the AVD KB, so one path makes the shared code truly the same |
| Ship as `format_version: 2` together with AVD 0009, so siblings bump once | Change (C6) |

### Changes to bring back to the AVD project

- **C1. "Outside the family" instead of "outside the connected repos".** "Connected repos" is an
  avd-swarm term. Family wording: an agent may open issues and PRs only on repos listed in
  `family.yaml` (and the project's own repos); anything else is upstream and a person files it. A
  draft also carries nothing from the private layer.
- **C2. Each KB names its own default upstream set.** Microsoft Learn is right for AVD and wrong
  for this KB, whose primary docs are Anthropic's. The family rule: the default set is the docs
  sites a KB names in a new optional `upstream_docs` list in `kb.toml` (an identity setting, since
  it's the one part that differs), plus the repos it watches in `sources.toml`.
- **C3. An explicit `upstream: []` means none applies.** Process pages, decision-like pages and
  write-ups of a KB's own runs build on no upstream. A missing field on a `verified` page warns;
  an empty list says someone checked and silences the warning. `plan` pages are skipped.
- **C4. Change detection for any host, and opt-in network.** GitHub URLs use the API with the
  built-in token (last commit on that path); Microsoft Learn uses `ms.date` or `updated_at`; any
  other site uses the `Last-Modified` header or an `article:modified_time` meta tag. A URL with no
  date it can read is listed once under "can't tell", never as changed. The fetches run only behind
  a `--upstream` flag that the monthly workflow passes, the way `--family` already works, and a
  failed fetch is reported, never fatal. Whether Anthropic's docs expose a usable date is
  *unverified*.
- **C5. Statuses carry their evidence.** `drafted` needs `draft`, and the draft file must exist;
  `raised` and `merged` need `link`. A missing `target` means the KB's primary upstream (the first
  `upstream_docs` entry).
- **C6. Bundle with what's already queued.** Format v2 already carries this KB's 0005 (review
  windows and revisit dates), 0007 (format ownership) and 0008 (directives). It should carry AVD
  0009 and this decision too, so the family bumps once for all five. This KB hasn't recorded its
  own position on AVD 0009 yet; that is a separate copy.

### Consequences

- Good, because a page that links its source tells the reader where the full, current answer is,
  and the freshness check says when that answer changes.
- Good, because what a run teaches has a route back to the people who can fix the product or the
  docs, and a person stays the one who files it.
- Bad, because the freshness check reaches sites outside GitHub, so it runs only in the monthly job,
  and some networks block it.
- Bad, because pages already marked `verified` don't yet link their sources; they show up in the
  monthly issue and are fixed as they're re-checked, not all at once.
- Neutral, because the v2 part is a proposal: no shared code changes until all four KBs accept it.

## More Information

Also recorded in [AVD 0011](https://github.com/nickprignano/avd-second-brain/blob/main/docs/knowledge/decisions/0011-family-format-upstream-sources.md)
(proposed in avd-second-brain#20, with its avd-swarm pair in avd-swarm#10). Proposed to the family
per [curation.md](../curation.md#staying-aligned-with-the-family). The writing rules apply here now,
in [curation.md](../curation.md#upstream-link-out-check-against-give-back) and the
[upstream asks page](../anthropic/upstream-contributions.md).
