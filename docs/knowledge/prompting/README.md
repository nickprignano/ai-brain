---
title: "Prompting"
summary: "System prompts, audience-specific prompts and structured output that held up in real apps"
topic: prompting
status: verified
last_reviewed: 2026-10-29
---

# Prompting

Prompts that held up in real use: system prompts, prompts tuned for an audience (for example by age), and structured output. Write the lesson, not the private prompt.

Reusable prompts for the family's own work (handoffs, red teams, research, closeouts) are in the
[prompt library](library/README.md), one generalized prompt per page.

## Rewriting text into a person's own voice

Lessons from building a personal skill that makes Claude's drafts sound like one specific writer
(and, in reverse, makes text not sound like them). Built 2026-10-18; each point below checked
against the shipped skill's instructions on 2026-10-29.

- **Strip the model's tells first.** Most of the gap between "sounds like Claude" and "sounds like
  a person" is removing habits, not adding them: stock openers and closers, inflated vocabulary,
  em-dash asides, "not X but Y" contrasts, rhythmic triplets, bullets and headers for what a person
  would say in a sentence, and a closing offer of more help. Keep these as an explicit avoid list.
- **Model a voice per register.** The same person writes chat, work email and public posts
  differently. Tag every trait with its register, and when one has no samples, fall back to the
  nearest one without its strongest tics (all-lowercase chat style in a work email reads as a
  caricature).
- **Weight samples by provenance.** Text the person wrote with AI help contaminates the profile
  with the model's own style. Writing done fully by the person counts in full. An AI draft paired
  with the person's final version is the best input: learn only from what they changed, and add
  what they cut to the avoid list. AI-assisted text with no draft to compare counts for little,
  never becomes a target trait on its own, and anything in it that matches the model's tells is
  dropped.
- **Dose the tics.** One or two signature habits per paragraph reads as the person; every habit
  in every sentence reads as parody.
