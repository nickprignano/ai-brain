---
name: 2ndbrain
description: Use in any chat or code session to capture lessons, root-cause analyses, procedures, decisions, goals or disagreements into a second brain, routing public-safe AI knowledge to the public hub KB and everything personal to the private layer, and to offer captures at the end of threads.
---

# 2ndbrain: capture

A second brain in two layers: a **public hub KB** (AI research, family KB format, changed by pull
request only) and a **private layer** (one person's notes vault). This skill captures what a thread
produced into the right one. v1 does capture only.

## Settings

Fill these in when you install the skill. The spec is `skills/2ndbrain/README.md` in the hub repo.

```yaml
hub_repo: <owner>/<public-kb-repo>     # public; changes by PR only
hub_kb_path: docs/knowledge
private_repo: <owner>/<private-repo>   # private; commit to its default branch
private_rules: notes/capture-rules.md  # the private layer's capture rules; they win over this file
private_layer: hidden                  # hidden | named (see "How openly the private layer is named")
```

## Triggers

| Capture | Trigger |
|---|---|
| Lesson | End of a thread that produced decisions, gotchas or facts worth keeping. Offer in one line; write on a yes or "lessons learned". |
| Root-cause analysis | Only when the user asked for help troubleshooting. |
| Procedure | Only when the user asked for steps they take part in. Include a "Who does what" table and a backout plan. |
| Decision | The user says "I don't know" or needs judgment on an open-ended question. Offer in one line at thread end. |
| Goal | Same trigger, when it is about a lasting aim. |
| Disagreement | Only when the user asks. Never offer or capture one on your own initiative. |

Also on an explicit ask: "2ndbrain", "capture this", "/2ndbrain". Make at most **one** offer line
per thread covering everything that applies, and skip it when nothing durable came out.

## Routing (every capture, before anything is written)

1. **Hard stop.** Secrets, keys, tokens and credentials go nowhere. Work material (employer,
   customer or tenant specifics, work repos) goes nowhere either; say in one line that it belongs
   in that work project's own KB, and stop.
2. **Classify.** AI tooling that is true for anyone (models and APIs, agents, MCP, skills,
   prompting, evals, AI platforms, learning resources)? Or about the user: their judgment, goals,
   life, their own "so what"?
3. **Route.**

   | What | Goes to |
   |---|---|
   | AI-technical fact, gotcha, fix or source | Hub: the topic page it belongs on, or the known-errors, field-reports or experts data file |
   | AI-technical decision | Hub: a decision record (MADR) |
   | Decision, goal, disagreement, root-cause analysis, procedure, anything personal | Private layer, always |
   | A thread that produced both | **Split.** The general part goes to the hub by PR. Only the personal takeaway goes to the private layer, as a lesson that links out to the hub page. |

   The flow is **2ndbrain → hub → private layer**. Never also copy a hub capture into the private
   layer: the private layer reads the hub on its own (for example a weekly roll-up). Only private
   material is written to the private layer directly, because it can't pass through a public repo.
4. **Public-safety gate** (hub side). Check the draft against the hub's `docs/guardrails.md`: no
   account, org or workspace IDs, domains, emails, IPs, private app names, prompts or user data,
   and no employer or customer names. Generalise it if you can ("in a personal app with per-user
   budgets") and show the result. If you can't, send it to the private layer instead and say so.
   Nothing that failed this gate goes public.
5. **Prior art** (hub side). Find the page that already covers the topic and add to it; start a
   new file only when none fits. Run the hub's prior-art check when it's available.

Links go one way: the private layer may link to hub pages; the hub never links into the private
layer.

## How openly the private layer is named

The private layer's contents stay private in both modes. `private_layer` only decides whether
public text may say it exists.

- `hidden`: hub text, PRs and commits never mention the private layer, its name or that a capture
  had a private half. Split captures are two independent notes.
- `named`: hub text may say the maintainer keeps a private layer that reads the hub and is never
  linked from it, and a PR may say "the personal takeaway was filed privately". Note names, paths,
  `[[links]]`, reasoning and contents are still refused. Switch to `named` only after the hub has a
  decision record allowing it, since a guardrail changes only by decision.

## Writing

**Hub** (with push access): branch, edit, run the hub's checks (`python3 scripts/kb/build.py`,
`python3 scripts/kb/validate.py`, `python3 -m unittest discover -s scripts/kb`), open a PR. It
lands when the owner merges.

**Private layer** (with push access): read `private_rules` and the target folder's `_template.md`,
write the note, add it to the index, run the stale check if the repo has one, commit to the
default branch.

**Without write access** (a plain chat): draft each note in full with its target repo and path (and
the index line for the private layer), and say plainly that it isn't filed yet.

Always end by saying where each piece went: path plus PR link or commit.

## Rules that always apply

1. Write from what actually happened, dead ends included. Never invent steps or results.
2. In decision notes, keep "Claude's view" (recommendation, why, confidence, what would change it)
   separate from the user's decision. Never rewrite your view to match the outcome.
3. Decided decisions get a revisit date and checkable assumptions. Goals carry status, rank,
   horizon and last-reviewed date.
4. Disagreements: the user's decision is final on their own calls. State your dissent once, fairly,
   then don't reargue it. This never stops you from raising a new, real risk.
5. No dollar figures and no employer or customer specifics in any note.
6. Fill every front-matter field, including the staleness fields for notes that state facts.
7. Before relying on an existing note, check whether it's past its review date and re-verify it.
