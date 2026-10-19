---
status: proposed
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
   Cloud sessions use a dev or preview environment's platform secret instead.
5. **Never in chat, repos, docs or Claude project environments.** That includes a claude.ai
   project's or cloud session's environment variables, and anywhere a connected tool can read it
   back into a session (a KV store, database or bucket a connector reaches). Claude only ever sees
   and writes key names; the owner runs every step that handles a value (guardrail 2).
   Connectors and MCP servers are standing credentials themselves: least scope, revoked when idle.
6. **One scoped key per purpose, with a cap.** One key per app and environment, with the
   narrowest permissions and model access the provider allows. Set a hard spend cap where the
   provider has one (often per workspace or project, not per key, so give each app its own); where
   it only offers budget alerts, set an alert and keep the key tightly scoped.
7. **A deployment note on every entry.** Each vault entry says where the key is deployed, for
   example "Cloudflare Worker secret, `<worker-name>`", and whether it has a hard cap or only an
   alert. The vault, not a doc, is the list of where keys live.
8. **Rotate on a leak, and on schedule.** Rotate when a key leaks, a device holding the vault is
   lost, or a connector or app is retired, and once a year. If usage shows abuse, revoke at the
   provider first. Otherwise create the new scoped key, paste it where the deployment note says,
   check it works, then revoke the old one, so nothing goes down. Then update the note and check
   the provider's usage for anything not yours. A key that was "only in a private place" still
   gets rotated.
9. **Protect the vault.** A passkey or hardware key as the second factor, the master password and
   recovery code on paper away from devices, and an emergency-access path to someone the owner
   trusts. Let the extension fill only on an exact domain match, and never paste a vault item into
   a page it didn't match: a cloned sign-in page is the likeliest attack.
10. **Push protection first, gitleaks as the backstop.** GitHub secret scanning push protection
    (free on public repos) blocks a push that holds a known key type. The `secrets` workflow runs
    gitleaks on every push and PR; add a custom rule for any key prefix it doesn't know. A hit
    after a push means the key is in history, so it's treated as leaked (step 8).

### Consequences

- Good, because a key lives in the vault, its one service, and at most the CI that deploys it, so
  a leak is easy to scope and the deployment note makes rotation a checklist.
- Good, because sessions can build and deploy everything except the paste, and never hold a value.
- Bad, because every new key or rotation is a manual step for the owner, and a deployment note
  that wasn't updated leaves a stale copy running after a rotation.
- Bad, because everything rests on the vault: if its sign-in is lost or phished, every key goes
  with it, which is why step 9 isn't optional.

## More Information

- Builds on [guardrail 2](../../guardrails.md), [0003](0003-claude-api-as-model-provider.md)
  (a workspace per app) and [0009](0009-second-model-family.md) (keys in each platform's secret
  store).
- How-to notes: [privacy and safety, keys and secrets](../privacy-and-safety/README.md#keys-and-secrets).
- Red-teamed 2026-10-19 with Fable: eight findings, all taken (deploy tokens, connectors, local
  dev, rotation order, vault protection, where spend caps exist, push protection, entry naming).
- Revisit when a provider the owner uses offers keyless access, or on 2027-04-19.
