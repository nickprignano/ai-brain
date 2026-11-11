---
title: "Privacy and safety"
summary: "Keys and secrets, prompt injection, local-only designs, building AI features for kids, teen games (gambling, brain-training claims), and AI safety tools"
topic: privacy-and-safety
status: verified
last_reviewed: 2026-11-11
sources:
  - https://github.com/microsoft/PyRIT
  - https://github.com/promptfoo/promptfoo
  - https://www.promptfoo.dev/docs/red-team/architecture/
  - https://github.com/NVIDIA/garak
  - https://github.com/meta-llama/PurpleLlama
  - https://developers.cloudflare.com/workers-ai/models/
  - https://arxiv.org/pdf/2607.00395
  - https://developers.cloudflare.com/workers/ci-cd/builds/build-branches/
  - https://developers.cloudflare.com/workers/previews/configuration/
  - https://developers.cloudflare.com/workers/ci-cd/builds/configuration/
  - https://developers.cloudflare.com/changelog/post/2026-08-22-wrangler-mcp-optional-oauth-scopes/
  - https://codeql.github.com/codeql-query-help/javascript/js-clear-text-logging
  - https://support.claude.com/en/articles/15591275-child-safety-guidance-for-developers
  - https://github.com/roostorg/awesome-safety-tools
  - https://learn.microsoft.com/en-us/azure/sentinel/datalake/sentinel-mcp-create-custom-tool
  - https://github.com/beelzebub-labs/beelzebub
  - https://docs.canarytokens.org/guide/entraid-token
  - https://archive.aicyberchallenge.com/
  - https://www.askaboutgames.com/news/pegi-rating-for-gambling-is-now-always-18
  - https://www.classification.gov.au/classification-ratings/new-classifications-for-gambling-content-video-games
  - https://link.springer.com/content/pdf/10.3758/s13423-024-02466-8.pdf
  - https://www.eurekalert.org/news-releases/1115744
  - https://ftc.gov/news-events/press-releases/2016/01/lumosity-pay-2-million-settle-ftc-deceptive-advertising-charges
---

# Privacy and safety

Keeping AI features safe and private: handling keys, prompt injection from untrusted text, local-only
designs where data never leaves the device, and extra care for apps children use. Keys, making a repo
public and the security tools survey are written so far.

## Keys and secrets

The rule is [decision 0016](../decisions/0016-secrets-handling.md): one password manager holds the
master copy, and each key is pasted by the owner into the secret store of the one service that uses
it. What that means in practice:

- **Claude needs names, not values.** A session can write the code, the config and the deploy step
  that reads `<PROVIDER>_API_KEY`; only the paste is the owner's. That's why a vault that connects to
  Claude adds risk without saving work.
- **Prefer no key at all.** Managed identity, workload identity federation and OIDC from CI remove
  the key instead of storing it.
- **A cloud session's environment is not a secret store.** Anything set there is readable by every
  command the session runs, including ones a prompt injection talks it into.
- **Scope and cap at the provider.** One key per app and environment, narrowest permissions, and a
  provider-side spend limit, so a leak costs a known, small amount.
- **The deployment note is the rotation checklist.** Writing where a key is deployed on its vault
  entry is what makes "revoke and replace" a five-minute job instead of a search.
- **Deploy tokens and connectors are keys too.** A CI token that deploys a Worker, or a connector
  that reads a KV store, can reach more than a model key. Prefer OIDC from CI, and never park a key
  where a connector can read it back into a session.
- **A session that can deploy can leak a key without seeing it** (a handler that returns it, a
  log line, a `fetch` elsewhere). Both reviewers in the first outside review found this and the
  Fable pass didn't, so production deploys only from CI on `main`, and a session's own platform
  token reaches previews only ([decision 0016](../decisions/0016-secrets-handling.md), step 6).
