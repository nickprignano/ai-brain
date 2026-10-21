---
name: brand-profile
description: Use when making a page, artifact, slide, image or README header for a project, so it follows that project's brand from its brand/profile.json; and to set up or update a project's brand profile.
---

# Brand profile

Each project keeps its brand in one file at `brand/profile.json` in its repo: colors for light and dark, the
roles those colors play, type, every logo and brand image with what it is for, starter files, the lines every
page must carry, voice and rules. This skill reads that file before making anything for the project, and writes
it when a brand is set up or changes. The format is `profile.schema.json`, kept with this skill in the 2ndbrain
template (https://github.com/nickprignano/2ndbrain, `skills/brand-profile/`) beside `profile.example.json`, a
filled-in profile with placeholder values. If neither file is next to this one, take them from there with git.
The required top-level fields are `schemaVersion` (1), `name`, `visibility`, `colors`, `roles`, `type` and
`assets`.

No profile is the default. A project uses a brand only when its repo has a profile or the person names one.

## Known profiles

| Project | Repo | Visibility |
|---|---|---|
| _example-project_ | _https://github.com/example-owner/example-repo_ | _public_ |

Replace the example row with your own projects. When you set up a profile for another project, add its row
here by proposing an update to this skill.

## 1. Find the profile

1. In the repo you're working in: `brand/profile.json`.
2. Otherwise the project's row above, when the person names that project, or the repo's README or AGENTS.md names that brand. Get it with git,
   not by retyping (set REPO from the row):

```bash
REPO=https://github.com/example-owner/example-repo; rm -rf /tmp/brand-src && git clone -q --depth 1 "$REPO.git" /tmp/brand-src && ls /tmp/brand-src/brand
```

3. No profile and no row: ask which project it is for, or offer to set one up (section 3). Never invent a brand,
   and never fall back to another project's.

The default branch is current inside the brand's own repo. For any copy made outside it (an artifact, or a page
committed to another repo), check out the profile's `release.tag` if the tag exists (`git -C /tmp/brand-src fetch --depth 1 origin tag <tag>`), and fall
back to the default branch if it doesn't exist yet.

## 2. Make something with it

### From a starter

When `starters` has one for the job (`page` for a page committed to a repo, `artifact` for a Claude artifact,
and so on), start from it. A starter carries a whole release of the brand; don't rebuild what it already holds.

1. Copy it with the shell (`cp -n /tmp/brand-src/<starter> page.html`); don't retype it.
2. Rename `<title>` (a two to four word name) and, for a page, the description meta.
3. Replace only the region the starter marks as the page's own content (a comment pair such as
   `<!-- page:start -->` ... `<!-- page:end -->`). Leave the header bar, notice, footer, credit line and the
   inlined style and script blocks as they are.
4. Use the shared classes the design system documents (`sourceOfTruth.docs`) before writing new ones.
5. Page styles: in an artifact, a second `<style>` after the inlined one; in a repo, the page's own stylesheet,
   with no inline style or script.

### Without a starter

Build from the profile. Write the `colors` as CSS custom properties: every token's light value on `:root`, the
dark values again under `@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) }` and under
`:root[data-theme="dark"]`. Use `roles` to know which token is the background, text, accent and so on. Fonts
from `type`: self-hosted `files` in a repo; `googleFonts` in a Claude artifact (the only font host it may load),
always with the `fallback` stack.

### Either way

- **Colors only through tokens.** If a color is missing, it becomes a token in the `sourceOfTruth` file first,
  with light and dark values, then in the profile. Status colors (good, caution, bad, info) mean results, never
  decoration, and always come with a word.
- **Logos and images:** pick from `assets` by `kind`, `background` and `use`; never redraw or recolor one. In an
  artifact, embed the SVG as a `data:` URI. A file marked `generated` is rebuilt by its script, not edited.
- **Required lines:** every item in `required` appears where its `where` says (notices, credit lines, license
  lines). A repo whose own notice says more keeps its own wording.
- **Voice and rules:** follow `voice` and every line of `rules`. `visibility: private` means nothing made from the
  profile goes on a public page, and a public page never names a private project.
- **Pinned copies:** a page committed to a repo takes a pinned copy of the brand's files (the design system's
  docs say how) and never loads the brand's website or a CDN at run time.
- Design both themes, keep a 16px gutter, no sideways scroll at 390px and 44px touch targets, and meet the
  artifact-design contract for an artifact.

## 3. Set up a profile for a project

1. Gather what the repo already has before asking: stylesheets with custom properties, theme files, logos and icons,
   fonts, the README's name and tagline, any design doc.
2. Ask the person only for what's missing (name, tagline, the main colors, logo files). Images they share go into the
   repo under `brand/` (`png/`, `source/`), never into chat history alone.
3. Write `brand/profile.json` to the schema (copy `profile.schema.json` beside it), with `sourceOfTruth` naming the
   files that define the brand if the repo has them, every brand file in `assets`, and `visibility`. Add
   `brand/README.md` listing the files.
4. Add a test, in the repo's own test runner, that the profile matches the schema and its source of truth (the same
   token values) and that every file in `assets` exists.
5. Propose it as a pull request, then propose this skill's Known profiles row.

## 4. Update a profile or its theme

1. If `sourceOfTruth` names a file for what changes (a token stylesheet, a logo), change that first.
2. Change `brand/profile.json` to match, set `updated` to today, and bump `release` if the repo releases its brand
   (and the version line in every design-system file that carries one).
3. Rebuild generated files with their scripts (the `generated` field names them) and run the repo's tests. The
   repo's design-system doc or AGENTS.md lists any other build steps.
4. Pull request. If the repo tags brand releases, the owner tags it after the merge; Claude sessions can't push
   tags.

## Never

- Put secrets, IDs, emails, customer or tenant names in a profile or a brand file.
- Use one project's brand for another, or a public brand on a private project's page.
- Load a brand's files from its website at run time; repos take a pinned copy.
