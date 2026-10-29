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
| UnicodeDecodeError: 'charmap' codec can't decode byte ... (or mangled non-ASCII text) when a KB script reads or writes a file on Windows | Before Python 3.15 (PEP 686, final), open(), Path.read_text() and Path.write_text() without encoding= use the locale encoding, which on Windows is the ANSI code page (locale.getencoding()), not UTF-8. | Pass encoding="utf-8" to every text open; EncodingTests in scripts/kb/test_kb.py fails on one that doesn't. | [link](https://peps.python.org/pep-0686/) |
| A gh --jq or jq filter such as test("^- \\[x\\]"; "m") never matches a ticked checkbox that isn't on the issue body's first line | In jq (Oniguruma) and gh's built-in gojq (RE2), ^ matches only the start of the string; the "m" flag doesn't make it match after each newline as it does in Python or JavaScript. | Match the line start explicitly: test("(^\|\n)- \\[[xX]\\]"). kb-curator.yml uses this to find digests with ticked items. | [curation.md](../curation.md#weekly-digest-kb-curator) |
| A scheduled check's tracking issue (kb-freshness, a drift or health check) stays open after every item is fixed | The workflow's issue step ran only when the check found items (if: items != '0'), so a clean run had no step that could close the open issue. | Run the issue step on every run and branch inside it: close the open issue with a comment when items is 0, otherwise edit or open it. | [curation.md](../curation.md#freshness-check-kb-freshness) |
| Weekly kb-digest issues pile up open with nothing ticked, and a ticked digest still needs someone to copy each item into the KB by hand | kb-curator opened a new issue every week but never closed older ones, and kb-feedback only turned feedback, known-error and source issues into pull requests. | kb-curator closes older open digests with nothing ticked as superseded by the new one; labeling a digest kb-accepted makes kb-feedback add its ticked items to their pages in a PR that closes it. | [curation.md](../curation.md#feedback-loop-kb-feedback) |
| A digest lists a working feed under 'Sources that failed this run' with HTTPError: HTTP Error 500 (seen on YouTube's channel feeds) | Some feeds return a transient 5xx; one failed request dropped the whole source for that week. | sources.http_get retries once after two seconds on a 5xx and raises on anything else. | [curation.md](../curation.md#weekly-digest-kb-curator) |
| The freshness issue says a tracked expert has 'nothing in the digests ... check the feed still works' on a KB that has no digests yet, or right after the expert was scored | Expert yield ran whenever a digest list was passed, even an empty one, and judged experts scored inside the review window. | freshness.py skips yield when there are no digest issues and for experts scored within --max-age-days. | [curation.md](../curation.md#freshness-check-kb-freshness) |
| The freshness check counts a claim 'marked unverified' on a page whose only hit is ordinary prose | The inline marker check matches *unverified, *not verified and the phrase 'not yet reviewed' anywhere outside code, so a sentence such as 'Not yet reviewed, for the next pass' counts as a marker. | Word open items without those phrases ('Reviewed on <date> and left out', 'No run has tried ...'), or put them in code; keep *unverified* for claims that need a check. | [curation.md](../curation.md#freshness-check-kb-freshness) |
| The freshness check reports a sibling with "couldn't read its family.yaml (HTTPError); private repo, or not set up yet" although the sibling's KB is public | The sibling moved its KB to another repo, and family.yaml and sources.toml still named the old one. | Point the sibling's repo in family.yaml and its two sources.toml entries at the repo that now holds docs/knowledge/family.yaml. | [curation.md](../curation.md#staying-aligned-with-the-family) |
<!-- END GENERATED: known-errors -->

## Adding an entry

Add an entry to [known-errors.yaml](known-errors.yaml) with the exact error text as the symptom,
the versions it was seen on in `applies_to`, and a `source` (a KB page or an https link). Or open a
**Known error** issue, and a maintainer turns it into a pull request.
