"""Point the owner at pull request changes that could make a secret reachable (decision 0016, step 6).

A session that writes and deploys code can leak a key without ever seeing it: a handler that returns
it, a log line that prints it, a call that sends it to another host. This lists the places in a diff
where that could happen, so the owner reads those lines. It's a prompt to read, not a gate: it
always exits 0 unless it breaks, and it can't prove a change is safe.

Stdlib-only and git-only, so a repo without the KB scripts can copy this one file:

  python3 scripts/kb/secrets_touch.py --base origin/main [--head HEAD] [--markdown out.md]
      Compares head with its merge base on base, prints what it found, and writes a PR comment
      (with links when $GITHUB_REPOSITORY is set) to --markdown, or an empty file when nothing is
      flagged. The secrets-touch workflow runs it from the base branch and posts the comment.

What it flags, in changed files that aren't Markdown or the knowledge base:
  - a file that reads a secret-named binding (`env.API_KEY`, `os.environ["X_TOKEN"]`, `secrets.X`)
  - an added line that uses the whole environment (`JSON.stringify(env)`, `printenv`, `os.environ`)
  - an added line that logs, returns or responds with a secret-named value
  - an added line that names a host not on the allowlist, or calls an address built at runtime
  - an added third-party action in a workflow, and a workflow that runs on pull_request_target
  - any change to what agent sessions are told (AGENTS.md, CLAUDE.md, skills, .claude/), to
    dependencies or build scripts, to Worker config, or to this check's own settings

The comment puts the likeliest leaks first and the file-level and runtime-address notes under
"Also", so the owner can read the first table in seconds.

Settings come from docs/knowledge/kb.toml in a repo with a KB, or .claude/kb-capture.toml in one
without (the same files as the kb-capture settings):

  egress_allow = ["api.example.com", "*.example.net"]   # hosts this app may call
  secrets_touch_ignore = ["vendor/**"]                  # paths not to scan
"""

from __future__ import annotations

import argparse
import fnmatch
import os
import re
import urllib.parse
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KB_PATH = "docs/knowledge/"
MARKER = "<!-- secrets-touch -->"
MAX_ROWS = 50
# Prose and generated files: a URL or a variable name there doesn't run.
DEFAULT_IGNORE = ["docs/knowledge/**", "*.md", "llms.txt", "*.lock", "**/*.lock", "package-lock.json",
                  "**/package-lock.json", "poetry.lock", "uv.lock", "LICENSE", "NOTICE",
                  # Its own patterns and test samples would flag them; neither merges itself (0014).
                  "scripts/kb/secrets_touch.py", "scripts/kb/test_kb.py"]
# Hosts that are identifiers or placeholders, not somewhere code sends data.
DEFAULT_ALLOW = ["localhost", "127.0.0.1", "0.0.0.0", "example.com", "example.org", "example.net",
                 "*.example.com", "*.example.org", "*.example.net", "*.example", "*.test", "*.invalid",
                 "*.localhost", "json-schema.org", "www.w3.org"]
# What agent sessions are told: a change here can steer every later session, so it's always read.
INSTRUCTIONS = ["agents.md", "*/agents.md", "claude.md", "*/claude.md", "*skill.md", ".claude/*",
                "*/.claude/*", ".github/copilot-instructions.md", "*.cursorrules", "*.mdc"]
# Files where a change runs new code or reroutes data without a suspicious line in the diff.
WHOLE_FILE = [
    (["package.json", "*/package.json", "package-lock.json", "*/package-lock.json", "*.lock",
      "pnpm-lock.yaml", "*/pnpm-lock.yaml", "requirements*.txt", "*/requirements*.txt",
      "pyproject.toml", "*/pyproject.toml"],
     "changes dependencies or build scripts: new code runs with the app's secrets in scope"),
    (["wrangler.toml", "wrangler.json", "wrangler.jsonc", "*/wrangler.toml", "*/wrangler.json",
      "*/wrangler.jsonc"],
     "changes Worker config (bindings, tail consumers, routes, previews): read it whole"),
    ([KB_PATH + "kb.toml", ".claude/kb-capture.toml"],
     "changes this repo's settings, which can widen the egress allowlist for later PRs"),
]
# Notes that are worth a look but fire often; they go under "Also".
FYI = ("this file reads", "calls an address built at runtime")
# The workflow's own token, scoped by the workflow's `permissions:` block.
RUN_TOKENS = {"GITHUB_TOKEN", "GH_TOKEN"}

