---
status: accepted
date: 2026-10-19
decision-makers: [maintainer]
---

# 0016. Secrets: one password manager as the master copy, keys only in each service's own secret store

## Context and Problem Statement

The owner's apps now need API keys from more than one provider (the Claude API, and the second
model family in [0009](0009-second-model-family.md)), deployed to more than one platform.
[Guardrail 2](../../guardrails.md) already says keys never pass through chat, the repo or the KB,
but not where the master copy lives, how a key reaches the service that uses it, or what to do when
one leaks. Without that, keys end up in notes, chat or a cloud session's environment because it is
the nearest box to paste into. Where do keys live, and how do they move?

## Considered Options

- No rule beyond guardrail 2: each project keeps keys wherever is handy
- A password manager that connects to Claude, so sessions can fetch keys themselves
- One password manager as the master copy, with each key pasted by the owner straight into the
  secret store of the one service that uses it

## Decision Outcome

Chosen option: "One password manager as the master copy", because Claude never needs a key's
value, only its name, so nothing gains from letting a session read the vault, and every place a key
is copied is another place it can leak.

1. **Master copy.** Every key lives in the owner's password manager, Bitwarden (the free plan is
   enough). The browser extension is the everyday way in, since keys are pasted into provider and
   platform dashboards in the browser; the phone app is the backup way in. Another manager the
   owner already uses daily works the same way. The vault entry's title is the variable name the
   code reads, such as `<PROVIDER>_API_KEY`, so Claude's code and the owner's paste use one word.
2. **One home per key.** A key is pasted by the owner from the vault into the secret store of the
   service that uses it, and nowhere else: a Cloudflare Worker secret, Azure Key Vault or app
   settings, or the platform's equivalent. Where the platform offers keyless sign-in (managed
   identity, workload identity federation, OIDC from CI), use that and have no key at all. A key
   that needs a second home is shared and should be split into two keys.
3. **Deploy credentials count too.** A token that deploys to a platform can usually read or
   replace code and secrets there, so it's worth more than any model key. Prefer OIDC federation
   from CI; where a token can't be avoided, scope it to one account and one repo, keep it in a
   GitHub environment secret that needs a reviewer, and give it a vault entry like any other key.
4. **Local development uses its own key.** A separate dev-scoped key goes in the stack's
   gitignored local file (`.dev.vars`, `.env`, `local.settings.json`), never a production key.
   Cloud sessions use a dev or preview environment's platform secret instead. Treat dev and
   preview keys as seen by AI sessions, since a session reads the workspace and can run code that
   prints them: give them their own workspace or project with a small hard cap. They're rotated
   on the yearly check, not after every session, because the cap bounds the loss.
5. **Never in chat, repos, docs or Claude project environments.** That includes a claude.ai
   project's or cloud session's environment variables, and anywhere a connected tool can read it
   back into a session (a KV store, database or bucket a connector reaches). Claude only ever sees
   and writes key names; the owner runs every step that handles a value (guardrail 2).
   Connectors and MCP servers are standing credentials themselves: least scope, and removed when
   unused for 30 days.
6. **Knowing only names isn't enough.** A session that can write and deploy code can make a key
   reachable without seeing it (a handler that returns it, a log line, a `fetch` to another host),
   and a prompt-injected page or issue can ask it to. So:
   - Production deploys only from CI on the main branch, after the owner's merge; a platform
     build from `main` (Cloudflare Workers Builds) is simplest, since the platform holds the
     deploy token. A session's platform connector token is scoped to previews or a
     non-production account, or the session has none. Preview secrets are the capped dev keys of
     step 4, never production ones.
   - For an app that holds production keys, the build from `main` only uploads a version
     (`wrangler versions upload` as the Workers Builds deploy command) and the owner releases it
     in the platform dashboard, so a merge alone puts nothing live. Branch builds stay off: they
     run the branch's own build scripts with the build token, which by default can edit every
     Worker on the account. The build still runs merged scripts with that token, so a change to
     dependencies or build scripts in such an app is read before merging.
   - No repository-level Actions secrets: a workflow on any pushed branch can print them.
     Environment secrets only, limited to `main`, with the owner as required reviewer (free on
     public repos; private repos need GitHub Pro). A PR that changes `.github/workflows/` never
     merges itself ([0014](0014-family-format-auto-merge-low-risk-prs.md)).
   - These gates are policy for a session that pushes as the owner's account, since GitHub can't
     tell them apart: a session never merges to `main`, approves a deployment or changes a
     ruleset except on the owner's own words in chat. The technical backstop is a ruleset on
     `main` that requires a PR and the CI checks, so nothing lands unseen by CI. Planned, to
     revisit once the deploy gate is in use: a separate GitHub account for sessions, a
     collaborator that can't change settings, with one required approval on `main` in the repos
     that hold keys, so a merge there needs the owner's own click.
   - A CI check flags any PR that touches a file reading a secret binding or `env` as a whole,
     or adds an outbound host not on the app's allowlist, so the owner reads that part. It's a
     prompt to read, not a gate: a check the session can edit can't be one.
   - Mail, calendar and file connectors live in one Claude project used for nothing else; coding
     projects don't have them attached (set once per project). A mailbox holds the password
     resets for every other account. Until that split exists, treat the mailbox as reachable from
     sessions. Either way, every provider account has a second factor that isn't email.
