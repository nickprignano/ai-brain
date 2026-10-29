---
title: "Prompt: Move sensitive OneNote notebooks to markdown safely"
summary: "Has an organization-approved Claude walk you through backing up, converting with onenote-md-exporter and verifying OneNote notebooks, with no data lost or leaked"
topic: prompting
status: verified
last_reviewed: 2026-10-29
---

# Prompt: Move sensitive OneNote notebooks to markdown safely

**Use when** you want years of OneNote notes as markdown files (for Obsidian or any other
markdown editor), the notebooks hold data you can't afford to lose or leak (such as customer
information on a work account), and you want Claude to help without the content leaving where it
is allowed to be.

**Paste into** a Claude that your organization has approved for this data, such as your
organization's Claude workspace. Never use a personal Claude account, a personal repo or a shared
project for notes you don't own.

**Run so far:** not yet.

## Placeholders

| Placeholder | What goes in | Example |
|---|---|---|
| `{{NOTEBOOKS}}` | The notebooks to move, by a label you're happy for Claude to see | "Notes 2016-2020", "Team wiki" |
| `{{POLICY_ANSWER}}` | What your IT or data owner said about markdown copies of this data | Allowed in the work OneDrive on a managed laptop; no other copies |
| `{{BACKUP_DIR}}` | Where the full-fidelity backup goes, inside the approved storage | the OneNote-backup folder in your work OneDrive |
| `{{VAULT_DIR}}` | Where the markdown goes, inside the approved storage | the Notes-vault folder in your work OneDrive |
| `{{AFTER}}` | What happens to OneNote afterwards | keep OneNote as the record and read in Obsidian / retire notebooks once verified |

## The prompt

```text
Help me move these OneNote notebooks into markdown files I can open in Obsidian:
{{NOTEBOOKS}}. They hold data I must not lose or leak. Guide me step by step; I run every
step on my own Windows PC, and you wait for my result before the next one.

Hard rules for this whole conversation:
- My data owner's answer on where copies may live is: {{POLICY_ANSWER}}. Every file you have me
  create goes under {{BACKUP_DIR}} or {{VAULT_DIR}}, nowhere else: no personal cloud, no
  USB stick, no git remote, no sharing links, and every temp file gets cleaned up.
- You never see note content. No pasting, screenshots, uploads, or copying the baseline CSV or
  logs into this chat. Ask only for counts, error types and line numbers. File, page, section
  and notebook names are content too (titles often hold names): if one is needed, have me
  replace it with a number first. If I share content anyway, tell me and don't repeat it.
- Nothing is deleted from OneNote until the verification step passes and I say so.
- Only tools that run locally: onenote-md-exporter (github.com/alxnbl/onenote-md-exporter,
  GPL-3.0, offline, drives the OneNote and Word desktop apps and Pandoc) and scripts you write
  that I can read before running. No tool that needs a cloud sign-in or sends content anywhere.
- If a step's result surprises you, stop and say so instead of working around it.

Steps:
1. Preflight. Check with me that I have Windows 10 or later, the OneNote desktop app from
   Microsoft 365 or OneNote 2013 or later (not the retired "OneNote for Windows 10" app) and
   Word 2013 or later. Have me confirm with IT that running this third-party tool and my own
   PowerShell scripts is allowed on this PC. Have me turn on "Download all files and images" in
   OneNote and sync every notebook fully. Password-protected sections are lost unless unlocked,
   and unlocking produces plaintext copies: only unlock them if my data owner approved that.
2. Backup. Have me export each notebook from the OneNote desktop app (File > Export > Notebook,
   OneNote Package .onepkg) into {{BACKUP_DIR}}. Test one: open it as a scratch notebook,
   confirm a page renders, close it. If .onepkg export isn't offered for a notebook, use
   OneNote's own notebook backup instead and tell me where it lands.
3. Baseline. Write a read-only PowerShell script that uses the OneNote COM API (GetHierarchy,
   GetPageContent) and records, per page: section, page level (subpages), created and modified
   dates, text length, and counts of images and attached files. Skip the recycle bin and
   deleted pages. Save it as a CSV in {{BACKUP_DIR}}, and give pages numbers so we can talk about
   them without names. Have me run it non-elevated with OneNote already open. Explain each line
   before I run it, and ask me only for the totals.
4. Pilot. Have me export one small section first with onenote-md-exporter in Markdown format
   into {{VAULT_DIR}}. Walk me through its settings and recommend: front matter on (keeps
   dates), OneNote links converted to wikilinks, HTML styling on (keeps complex tables), and
   resources stored next to their pages. Have me open a few pages in Obsidian and report by page
   number what looks wrong: images, tables, attachments, links, dates.
5. Full export. Once the pilot looks right, export each notebook. Collect error types. Then find
   where the exporter and Pandoc left intermediate files (its working folder and %TEMP%), and
   have me delete them and empty the Recycle Bin.
6. Verify. Write a script that matches the baseline CSV against {{VAULT_DIR}}: every page has a
   .md file (subpages included), text sizes are in proportion, image and attachment counts
   match, dates match the front matter, and no referenced file is missing. Watch for pages with
   duplicate titles that collided into one file. Every difference gets explained or fixed
   before we go on.
7. Known losses. List what the export can't carry over (handwriting, drawings flattened to
   images, cross-notebook and section links, page order, complex tables kept as HTML, page
   version history, authors, tag and to-do state, audio and video recordings, text recognized in
   images) and help me check which of my notebooks rely on those.
8. Vault hygiene. Before I use the vault day to day: Obsidian's Restricted mode on (no community
   plugins), no Obsidian Sync or Publish, no git, no AI plugins; no sharing links on
   {{VAULT_DIR}}; and a reminder that OneDrive version history keeps earlier copies. Ask whether
   my policy wants the folder excluded from Windows Search.
9. Afterwards: {{AFTER}}. If that means retiring OneNote notebooks, keep the .onepkg backups and
   the notebooks read-only for an agreed period first, and remind me nothing is deleted until I
   say so.

Finish with a short checklist of what was done, what was verified, what was lost and why, and
where the backup and vault live.
```