# A name counts as a secret by its `_`-separated words (camelCase is split first): SECRET, PASSWORD
# or CREDENTIAL anywhere, TOKEN and KEY unless a neighbour says they mean something else.
SECRET_WORDS = {"SECRET", "SECRETS", "PASSWORD", "PASSWD", "CREDENTIAL", "CREDENTIALS", "APIKEY",
                "PRIVATEKEY"}
NOT_A_KEY = {"CACHE", "SORT", "PARTITION", "PRIMARY", "FOREIGN", "IDEMPOTENCY", "ROUTING", "LOOKUP",
             "OBJECT", "HASH", "PUBLIC", "KV", "MAP", "DEDUPE", "STORAGE"}
NOT_A_TOKEN = {"MAX", "PAGE", "NEXT", "CURSOR", "CONTINUATION", "BUDGET", "LIMIT", "COUNT", "USAGE",
               "TOTAL", "INPUT", "OUTPUT"}
# A read of a named binding: env.X, env["X"], process.env.X, os.environ["X"], os.environ.get("X"),
# os.getenv("X"), Deno.env.get("X"), $env:X, secrets.X, Environment.GetEnvironmentVariable("X").
SECRET_READ = re.compile(
    r"(?:\benv|\benviron|\bgetenv|\bsecrets|GetEnvironmentVariable|\$env:)"
    r"\s*(?:\??\.\s*get\s*\(|\??\.|\[|\()?\s*[\"'`]?([A-Za-z_][A-Za-z0-9_]*)", re.I)
# const { X_API_KEY, OTHER } = env (or c.env, process.env), the usual Workers form.
DESTRUCTURE = re.compile(r"\{([^}]*)\}\s*=\s*(?:[\w.]*\.)?env\b")
WHOLE_ENV = [
    re.compile(r"\bprocess\.env\b(?!\s*(?:\??\.|\[))"),
    re.compile(r"\bimport\.meta\.env\b(?!\s*(?:\??\.|\[))"),
    re.compile(r"\bos\.environ\b(?!\s*(?:\[|\.get\b|\.setdefault\b|\.pop\b))"),
    re.compile(r"\bDeno\.env\.toObject\b"),
    re.compile(r"\bEnvironment\.GetEnvironmentVariables\b"),
    re.compile(r"\b(?:Get-ChildItem|gci|dir|ls)\s+env:", re.I),
    re.compile(r"\bprintenv\b"),
    re.compile(r"^\s*(?:-\s*)?(?:run:\s*)?env\s*(?:\||$)"),
    re.compile(r"\btoJSON\(\s*(?:secrets|env)\s*\)"),
    re.compile(r"\bsecrets:\s*inherit\b"),
    re.compile(r"\.\.\.\s*env\b(?!\s*(?:\??\.|\[))"),
    re.compile(r"\bin\s+(?:process\.)?env\b(?!\s*(?:\??\.|\[))"),
    re.compile(r"\b(?:process\.)?env\s*\[\s*(?![\"'`\s])"),
    re.compile(r"\b(?:JSON\.stringify|Object\.(?:keys|values|entries|assign)|json\.dumps|"
               r"Response\.json|new\s+Response)\s*\([^)]*\benv\b(?!\s*(?:\??\.|\[))"),
    re.compile(r"\breturn\s+env\s*;?\s*$"),
]
SINK = re.compile(r"console\.\w+\s*\(|\bprint\s*\(|\blog(?:ger|ging)?\.\w+\s*\(|Write-(?:Host|Output|"
                  r"Verbose|Information)\b|\becho\b|new\s+Response\s*\(|Response\.json\s*\(|"
                  r"\bres\.(?:send|json|write)\s*\(|\breturn\b|\.set(?:Header)?\s*\(", re.I)
SECRET_WORD = re.compile(r"(?i)api_?key|access_?key|secret|password|passwd|credential|private_?key|"
                         r"(?<!next_)(?<!page_)(?<!max_)(?<![a-z])token(?!s|iz|_count|_budget|_limit)|"
                         r"(?<=[a-z])Token(?!s|iz)")
# String literals with nothing interpolated: a secret's name in a message isn't the secret.
PLAIN_STRING = re.compile(r"'[^'${\\]*'|\"[^\"${\\]*\"")
HOST = re.compile(r"\b(?:https?|wss?)://([A-Za-z0-9.-]+)")
DYNAMIC_CALL = re.compile(
    r"\b(?:fetch|axios(?:\.\w+)?|requests\.\w+|httpx\.\w+|urlopen|urllib\.request\.Request|"
    r"Invoke-(?:WebRequest|RestMethod)|new\s+WebSocket|new\s+EventSource|sendBeacon)\s*\(\s*"
    r"(?![frbFRB]?[\"'`](?:https?|wss?)://|\))|"
    r"\b(?:fetch|axios(?:\.\w+)?|requests\.\w+|httpx\.\w+|new\s+WebSocket)\s*\(\s*`(?:(?:https?|wss?)://)?\$\{")
