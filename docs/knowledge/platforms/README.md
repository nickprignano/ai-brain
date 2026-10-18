---
title: "Platforms for AI apps"
summary: "Hosting AI apps: serverless workers, databases, sign-in inside app wrappers, calling GitHub's API"
topic: platforms
status: verified
last_reviewed: 2026-10-17
sources:
  - https://docs.github.com/en/rest/using-the-rest-api/getting-started-with-the-rest-api
---

# Platforms for AI apps

Where and how AI apps run: serverless workers and their databases, sign-in from inside app
wrappers, and calling third-party APIs from them.

## Calling GitHub's API from Cloudflare Workers

GitHub's REST API requires a `User-Agent` header on every request. Browsers and curl send one
automatically, but `fetch()` in a Cloudflare Worker doesn't, so calls fail until you set one. Any
value that names your app works. Observed on a site that lists repos from a Worker, and fixed by
adding the header (2026-09).

- Unauthenticated calls are rate limited per IP (60 an hour at last check), and Workers can share
  IPs, so add a token for anything that refreshes often.

## Google sign-in inside Android app wrappers

Google OAuth refuses sign-in inside an embedded Android WebView, with the error
`disallowed_useragent`. To ship a web app that uses Google sign-in as an Android app, use a Trusted
Web Activity (TWA), which runs in real Chrome, or install it as a PWA from Chrome. Observed on
2026-09-11 while making a web app installable on Android.

- Installing the PWA from Chrome needs no build at all and is the quickest path.
- A TWA (for example built with Bubblewrap) needs a signing keystore and a matching fingerprint in
  `/.well-known/assetlinks.json`, or the app shows the browser bar.
- A PWA's service worker should never cache API routes.
