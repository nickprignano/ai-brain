---
title: "Platforms for AI apps"
summary: "Hosting AI apps: Workers, Cloudflare Access, installable web apps, app-wrapper sign-in, GitHub API, local media GPUs, paying for media, posting to X"
topic: platforms
status: verified
last_reviewed: 2026-11-10
sources:
  - https://docs.github.com/en/rest/using-the-rest-api/getting-started-with-the-rest-api
  - https://developers.cloudflare.com/cloudflare-one/identity/authorization-cookie/validating-json/
  - https://developers.cloudflare.com/workers/ci-cd/builds/
  - https://willitrunai.com/blog/video-generation-gpu-guide-2026
  - https://rocm.blogs.amd.com/artificial-intelligence/comfyui-windows/README.html
  - https://tomshardware.com/pc-components/ram/ram-price-index-2026-lowest-price-on-ddr5-and-ddr4-memory-of-all-capacities
  - https://developers.cloudflare.com/workers-ai/platform/pricing/
  - https://docs.x.ai/developers/models
  - https://docs.x.com/changelog
  - https://docs.x.com/x-api/getting-started/pricing
  - https://support.buffer.com/article/859-does-buffer-have-an-api
  - https://developers.buffer.com/guides/integrations/claude.md
---

# Platforms for AI apps

Where and how AI apps run: serverless workers and their databases, sign-in from inside app
wrappers, and calling third-party APIs from them.

## Cloudflare repos worth watching

For apps and remote MCP servers on Workers, watch these for releases (GitHub: Watch > Custom >
Releases). Checked 2026-10-20 as the union of two independent searches:

