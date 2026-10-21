---
title: "Keeping the knowledge base current"
summary: "How the KB stays current: the weekly digest, the prior-art check, the feedback loop, the freshness check and family alignment"
topic: curation
status: verified
last_reviewed: 2026-10-20
---

# Keeping the knowledge base current

Four tools keep the KB current without spending time (or LLM tokens) rediscovering things. Two
bring new information in (the weekly digest and the prior-art check), and two check that what's
already here still holds (the feedback loop and the monthly freshness check). A fifth part keeps
this KB aligned with its siblings, and a sixth keeps it pointed at the upstream sources it builds on.

## Weekly digest (`kb-curator`)

[`.github/workflows/kb-curator.yml`](../../.github/workflows/kb-curator.yml) runs every Monday.
It reads [sources.toml](sources.toml), collects anything new from the last 8 days and opens an
issue labelled **kb-digest** with a checklist grouped by source. Each source names the KB page its
findings belong on. Items whose URL is already linked from the KB are left out, and so are merge
commits and dependency bumps; an item listed under one source isn't listed again under a later
one. If nothing is new, no issue is opened.

Watched today:

- Anthropic's Claude Code and Python SDK releases, and the Anthropic cookbook and courses repos
- The Model Context Protocol specification
- The sibling KBs' decisions and other changes (see [Staying aligned](#staying-aligned-with-the-family))

Blog and newsletter feeds come next. Each one is added only once a curator run shows it works, and
people are chosen with the method in [experts.md](experts.md).

Working a digest: for each ticked item, add what matters to the page named next to the source
(facts, versions, fixes; not a link dump), then close the issue.

To watch something else, add a `[[source]]` table to [sources.toml](sources.toml). Supported
kinds: `github_releases`, `github_commits` (optionally limited to one `path`), `github_issues`,
`github_org_repos`, `github_user_repos`, `github_search`, `feed`
(RSS/Atom, with optional `keywords`) and `zendesk`. Run it locally with:

```bash
GITHUB_TOKEN=$(gh auth token) python3 scripts/kb/curate.py --since-days 30
```

A source that fails (rate limit, site down) is listed at the bottom of the digest and doesn't
stop the others.

## Prior-art check (`kb-prior-art`)

Before building something new, check whether it's already solved:

```bash
GITHUB_TOKEN=$(gh auth token) python3 scripts/kb/prior_art.py "prompt caching"
```

or run **Actions > kb-prior-art** with the topic. It searches, in order: this KB, each sibling KB
in [family.yaml](family.yaml), GitHub repositories (best match, then most stars), Python and
TypeScript code, and issues and pull requests. If something useful turns up, record it on the
relevant topic page, so the next person doesn't search again.

### Searching well: what a head-to-head showed

On 2026-10-20 Claude (in a claude.ai cloud session) and GitHub Copilot Chat on github.com ran
the same three prior-art searches and two freshness tasks, scored against answer keys written
before Copilot's answers came in. One run of five tasks, first answers only, so the find rates
are indicative:

| Task | Claude | Copilot |
| --- | --- | --- |
| OneNote to Obsidian tools | 4/4 | 3/4, plus one find Claude missed |
| Well-known Claude Code skills | 1/4 | 2/4, plus one new find |
| Cloudflare repos to watch | 2/4 | 3/4, plus one repo that wouldn't load |
| Weekly digest of three repos | 6/6 | 1/6, three items from a months-old changelog section |
| Re-check three KB claims | 1 settled | 1 moved forward, 2 wrong or unanswered |

What it means for how we search:

- **Search from more than one angle.** One star-sorted query missed the three skills repos this
  KB had already vetted, because the most-starred results were hyped ones. Use best match and
  stars, the curated index for the area (for skills, skills.sh and Anthropic's plugin directory;
  for a platform, the vendor's own GitHub org) and a web search. The union of both tools' lists
  beat either one.
- **For tools that read a data format, search code for the format's own names.** On 2026-10-21
  a survey of tools for a social-network data export found its privacy-audit tools only through
  GitHub code search for the export's file and field names; repo search by name, description and
  stars returned viewers and chat-stats scripts instead. Small tools often have vague names but
  have to spell out the field names in their code.
- **Open every candidate before it goes in the KB.** Copilot's answers listed "checked on repo"
  in place of licences, stars and dates, included one repo that wouldn't load, and passed off a
  changelog section about 300 versions old as current. Its finds are leads until opened.
- **Read the source for a digest.** Reading the changelog and release pages directly beat
  search-based summaries for "what changed this week".
- **Know what a cloud session can't reach.** In a claude.ai cloud session the proxy blocks
  `api.github.com`, so `prior_art.py`'s GitHub sections fail there (checked 2026-10-20); run
  **Actions > kb-prior-art** instead and read its log. The session's GitHub tools can search all
  of GitHub but only read commits and files in attached repos, so a freshness check that needs
  another repo's history has to attach it first.
- **Batch licence lookups with `repo:` qualifiers.** In a cloud session, GitHub repo search with
  several free-text terms plus a `stars:>N` filter often returned nothing (2026-10-20), while one
  query of 20 `repo:owner/name` qualifiers returned stars, licence and last push for all of them in
  one call. Search broadly first, then batch the finalists that way.
- **Copilot is worth a paste before publishing a survey list**, where one or two extra finds
  matter. It isn't worth automating: every item still has to be checked.

The digest and prior-art scripts use only the Python standard library (3.11+).

## Feedback loop (`kb-feedback`)

Real results flow back into the KB through three issue forms:

- **Knowledge base feedback:** what worked, broke, went out of date or is missing, for one page
  (label `kb-feedback`).
- **Known error:** an error, its cause and fix, for the [troubleshooting catalog](troubleshooting/README.md)
  (label `kb-known-error`).
- **Suggest an expert to follow:** a nomination for the [experts study](experts.md) (label `kb-source`).

Each form has a required public-safe tick box. A maintainer reviews the issue and, if it's useful
and public-safe, labels it **kb-accepted**.
[`.github/workflows/kb-feedback.yml`](../../.github/workflows/kb-feedback.yml) then appends it to
[field-reports.yaml](field-reports.yaml), [known-errors.yaml](troubleshooting/known-errors.yaml) or
[experts.yaml](experts.yaml), regenerates and validates the KB, and opens a pull request that closes
the issue. If the form is incomplete or fails validation, the workflow comments on the issue instead.

The label is the safety gate: issue text from anyone is only parsed as data, never executed, the PR
still goes through review, and gitleaks and the KB checks run on it. Two one-time settings matter:

- Run **Actions > kb-freshness** once so the `kb-*` labels exist (issue forms only apply labels
  that already exist).
- Turn on **Settings > Actions > General > Allow GitHub Actions to create and approve pull
  requests**. Without it, the workflow pushes the branch and asks you to open the PR.

Pull requests opened by the workflow's own token don't start other workflows. The job runs the KB
checks itself; close and reopen the PR to run the full CI before merging.

## Freshness check (`kb-freshness`)

[`.github/workflows/kb-freshness.yml`](../../.github/workflows/kb-freshness.yml) runs on the 1st
of each month and keeps one open issue labelled **kb-freshness** listing:

- pages reported broken or outdated in field reports that aren't marked `resolved` yet
- pages whose `last_reviewed` is more than 90 days old (pages with status `plan` are skipped)
- pages with status `unverified` or `partial`, with the number of claims still marked *unverified*
- known errors whose fix is still unverified
- experts due for re-scoring, with each tracked expert's digest yield
- sibling KBs on a different family format version, or whose `family.yaml` can't be read

Work it by re-checking each item against a primary source or a real run, then updating the page's
text, `last_reviewed` and `status`. Open claim re-checks as a pull request labelled
`no-auto-merge`: a wrong "still true" or "now false" changes what the KB tells people. Run it locally with `python3 scripts/kb/freshness.py --family`.

## Staying aligned with the family

[family.yaml](family.yaml) lists every KB in the family, this one included (`self: true`): its
repo, KB path, role, focus, what it's the source of truth for (`owns`) and the family format version.
This KB is the hub: it owns the AI knowledge the others use. nerdio-hcl is the format's reference
implementation. A sibling without a `repo` isn't linked yet. `build.py` turns the file into the
"Related knowledge bases" table in the [KB README](README.md#related-knowledge-bases) and a section
in `llms.txt`. The schema and the family code in `scripts/kb/` are the same in every KB.

- **Watch each other.** Each set-up sibling gets two `github_commits` sources in
  [sources.toml](sources.toml): one with `path` set to its decisions folder, and one with `path` set
  to its KB folder. `validate.py` fails if either is missing for a sibling with a `repo`. A private sibling can't be read with
  the built-in token; its sources stay in and start working once the repo is public.
- **Link instead of copying.** When a fact belongs to a sibling's topic, link to their page. When we
  learn something they need, open an issue or PR on their repo with the evidence. If two KBs
  disagree, the one closer to the topic is the source of truth, and the other links to it.
- **Share the format, not the content.** The schemas, scripts, checks, workflows and guardrails stay
  the same in every KB. To change them, write a proposed decision titled "Family format: ..." in
  one KB, open the same change in the others, and bump `format_version` in every `family.yaml` once
  all of them have merged. The freshness check flags a sibling whose version differs.
- **Cross-project decisions.** A decision that affects more than one project is recorded in each
  affected KB, and each copy says "Also recorded in ..." with links.

## Upstream: link out, check against, give back

This KB is not a second copy of anyone's documentation. Vendor docs and product or SDK repos are
upstream, the sources of truth for what a product is documented to do; the rules are in the
[family spec](../2ndbrain/SPEC.md#5-upstream-sources), section 5. The upstream set is the docs
sites this KB's topics build on plus the repos watched in [sources.toml](sources.toml).

- **Link out.** A topic page links the upstream page each fact builds on and adds only what
  upstream doesn't say. Upstream wins on what a product is documented to do; a real run wins on
  what it did, and when they disagree the page keeps both links and the gap becomes an upstream ask.
- **Check against it.** When the weekly digest shows an upstream change that touches a page,
  re-check the page and update `last_reviewed`. A page is `verified` only when its claims about
  documented behavior link the source they were checked against. Format version 2 proposes an
  `upstream:` front matter list that the monthly freshness check compares with each source's own
  last-changed date.
- **Give back.** When a run shows a gap or a docs error, add an entry to the KB's `upstream.yaml`,
  draft the text for review in a PR, and have a person file it under their own account and record
  the link. No agent opens an issue or PR outside the family's own repos, and nothing from a real
  account or the private layer goes upstream.

## Capture check (`kb-capture`)

Code that changes without a KB entry loses what was learned, so two checks ask for one
(family decision 0011, in the [family spec](../2ndbrain/SPEC.md#3-keeping-a-kb-current)). Both use only git and
[`scripts/kb/capture_check.py`](../../scripts/kb/capture_check.py):

- **Stop hook.** [`.claude/settings.json`](../../.claude/settings.json) runs it when a Claude Code
  session ends. If files outside `docs/knowledge/` changed and nothing inside it did, it asks once
  for the lesson, or for one line saying why there's none. `capture_hook` in [kb.toml](kb.toml)
  sets it to `block`, `warn` (a reminder only) or `off`.
- **PR check.** [`.github/workflows/kb-capture.yml`](../../.github/workflows/kb-capture.yml) fails a
  pull request that changes code without changing `docs/knowledge/`, unless it has the `no-kb`
  label and a `No KB entry: <reason>` line in its body. It reruns when the label or body changes.
  PRs from the family's automation are exempt.
- **A repo without its own KB** puts `capture_hook` and `kb_repos` in `.claude/kb-capture.toml`
  and passes with a `KB: <link>` line to the lesson in one of those KB repos.

Paths in `capture_ignore` (and `llms.txt` and lockfiles) don't count as code.

## Checks on every change (`kb-validate`)

[`.github/workflows/kb-validate.yml`](../../.github/workflows/kb-validate.yml) runs on pull
requests that touch the KB. It runs `validate.py` (front matter and YAML against the
[schemas](schema/page.schema.json), MADR sections, duplicate ids, KB paths the data references,
links and anchors, email and public-IP patterns, and the family checks), checks the generated
tables and `llms.txt` are up to date (`build.py --check`), and runs the KB scripts' unit tests.
Secrets are caught by gitleaks in [`secrets.yml`](../../.github/workflows/secrets.yml), on every PR.