- **The secrets-touch comment says which lines to read** (step 6, added 2026-10-20). The
  `secrets-touch` workflow runs `scripts/kb/secrets_touch.py` from the base branch on every PR and
  posts one comment listing changed files that read a secret-named binding, and added lines that
  use the whole environment, log or return something secret-named, name a host outside the repo's
  `egress_allow`, or call an address built at runtime. Running from the base branch means a PR
  can't quiet the check reading it; it never fails a PR, because a regex can't prove code safe and
  a red check people learn to ignore is worse than a comment. It misses a key passed through a
  variable with an innocent name, which is where data-flow tools such as GitHub CodeQL's
  clear-text-logging queries do better, so turn CodeQL on as well (free on public repos only, so
  a private app repo has just the comment). The comment is posted on every PR, even when nothing
  is flagged and with the commit it checked, so a missing or stale one means the check didn't run.
  Changes to dependencies, Worker config and the repo's own settings are always listed, since new
  code or a new binding can move a key without a suspicious line in the diff.
- **A connector that can call a platform's whole API can deploy.** Cloudflare's full-API connector
  signs in as the user, so a session with it can upload a Worker that returns a secret. Keep its
  scopes to the minimum in coding projects (its consent page lets you edit them), and leave out
  the read scopes for logs, KV, D1 and R2 too, since a leaked key lands there and a session that
  reads them brings it back. Let the platform's own build from `main` deploy, so sessions need no
  deploy token.
- **Leave branch builds off on a Worker that holds real keys.** A Workers Builds build runs the
  branch's own build scripts with the build token, which by default is a user token that can edit
  every Worker, KV namespace, R2 bucket and route on the account, so any pushed branch could
  deploy to production or copy the token. Workers connected before Worker Previews (September
  2026) also build branches with production secrets until a one-time, irreversible switch. Test
  with `wrangler dev` and dev keys; if branch previews are worth it, build them in a second
  account that holds only dev keys.
- **Rotate without an outage.** Create and deploy the new key, check it, then revoke the old one;
  revoke first only when usage shows abuse.
- **Push protection catches it early, gitleaks late.** GitHub's push protection blocks known key
  types before they're public; a gitleaks hit after a push means the key is in history, so rotate it.

## Before making a repo public

Checks before flipping a private repo to public (2026-10-18):

- **Scan the full history and PR text,** not just the current tree. Old commits and PR
  descriptions keep hostnames, IDs and names that were removed later. If they're there, either
  rewrite history before publishing or treat every value as public and rotate what needs it.
- **Check every branch, not just the default one.** Scrubbing `main` or squashing a fresh history
  leaves the old branches public. A branch with no merge base with `main` is usually the
  pre-publication history and still carries what was scrubbed. List them with
  `git branch -r` and `git merge-base origin/main <branch>`, then delete or scrub each one before
  the flip (2026-10-20, found two days after a repo went public).
- **Add a LICENSE.** With none, the repo is all rights reserved and nobody can reuse it.
- **Safety filters teach what they block.** Publishing the patterns an app flags shows users,
  kids included, how to word around them. Keep those lists out of the public repo.
