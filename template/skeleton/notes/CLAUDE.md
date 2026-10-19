# Instructions for AI assistants: the private layer

notes/, outbox/ and hub.toml are this repo's private layer. Before writing or changing any note:

1. Read [capture-rules.md](capture-rules.md). It decides which note type to write and when.
2. Copy the `_template.md` in the target folder, fill in every front-matter field, and add the note
   to [index.md](index.md).
3. Run `python3 scripts/privacy_check.py`, `python3 scripts/stale_check.py` and
   `python3 scripts/outbox_check.py` before committing. If the privacy check says the repo is
   public, stop: write nothing here until the owner makes it private.

Never let this layer's contents reach a public repo:

- No note names, paths, quotes, reasoning or this repo's name in any public repo, issue, PR or
  commit. Public repos may say a private layer exists, nothing more.
- What goes out is a directive in `outbox/`, written only after the owner says yes to it, and only
  as a pull request the owner merges.
- No secrets, keys or tokens anywhere, and never ask for one in chat.
- No employer or customer material, and no copies of public pages: link to them.
- Lessons about yourself or your way of working go here, not in docs/knowledge/. The knowledge
  base holds what was learned about the project's subject.
