---
title: "Prompt: Summarize the weekly KB digest"
summary: "Has a scheduled Claude routine turn the raw kb-digest issue into the handful of changes that matter, read from the sources, and open one PR of KB adds"
topic: prompting
status: verified
last_reviewed: 2026-10-29
---

# Prompt: Summarize the weekly KB digest

**Use when** a KB's weekly `kb-curator` run opens a digest issue with more items than anyone will
read, and you want a scheduled Claude routine to pick out what matters.

**Paste into** a scheduled Claude routine on the KB's repo, set to run a few hours after the
curator (Mondays, after 13:00 UTC for this family).

**Run so far:** not yet as written; the summary step matched a hand-run test on 2026-10-20.

## Placeholders

| Placeholder | What goes in | Example |
|---|---|---|
| `{{REPO}}` | The KB's repo | owner/ai-brain |
| `{{READER}}` | Who the KB is for, in a sentence | someone running Claude Code in cloud sessions with skills, hooks, subagents and MCP servers |

## The prompt

```text
Work the newest open issue labelled kb-digest in {{REPO}}. If it was opened more than 3 days ago,
or already has a summary comment from you, stop and say so in one line.

1. For each source in the issue, read the source itself (CHANGELOG.md, release pages, the
   commits), not search results, and only for the issue's date range.
2. Pick the 5 to 8 changes that matter most to {{READER}}. Skip dependency bumps, merge commits,
   and release notes that say only "bug fixes".
3. Post one comment on the issue: each change in one line, with its version or commit and a link,
   and the KB page it belongs on. Tick those items in the issue body.
4. Open one pull request that adds the facts to those pages (facts, versions, fixes; not links
   alone), following the repo's AGENTS.md. Don't change claims marked unverified or re-check old
   claims: that is the monthly freshness pass. If nothing is worth adding, open no PR and say so
   in the comment.
5. Close the digest issue once the PR is open, or once the comment says nothing was worth adding.
```

## Notes

- **Read the sources, don't search for them.** In a 2026-10-20 test, reading the changelog got all
  six key changes; a search-based summary got one and mixed in a months-old changelog section.
  See [Searching well](../../curation.md#searching-well-what-a-head-to-head-showed).
- **Keep claim re-checks out of it.** A digest PR of new facts is low risk and can auto-merge; a
  verdict on an old claim needs the owner's eyes, so it goes in the freshness pass with
  `no-auto-merge`.
