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
| Weekly `kb-digest` issues stay open for weeks and pile up, and a ticked digest never becomes a pull request | kb-curator only opened issues; nothing closed an unworked digest, and kb-feedback acted on kb-accepted for the issue forms but not for digests | A new digest closes older open digests with no ticked item and no comment (`scripts/kb/digest.py supersede`); kb-accepted on a ticked digest adds its items to their pages and opens a PR that closes it (`digest.accept`) | [curation.md](../curation.md#weekly-digest-kb-curator) |
| The `kb-freshness` issue stays open with items that were fixed long ago | The workflow ran its issue step only when `items != 0`, so a clean run never touched the open issue; it also runs only monthly, so the body goes stale between runs | An explicit clean branch closes the open issue when the check finds nothing; run the workflow by hand after a fix to refresh it | [curation.md](../curation.md#freshness-check-kb-freshness) |
| The freshness check says a tracked expert has "nothing in the digests" on a new KB, or right after the expert was added | Yield was counted over the whole 90-day window even when no digest, or none since the expert was scored, existed yet | Count yield only over digests opened since the expert's `reviewed` date, and skip the expert when there are none | [curation.md](../curation.md#freshness-check-kb-freshness) |
| A digest lists a feed (often a YouTube channel feed) under "Sources that failed this run" with `HTTPError: HTTP Error 500`, and the next run works | The feed answered a transient 5xx and the fetcher had no retry for server errors | `http_get` retries a 5xx once after a short wait; a 4xx still fails at once | [curation.md](../curation.md#weekly-digest-kb-curator) |
| Every freshness run lists "<sibling>: repo not linked yet" or "couldn't read its family.yaml (HTTPError)" for a sibling that has a working KB | The sibling's row in family.yaml had no `repo`, or still named a repo the KB had moved out of (here the AVD KB moved to another account and the Liquidware KB to a new repo) | Point the row at the repo that holds the sibling's docs/knowledge/family.yaml, copy `owns` from the sibling's own row, and move its two sources in sources.toml with it | [curation.md](../curation.md#staying-aligned-with-the-family) |
| A PR shows one failed `kb-capture` run next to a green one on the same commit | The `opened` run checked the PR before its `KB:` line or `no-kb` label was added; the `labeled` or `edited` rerun passed, but the failed run stays listed | Open the PR with the `KB:` line already in the body, or the `no-kb` label set at creation | [curation.md](../curation.md#capture-check-kb-capture) |
<!-- END GENERATED: known-errors -->

## Adding an entry

Add an entry to [known-errors.yaml](known-errors.yaml) with the exact error text as the symptom,
the versions it was seen on in `applies_to`, and a `source` (a KB page or an https link). Or open a
**Known error** issue, and a maintainer turns it into a pull request.
