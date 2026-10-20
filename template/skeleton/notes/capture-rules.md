# Capture rules

These decide which note to write and when. They win over any summary elsewhere. An agent working in
this repo follows them exactly, and asks before writing anything not listed here.

| Type | Folder | Written when | How |
|---|---|---|---|
| Lesson | `lessons/` | A piece of work ends and something was learned that will still be true later | Automatically, at the end of the work, in a line or two per lesson |
| Root-cause analysis | `rca/` | Only after troubleshooting that the person asked for | Symptom, timeline, cause, fix, and what prevents it next time |
| Procedure | `procedures/` | Steps the person is in the loop for, done more than once | Numbered steps, with the checks after each |
| Decision | `decisions/` | The person had to make a call that needed judgment | Offered in one line at the end; written only on a yes. Carries a `revisit_on` date |
| Goal | `goals/` | The person states something they want to reach | Offered in one line; written only on a yes. Reviewed every 90 days |
| Disagreement | `disagreements/` | Only when the person asks for one | Both positions in their strongest form, and what would settle it |
| Parked idea | `parked/` | The person parks a side idea that isn't main quest (the park-it skill) | What was checked, why it's parked, and what would bring it back. Check here before researching an idea again |
| Pattern | `patterns/` | The same lesson or decision shows up in two or more knowledge bases, or one is plainly general | Offered in one line when the weekly roll-up shows one; written only on a yes |

## Every note

- Copy the `_template.md` in its folder, fill in every front-matter field, and add a line to
  [index.md](index.md).
- One subject per note. When something new is learned about the same subject, update that note
  instead of starting another.
- Write the fact or rule and its reason, not the story of how it was learned.
- Run `python3 scripts/stale_check.py` before committing.

## What never goes in

- Secrets, keys, tokens or passwords.
- Material from an employer or a customer: names, systems, data or anything learned under their
  confidentiality. This layer is personal.
- Copies of public knowledge base pages. Link to them in `sources` instead.
