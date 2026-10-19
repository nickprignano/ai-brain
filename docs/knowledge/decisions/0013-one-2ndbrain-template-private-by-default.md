---
status: accepted
date: 2026-10-19
decision-makers: [maintainer]
---

# 0013. One 2ndbrain template, set up as public or private, private by default

## Context and Problem Statement

The format shipped as two template repos: 2ndbrain-public (the KB machinery, exported from this
repo weekly) and 2ndbrain-private (an empty private wisdom layer, written by hand). Their shared
scripts were kept in step by hand, there were two things to keep current, and someone adopting the
kit had to work out which one they needed. Should there be one template, and if so, how does it
stay safe for private notes?

## Considered Options

- One template repo with public or private chosen at setup, private by default
- Keep two template repos
- One template with a config switch (for example `visibility = "private"` in a settings file)

## Decision Outcome

Chosen option: "One template, chosen at setup, private by default". 2ndbrain-public was renamed to
[2ndbrain](https://github.com/nickprignano/2ndbrain) and the private layer moved into this repo's
`template/skeleton/`, so this repo's export is still the one sync. A config switch was rejected:
the repo's real visibility is the only thing worth checking, and a setting can only disagree with
it.

- `scripts/setup.py` (default private) refuses unless an unauthenticated GitHub request for the
  repo gets a 404, and installs a pre-commit hook running `privacy_check.py`. `--public` deletes
  the layer, and refuses if it already holds a real note.
- A `privacy` workflow, kept in both modes, fails any public repo that has the layer. The template
  repo itself passes only while the layer is empty, and the export refuses to ship anything in it
  but its templates.
- `template-sync` runs only in the template repo; setup removes it from copies, since its clean
  export would otherwise propose deleting a copy's own notes.
- The private layer's scripts keep their paths and bytes, so a private layer that diffs its
  scripts against the template only needs to point at the new repo.

### Consequences

- Good, because there's one template, one export and one sync to keep healthy.
- Good, because the strict default fails loudly: a public copy that skips setup goes red at once.
- Bad, because detection in CI happens after a push. The pre-commit hook and setup's check are the
  guards before it, and both need the copy to be set up.
- Neutral, because 2ndbrain-private is no longer a template; its owner reuses the repo for other work.

## More Information

Red-teamed with Fable before building. It found the setup check failing open on a 403, the
template-sync workflow reaching copies, `kb-capture` treating notes as code, and that naming the
owner's real private layer in a forbid list would itself leak it; all four were fixed. See
[the spec](../../2ndbrain/SPEC.md#9-templates).
