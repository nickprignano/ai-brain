# Adding a KB to this family

How a new project gets its knowledge base in this family, the same way every time. The generic
steps are in the [2ndbrain-kb skill](../../.claude/skills/2ndbrain-kb/SKILL.md#setting-up-a-new-kb).
This page adds what's particular to this family, with ai-brain as the hub, and a prompt to paste
into the new project's chat so its Claude does the work.

## Before you paste the prompt

1. The project's repo exists on GitHub (public, since family KBs are public). An existing repo is
   fine; the KB goes in at `docs/knowledge/`.
2. The project has both repos added: its own repo and `nickprignano/ai-brain`. The second is needed
   for step 5 of the prompt.
3. Its row in [family.yaml](../knowledge/family.yaml) says what the KB `focus`es on and `owns`. If
   it has no row yet, the prompt adds one.

## The prompt

Fill in the placeholders and paste it into the new project's chat.

| Placeholder | What goes in | Example |
|---|---|---|
| `{{NAME}}` | The project's display name | Example Tool |
| `{{ID}}` | Its family id, lowercase with hyphens | example-tool |
| `{{REPO}}` | Its repo, `owner/name` | nickprignano/example-tool |
| `{{ROLE}}` | Its family role, `member` unless it owns the format | member |
| `{{FOCUS}}` | One line on what the KB covers | Example Tool on virtual desktops |
| `{{TOPICS}}` | The first topics, as short folder names | install, profiles, troubleshooting |
| `{{SOURCES}}` | Public upstream sources to watch | the vendor's release notes and docs |

Names of employers and customers never go in a placeholder: the prompt's output is public.

```text
Set up a family knowledge base for {{NAME}} in {{REPO}}, the same way the other family KBs have
theirs. Follow the "Setting up a new KB" steps in the 2ndbrain-kb skill in nickprignano/ai-brain
(.claude/skills/2ndbrain-kb/SKILL.md) and docs/2ndbrain/new-family-kb.md there.

1. Install: export the machinery from ai-brain's main with
   `python3 scripts/kb/export_template.py <empty folder>`, run `python3 scripts/setup.py --public`
   in that folder to drop the private layer, and copy it into {{REPO}} except the
   template's README.md, NOTICE and template-sync workflow. Keep the existing README and add a short
   knowledge base section. Write a NOTICE crediting ai-brain and nerdio-hcl under Apache-2.0.
2. Make it ours: in docs/knowledge/kb.toml set name "{{ID}}", the title, tagline and user_agent,
   and topic_order. Add these topics to schema/page.schema.json: {{TOPICS}}. Replace
   getting-started/ with the first real topic page. In sources.toml, watch {{SOURCES}}, and keep the
   2ndbrain source.
3. Join the family: copy ai-brain's docs/knowledge/family.yaml, mark {{ID}} as self, and set its
   repo {{REPO}}, kb_path docs/knowledge, role {{ROLE}} and ai-brain's format_version. Add the two
   github_commits sources (decisions folder and KB folder) for every sibling that has a repo.
4. Family conventions: run `python3 scripts/kb/directives.py list` and follow what applies. Add a
   decision that points to ai-brain decision 0006, the model-selection convention, the way
   nerdio-hcl 0022 does. Pin `model` and `effortLevel` in .claude/settings.json to the thread
   default it names.
5. Hub side: open a PR on nickprignano/ai-brain that fills in the {{ID}} row of its family.yaml
   (repo, kb_path, format_version) and adds {{REPO}}'s two sources to its sources.toml.
6. Run build.py, validate.py and the unit tests until they're clean. Open everything as pull
   requests for me to merge.

Follow docs/guardrails.md: no employer, customer or private-project names, no account or tenant
IDs, domains, IPs or emails, and no secrets. Vendor documentation is linked, not copied.
When you're done, tell me the steps only I can do.
```

## After the PRs merge

These are the maintainer's, because they change repo or project settings:

- In the new repo, **Settings > Actions > General**: turn on **Allow GitHub Actions to create and
  approve pull requests**. Then run **Actions > kb-freshness** once, so the `kb-*` and `handoff` labels exist.
- In the new project's instructions, add the model line from
  [decision 0006](../knowledge/decisions/0006-model-selection-convention.md).
- Other siblings add the new KB's two sources the next time they update their `family.yaml`; their
  freshness check reminds them.

## Why the hub's export, not the template repo

The template repo, [2ndbrain](https://github.com/nickprignano/2ndbrain), is the same
export but only as new as its last merged `template-sync` pull request. Exporting from ai-brain's
main gets the current machinery, including anything the template hasn't pulled yet. Once the
template is in step, copying from it gives the same files.