SOCKETS = re.compile(r"[\"']cloudflare:sockets[\"']")
THIRD_PARTY_ACTION = re.compile(r"^\s*(?:-\s*)?uses:\s*[\"']?(?!actions/|github/|\./|docker://)([\w.-]+)/")
COMMENT = re.compile(r"^\s*(?:#|//|/?\*|<!--|--\s)")
HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")


def load_config(root: Path = ROOT) -> dict:
    kb_toml = root / KB_PATH / "kb.toml"
    path = kb_toml if kb_toml.exists() else root / ".claude" / "kb-capture.toml"
    cfg = {}
    if path.exists():
        with path.open("rb") as f:
            cfg = tomllib.load(f)
    return {
        "allow": DEFAULT_ALLOW + [h.lower() for h in cfg.get("egress_allow", [])],
        "ignore": DEFAULT_IGNORE + list(cfg.get("secrets_touch_ignore", [])),
    }


def ignored(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatchcase(path, p) for p in patterns)


def host_allowed(host: str, allow: list[str]) -> bool:
    host = host.lower().rstrip(".")
    for pattern in allow:
        if pattern.startswith("*."):
            if host.endswith(pattern[1:]):
                return True
        elif host == pattern:
            return True
    return False


def parse_diff(text: str) -> dict[str, list[tuple[int, str]]]:
    """Added lines per new path, from `git diff --unified=0`. Deleted and binary files are dropped."""
    added: dict[str, list[tuple[int, str]]] = {}
    path = None
    line = 0
    for raw in text.splitlines():
        if raw.startswith("diff --git "):
            path = None
        elif raw.startswith("+++ "):
            target = raw[4:]
            # With core.quotePath=false git still quotes a path holding a quote or backslash.
            if target.startswith('"') and target.endswith('"'):
                target = re.sub(r'\\(["\\])', r"\1", target[1:-1])
            path = target[2:] if target.startswith("b/") else None
            if path is not None:
                added.setdefault(path, [])
        elif raw.startswith("@@"):
            m = HUNK.match(raw)
            line = int(m.group(1)) if m else 0
        elif path is not None and raw.startswith("+"):
            added[path].append((line, raw[1:]))
            line += 1
    return added


def is_secret_name(name: str) -> bool:
    words = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", name).upper().split("_")
    if "_".join(words) in RUN_TOKENS:
        return False
    for i, w in enumerate(words):
        before = words[i - 1] if i else ""
        after = words[i + 1] if i + 1 < len(words) else ""
        if w in SECRET_WORDS:
            return True
        if w == "KEY" and before not in NOT_A_KEY:
            return True
        if w == "TOKEN" and before not in NOT_A_TOKEN and after not in NOT_A_TOKEN:
            return True
    return False


def secret_reads(line: str) -> list[str]:
    names = SECRET_READ.findall(line)
    for group in DESTRUCTURE.findall(line):
        names += re.findall(r"([A-Za-z_]\w*)\s*(?:[,:=]|$)", group)
    return [n for n in names if is_secret_name(n)]


def scan_line(path: str, text: str, allow: list[str]) -> list[str]:
    """What to check on one added line, as short messages."""
    if COMMENT.match(text):
        return []
    found = []
    code = PLAIN_STRING.sub("''", text)
    if any(p.search(code) for p in WHOLE_ENV):
        found.append("uses the whole environment, so every secret in it can go wherever this goes")
    if SINK.search(code) and (secret_reads(code) or SECRET_WORD.search(code)):
        found.append("logs, returns or sends something secret-named")
    for host in sorted({h for h in HOST.findall(text) if not host_allowed(h, allow)}):
        found.append(f"names host `{host}`, which isn't on the egress allowlist")
    if SOCKETS.search(text):
        found.append("opens raw TCP sockets, which the host checks above don't see")
    if DYNAMIC_CALL.search(text):
        found.append("calls an address built at runtime: check where it can point")
    if path.startswith(".github/workflows/"):
        if "pull_request_target" in text:
            found.append("this workflow runs with a write token on PR events: it must never check out "
                         "or run PR code")
        action = THIRD_PARTY_ACTION.match(text)
        if action:
            found.append(f"adds a third-party action from `{action.group(1)}`: pin it to a commit and "
                         "check which secrets its job can read")
    return found


