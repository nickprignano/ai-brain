---
title: "Prompt: Make a static web game installable"
summary: "Has Claude turn a no-build static web app or canvas game into an installable app that plays offline on iPhone, iPad and Android, with tests and a manual device checklist"
topic: prompting
status: verified
last_reviewed: 2026-11-08
---

# Prompt: Make a static web game installable

**Use when** a static site (plain HTML, CSS and ES modules, no bundler) should install to the home
screen and work offline: small browser games, single-page tools. Put it in the first build of a
new game rather than adding it later.

**Paste into** the thread or project that owns the game's repo.

**Run so far:** a close earlier version made a canvas pinball game installable (2026-11-08):
Chrome reported no installability errors and it played offline with the server stopped. Real
devices not yet checked.

## Placeholders

| Placeholder | What goes in | Example |
|---|---|---|
| `{{REPO}}` | The game's repo, `owner/name` | example/space-game |
| `{{NAME}}` | App name, 12 characters or fewer for the home screen | Starfield |
| `{{ORIENTATION}}` | `portrait`, `landscape` or `any` | portrait |
| `{{BG}}` | Background color while it loads | #0d1117 |
| `{{HOST}}` | How it's served, and whether `/index.html` redirects to `/` | Cloudflare Workers static assets (redirects) |
| `{{CROSS_ORIGIN}}` | Files loaded from other hosts, pinned to a version | a theme stylesheet on a CDN, pinned to a commit |

## The prompt

```text
Make {{REPO}} an installable web app that plays offline on iPhone, iPad and Android. It's static
files with no build step; keep it that way and add no dependencies to the game. It's served by
{{HOST}}. Name: {{NAME}}. Orientation: {{ORIENTATION}}. Background: {{BG}}.

1. Manifest (manifest.webmanifest): id "/", start_url "/", scope "/", display "standalone" (not
   fullscreen: it hides the Android clock), orientation, background_color and theme_color, and
   PNG icons 192 and 512 "any" plus 512 "maskable" with the artwork inside the central 80% circle.
2. Icons: original artwork as one SVG; a small tool script (outside the served files) renders the
   PNGs, including a 180px opaque apple-touch-icon. Use the SVG as the favicon.
3. Page head: manifest link, icon links, theme-color meta, mobile-web-app-capable,
   apple-mobile-web-app-capable, apple-mobile-web-app-status-bar-style "default" (not
   black-translucent: it breaks light themes), apple-mobile-web-app-title, viewport-fit=cover.
   If the game has light and dark themes, set theme-color from the page background on each
   theme change.
4. Service worker at the site root, one versioned cache, cache first:
   - Precache every served game file, as a list written into the worker by a tool script along
     with a content hash of those files as the version. Add a test that fails when the list or
     the hash is stale, with a message naming the script to run.
   - Cache the page as "/" and answer every navigation with it (query strings included) when the
     host redirects /index.html.
   - Fetch the precache with { cache: 'reload' } so a new version never stores old files.
   - Files in {{CROSS_ORIGIN}} go in best effort: install doesn't fail if they don't load, and
     the game must still work without them.
   - Activate deletes old caches and claims clients.
5. Updates: a new version downloads in the background. Show an "Update" button somewhere
   already visible between games (a menu, not a full toolbar). Tapping it posts skip-waiting,
   and the page reloads on controllerchange only if the player tapped it: claim() fires
   controllerchange on the first visit too. Call registration.update() when the page becomes
   visible again, since installed apps are reopened rather than reloaded.
6. Install help: an "Install" button from beforeinstallprompt on Chromium; on iPhone and iPad
   (iPadOS reports a Mac with touch points) a line saying "tap Share, then Add to Home Screen".
   Hide both when already running installed (display-mode standalone, or navigator.standalone).
7. Phone details: env(safe-area-inset-*) padding on edges that hold controls,
   touch-action: manipulation on buttons, Web Audio resume() on every tap (iOS interrupts it
   after a lock), and a readable message instead of a blank page if the first data fetch fails.
   Register the service worker before that fetch.
8. Check it: the repo's tests (including the new one), then a headless Chromium run against a
   local server: the worker controls the page, CDP Page.getInstallabilityErrors and
   Page.getAppManifest return no errors, the game reloads and plays with the server stopped, and
   after a changed file the Update button appears without a reload and switches caches when
   tapped. Lighthouse has no PWA category any more; don't cite it.
9. Red team the plan before building, open one pull request, and reply with this list of checks
   for me to do on real devices:
   - iPhone Safari: Share, Add to Home Screen; icon looks right; opens without browser bars;
     status bar readable in light and dark; play with Airplane Mode on; lock the phone mid-game,
     unlock, and check sound comes back.
   - iPad: same, in both orientations.
   - Android Chrome: Install prompt or menu Install app; icon not cropped; play offline.
   - After the next deploy: reopen the installed app, check the Update button appears, tap it.
```

## Notes

- **Why the content hash.** A cache-first worker only updates when its own bytes change. A
  hand-bumped version gets forgotten; a hash checked by a test can't be.
- **Leave splash screens out.** iOS startup images need one file per device size; the background
  color is enough.
- **What this doesn't cover.** Push notifications, background sync and app-store wrappers. The
  platform traps behind each step are in
  [Platforms: home-screen web apps](../../platforms/README.md#home-screen-web-apps-ios-and-pwa-installs).
