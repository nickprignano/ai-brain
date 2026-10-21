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
| UnicodeDecodeError: 'charmap' codec can't decode byte ... (or mangled non-ASCII text) when a KB script reads or writes a file on Windows | Before Python 3.15 (PEP 686), open(), Path.read_text() and Path.write_text() without encoding= use the ANSI code page on Windows, not UTF-8. | Pass encoding="utf-8" to every text open; EncodingTests in scripts/kb/test_kb.py fails on one that doesn't. *(unverified)* | [link](https://peps.python.org/pep-0686/) |
<!-- END GENERATED: known-errors -->

## Adding an entry

Add an entry to [known-errors.yaml](known-errors.yaml) with the exact error text as the symptom,
the versions it was seen on in `applies_to`, and a `source` (a KB page or an https link). Or open a
**Known error** issue, and a maintainer turns it into a pull request.
