---
title: "Platforms for AI apps"
summary: "Hosting AI apps: serverless workers, Cloudflare Access, iOS home-screen apps, sign-in inside app wrappers, calling GitHub's API, local GPUs for media models"
topic: platforms
status: verified
last_reviewed: 2026-10-20
sources:
  - https://docs.github.com/en/rest/using-the-rest-api/getting-started-with-the-rest-api
  - https://developers.cloudflare.com/cloudflare-one/identity/authorization-cookie/validating-json/
  - https://developers.cloudflare.com/workers/ci-cd/builds/
  - https://willitrunai.com/blog/video-generation-gpu-guide-2026
  - https://rocm.blogs.amd.com/artificial-intelligence/comfyui-windows/README.html
  - https://tomshardware.com/pc-components/ram/ram-price-index-2026-lowest-price-on-ddr5-and-ddr4-memory-of-all-capacities
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

## Running open image, video and audio models on your own PC

Checked 2026-10-20 for a Windows PC (ComfyUI, NVIDIA):

- **VRAM decides what loads; system RAM is the overflow.** 16 GB runs every image and audio model and
  LTX-2.3 video with offloading; 24 GB runs Wan 2.2 14B at 720p in FP8, the open quality benchmark;
  full-precision Wan needs 54-65 GB ([Will It Run AI](https://willitrunai.com/blog/video-generation-gpu-guide-2026)).
  Pair 16-24 GB cards with 64 GB of RAM or more.
- **One bigger card beats two.** ComfyUI doesn't split one image or video job across GPUs, and a used
  24 GB RTX 3090 beats a faster 16 GB card for video.
- **NVIDIA first on Windows.** AMD's Ryzen AI Max+ 395 loads big models in its shared memory but ran a
  Wan 2.2 640x640 clip in 27 minutes, needs Python 3.12, and ComfyUI's install can replace its ROCm
  PyTorch with a CUDA one ([AMD ROCm blog](https://rocm.blogs.amd.com/artificial-intelligence/comfyui-windows/README.html)).
- **Local video still trails hosted video.** Open models make ~5 s clips in 10+ minutes on a 24 GB card;
  hosted APIs make longer clips with sound in a minute or two. Open stills and speech are close to hosted,
  and open speech models can clone voices.
- **Cost rarely pays back for one person.** In October 2026 GPU and DDR5 prices were up several-fold
  on a memory shortage (64 GB of DDR5 at ~$989 against a $159 low,
  [Tom's Hardware](https://tomshardware.com/pc-components/ram/ram-price-index-2026-lowest-price-on-ddr5-and-ddr4-memory-of-all-capacities)).
  At a few hundred images a month, a ~$2,700 entry PC buys years of API credits. Buy for privacy,
  unlimited iteration, voice cloning or music; rent a cloud GPU by the hour to learn first.
- **ComfyUI's local HTTP API makes it an easy MCP backend.** A media MCP server can post a saved
  workflow to `127.0.0.1:8188` instead of calling a paid API, cost 0, with the same job-id polling as
  hosted video.
