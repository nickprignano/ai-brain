---
name: park-it
description: Use when the user says "park it", "park this", "not main quest" or asks whether they already looked into an idea. Records a side idea as a parked note in the private layer's parked bucket, or finds one that's already there.
---

# park-it: a shelf for side ideas

Some ideas get researched, or just named, and then set aside on purpose. Parking keeps what was
learned so nobody redoes it, and says what would make the idea worth picking up again. Parked
ideas live in one bucket in the private layer, one note each.

## Settings

Fill these in when you install the skill.

```yaml
brain_repo: <owner>/<private-repo>     # the private layer (a 2ndbrain copy set up private)
parked_path: notes/parked              # the bucket; its _template.md is the note format
index: notes/index.md                  # add a line under "Parked ideas"
rules: notes/capture-rules.md          # the private layer's rules; they win over this file
```

## When

- **Park:** the user says "park it", "park this", "not main quest", or decides to stop on an idea
  for now. Write the note without asking again: the ask is the yes.
- **Look up:** the user asks "did I already look into X?" or starts researching an idea. Search
  `parked_path` first and report what's there, with its status and revisit triggers, before
  researching again.
- **Revisit:** a revisit trigger in a parked note fires, or the note comes due in
  `scripts/stale_check.py`. Re-check the triggers, and change the status only on the user's word.

## Writing a parked note

1. **Hard stop.** No secrets, and no employer or customer material, even generalised. Say in one
   line where that belongs instead, and stop.
2. **Prior note.** Search `parked_path` for the same idea. If one exists, update it (add what's
   new, set `updated` and `last_verified`) instead of starting another.
3. **Write.** Copy `parked_path/_template.md` to `parked_path/<slug>.md` and fill in every
   front-matter field. In the body:
   - **What was checked:** findings from the thread, each with a source and a confidence. Mark
     anything not confirmed as unverified. Say if nothing was built.
   - **Why it's parked:** the reasons, a sentence each.
   - **Revisit if:** concrete triggers that would change the answer.
   Write only what actually happened in the thread. Never invent findings or sources.
4. **Index.** Add `- [Title](parked/<slug>.md): one line (parked YYYY-MM-DD)` under "Parked
   ideas" in `index`, in the link style the index already uses.
5. **Check and commit.** Run `python3 scripts/stale_check.py`, then commit to the default branch
   and push, the way the private layer's rules say.
6. **Report** the path and commit in one line.

Without write access (a plain chat), draft the note and its index line in full, with the path,
and say plainly that it isn't filed yet.

## Statuses

| Status | Means |
|---|---|
| `parked` | Set aside on purpose; no work planned. |
| `revisit` | A trigger fired; look at it again. |
| `unparked` | Moved into real work. Keep the note and link to where the work went. |
| `dropped` | Won't come back. Keep the note so the idea isn't researched again. |

## Rules that always apply

1. The parked note is the one home for the idea. A chat summary or project memory keeps a
   one-line pointer to it, never a copy.
2. A parked idea never goes to a public knowledge base, and public text never names the bucket or
   links to a parked note. When the research also found something true for anyone, that part
   goes to a public KB through the 2ndbrain skill, and the parked note links out to it.
3. No dollar figures and no employer or customer specifics in any note.
