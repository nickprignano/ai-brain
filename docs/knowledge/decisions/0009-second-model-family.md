---
status: proposed
date: 2026-10-19
decision-makers: [maintainer]
---

# 0009. Claude stays primary; Grok is the one second model family, for named jobs only

## Context and Problem Statement

[Decision 0003](0003-claude-api-as-model-provider.md) made the Claude API the model provider and
turned down "several providers behind an abstraction layer". Since then the apps have hit things
Claude doesn't do (it reads images but makes no images, video or speech, and has no embedding
model), and a few designs want a judge or safety check whose blind spots differ from Claude's
(avd-swarm's shadow judge, spec §6b). The maintainer wants at most two AI vendors to pay. Which
second family do the apps use, for what, and with which data?

## Considered Options

- Claude primary, plus xAI Grok for media and as the second family, reached through the app's
  own platform where it can be
- Claude primary, plus OpenAI (direct or on Azure) for media and as the second family
- Claude primary, plus Google Gemini, the only family that covers every media gap including video
- Claude only, leaving the gaps unfilled

## Decision Outcome

Chosen option: "Claude primary, plus xAI Grok", because the maintainer already uses Grok, xAI's
API covers images, video and speech in one account, and Grok's text models are sold by Azure, so
apps on Azure reach them keylessly on a bill they already have. OpenAI no longer has a video API
(retired 2026-09-24), and Google's Gemini API terms bar apps likely to be used by under-18s.

The rules:

1. **Claude is the primary model.** The second family gets four jobs only: filling a capability
   gap (images, video, speech), an independent safety classifier, a judge or cross-check that
   never acts on its own, and an outage fallback. Any other use is a per-app override decision.
2. **Two AI bills: Anthropic and xAI.** Platform accounts an app already runs on (Azure,
   Cloudflare) aren't new vendors, so a model they sell is allowed:
   - Apps on Azure use Grok text models on Foundry with Entra ID and no stored key, as
     [0006](0006-model-selection-convention.md) requires. If they ever need images, Azure
     OpenAI's image model, not xAI's own API, because that would need a stored key.
   - Apps on Cloudflare can use Workers AI (Llama Guard, open image and speech models), which
     doesn't train on or keep request data.
   - Everything else reaches xAI's own API with a key in the platform's secret store, in its own
     xAI team with a monthly spend limit, as 0003 does for Claude.
3. **Data classes are enforced in code.** Each app lists its data classes and which provider may
   see each, with tests that refuse every forbidden pair. Personal data of children goes only to
   Claude and to in-platform services that keep nothing, never to xAI.
4. **No Grok media in anything children use.** In 2026 Grok's image generator made sexualized
   images including minors, which drew a California Attorney General cease-and-desist and EU and
   UK investigations. An app with child profiles makes their images and speech in-platform, and
   checks every generated image with Claude before showing it.
5. **One thin layer per app, no framework.** One call shape that returns text, usage, a normalised
   stop reason, provider and model, with an adapter per provider. Apps read
   `<APP>_SECOND_PROVIDER` and `<APP>_SECOND_MODEL` next to 0006's variables. Usage from every
   provider goes through the app's own budget.
6. **A second family earns each job on evals.** It is switched on for a job only after passing the
   app's eval set (for a safety-tiered app, the tier's safety set). A judge is promoted only by a
   paired comparison, never by counting its wins, as in avd-swarm §6b.
7. **Every provider sits behind the kill switch and an in-process spend cap.**

The provider facts this rests on (terms, retention, prices, which models each platform sells) are
on the [Claude API page](../claude-api/README.md#other-model-families), checked on 2026-10-19.

### Consequences

- Good, because the media gaps are filled with one extra vendor, and apps on Azure need nothing
  new.
- Good, because the judge and safety designs get a second family with different blind spots.
- Bad, because xAI's API keeps requests 30 days by default and needs a stored key outside Azure.
- Bad, because Grok's safety record rules it out for children, so apps with children need a
  second, in-platform path for media.
- Neutral, because video understanding and embeddings stay unfilled by xAI: send frames to Claude
  as images, and use the platform's embedding models.

## More Information

Amends 0003 (a second provider is now allowed, for these jobs only) and extends 0006 layer 3.
Revisit by 2027-04-19, or sooner if xAI's terms or safety record change, if Grok's media models
appear on Azure, or if OpenAI or Google change the facts that ruled them out.
