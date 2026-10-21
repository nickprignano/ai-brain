---
title: "Prompt: Park an idea for later"
summary: "Has Claude file a researched side idea as one note in the owner's private parked-ideas folder, with findings, why it's parked and when to revisit"
topic: prompting
status: verified
last_reviewed: 2026-10-21
---

# Prompt: Park an idea for later

**Use when** a thread has researched a side idea that isn't main-quest work, and the owner wants
it kept somewhere they'll find it again instead of acted on now.

**Paste into** the thread that did the research, if the repo holding the parked-ideas folder is
attached there, or the Claude project that owns that repo.

**Run so far:** a close earlier version parked a data-export analysis survey (2026-10-21).

## Placeholders

| Placeholder | What goes in | Example |
|---|---|---|
| `{{PARKING_REPO}}` | The private repo that holds parked ideas, `owner/name` | example/notes |
| `{{PARKED_PATH}}` | The folder in it, with a `_template.md` note format | notes/parked |
| `{{IDEA}}` | One sentence: what the idea is and the constraint that matters | analyze my photo library's metadata locally, nothing uploaded |
| `{{FINDINGS_LINK}}` | Where the full research lives | the project file `photo-tools/prior-art.md` |
| `{{KEY_POINTS}}` | Three to five bullets: the recommendation and the traps | only one maintained tool; block its network access first |
| `{{WHY_PARKED}}` | Why not now | side project; no evening free for the import |
| `{{REVISIT_WHEN}}` | The condition that should bring it back | I want the privacy summary, or the tool reaches 1.0 |

## The prompt

```text
Park an idea in {{PARKED_PATH}} in my private repo {{PARKING_REPO}}. Check that folder for an
existing note on the same idea first and update it if there is one. Otherwise copy its
_template.md, fill in every field, add a line to the repo's index, and commit the way that repo's
own rules say. Nothing else.

Idea: {{IDEA}}
Status: parked (today's date).
Findings so far: {{FINDINGS_LINK}}. Copy the recommendation into the note, then link to the full
findings. Don't copy the whole survey. Key points:
{{KEY_POINTS}}
Why parked: {{WHY_PARKED}}
Revisit when: {{REVISIT_WHEN}}

Rules: the parked note is the one record; anywhere else gets a pointer, not a copy. Never
ask for, read or copy any of my personal data the idea is about. If the repo is private, keep its
name out of any public repo, issue or PR.
```

## Notes

- **One note, one source of truth.** A parked idea copied into several places drifts; the other
  places link to the note.
- **"Revisit when" is the useful line.** Without a trigger, a parked idea is just forgotten.
- **Keep the research and the personal data apart.** The note holds what was learned about the
  tools, never anything from the data itself.
