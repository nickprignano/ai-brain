---
title: "Privacy and safety"
summary: "Keys and secrets, prompt injection, local-only designs, building AI features for kids, and open-source AI tools for fighting bad actors"
topic: privacy-and-safety
status: partial
last_reviewed: 2026-10-19
sources:
  - https://github.com/microsoft/PyRIT
  - https://github.com/promptfoo/promptfoo
  - https://www.promptfoo.dev/docs/red-team/architecture/
  - https://github.com/NVIDIA/garak
  - https://github.com/meta-llama/PurpleLlama
  - https://developers.cloudflare.com/workers-ai/models/
  - https://arxiv.org/pdf/2607.00395
  - https://support.claude.com/en/articles/15591275-child-safety-guidance-for-developers
  - https://github.com/roostorg/awesome-safety-tools
  - https://learn.microsoft.com/en-us/azure/sentinel/datalake/sentinel-mcp-create-custom-tool
  - https://github.com/beelzebub-labs/beelzebub
  - https://docs.canarytokens.org/guide/entraid-token
  - https://archive.aicyberchallenge.com/
---

# Privacy and safety

Keeping AI features safe and private: handling keys, prompt injection from untrusted text, local-only
designs where data never leaves the device, and extra care for apps children use. Only the section
below is written so far.

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
  run on every PR. It has been part of OpenAI since 2026-03-09 and is still MIT. Its red-team mode
  generates attacks through promptfoo's cloud by default and sends the target's replies back there
  for follow-up attacks
  ([architecture](https://www.promptfoo.dev/docs/red-team/architecture/)), so run it against a test
  deployment with synthetic users, or configure local attack and judge models.
- **[garak](https://github.com/NVIDIA/garak)** (NVIDIA, Apache-2.0) is a broad vulnerability scanner
  that gives a quick baseline. **[PurpleLlama](https://github.com/meta-llama/PurpleLlama)** (Meta)
  holds CyberSecEval, LlamaFirewall, Prompt Guard 2 and Llama Guard.
- Dead: `protectai/llm-guard` was archived on 2026-07-09 with no successor named.

### Safety classifiers for apps children use

- **Llama Guard 3 8B is the only safety model in the Cloudflare Workers AI catalog** (no Llama Guard
  4, Prompt Guard, ShieldGemma or gpt-oss-safeguard as of this check). That makes it the default
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
