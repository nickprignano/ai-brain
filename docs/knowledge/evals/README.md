---
title: "Evals and testing"
summary: "Testing features built on LLMs: unit tests for guardrails, LLM-as-judge and regression checks"
topic: evals
status: plan
last_reviewed: 2026-11-11
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

## Checking teaching content when no solver can grade it

From the spec of a learn-anything course app for teenagers (`nickprignano/tangent`, 2026-11-10),
where one model writes each lesson on any topic and a second model checks it. The spec went through
a Fable red team and an outside review by Gemini. Nothing is built yet, so these are design rules,
not results.

- **Make the checker blind, then check the prose separately.** The checker answers each question
  with the answer, explanation and lesson text removed and the options shuffled; a question stays
  only if its pick matches the writer's key with no flag. Showing it the lesson text lets a false
  sentence steer it into agreeing. A second call, with answers shown, reads the lesson text and the
  explanations, which the blind pass never sees and which do most of the teaching.
- **Ask for the checker's own short answer before it picks an option.** Four options cue a shared
  guess, so an answer written first is a more independent check.
- **Budget for correlated errors.** Two models from one vendor share training data and a cutoff,
  so both can be wrong the same way (records, rule changes, popular myths). Useful flags: "may have
  changed since training", "answer given away by the wording", "opinion not fact". True or false is
  capped at 2 a lesson, because two independent guessers agree on a coin flip half the time.
- **Contextual and blind questions conflict.** A question that only makes sense after the lesson
  text ("as above", pronouns, fill-the-gap from the passage) fails a blind check and burns a
  rewrite. Write questions that stand alone but test the lesson's ideas.
- **State the error bar honestly, per course.** A 2% error rate per question still means about half
  of 35-question courses teach at least one wrong answer, so the app says "it can still be wrong"
  and has a report button. A human spot check of 40 items alone only bounds the rate near 7%, and an
  LLM checking the rest shares the checker's blind spots, so a miss in the human sample fails the
  run.
- **Let the quality run pick the models.** Run the cheapest writer and checker pair first (here
  Haiku 5.5 writing, Sonnet 5.5 checking, about $0.035 a lesson at list price) and move up only if
  it fails the bar.

For the free-text topic box this app needs, see
[When one free-text box can't be avoided](../privacy-and-safety/README.md#when-one-free-text-box-cant-be-avoided).

