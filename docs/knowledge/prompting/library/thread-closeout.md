---
title: "Prompt: Thread closeout"
summary: "The closeout a thread runs before its final reply: lessons to the project KB, and to shared or private layers only after the owner's yes"
topic: prompting
status: verified
last_reviewed: 2026-10-19
---

# Prompt: Thread closeout

**Use when** a thread's work is done, before its final reply. It can also go in a project's
instructions, so every thread runs it.

**Paste into** the thread, or into the project instructions in the form shown under Notes.

## Placeholders

| Placeholder | What goes in | Example |
|---|---|---|
| `{{PROJECT_KB}}` | The project's own KB repo | example/tool-kb |
| `{{SHARED_KB}}` | The family's shared or public KB, or "none" | example/hub |
| `{{PRIVATE_LAYER}}` | The owner's private notes, or "none" | the private notes repo |

## The prompt

```text
Before your final reply, run the closeout:

1. List what this thread learned that someone would otherwise have to rediscover: facts,
   gotchas with versions, decisions and their reasons, prompts worth reusing.
2. Put each lesson on the topic page it belongs to in {{PROJECT_KB}}, in this work's pull request
   or a follow-up one. A reusable prompt goes, generalized, into the prompt library.
3. Lessons that belong in {{SHARED_KB}} (general, no employer or customer specifics) or in
   {{PRIVATE_LAYER}}: list them and wait for my one yes for the batch before writing them.
4. If nothing was worth recording, say so and why.

Your final reply says what was recorded where, or that nothing was and why.
```

## Notes

- **One yes per batch for anything outside the project.** It keeps writes to shared and private
  layers deliberate without a question per lesson.
- **"Nothing, and why" is a valid closeout.** Requiring the reason stops it becoming a reflex.
- Project-instructions form: "A thread runs the closeout before its final reply: lessons go to the
  project KB, and to the shared KB or the private layer only after my one yes per batch. The final
  reply says what was recorded where, or that nothing was worth recording and why. Don't resolve a
  thread until its closeout is recorded or I waive it."
- Enforced in the family by [decision 0011](../../decisions/0011-family-format-enforced-kb-capture.md).
