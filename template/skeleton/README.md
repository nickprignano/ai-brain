# 2ndbrain

A template for an **agent-ready knowledge base** that lives in your project repo and keeps
itself current: facts and gotchas with versions, decision records, known errors, a weekly digest of
what changed upstream, and a monthly freshness check. People, tools and AI agents all read the same
files. The tooling runs on GitHub Actions with the built-in token: no LLM calls, no API keys, no
paid services.

The full system is in [docs/2ndbrain/SPEC.md](docs/2ndbrain/SPEC.md). Agents follow the
[2ndbrain-kb skill](.claude/skills/2ndbrain-kb/SKILL.md).

It sets up one of two ways, and **private is the default**:

- **Private:** the knowledge base plus a private wisdom layer above your public KBs: lessons, root
  causes, procedures, decisions, goals, disagreements, parked side ideas and the patterns you notice
  across projects ([notes/](notes/capture-rules.md)). Only short directives you approve ever leave it
  ([outbox/](outbox/README.md)).
- **Public:** the knowledge base alone, for a project you work on in the open. Setup removes the
  private layer for good.
- **Sandbox:** a private repo where assistants from other vendors can work on material that's safe
  to share with them, out of reach of your private layer. Setup removes the private layer and puts
  the sandbox rules at the top of AGENTS.md ([sandbox/](sandbox/README.md)).

## Start your own

1. Press **Use this template** and create your repo. Pick **Private** unless you're sure you want
   a public KB. Never fork it publicly.
2. Clone it and run setup once:

   ```bash
   python3 scripts/setup.py            # private (the default): checks GitHub agrees the repo is private
   python3 scripts/setup.py --public   # public: removes notes/, outbox/ and hub.toml
   python3 scripts/setup.py --sandbox  # sandbox: private, no private layer, rules for outside agents
   ```

   The `privacy` workflow fails any public repo that still has the private layer, and a public
   repo with a real note in it fails even if it's the template.
3. Private only: edit [hub.toml](hub.toml) with your public hub KB (`owner/repo`), and in
   `private_names` this repo's name and anything else that must never appear in a public repo.
   Optionally, add an `observer` row to the hub's `family.yaml`: it says the layer exists and
   nothing else.
4. Edit [docs/knowledge/kb.toml](docs/knowledge/kb.toml) to set your KB's name, title, tagline and
   topics. Then add your topics to the `topic` list in
   [page.schema.json](docs/knowledge/schema/page.schema.json).
5. Replace [getting-started/](docs/knowledge/getting-started/README.md) with your first real topic
   page, and add the sources you want watched to
   [sources.toml](docs/knowledge/sources.toml).
6. In **Settings > Actions > General**, turn on **Allow GitHub Actions to create and approve pull
   requests**. Then run **Actions > kb-freshness** once, so the `kb-*` and `handoff` labels exist.
7. Run the checks (or let CI do it):

   ```bash
   pip install -r scripts/kb/requirements.txt
   python3 scripts/kb/build.py && python3 scripts/kb/validate.py
   python3 -m unittest discover -s scripts/kb
   python3 -m unittest discover -s scripts
   ```

   In a private repo the scheduled workflows count against your plan's included GitHub Actions
   minutes. Public repos run them free.

To join a family of KBs, list them in [family.yaml](docs/knowledge/family.yaml) and add their two
sources.

## How the private layer moves

- **Up:** a weekly `rollup` workflow reads your public hub (its digest, freshness issues,
  decisions, field reports and known errors) and opens an issue here listing what's new. Tick what's
  worth a pattern note. Monthly, it also lists notes due for review. It runs only in a private repo,
  with this repo's own `GITHUB_TOKEN`; the hub is public, so reading it needs no other credential.
- **Down:** you write a directive in `outbox/`. A scheduled Claude session, or you by hand, opens it
  as a pull request in the hub under your own account. It takes effect only when you merge it there.
  No workflow here can write to another repo.
- **Notes' license:** if you want a different license for your notes, change LICENSE and NOTICE in
  your copy. The kit's code stays Apache-2.0.

## Staying current with the template

This repo is generated from a working knowledge base,
[ai-brain](https://github.com/nickprignano/ai-brain), which owns the format. The private layer is
written generically as an empty starting point; nothing in it comes from anyone's private notes. The
`github_commits` source in your `sources.toml` watches this template, so the weekly digest tells
you when the machinery changes. Adopt a change by copying it in a PR.

## Where the idea came from

The project second brain started as a work prototype for a complex enterprise migration
engagement: an agent grounded in a human-curated document site, with a chat front end for everyone
on the project. Brian Madden (Citrix) put the name "second brain" on it in one of his videos, and
Meta's article on an organizational second brain showed where it could go the same day.

## License

Apache-2.0 ([LICENSE](LICENSE)). See [NOTICE](NOTICE) for what's adapted from where.
