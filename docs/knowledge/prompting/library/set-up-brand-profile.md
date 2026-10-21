---
title: "Prompt: Set up a brand profile in a repo"
summary: "Has a project write brand/profile.json from the brand files its repo already has, with a test that keeps it equal to the stylesheet"
topic: prompting
status: partial
last_reviewed: 2026-10-21
---

# Prompt: Set up a brand profile in a repo

**Use when** a project has a look (a token stylesheet, logos, fonts) but no `brand/profile.json`
yet, so the [brand-profile skill](../../../../skills/brand-profile/README.md) can't use it.

**Paste into** the project that owns the repo. Send it there rather than doing it from another
project, so only that project reads its repo.

**Run so far:** written for one app's brand (2026-10-21); the same steps were run by hand for a
shared site theme the same day.

## Placeholders

| Placeholder | What goes in | Example |
|---|---|---|
| `{{BRAND}}` | The brand's name as it is written | example-brand |
| `{{REPO}}` | The repo that holds the brand's files, `owner/name` | example/app |
| `{{SCHEMA_SOURCE}}` | Where to copy `profile.schema.json` from | the 2ndbrain template's `skills/brand-profile/` |
| `{{OFF_LIMITS}}` | What the profile must never carry beyond the usual | user data, app content |

## Prompt

```text
Set up a brand profile for {{BRAND}} in {{REPO}}, using the brand-profile skill (section 3,
"Set up a profile for a project").

1. Gather what the repo already has: the stylesheet or theme file with the color custom
   properties (light and dark), fonts, logo and icon files, the name and tagline, and any design
   notes. Read only brand and theme files.
2. Write brand/profile.json to the brand-profile schema. Copy profile.schema.json beside it from
   {{SCHEMA_SOURCE}}. Set sourceOfTruth to the token stylesheet, list every brand file in assets,
   and set visibility to match the repo.
3. Add brand/README.md listing the files, and a test in the repo's own test runner that keeps the
   profile's colors equal to the stylesheet in both themes, checks every role names a color, and
   checks every asset file exists.
4. Keep everything that is not brand out of the profile: no {{OFF_LIMITS}}, no names, emails,
   IDs or secrets.
5. Open a pull request, then tell me so the brand's row in my brand-profile skill can point at it.
```

## Notes

- **The test is the point.** A profile copied from a stylesheet drifts the first time the
  stylesheet changes; a test that compares the two in both themes catches it in CI.
- **No logo is fine.** A theme with no logo files can list its token stylesheet as the one
  `source` asset.
- **Leave identity out.** Header code often holds the owner's email or social links; the profile
  takes colors, type and rules only.
