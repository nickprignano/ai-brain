---
status: proposed
date: 2026-10-21
decision-makers: [maintainer]
---

# 0018. Family format: a stronger leak check and reviewed model-drafted entries

## Context and Problem Statement

The family's `validate.py` catches email addresses and public IPv4 addresses. The AVD KB's guard
also catches GUIDs that aren't placeholders, UNC paths, default Windows machine names and names on
a hashed customer denylist, and runs over its `docs/knowledge/` through `scripts/Test-KbLeaks.ps1`.
Every KB in the family writes up real runs, so a tenant ID or a storage account name can slip into
any of them, and a check only one KB runs protects only that one. Separately, nothing in the format
marks an entry a model drafted, so it can't be told apart from one a person checked. Should the
shared format carry both checks?

## Considered Options

- Keep format v1 as it is; the AVD KB keeps its extra check on its own
- Propose both for format v2, in all four KBs

## Decision Outcome

Chosen option: "Propose both for format v2", because every KB in the family writes up real runs.

- **Stronger leak check in `validate.py`:** GUIDs other than an allowlist of placeholders (the
  all-zero GUID and documented examples), UNC paths, default Windows machine names, and an
  optional `denylist.sha256` of lowercase customer names for private forks.
- **Reviewed model-drafted entries:** a YAML entry or page with `source: llm` needs `reviewed_by`
  and `reviewed_on` before it validates.
- Ships as `format_version: 2` once all four KBs agree. Until then each stays on 1, and the AVD KB
  keeps `Test-KbLeaks.ps1`.

### Consequences

- Good, because all four KBs get the same protection.
- Bad, because the GUID check needs tuning: public IDs (well-known Microsoft role or app IDs)
  need the allowlist.
- Neutral, because it is a proposal: no shared code changes until all four KBs accept it.

## More Information

Also recorded in [AVD 0009](https://github.com/nickprignano/avd-second-brain/blob/main/docs/knowledge/decisions/0009-family-format-stronger-leak-check.md),
accepted there by the owner on 2026-10-21. Written here first because this KB owns the format
([0007](0007-family-format-ai-brain-as-format-source.md)); nerdio-hcl and the Liquidware KB adopt
it by PR once it is accepted here.
