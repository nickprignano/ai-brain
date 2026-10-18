# ai-brain

A living, public knowledge base for AI research: the Claude API, agents and the tooling around
them. It holds findings, gotchas, fixes with versions, and the decisions behind them, written for
people, tools and LLM agents alike.

Start at [docs/knowledge/](docs/knowledge/README.md). Agents start at [llms.txt](llms.txt).

## Part of a family

This is one of a family of knowledge bases that share one format (schemas, scripts, checks and
guardrails) but not their content. Each one is the source of truth for its own topic and links to
the others instead of copying them. The list is in
[docs/knowledge/family.yaml](docs/knowledge/family.yaml), and the format comes from the reference
implementation, [nickprignano/nerdio-hcl](https://github.com/nickprignano/nerdio-hcl).

## How it stays current

Nothing here spends LLM tokens to run. Plain Python 3.11+ (PyYAML, jsonschema) and GitHub Actions
with the built-in `GITHUB_TOKEN` do the work:

- **kb-validate** checks every change: front matter and YAML against JSON Schemas, decision
  records, links and anchors, leak patterns, generated files in sync, and unit tests. Gitleaks
  scans every PR for secrets.
- **kb-curator** opens a digest issue every Monday with what's new in the sources it watches.
- **kb-freshness** keeps one issue listing pages due for a re-check, once a month.
- **kb-feedback** turns accepted issue forms into pull requests.
- **kb-prior-art** searches this KB, its siblings and GitHub before anything new gets built.

See [curation.md](docs/knowledge/curation.md).

## Guardrails

This repo is public. Nothing in it identifies a real person's account, an employer, a customer or
a private project, and secrets never pass through it or through chat. Every change goes through a
reviewed pull request. The full rules are in [docs/guardrails.md](docs/guardrails.md).

## Start your own

The system this repo runs on is specified in [docs/2ndbrain/SPEC.md](docs/2ndbrain/SPEC.md), and
agents follow the [2ndbrain-kb skill](.claude/skills/2ndbrain-kb/SKILL.md). This repo is the working
prototype. Two template repositories carry it to anyone who wants one:

- [2ndbrain-public](https://github.com/nickprignano/2ndbrain-public): the machinery and an empty
  knowledge base, generated from this repo by `scripts/kb/export_template.py` following
  [template/manifest.toml](template/manifest.toml).
- [2ndbrain-private](https://github.com/nickprignano/2ndbrain-private): a private wisdom layer that
  sits above your public KBs. The maintainer keeps one too. Its contents stay private by design.

## Where the idea came from

The project second brain started as a work prototype for a complex enterprise migration
engagement. It used a Copilot Studio agent grounded in a human-curated SharePoint site, with
instructions for how to use those files to answer engagement questions and improve delivery
quality, and a Teams chatbot front end so everyone on the project could talk to it. It worked well.

Brian Madden (Citrix) was the first to put the name "second brain" on it, in one of his videos.
The same day, Meta's article on an organizational second brain showed where the idea could go.
This family of knowledge bases grew from those three pieces. Credit where it's due.

## License

Apache-2.0 ([LICENSE](LICENSE)). The KB scripts, schemas, workflows and issue forms are adapted
from nerdio-hcl under the same license; see [NOTICE](NOTICE).