7. **One scoped key per purpose, with a cap.** One key per app and environment, with the
   narrowest permissions and model access the provider allows. Set a hard spend cap where the
   provider has one (often per workspace or project, not per key, so give each app its own); where
   it only offers budget alerts, use prepaid credit with auto top-up off, or route the calls
   through a gateway spend limit (Cloudflare AI Gateway blocks with a 429, but only for models
   whose pricing it knows, so check media models, and a burst can briefly pass it, so add a rate
   limit too). Any endpoint that spends provider money needs owner-only sign-in or a rate limit, since
   anyone who can call it can spend without the key.
8. **A deployment note on every entry.** Each vault entry says where the key is deployed, for
   example "Cloudflare Worker secret, `<worker-name>`", and whether it has a hard cap or only an
   alert. The vault, not a doc, is the list of where keys live.
9. **Rotate on events; check once a year.** Rotate when a key leaks or may have, a device
   holding the vault is lost, or a connector or app is retired. Once a year a scheduled issue
   checks each deployment note against the secret names actually deployed, looks at each
   provider's usage for traffic that isn't yours, and removes idle connectors; calendar rotation by hand adds outage risk for little gain. If usage shows abuse,
   revoke at the provider first. Otherwise create the new scoped key, paste it where the deployment note says,
   check it works, then revoke the old one, so nothing goes down. Then update the note and check
   the provider's usage for anything not yours. A key that was "only in a private place" still
   gets rotated.
10. **Protect the vault.** A passkey or hardware key as the second factor, the master password and
   recovery code on paper away from devices, and an emergency-access path to someone the owner
   trusts (Bitwarden's emergency access is a Premium feature; the free path is a sealed paper
   sheet with that person). Keep each provider account's recovery codes on paper too, not only in
   the vault: keys can be reissued, but not without the accounts. Let the extension fill only on
   an exact domain match, and never paste a vault item into a page it didn't match: a cloned
   sign-in page is the likeliest attack.
11. **Push protection first, gitleaks as the backstop.** GitHub secret scanning push protection
    (free on public repos) blocks a push that holds a known key type. The `secrets` workflow runs
    gitleaks on every push and PR; add a custom rule for any key prefix it doesn't know. A hit
    after a push means the key is in history, so it's treated as leaked (step 9).

### Consequences

- Good, because a key lives in the vault, its one service, and at most the CI that deploys it, so
  a leak is easy to scope and the deployment note makes rotation a checklist.
- Good, because sessions can build and deploy everything except the paste, and never hold a value.
- Bad, because every new key or rotation is a manual step for the owner, and a deployment note
  that wasn't updated leaves a stale copy running after a rotation.
- Bad, because everything rests on the vault: if its sign-in is lost or phished, every key goes
  with it, which is why step 10 isn't optional.

## More Information

- Builds on [guardrail 2](../../guardrails.md), [0003](0003-claude-api-as-model-provider.md)
  (a workspace per app) and [0009](0009-second-model-family.md) (keys in each platform's secret
  store).
- How-to notes: [privacy and safety, keys and secrets](../privacy-and-safety/README.md#keys-and-secrets).
- Red-teamed 2026-10-19 with Fable: eight findings, all taken (deploy tokens, connectors, local
  dev, rotation order, vault protection, where spend caps exist, push protection, entry naming).
- Outside review 2026-10-20 (Gemini), [decision 0017](0017-outside-review-for-high-stakes-work.md)'s
  first pilot, with a fresh Claude as control: both found that a session able to deploy code can
  leak a key without seeing it, which the Fable pass missed. Steps 4 to 7, 9 and 10 changed;
  step 6 is new. Owner accepted the amended version on 2026-10-20. Red-teamed again with Fable the same day: six findings, all taken (the gates are
  policy when agents push as the owner, a CI check that can be edited is a prompt not a gate,
  the connector split, gateway pricing limits, usage in the yearly check, GitHub plan limits). Calendar rotation was dropped on Gemini's point alone. Putting step 6 into practice
  (2026-10-20) got a Fable pass and a fresh-Claude control: the control found that branch builds
  run branch code with an account-wide token and that a read-only connector still reads logs and
  storage; the owner chose the deploy gate over a separate GitHub account for now. *Unverified:* whether an
  Anthropic workspace spend limit blocks requests or only alerts.
- Revisit when a provider the owner uses offers keyless access, or on 2027-04-19.