- [cloudflare/workers-sdk](https://github.com/cloudflare/workers-sdk): Wrangler, Miniflare and the
  Vitest pool; the most direct signal for local dev and deploys. Releases several times a week.
- [cloudflare/agents](https://github.com/cloudflare/agents): the Agents SDK that remote MCP servers
  on Workers are built on.
- [cloudflare/workers-oauth-provider](https://github.com/cloudflare/workers-oauth-provider): OAuth
  for a remote MCP server on Workers.
- [cloudflare/mcp-server-cloudflare](https://github.com/cloudflare/mcp-server-cloudflare) and
  [cloudflare/mcp](https://github.com/cloudflare/mcp): Cloudflare's own MCP servers.
- Lower priority: [cloudflare/workerd](https://github.com/cloudflare/workerd) (the runtime),
  [cloudflare/skills](https://github.com/cloudflare/skills) (agent skills for building on
  Cloudflare), [cloudflare/sandbox-sdk](https://github.com/cloudflare/sandbox-sdk) and
  [cloudflare/ai](https://github.com/cloudflare/ai).

Skip cloudflare/miniflare: Miniflare now lives in workers-sdk.

**Microsoft overlap is thin.** Searching the cloudflare org on 2026-10-20 for Azure, Microsoft,
Windows, Entra, Intune and Teams found one Microsoft-specific repo:
[cloudflare/msft-risky-user-ad-sync](https://github.com/cloudflare/msft-risky-user-ad-sync), a
scheduled Worker that copies Entra ID risky users into groups for Zero Trust policies (small, a
handful of stars, open issues). The rest lives in
[cloudflare/cloudflare-docs](https://github.com/cloudflare/cloudflare-docs), which takes outside PRs:
about 35 Zero Trust pages on Entra ID (SSO, SCIM, Conditional Access, risky users) plus Intune
deployment, Microsoft 365 egress IPs and browser-based RDP, but nothing on Azure Virtual Desktop,
Windows 365 or VDI. Realistic ways to contribute from Microsoft experience: an issue or fix in that
small repo, a generic virtual-desktop tutorial in the docs, Windows issues in
[cloudflare/cloudflared](https://github.com/cloudflare/cloudflared) (the Tunnel client runs as a
Windows service), and an Entra ID upstream-login example for workers-oauth-provider, which no issue
asks for yet.

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

## Home-screen web apps (iOS and PWA installs)

Things that differ from Android and desktop when a web app is added to an iPhone home screen
(2026-10-19; sign-in not yet checked on a real device):

- **Icons.** iOS paints transparent corners black, so ship a square, opaque `apple-touch-icon`.
- **Speech.** Speech recognition can be refused inside a home-screen app. Fall back to the
  keyboard's mic button rather than telling users to change settings.
- **Sign-in.** The app keeps its own login, separate from Safari's. Google sign-in and Access
  sign-in leave the app briefly; a PIN form inside the app doesn't.

Learned making a static canvas game installable (2026-11-08; checked in headless Chromium, real
devices not yet):

- **Storage is separate too.** The home-screen app gets its own `localStorage`, so scores or
  settings saved in Safari don't carry over.
- **Status bar.** `apple-mobile-web-app-status-bar-style: black-translucent` forces white status
  text, which disappears on a light theme. `default` follows `theme-color` (iOS 15+); set that
  meta from the page's background when the theme toggles.
- **Sound stops after a lock.** iOS leaves the Web Audio context `interrupted` after the phone
  locks or the app goes to the background. Call `resume()` on every tap, not only the first.
- **Double-tap zoom.** Fast taps on a button zoom the page; `touch-action: manipulation` stops it.
- **No install prompt.** Safari never fires `beforeinstallprompt`; show "Share, then Add to Home
  Screen" instead. iPadOS reports itself as a Mac, so test for touch points too.
- **Service worker caching traps.** Cloudflare Workers static assets redirect `/index.html` to
  `/`, and a redirected response can't answer a navigation, so cache the page as `/`. Fetch the
  precache with `cache: 'reload'`, or a new version can store old files from the HTTP cache. If
  the worker calls `clients.claim()`, `controllerchange` fires on the first visit too, so reload
  only after the player asked for the update.
- **Checking it.** Lighthouse no longer has a PWA category. Chrome DevTools Protocol
  `Page.getInstallabilityErrors` gives Chrome's own verdict, and stopping the local server (not
  `setOffline`, which can miss service worker fetches) proves offline play. Nothing on Linux
  can test iOS install, so keep a short manual list for a real iPhone.
  The full recipe is the [installable web app prompt](../prompting/library/installable-web-app.md).

Learned on a second canvas game, a terminal plus a reflex game (2026-11-09; headless Chromium at
phone and desktop sizes):

- **`hidden` loses to CSS.** A rule such as `.prompt { display: flex }` overrides the `hidden`
  attribute, so add `[hidden] { display: none !important; }`.
- **Hover sticks on phones.** A tapped button keeps its `:hover` style; put hover rules inside
  `@media (hover: hover)`.
- **Glow without `shadowBlur`.** It is slow on iPhones. A wide, faint stroke under a thin, bright
  one with `globalCompositeOperation = 'lighter'` looks the same and stays fast.
- **A fixed-shape playfield wastes a portrait phone.** A 1000 × 600 field scaled to fit left a
  thin strip of sky on an upright phone; choosing a tall field at game start fixed it.
- **Flash safety as a pure, tested limiter.** For a game with explosions, the game logic asks a
  limiter for each glow (at most 3 a second, each under a quarter of the playfield, none when
  reduced motion is on), so the WCAG 2.3.1 limit is checked by unit tests, not by eye.

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

## Paying for image, video and speech at low volume

Checked 2026-10-20 for one person making a few images, short clips and a podcast a month:

- **A usage-billed API's spend cap isn't its cost.** xAI's media API has no monthly fee (images from
  $0.02, video from $0.02 a second, speech $15 per million characters,
  [xAI models](https://docs.x.ai/developers/models)), so light use costs a few dollars a month
  whatever the cap is. Before looking for a cheaper provider, price the actual volume.
- **A free tier is the only bigger lever.** Workers AI gives 10,000 neurons a day free on both
  Workers plans, enough for roughly 90 FLUX.2 klein 1024px images a day; overage needs Workers Paid
  ([Workers AI pricing](https://developers.cloudflare.com/workers-ai/platform/pricing/)). It has
  image, speech and transcription models but no video, so a hosted video API stays in the kit.
- **Workers AI doesn't need a Worker.** It has a plain REST API, so a script or skill with an API
  token can call it; a Worker or MCP server is extra build for a personal tool.
- **Transcribe podcasts locally.** Whisper (whisper.cpp or faster-whisper) runs free on a CPU on
  Windows and macOS and keeps audio on the machine. Hosted transcription of an hour-long file has to
  be chunked to fit request-size limits.
- **Podcast cover art is 3000x3000.** Apple and Spotify want 3000 px (1400 minimum), above what image
  models make by default. Generate a background, set the type as SVG, render to 3000 px locally.
- **Hosted audio cleanup is another data processor.** Free web tools that enhance speech upload the
  recording; keep them off any episode with a child's voice if the data rules forbid that.


## Posting to X from Claude or a script

Compared on 2026-11-10 for one person posting by hand at low volume, wanting to post from chat
and from a terminal without logging in to X each time.

- **X's own API is no longer free to start.** Pay-per-use replaced the free tier on 2026-02-06,
  and from 2026-04-20 a post costs $0.015, or **$0.20 if it contains a URL**
  ([X changelog](https://docs.x.com/changelog), [pricing](https://docs.x.com/x-api/getting-started/pricing)).
  Link posts are the expensive case, which matters for someone sharing their own blog posts. X's
  official CLI, [xurl](https://docs.x.com/tools/xurl.md), handles the OAuth sign-in once and keeps the
  tokens locally, but it still needs your own developer app and credits.
- **Buffer is the free route, and it covers both chat and scripts.** Its API comes with every plan,
  Free included, through one API key on the GraphQL endpoint, and an official MCP server covers chat
  ([Buffer help](https://support.buffer.com/article/859-does-buffer-have-an-api),
  [Claude setup](https://developers.buffer.com/guides/integrations/claude.md)). You don't need an
  X developer account. The Free plan allows 3 channels and 10 scheduled posts per channel
  ([pricing](https://buffer.com/pricing)).
  - The posts guide documents only `addToQueue` and `customScheduled`. `shareNow` (publish right away)
    and `shareNext` appear only in the API reference and in the MCP tool's schema. The MCP tool
    defaults to `addToQueue`.
  - On a new Free account, each MCP response showed three rate-limit windows: 150 requests per
    15 minutes, 600 per day, and 1,000 per 30 days for each connected channel (it went to 2,000 when
    a second channel was added). Buffer documents up to 3,000 a month, and says the API key and MCP
    draw on the same budget.
  - Buffer also ships an official CLI (`npm install -g @bufferapp/cli`, reads `BUFFER_API_KEY`). It's
    complete but wordy for one-line posts, so a short PowerShell wrapper over the GraphQL
    `createPost` mutation was written instead (not yet run against a real account).
- **A connector added mid-session can reach a running cloud session.** After the owner connected
  Buffer in claude.ai, its tools appeared through tool search in a Claude cloud session that was
  already running, with no restart needed. A search of the connector directory earlier in that
  session hadn't listed Buffer. Buffer's docs give `https://mcp.buffer.com/mcp` for adding it as a
  custom connector, but the owner didn't need that here.
- **Zapier and Make are out.** Zapier removed its Twitter integration on 2023-08-31, and Make
  removed X on 2025-04-03
  ([Zapier community](https://community.zapier.com/general-discussion-13/make-is-officially-decommissioning-x-formerly-twitter-app-will-it-still-be-supported-by-zapier-48640)).
  IFTTT wasn't checked, because it's built around triggers rather than posting on demand.
- **Typefully** also has an API key with a "publish now" option and an MCP server
  ([API docs](https://typefully.com/docs/api)). A third-party page lists the Free plan at 10 posts a
  month, *unverified*, since Typefully's own pricing page didn't show plan details.
- **Most search results on X API pricing are marketing from competing posting tools.** The figures
  checked out against X's own changelog, but the framing tilts toward their products, so go to
  docs.x.com first.
