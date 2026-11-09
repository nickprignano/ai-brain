---
title: "Evals and testing"
summary: "Testing features built on LLMs: unit tests for guardrails, LLM-as-judge and regression checks"
topic: evals
status: plan
last_reviewed: 2026-11-09
---

# Evals and testing

How to test features built on a model: deterministic tests for the guardrails around it, LLM-as-judge, and regression checks when a model changes. Only the first notes are written so far.

## Checking teaching content an agent writes

From a design-stage red team of a game theory course for teenagers (2026-11-08), whose lessons
and exercises Claude will write. Nothing is built yet, so these are design rules, not results.

- **Test a lesson's claim over many runs, not the run that inspired it.** The draft checked a
  strategy tournament's winner "over the seeds the lessons use", which only confirms the cherry-pick:
  who wins a repeated prisoner's dilemma depends on the field and the number of rounds. The fix
  keeps each claim in one data file that the lesson text and the test both read, and the test
  asserts it holds in at least 95% of 1,000 seeded runs. Lesson text says "in this field".
- **Generate what a solver can grade; hand-write only what it can't.** About 300 hand-written
  exercises can't be reviewed well. About 60 hand-written payoff tables and 40 stories, with
  the rest generated from a table and a seed and graded by a small solver, cut the hand-written
  volume by more than half and leave the human review on the part no test can read (does this
  story match this table?).
- **Make labels a test can compute disjoint.** "Coordination game" and "stag hunt" overlap, so a
  classifier can't grade one against the other. Defining each label by a strict payoff order
  (prisoner's dilemma T > R > P > S, stag hunt R > T > P > S, chicken T > R > S > P) makes them
  computable and exclusive.
- **Check what a short game will show the player.** "You can't beat a random mix" is false over
  10 rounds of rock-paper-scissors, so a lucky player would see the lesson contradicted. The
  result screen shows a 1,000-round simulation next to the player's rounds.

The red team was a Fable worker; see [When to reach for Fable](../agents/README.md#when-to-reach-for-fable).