## Notes

- **The policy question comes before the tool.** Customer or employer data usually can't be
  copied anywhere the data owner hasn't approved, and sensitivity labels or DLP rules may forbid
  local copies even inside approved storage. Ask first, then fill `{{POLICY_ANSWER}}`.
- **Why onenote-md-exporter over Obsidian Importer for this case.** The
  [Obsidian Importer](https://obsidian.md/help/import/onenote) reads notebooks through a
  Microsoft account sign-in, which on a work account means consenting a third-party app in the
  organization's tenant; IT often blocks it. [onenote-md-exporter](https://github.com/alxnbl/onenote-md-exporter)
  runs offline against the desktop apps. Its README lists Markdown and Joplin as formats, with
  wikilinks by default, which Obsidian reads; it names Obsidian as a target but has no separate
  Obsidian format, and it doesn't support the Microsoft Store OneNote app (checked 2026-10-29).
- **Obsidian Importer now has an offline path too.** Its file import reads `.onepkg` and `.one`
  files on disk with no sign-in or connection (checked 2026-10-29), so the step-2 backup can feed
  it. It skips password-protected sections and recycle-bin pages and can't read rights-protected
  (sensitivity-labeled) files. Not tried in a run; if you use it instead, keep the same baseline
  and verification steps.
- **If DLP blocks the export.** [segunak/one-note-to-markdown](https://github.com/segunak/one-note-to-markdown)
  (MIT, a Windows desktop app) reads each page's XML over COM with `GetPageContent()` and, per
  its README, avoids OneNote's `Publish()` because DLP policies can block the intermediate files
  it writes (checked 2026-10-20). Not tried in a run; give it the same backup and page-count checks.
- **The .onepkg backup and the page-count baseline are what make "no data lost" checkable.**
  The tool's own README warns some data can be lost on export, so the prompt treats the
  conversion as a copy to verify, never a move.
- **Claude never needs the content.** Counts, page numbers and error types are enough to drive
  and check every step, which keeps the conversation itself from becoming another copy. Names
  count as content: exported file names are page titles, which often hold the sensitive part.
- **A page count alone doesn't prove nothing was lost.** The baseline records text size and
  image and attachment counts per page so the check can catch pages that exported empty.
