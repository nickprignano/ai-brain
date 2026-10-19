---
status: accepted
date: 2026-10-18
decision-makers: [maintainer]
---

# 0008. Family format: maintainer directives and a pause switch

## Context and Problem Statement

The maintainer sometimes needs to tell every KB in the family the same thing at once: pause the
weekly automation, stop using a source, apply a break-fix. Today that means four separate edits,
and nothing tells agents working in a sibling repo that an instruction exists. A directive may come
from private context the maintainer doesn't publish. How can the family receive one instruction,
from one place, with the maintainer's approval, without spreading credentials between repos?

## Considered Options

- One owner-only `directives.yaml` here, which every sibling reads before its automated runs, plus a
  `KB_PAUSED` repository variable in each repo as the local emergency stop
- A directive issue in each repo, posted by hand
- A workflow here that writes issues or variables into each sibling

## Decision Outcome

Chosen option: "One owner-only `directives.yaml` here", because siblings can read a public file with
no credential, one merge reaches the whole family, and nothing here needs write access to another
repo.

- **The file.** `docs/knowledge/directives.yaml`, checked against `schema/directive.schema.json`.
  Each entry has an `id`, the `directive` (at most 280 characters), a `scope` (`all` or family
  ids), an optional `pause` list of `kb-*` workflow names, an optional `until` date and an `opened`
  date. There's no field for reasons: a directive carries only the instruction.
- **Owner-only.** CODEOWNERS covers the file, and `kb-validate` fails a pull request that changes it unless the
  repo owner opened it. At most five directives may be active at once.
- **Fan-out.** Every automated `kb-*` workflow (curator, freshness, feedback, prior-art) in every KB
  starts by reading this file from the public repo, and skips when a pause covers it.
  `kb-validate` and the secret scan always run. A daily `kb-directives` workflow in each sibling
  opens a local pointer issue (label `kb-directive`) for each new directive in its scope, using its
  own token, and closes it once the directive is removed or expires.
- **Agents.** One line in each repo's `AGENTS.md`: read the open directives that apply to this KB
  before starting work. They never override the guardrails or the user's own word.
- **Emergency stop.** A `KB_PAUSED` repository variable in each repo pauses that repo's automated
  `kb-*` workflows at once, even when this repo can't be read.
- **Expiry.** The freshness check flags a directive past its `until` date for removal.

### Consequences

- Good, because one merge pauses or instructs the whole family, and the merge is the approval.
- Good, because no repo holds a credential for another.
- Bad, because a pause takes effect at each sibling's next run, not instantly. `KB_PAUSED` covers
  the urgent case.
- Bad, because it's a shared format change: every KB adds the read step, the pointer workflow and
  the `AGENTS.md` line.

## More Information

Ships in the same `format_version` bump as [0005](0005-family-format-review-windows-and-revisit-dates.md)
and [0007](0007-family-format-ai-brain-as-format-source.md), so the family changes version once.
Accepted by the maintainer on 2026-10-18. Built here in `scripts/kb/directives.py`, the gate job in
each automated `kb-*` workflow, and `kb-directives.yml`.
