# 2ndbrain-public

A template for a **public, agent-ready knowledge base** that lives in your project repo and keeps
itself current: facts and gotchas with versions, decision records, known errors, a weekly digest of
what changed upstream, and a monthly freshness check. People, tools and AI agents all read the same
files. The tooling runs on GitHub Actions with the built-in token: no LLM calls, no API keys, no
paid services.

The full system is in [docs/2ndbrain/SPEC.md](docs/2ndbrain/SPEC.md). Agents follow the
[2ndbrain skill](.claude/skills/2ndbrain/SKILL.md).

## Start your own

1. Press **Use this template** and create your repo.
2. Edit [docs/knowledge/kb.toml](docs/knowledge/kb.toml) to set your KB's name, title, tagline and
   topics. Then add your topics to the `topic` list in
   [page.schema.json](docs/knowledge/schema/page.schema.json).
3. Replace [getting-started/](docs/knowledge/getting-started/README.md) with your first real topic
   page, and add the sources you want watched to
   [sources.toml](docs/knowledge/sources.toml).
4. In **Settings > Actions > General**, turn on **Allow GitHub Actions to create and approve pull
   requests**. Then run **Actions > kb-freshness** once, so the `kb-*` labels exist.
5. Run the checks (or let CI do it):

   ```bash
   pip install -r scripts/kb/requirements.txt
   python3 scripts/kb/build.py && python3 scripts/kb/validate.py
   python3 -m unittest discover -s scripts/kb
   ```

To join a family of KBs, list them in [family.yaml](docs/knowledge/family.yaml) and add their two
sources. For a private layer above your KBs, start from
[2ndbrain-private](https://github.com/nickprignano/2ndbrain-private).

## Staying current with the template

This repo is generated from a working knowledge base,
[ai-brain](https://github.com/nickprignano/ai-brain), which owns the format. The
`github_commits` source in your `sources.toml` watches this template, so the weekly digest tells
you when the machinery changes. Adopt a change by copying it in a PR.

## Where the idea came from

The project second brain started as a work prototype for a complex enterprise migration
engagement: an agent grounded in a human-curated document site, with a chat front end for everyone
on the project. Brian Madden (Citrix) put the name "second brain" on it in one of his videos, and
Meta's article on an organizational second brain showed where it could go the same day.

## License

Apache-2.0 ([LICENSE](LICENSE)). See [NOTICE](NOTICE) for what's adapted from where.
