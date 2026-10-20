---
title: "Platforms for AI apps"
summary: "Hosting AI apps: serverless workers, Cloudflare Access, iOS home-screen apps, sign-in inside app wrappers, calling GitHub's API"
topic: platforms
status: verified
last_reviewed: 2026-10-20
sources:
  - https://docs.github.com/en/rest/using-the-rest-api/getting-started-with-the-rest-api
  - https://developers.cloudflare.com/cloudflare-one/identity/authorization-cookie/validating-json/
  - https://developers.cloudflare.com/workers/ci-cd/builds/
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

## Cloudflare Access in front of a Worker

Access only protects the hostnames it covers, so both halves are needed (2026-10-18):

- **The Worker checks the Access JWT itself** (the `Cf-Access-Jwt-Assertion` header against the
  team's keys and the app's AUD tag), and the `workers.dev` and preview URLs are turned off.
  Otherwise those URLs reach the Worker without going through Access.
- **Keep PWA install working** with a second Access app on the manifest, icons and
  `/.well-known/assetlinks.json` with a Bypass/Everyone policy. The more specific path wins.
- **A lockout is recoverable.** The Cloudflare dashboard isn't behind your Access apps. To back
  out, turn off the Worker's Access check first, then delete the apps.
- The Zero Trust menus were renamed: identity providers are under Integrations, apps under
  Access controls → Applications ("Self-hosted and private"), and the AUD tag under the app's
  Configure → Additional settings (checked 2026-10-18).

## Workers Builds failures you can't see

A cloud session can't read Cloudflare's build logs. Reproduce the build locally instead: run the
build with no settings to see the failure, then with sample values plus
`npx wrangler deploy --dry-run` to see it pass. When config moves into build variables, the
deploy command has to run the step that applies them first (for example
`npm run configure && npx wrangler deploy`, and the same before `wrangler versions upload` for
preview builds). Keep preview builds strict: a build that skips quietly shows green while a
setting is missing (2026-10-19).

## iOS home-screen web apps

Things that differ from Android and desktop when a web app is added to an iPhone home screen
(2026-10-19; sign-in not yet checked on a real device):

- **Icons.** iOS paints transparent corners black, so ship a square, opaque `apple-touch-icon`.
- **Speech.** Speech recognition can be refused inside a home-screen app. Fall back to the
  keyboard's mic button rather than telling users to change settings.
- **Sign-in.** The app keeps its own login, separate from Safari's. Google sign-in and Access
  sign-in leave the app briefly; a PIN form inside the app doesn't.
