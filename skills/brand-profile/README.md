# brand-profile: one brand file per project

A Claude skill that makes pages, artifacts, slides and images in a project's own look. Each project
keeps its brand in one file, `brand/profile.json`: colors for light and dark, which color plays
which role, type, every logo with what it's for, starter files, the lines every page must carry,
voice and rules. The skill reads it before making anything and writes it when a brand is set up or
changes. The skill itself is [SKILL.md](SKILL.md).

## Why one file

A brand spread across stylesheets, logo folders and a design doc gets rebuilt by hand, slightly
wrong, every time something new is made. One machine-readable file, kept equal to the stylesheet
by the repo's tests, lets any tool use the brand without knowing its token names, and a starter
file per output carries the whole release so nothing is retyped. Nothing is a default brand: with
no profile, the skill asks.

## Files

- [SKILL.md](SKILL.md): the skill.
- [profile.schema.json](profile.schema.json): the profile format. Copy it next to each new
  `brand/profile.json`.
- [profile.example.json](profile.example.json): a filled-in profile with placeholder values.

## Install

1. Copy this folder into a new skill in your Claude account: SKILL.md plus the schema and example
   (a skill can hold supporting files). SKILL.md alone also works; it fetches the schema from this
   template when it needs it.
2. In "Known profiles", delete the example row and add a row for each of your projects that has a
   `brand/profile.json`. With no rows, the skill still finds the profile in the repo you work in.
3. Set up a profile in a project by asking for one ("set up a brand profile for this repo").
