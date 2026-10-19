---
title: "Prompt: Red team a design or decision"
summary: "Has a second model attack a design, spec or decision record, returning numbered findings with severity, a fix and what's acceptable as is"
topic: prompting
status: verified
last_reviewed: 2026-10-19
---

# Prompt: Red team a design or decision

**Use when** a thread has produced a design, a spec or a decision record, before it's presented as
final or anything is built from it.

**Paste into** the thread that wrote the design. That thread hands the attack to a sub-agent
running the second model and keeps the fixing for itself, so the red team never grades its own
findings.

**Run so far:** yes, on several designs and decisions in this family (2026-10-19).

## Placeholders

| Placeholder | What goes in | Example |
|---|---|---|
| `{{DOC}}` | The design to attack, as a path or link | docs/spec.md, sections 4 to 6 |
| `{{MODEL}}` | The model that does the red team, not the one that wrote it | a model other than the author's, as your model convention picks |
| `{{SCOPE}}` | What to attack hardest | security, privacy, cost and whether the thresholds can fire |
| `{{CONTEXT}}` | Facts the attacker needs: volumes, who uses it, what's out of scope | one operator; 10 to 50 eval questions a run |
| `{{PREFIX}}` | A short ID prefix for findings | RT |
| `{{OUT}}` | Where the findings file goes | docs/red-team.md |

## The prompt

```text
Red team {{DOC}} with {{MODEL}}, a different model from the one that wrote it. Give the
sub-agent running {{MODEL}} only the next three paragraphs, and keep the last one for yourself.

Attack {{SCOPE}} hardest. Context: {{CONTEXT}}. Don't edit the design. Assume the design is wrong somewhere and find where. For each finding:
- an ID ({{PREFIX}}-1, {{PREFIX}}-2, ...), a one-line title and a severity (High, Medium, Low);
- the verdict in one or two sentences;
- what goes wrong, with a concrete case: inputs, numbers, an attacker's steps or a failure path
  through the design;
- the changes, as numbered edits naming the file and section;
- what is acceptable as is, so nobody "fixes" it later.

Check numbers with arithmetic, not intuition: thresholds, rates, costs, sample sizes. Say when a
claim in the design has no source. Don't pad: three real findings beat ten weak ones.

Return the findings with a summary table first (ID, title, severity).

Then write the findings to {{OUT}} with a status column, fix what's in scope in the design itself, mark each finding Fixed, Accepted (with the reason) or Open,
and tell me what the red team found and what changed.
```

## Notes

- **Use a different model from the author.** The same model tends to approve its own reasoning;
  a second model finds the overstated claims and the arithmetic that doesn't hold.
- **Give it the numbers.** Findings about thresholds and false alarms were only possible because
  the prompt said how many runs and samples there are.
- **Name the questions the first pass couldn't settle,** and point the attacker at the code and
  schemas the design leans on, not only the design. On a swarm spec (2026-10-19), the two
  strongest findings came from reading the directive schema and the handoff script, which the
  design only described.
- **"Acceptable as is" matters.** It records what was checked and passed, which stops the next
  reviewer from reopening it.
- When the fixes belong to another project, follow with
  [Apply red-team findings in another project](apply-red-team-fixes.md).
