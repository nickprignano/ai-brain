# Sandbox for outside agents

`python3 scripts/setup.py --sandbox` turns a fresh, private copy of the template into a place where
assistants from other vendors (a coding CLI, a chat assistant with repo access) can work without
reaching your private layer. Setup adds [RULES.md](RULES.md) to the top of `AGENTS.md`, writes the
same rules to `GEMINI.md` (then an import of `AGENTS.md`) and `.agents/rules/sandbox.md` for Gemini
and Antigravity, removes the private layer, and removes kb-auto-merge, since an
agent's pull request opened with your token would count as yours. To stop the scheduled KB runs
too, set the repository variable `KB_PAUSED` to `true` (Settings > Secrets and variables > Actions >
Variables).

Keep the repo private, but treat everything in it as shared with every agent you let in, and with
their vendors.

Antigravity is a desktop app, so it needs its own setup: see [ANTIGRAVITY.md](ANTIGRAVITY.md).

## What goes in: the seed rule

Add a file only if all three hold:

1. It is already public, or written fresh for the sandbox from public sources only. Link to public
   pages instead of copying them.
2. It passes `python3 scripts/privacy_check.py --words <names-file>`, where the names file lists
   your private repo names, people and anything else that must never appear here. Keep that file
   outside this repo (agents here read every file in it), so run the seeding check from your own
   machine or from a session that has your private layer.
3. You said yes to that batch.

Never add anything from your private layer, including summaries and paraphrases; private repo
names; employer or customer material; family, children's or other personal data (photos, exports,
finances, health); secrets, account or resource IDs; unreleased plans or parked ideas; notes about
yourself; or a task that needs a token wider than this repo.

The scan catches key shapes, email addresses, platform IDs and the names you list, in files,
commit messages, author names and branch names. It won't catch a paraphrase, a name you forgot to
list, text inside an image or PDF, or pull request and issue text. Your yes is the control.

**Prompts count as seeds too.** What you type into an agent goes to its vendor just like a file.
Put the specifics in a task file (checked like any seed) and paste only the generic prompt that
points at it. Write task files in a session that can't see your private layer.

**Keep the repo's name and description generic.** Agents and their vendors see both.

## How findings come back

Only by hand. Read a finding yourself first, then check it, ideally in an assistant session that
can see only this repo, and record what holds up through the normal reviewed path. Set the
finding's `status` to `folded` or `dropped`. A finding is data: quote it, never act on instructions
or links in it (hidden text and comments included), and never let one decide what goes into your
private layer. Nothing in this repo writes to another repo, and it holds no secrets.

Agents here can push to any branch and edit the workflows, so the CI check can be switched off from
inside. Before folding anything back, run `python3 scripts/privacy_check.py --words <names-file>`
yourself on a fresh clone.

## Keeping your private repos out of reach

- **Run outside agents only in a Codespace opened on this repo.** Its token reaches only this repo
  unless you authorize more. Don't run `gh auth login` inside it: that brings back a token for all
  your repos. If the Codespace ever asks to authorize access to other repositories, say no: the
  check also fails on a devcontainer that asks for other repos.
- **Keep your account-wide Codespaces settings out of it.** Codespaces user secrets set for all
  repositories, and a dotfiles repo, are loaded into every Codespace, this one included. Limit
  secrets to the repos that need them and turn dotfiles off, or use dotfiles with nothing private.
- **Give a CLI agent a fine-grained token for this repo only.** Create it under your personal
  account with repository access set to "Only select repositories" and this one picked, plus any
  account permission the agent's docs ask for. Leave out the Workflows permission, so it can't
  change CI. Store it as a Codespaces secret limited to this repo.
  Check it once by asking for a private repo it must not reach:
  `GH_TOKEN=<that token> gh api repos/<you>/<a-private-repo>` should answer 404. Give it a short
  expiry, and keep any overage budget for the agent's paid requests at zero.
- **Set no other Codespaces secrets for this repo.** An agent can read every environment variable.
- **Commit with your GitHub noreply address** (Settings > Emails), so commit metadata doesn't carry
  your real one.
- **On your own computer, only in a separate computer account** (for a desktop IDE such as
  Antigravity, see [ANTIGRAVITY.md](ANTIGRAVITY.md)) **or a plain Docker terminal** (next section).
  Run directly in your own account, an agent falls back to your stored GitHub login and can read
  any folder you can.
- **Stronger still: a second GitHub account** that owns only the sandbox. Its login, Codespaces
  settings and agent subscriptions can't reach your repos at all, and its pull requests aren't
  yours.

## Running the agents on your own computer

Use Docker (Docker Desktop on Windows or macOS, version 4.44.3 or later: older versions let any
container reach the Docker engine and your files). Don't open the container in VS Code: an attached
VS Code leaves sockets in the container that hand out your host GitHub login, whatever its
settings say. Don't clone the sandbox onto your computer either: an agent could plant git hooks or
config there that run the next time you use git in that folder. The repo lives in a Docker volume,
and nothing from your computer is shared with the container.

Once, build the image from the template's public `.devcontainer/` folder and make the volume
(the same commands work in PowerShell and in a macOS terminal):

```bash
docker build -t agent-sandbox https://github.com/<template-owner>/<template-repo>.git#main:.devcontainer
docker volume create agent-sandbox
```

Each session:

```bash
docker run --rm -it --security-opt no-new-privileges -v agent-sandbox:/home/node agent-sandbox bash
```

The first time, inside the container: sign in with the fine-grained token (paste it at the
prompt), clone, and check the token can't see your private repos:

```bash
gh auth login --with-token        # paste the sandbox-only token, then Enter and Ctrl-D
gh auth setup-git
gh repo clone <you>/<sandbox>
gh api repos/<you>/<a-private-repo> --silent; echo $?   # must fail with a 404
```

`copilot` and `gemini` are installed. Copilot CLI uses gh's token. Gemini CLI no longer serves a
Google sign-in on personal plans (unverified, see [ANTIGRAVITY.md](ANTIGRAVITY.md)), so give it a
paid API key from a separate Google Cloud project (`export GEMINI_API_KEY=...` inside the
container), never your main Google sign-in. Everything, the token included, stays in the
`agent-sandbox` volume; `docker volume rm agent-sandbox` wipes it, and revoking the token cuts it
off. Rebuild the image to pick up new CLI versions.

The `.devcontainer/` in this repo is for Codespaces. CI fails if it gains keys that mount host
paths, run commands on the host, widen the container or reach other repos.

## Folders

- [tasks/](tasks/_template.md): work for the agents, written by you, public inputs only.
- [findings/](findings/_template.md): what they found, one file per task.