- **Public Actions logs are public too,** so check what workflows print (see the red-team patterns
  on the [agents page](../agents/README.md#swarms-and-multi-agent-patterns)).

## Open-source AI tools for fighting bad actors

A survey of what exists on GitHub and the wider web, checked on 2026-10-19. Star counts and dates
came from repo pages, because the GitHub API was blocked in that session. Years that the page left
out are inferred and marked *(inf.)*. Nothing was installed or run, so maturity is judged from
activity and adoption, not tested.

### Start by attacking your own AI app

For a small app with an LLM in it, the most useful "AI against bad actors" is an automated attacker
pointed at your own app before a real one shows up.

- **[PyRIT](https://github.com/microsoft/PyRIT)** (Microsoft AI Red Team, MIT, v1.1.0 Sep 2026
  *(inf.)*). It has orchestrators built for multi-turn attacks, such as a long grooming-style
  conversation. The old `Azure/PyRIT` repo was archived on 2026-03-27; use `microsoft/PyRIT`.
- **[promptfoo](https://github.com/promptfoo/promptfoo)** (MIT, ~24k stars). The easiest red-team to
  run on every PR. It has been part of OpenAI since 2026-03-09 and is still MIT. Its red-team
  client asks promptfoo's cloud service for each attack and builds follow-up probes from the
  target's earlier replies ([architecture](https://www.promptfoo.dev/docs/red-team/architecture/),
  checked 2026-10-29; the page doesn't say whether those replies leave your environment), so run it
  against a test deployment with synthetic users, or configure local attack and judge models.
- **[garak](https://github.com/NVIDIA/garak)** (NVIDIA, Apache-2.0) is a broad vulnerability scanner
  that gives a quick baseline. **[PurpleLlama](https://github.com/meta-llama/PurpleLlama)** (Meta)
  holds CyberSecEval, LlamaFirewall, Prompt Guard 2 and Llama Guard.
- Dead: `protectai/llm-guard` was archived on 2026-07-09 with no successor named.

### Safety classifiers for apps children use

- **Llama Guard 3 8B is the only safety model in the Cloudflare Workers AI catalog** (no Llama Guard
  4, Prompt Guard, ShieldGemma or gpt-oss-safeguard; [catalog](https://developers.cloudflare.com/workers-ai/models/)
  re-checked 2026-10-29). That makes it the default
  gate when kids' data must stay inside one provider. Its limits: it judges one message at a time,
  covers 8 languages, and one incident-based child-safety evaluation measured roughly 48-51% recall
  for Llama Guard models on unsafe education prompts ([arXiv 2607.00395](https://arxiv.org/pdf/2607.00395)).
  Use it as a gate. Multi-turn and grooming patterns have to be caught by the main model plus a
  red-team eval set.
- **gpt-oss-safeguard** (OpenAI, Apache-2.0, Oct 2025) classifies against a policy you write in plain
  words, which suits per-age rules, but you have to host it yourself or use a third party.
  **Hive's CSE text classifier** carries Thorn's grooming label (English and Spanish), but it is a
  third-party API. Both are worth tracking for when their hosting fits your data rules.
- Anthropic's [child-safety guidance for developers](https://support.claude.com/en/articles/15591275-child-safety-guidance-for-developers)
  names Thorn Safer and the IWF, and covers NCMEC reporting for US platforms. Read it before shipping
  anything children use.
- [ROOST](https://github.com/roostorg) (an open online-safety group) open-sourced Osprey, Discord's
  safety rules engine, and Coop, a moderation queue. They are built for large platforms.
  [awesome-safety-tools](https://github.com/roostorg/awesome-safety-tools) is the best map of the
  space. Other mature pieces: Meta's ThreatExchange (PDQ hashing, Hasher-Matcher-Actioner), Thorn's
  `perception` (hash matching; it needs NCMEC or Thorn hash lists), detoxify (toxicity) and nsfwjs
  (image classifier in JavaScript).

### Structured-only input for an AI feature kids use

The simplest guard against prompt injection in a kids' app is to give the user no text that
reaches the model. The chess coach spec (`nickprignano/chess`) does it this way:

- There is no chat box. The browser sends a move list, a level from three values, and a "style
  card" with a fixed schema (opening codes, percentages and set values, no free text).
- The server replays every move and every engine line with a rules library, and checks that
  scores are in range, before anything reaches Claude. PGN headers and comments are never
  accepted, because they are free text.
- The output goes through a JSON schema with a length cap, is rendered as plain text, and is
  labelled as written by AI.
- Sign-in sits behind a closed allowlist (Cloudflare Access with an email-code fallback for a
  child whose Google account can't sign in to other sites). A hashed account ID is still a
  persistent identifier, so it counts as personal data and must be deletable.

### When one free-text box can't be avoided

A learn-anything app (`nickprignano/tangent` spec, 2026-11-10) needs a topic box, so structured-only
input isn't possible. What the red team and outside review settled on for teenagers:

- **Screen before any model call.** The server refuses text that looks like an email, a phone
  number, "my name is" or an age, and checks a short list of self-harm phrases so those get a
  support line without being sent anywhere. A model-side refusal can't show that line, because a
  safety classifier may stop the call before the app's own refusal code comes back.
- **Show the support line on an unexplained refusal too**, so a self-harm topic the list missed
  still gets it.
- **Sign the state the server hands out.** If the server keeps nothing, the browser must send the
  checked topic back, so the server signs it (with its verdict, the outline and an expiry) and
  refuses anything unsigned. Otherwise a user can skip the topic check.
- **Wrap model-written strings as data** in later prompts, and strip `<`, `>` and control
  characters before signing them.
- **Retention isn't one number.** Anthropic keeps API inputs and outputs about 30 days, but data its
  safety classifiers flag can be kept up to 2 years
  ([Anthropic privacy center](https://privacy.claude.com/en/articles/7996866-how-long-do-you-store-my-organization-s-data),
  checked 2026-11-11). A privacy page should say both.
- **Reports can identify a teen in a small group.** In an invite-only app, a report on a puberty or
  mental-health question plus the sign-in log could point to one person, so reports on sensitive
  topics carry only the reason.

### Games with simulated gambling for teenagers

Learned specifying a play-money poker app for 13 and up with a Claude coach (`nickprignano/cards`,
2026-11-10; spec only, red-teamed by Fable and reviewed by Gemini):

- **Gambling needs a stake, chance and a prize.** Keep the stake and the prize out entirely: no
  chips to buy, win, keep, transfer or cash out, every match starting even, and no daily bonuses,
  wheels, streaks or "near miss" effects. That is what separates a card game from a social casino.
- **Formal raters are stricter than US norms.** PEGI rates realistic simulated gambling 18 (its
  2025 revision after the Balatro appeal relaxed only fantastical presentation), and Australia
  has classified games with simulated gambling R18+ since 2024. A web app in no store needs no
  rating, but 13+ is then the owner's knowing choice, so say it on first launch.
- **Keep the AI coach for adults.** A word filter on the output catches "casino" and "bankroll"
  but not paraphrased bankroll advice, and knowingly adding a child brings the model provider's
  safeguards for minors and, if the app were ever commercial, children's-privacy law. Teens get
  the on-device odds helper instead.
- **Match whole phrases in an output filter.** Fragments trip on poker's own words ("even money",
  "dead money", "opposite" for "site"); keep a test of the known false positives.
- **Score house games on decisions, not chips.** Against a house edge, chips won reward wild
  betting over good play, so a blackjack mode would use one-unit hands scored against basic
  strategy.
- **Family and school web filters judge domains.** A poker subdomain can be filed under gambling
  and, with some filters, block the whole domain and the other games on it.

### Claims in a brain-training-style game

Learned specifying a puzzle game the owner asked to "help improve cognitive function"
(`nickprignano/standup`, 2026-11-11; spec only, red-teamed twice by Fable):

- **Tell the owner the honest premise first.** A 2024 meta-analysis of computerized
  working-memory training (52 comparisons, 3,737 adults) found large gains on the practised
  tasks and none on fluid intelligence (SMD 0.007), switching or processing speed. The defensible
  promise is "you'll get better at these puzzles". In 2016 a large brain-training company paid
  $2M to settle US FTC charges over its ads.
- **A banned-words list is the wrong main control.** Substring matching trips on code
  (`preventDefault`, `unique`, `secure`), the obvious fix of whole-word matching misses
  "prevents" and "treatment", and the list never covers "sharper", "brain training" or "stay
  sharp". Claims also travel without words: skill labels on each puzzle, a rising chart next to
  a skill name.
- **Put every player-facing word in one file the owner approves**, with a test that fails if a
  view contains a display string from anywhere else. Keep a deny-list of word-start stems as a
  second net, and check citation URLs against an allow-list instead of exempting them.
- **Don't ship a self-test that can't measure.** A 20-trial check has a ±25-point band between
  two sittings, wider than the room left to improve, and with one person, no comparison group
  and retest effects it can't separate practice from noise. A tracked "reasoning" score for a
  teenager also reads as an IQ test. The spec cut it.
- **Keep health outcomes out of the app.** A 20-year trial linked one speed-training program
  with booster sessions to fewer dementia diagnoses in adults 65+; memory and reasoning
  training weren't linked. One trial, one program, one age group: a puzzle that looks like that
  task invites the claim by resemblance, so the app never mentions it and the speed puzzle waits
  for a patent and trademark check.

### Agents in security operations

- **Microsoft's hosted Sentinel MCP server** (Preview) lets an agent explore and triage Sentinel
  data with Entra identities. Saved advanced-hunting KQL can be turned into custom tools, which is
  also the only way to reach Defender XDR tables; Microsoft has no Defender MCP server. It needs the
  Sentinel data lake and Defender licences. Data lake tool calls bill per query, and Entity Analyzer
  uses Security Copilot units. Security Reader can call tools; creating them needs Security Operator
  or Admin ([custom tools](https://learn.microsoft.com/en-us/azure/sentinel/datalake/sentinel-mcp-create-custom-tool)).
  Platform-specific use belongs in the sibling KB for that platform ([family.yaml](../family.yaml)).
- Open-source SOAR with agent and MCP support: Tracecat (AGPL-3.0, pre-1.0) and Shuffle (AGPL-3.0,
  v2.3.0 added AI agent and MCP actions). Cisco's Foundation-Sec-8B is an open-weight security LLM
  for SOC summaries and MITRE mapping. Most other "AI SOC" repos are demos.
- **Prompt injection in an agent swarm:** use a classifier made for injected documents (for example
  Azure AI Content Safety Prompt Shields) as the control. Add **decoy MCP tools** as a tripwire:
  [Beelzebub](https://github.com/beelzebub-labs/beelzebub) (GPL-3.0) offers fake tools that a
  healthy agent never calls. Its README says decoys don't catch every attempt, and an injection that
  abuses real tools passes silently. *(judgment: decoys are an alarm, not a control)*

### Deception and honeypots

Beelzebub (LLM-backed SSH, HTTP and Postgres decoys) is the most mature LLM honeypot. Galah
(Apache-2.0) imitates any web app with an LLM, and T-Pot bundles both with 29 other honeypots.
Thinkst's [Canarytokens](https://docs.canarytokens.org/guide/entraid-token) has no AI, but its Entra
ID login token alerts when a phishing kit clones your sign-in page, which makes it a cheap win.

### Offensive tools, used defensively

Use these only on systems you own or are authorized to test, in a sandbox.

- **Autonomous pentest agents:** strix (Apache-2.0, ~69k stars since Aug 2025), shannon (AGPL-3.0,
  ~49k; 2.x moved off the Claude Agent SDK), pentagi (MIT) and PentestGPT (MIT, USENIX Security 2024).
  They are popular but young, and their results are mostly self-reported.
  `aliasrobotics/cai` was archived in Aug 2026 when its development moved to a paid product. News
  reports say attackers have used `hexstrike-ai`, an MCP wrapper around 150+ tools.
- **AI bug-finding:** the DARPA AIxCC systems were judged independently on real code
  ([archive](https://archive.aicyberchallenge.com/)). Trail of Bits' Buttercup (AGPL-3.0) is the one
  packaged to run on its own. Google's oss-fuzz-gen writes fuzz targets for OSS-Fuzz. Theori's
  archive has no license, so it is reference only.

### Spam, phishing and fraud

rspamd (mature mail filter with an LLM plugin that can use a local model), tg-spam (Telegram),
Sublime's MIT-licensed email detection rules and self-hosted platform, Jube (AGPL-3.0, fraud and
AML) and Marble (Elastic License 2.0, so it can't be offered as a hosted service). Phishpedia and
PhishIntention are research code. AI scam-baiting at scale, such as Apate.ai, is commercial only.
