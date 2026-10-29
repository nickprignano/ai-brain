---
title: "Known errors"
summary: "Errors hit with the Claude API, SDKs, agents and AI tooling: symptom, cause, fix and source"
topic: troubleshooting
status: verified
last_reviewed: 2026-10-18
---

# Known errors

Errors we've hit, what caused them and what fixed them. The table is generated from
[known-errors.yaml](known-errors.yaml); fixes marked *(unverified)* haven't been confirmed yet.

<!-- BEGIN GENERATED: known-errors (edit the YAML, then run scripts/kb/build.py) -->
| Symptom | Cause | Fix | Source |
|---|---|---|---|
| GitHub REST API calls fail from a Cloudflare Worker but work from a browser or curl | GitHub requires a User-Agent header, and fetch() in a Worker doesn't send one | Set a User-Agent header naming your app on every request | [README.md](../platforms/README.md#calling-githubs-api-from-cloudflare-workers) |
| `disallowed_useragent` from Google sign-in inside an Android app | Google OAuth blocks sign-in in embedded WebViews | Wrap the web app as a Trusted Web Activity, or install it as a PWA from Chrome | [README.md](../platforms/README.md#google-sign-in-inside-android-app-wrappers) |
| UnicodeDecodeError: 'charmap' codec can't decode byte ... (or mangled non-ASCII text) when a KB script reads or writes a file on Windows | Before Python 3.15 (PEP 686), open(), Path.read_text() and Path.write_text() without encoding= use the ANSI code page on Windows, not UTF-8. | Pass encoding="utf-8" to every text open; EncodingTests in scripts/kb/test_kb.py fails on one that doesn't. | [link](https://peps.python.org/pep-0686/) |
| Open kb-digest issues pile up week after week, and ticking items in one does nothing | kb-curator opened a new digest every Monday but nothing closed the old ones, and kb-feedback only handled the issue forms, so a ticked digest had no path to a pull request | The curator closes older unticked digests (keeping last week's open one more week); kb-accepted on a digest opens a no-auto-merge PR that adds the ticked links to their pages and closes it | [curation.md](../curation.md#weekly-digest-kb-curator) |
| The kb-freshness issue stays open with an old list after every item was fixed | The workflow's issue step ran only when items != 0, so a clean run never touched the open issue | Add an items == 0 step that closes the open issue, only on a run with the default window | [curation.md](../curation.md#freshness-check-kb-freshness) |
| Every tracked expert is flagged "nothing in the digests" on a newly set-up KB | The yield check counted digests in the whole window, so zero digests (or an expert scored after the last one) read as a dead feed | Judge yield only after two digests since the expert was scored, and flag a source straight away when a digest lists it as failed | [curation.md](../curation.md#freshness-check-kb-freshness) |
| A feed source (often a YouTube channel feed) shows "HTTPError: HTTP Error 500" under Sources that failed, then works next week | The feed host returns a transient 5xx and the curator didn't retry | sources.http_get retries once after five seconds on a 5xx; 4xx and timeouts still fail at once | [curation.md](../curation.md#weekly-digest-kb-curator) |
| A jq test("^- \\[x\\]"; "m") filter misses a ticked checkbox in an issue body | In jq 1.7, tried on a two-line body, ^ matched only at the start of the string, with or without the "m" flag | Match a line start with (^\|\n) instead, as kb-curator.yml does | [curation.md](../curation.md#weekly-digest-kb-curator) |
| A pull request opened by a workflow waits forever on required checks that never start | Events caused by a workflow's GITHUB_TOKEN don't trigger other workflows, so pull_request checks never run on the PR it opens | Close and reopen the PR once (a person's reopen starts them); kb-feedback's issue comment says so | [link](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows) |
<!-- END GENERATED: known-errors -->

## Adding an entry

Add an entry to [known-errors.yaml](known-errors.yaml) with the exact error text as the symptom,
the versions it was seen on in `applies_to`, and a `source` (a KB page or an https link). Or open a
**Known error** issue, and a maintainer turns it into a pull request.
