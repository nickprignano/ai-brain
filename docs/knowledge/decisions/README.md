# Decision records

Short records of choices that shape this knowledge base and the work it covers. One file per
decision, numbered in order, in [MADR 4](https://adr.github.io/madr/) format. Copy
[template.md](template.md) to add one. A decision stays `proposed` until the maintainer says yes.
A reversed decision gets a new record, and the old one is marked *Superseded by NNNN*. Each KB in
the family numbers its own decisions; refer to a sibling's as `<project> 0012`, with a link.

<!-- BEGIN GENERATED: decision-index (from front matter; run scripts/kb/build.py) -->
| # | Decision | Status |
|---|---|---|
| [0001](0001-adopt-family-kb-format.md) | Adopt the family knowledge base format, version 1 | Proposed |
| [0002](0002-public-kb-separate-from-personal-notes.md) | A public AI research KB, kept separate from personal notes | Proposed |
| [0003](0003-claude-api-as-model-provider.md) | The Claude API is the model provider, with a separate workspace per app | Proposed |
| [0004](0004-source-of-truth-for-claude-api-topics.md) | This KB is the family's source of truth for Claude API topics | Proposed |
| [0005](0005-family-format-review-windows-and-revisit-dates.md) | Family format: per-page review windows and revisit dates on decisions | Proposed |
| [0006](0006-model-selection-convention.md) | One convention for using Claude models, piloted on the family, with per-project overrides | Proposed |
| [0007](0007-family-format-ai-brain-as-format-source.md) | Family format: this KB is the source of truth for the format, and templates are generated from it | Accepted |
| [0008](0008-family-format-maintainer-directives-and-pause-switch.md) | Family format: maintainer directives and a pause switch | Accepted |
| [0009](0009-second-model-family.md) | Claude stays primary; Grok is the one second model family, for named jobs only | Proposed |
| [0010](0010-family-format-upstream-sources.md) | Family format: link to upstream sources of truth, check against them, and give back | Proposed |
| [0011](0011-family-format-enforced-kb-capture.md) | Family format: enforce knowledge capture with a Stop hook, a PR check and a thread closeout | Proposed |
<!-- END GENERATED: decision-index -->
