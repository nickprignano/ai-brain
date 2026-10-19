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

**Run so far:** yes, as a project instruction in the hub's own project (2026-10-19).

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
2. Route each one: the topic page it belongs to in {{PROJECT_KB}}; {{SHARED_KB}} when it's
   general (no employer or customer specifics); {{PRIVATE_LAYER}} when it's personal. A reusable
   prompt goes, generalized, to the hub's prompt library
   (docs/knowledge/prompting/library/ in the hub repo), as a pull request there.
3. Show me the batch as a short table (lesson, destination, one line each) and wait for my one
   yes for the whole batch, then write them as pull requests.
4. If nothing was worth recording, say so and why.

Your final reply says what was recorded where, or that nothing was and why.
```

## Notes

- **One yes for the whole batch.** It keeps writes deliberate without a question per lesson. This
  is the short form of the closeout in the family's 2ndbrain capture skill
  (`skills/2ndbrain/SKILL.md`); when a repo has that skill, it wins.
- **"Nothing, and why" is a valid closeout.** Requiring the reason stops it becoming a reflex.
- Project-instructions form: "A thread runs the closeout before its final reply: lessons go to the
  project KB, the shared KB or the private layer after my one yes for the batch. The final
  reply says what was recorded where, or that nothing was worth recording and why. Don't resolve a
  thread until its closeout is recorded or I waive it."
- Enforced in the family by [decision 0011](../../decisions/0011-family-format-enforced-kb-capture.md).