def scan(added: dict[str, list[tuple[int, str]]], head_text, cfg: dict) -> list[tuple[str, int, str]]:
    """Findings as (path, line, message). head_text(path) returns the file at head, or None."""
    findings = []
    for path in sorted(added):
        if ignored(path.lower(), INSTRUCTIONS):
            first = added[path][0][0] if added[path] else 1
            findings.append((path, first, "changes what agent sessions are told: read the whole diff"))
            continue
        whole = [msg for patterns, msg in WHOLE_FILE if ignored(path, patterns)]
        if whole:
            first = added[path][0][0] if added[path] else 1
            findings.append((path, first, whole[0]))
            continue
        if ignored(path, cfg["ignore"]):
            continue
        content = head_text(path)
        if content is None:
            continue
        line_findings = [(path, n, msg) for n, text in added[path]
                         for msg in scan_line(path, text, cfg["allow"])]
        # The file-level note only when the change could carry a value somewhere: it adds a
        # read, a sink or a network call. A typo fix in a file that reads a key stays quiet.
        risky = line_findings or any(secret_reads(t) or SINK.search(t) for _, t in added[path])
        for n, text in enumerate(content.splitlines() if risky else [], 1):
            names = secret_reads(text)
            if names and not COMMENT.match(text):
                findings.append((path, n, f"this file reads `{names[0]}`: read its changes for a path "
                                          "that returns, logs or sends it"))
                break
        findings.extend(line_findings)
    return findings


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True).stdout


def head_reader(head: str):
    def read(path: str):
        try:
            data = subprocess.run(["git", "show", f"{head}:{path}"], cwd=ROOT, check=True,
                                  capture_output=True).stdout
        except subprocess.CalledProcessError:
            return None
        if b"\0" in data[:8000]:
            return None
        return data.decode("utf-8", "replace")
    return read


def cell(text: str) -> str:
    return text.replace("|", "\\|").replace("`", "'").replace("\n", " ")


def table(findings: list[tuple[str, int, str]], repo: str, sha: str) -> list[str]:
    rows = ["| Where | What to check |", "|---|---|"]
    for path, line, msg in findings:
        where = f"`{cell(path)}:{line}`"
        if repo and sha:
            where = f"[{where}](https://github.com/{repo}/blob/{sha}/{urllib.parse.quote(path)}#L{line})"
        rows.append(f"| {where} | {msg} |")
    return rows


def markdown(findings: list[tuple[str, int, str]], repo: str, sha: str) -> str:
    if not findings:
        return ""
    shown = findings[:MAX_ROWS]
    first = [f for f in shown if not f[2].startswith(FYI)]
    also = [f for f in shown if f[2].startswith(FYI)]
    more = len(findings) - MAX_ROWS
    out = [
        MARKER,
        f"### Secrets touch: {len(first)} to read first, {len(also)} more at `{sha[:12]}`",
        "",
        "These lines could make a key reachable without anyone seeing it: returned, logged, or sent "
        "to another host (decision 0016, step 6). It's a prompt to read them, not a gate; a host "
        "this app should call goes in `egress_allow`. Only trust this comment from "
        "`github-actions[bot]` naming the PR's latest commit.",
        "",
    ]
    if first:
        out += ["**Read first**", "", *table(first, repo, sha), ""]
    if also:
        out += ["**Also**", "", *table(also, repo, sha), ""]
    if more > 0:
        out += [f"And {more} more: run `python3 scripts/kb/secrets_touch.py` locally.", ""]
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--base", required=True, help="branch or commit the PR merges into")
    ap.add_argument("--head", default="HEAD", help="the PR's head commit")
    ap.add_argument("--markdown", help="write the PR comment here (empty when nothing is flagged)")
    args = ap.parse_args()
    diff = git("-c", "core.quotePath=false", "diff", "--unified=0", "--no-color", "--no-ext-diff", "-M", f"{args.base}...{args.head}")
    findings = scan(parse_diff(diff), head_reader(args.head), load_config())
    for path, line, msg in findings:
        print(f"{path}:{line}: {msg}")
    print(f"{len(findings)} place(s) to read.")
    if args.markdown:
        sha = git("rev-parse", args.head).strip()
        Path(args.markdown).write_text(markdown(findings, os.environ.get("GITHUB_REPOSITORY", ""), sha), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
