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
  - a workflow that starts using pull_request_target

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
                 "*.example.com", "*.example.org", "*.example.net", "json-schema.org", "www.w3.org"]
# The workflow's own token, scoped by the workflow's `permissions:` block.
RUN_TOKENS = {"GITHUB_TOKEN", "GH_TOKEN"}

SECRET_NAME = r"[A-Za-z0-9_]*(?:KEY|TOKEN|SECRET|PASSWORD|PASSWD|CREDENTIAL|PRIVATE)[A-Za-z0-9_]*"
# A read of a named binding: env.X, env["X"], process.env.X, os.environ["X"], os.environ.get("X"),
# os.getenv("X"), Deno.env.get("X"), $env:X, secrets.X, Environment.GetEnvironmentVariable("X").
SECRET_READ = re.compile(
    r"(?:\benv|\benviron|\bgetenv|\bsecrets|GetEnvironmentVariable|\$env:)"
    r"\s*(?:\??\.\s*get\s*\(|\??\.|\[|\()?\s*[\"'`]?(" + SECRET_NAME + r")\b", re.I)
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
    re.compile(r"\b(?:JSON\.stringify|Object\.(?:keys|values|entries|assign)|console\.\w+|print|"
               r"json\.dumps|Response\.json|new\s+Response)\s*\([^)]*\benv\b(?!\s*(?:\??\.|\[))"),
    re.compile(r"\breturn\s+env\s*;?\s*$"),
]
SINK = re.compile(r"console\.\w+\s*\(|\bprint\s*\(|\blog(?:ger|ging)?\.\w+\s*\(|Write-(?:Host|Output|"
                  r"Verbose|Information)\b|\becho\b|new\s+Response\s*\(|Response\.json\s*\(|"
                  r"\bres\.(?:send|json|write)\s*\(|\breturn\b|\.set(?:Header)?\s*\(", re.I)
SECRET_WORD = re.compile(r"(?i)api_?key|access_?key|secret|password|passwd|credential|private_?key|"
                         r"(?<![a-z])token(?!s|iz|_count)|(?<=[a-z])Token(?!s|iz)")
HOST = re.compile(r"\b(?:https?|wss?)://([A-Za-z0-9.-]+)")
DYNAMIC_CALL = re.compile(
    r"\b(?:fetch|axios(?:\.\w+)?|requests\.\w+|httpx\.\w+|urlopen|urllib\.request\.Request|"
    r"Invoke-(?:WebRequest|RestMethod)|new\s+WebSocket|new\s+EventSource|sendBeacon)\s*\(\s*"
    r"(?![\"'`](?:https?|wss?)://|\))")
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


def secret_reads(line: str) -> list[str]:
    return [n for n in SECRET_READ.findall(line) if n.upper() not in RUN_TOKENS]


def scan_line(path: str, text: str, allow: list[str]) -> list[str]:
    """What to check on one added line, as short messages."""
    if COMMENT.match(text):
        return []
    found = []
    if any(p.search(text) for p in WHOLE_ENV):
        found.append("uses the whole environment, so every secret in it can go wherever this goes")
    if SINK.search(text) and (secret_reads(text) or SECRET_WORD.search(text)):
        found.append("logs, returns or sends something secret-named")
    for host in sorted({h for h in HOST.findall(text) if not host_allowed(h, allow)}):
        found.append(f"names host `{host}`, which isn't on the egress allowlist")
    if DYNAMIC_CALL.search(text):
        found.append("calls an address built at runtime: check where it can point")
    if path.startswith(".github/workflows/") and "pull_request_target" in text:
        found.append("runs with a write token on PR events: it must never check out or run PR code")
    return found


def scan(added: dict[str, list[tuple[int, str]]], head_text, cfg: dict) -> list[tuple[str, int, str]]:
    """Findings as (path, line, message). head_text(path) returns the file at head, or None."""
    findings = []
    for path in sorted(added):
        if ignored(path, cfg["ignore"]):
            continue
        content = head_text(path)
        if content is None:
            continue
        for n, text in enumerate(content.splitlines(), 1):
            names = secret_reads(text)
            if names and not COMMENT.match(text):
                findings.append((path, n, f"this file reads `{names[0]}`: read its changes for a path "
                                          "that returns, logs or sends it"))
                break
        for n, text in added[path]:
            findings.extend((path, n, msg) for msg in scan_line(path, text, cfg["allow"]))
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


def markdown(findings: list[tuple[str, int, str]], repo: str, sha: str) -> str:
    if not findings:
        return ""
    rows = []
    for path, line, msg in findings[:MAX_ROWS]:
        where = f"`{cell(path)}:{line}`"
        if repo and sha:
            where = f"[{where}](https://github.com/{repo}/blob/{sha}/{path}#L{line})"
        rows.append(f"| {where} | {msg} |")
    more = len(findings) - MAX_ROWS
    tail = [f"", f"And {more} more: run `python3 scripts/kb/secrets_touch.py` locally."] if more > 0 else []
    return "\n".join([
        MARKER,
        f"### Secrets touch: {len(findings)} place{'s' if len(findings) != 1 else ''} to read",
        "",
        "These lines could make a key reachable without anyone seeing it: returned, logged, or sent "
        "to another host (decision 0016, step 6). It's a prompt to read them, not a gate; a host "
        "this app should call goes in `egress_allow`.",
        "",
        "| Where | What to check |",
        "|---|---|",
        *rows,
        *tail,
        "",
    ])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--base", required=True, help="branch or commit the PR merges into")
    ap.add_argument("--head", default="HEAD", help="the PR's head commit")
    ap.add_argument("--markdown", help="write the PR comment here (empty when nothing is flagged)")
    args = ap.parse_args()
    diff = git("diff", "--unified=0", "--no-color", "--no-ext-diff", "-M", f"{args.base}...{args.head}")
    findings = scan(parse_diff(diff), head_reader(args.head), load_config())
    for path, line, msg in findings:
        print(f"{path}:{line}: {msg}")
    print(f"{len(findings)} place(s) to read.")
    if args.markdown:
        sha = git("rev-parse", args.head).strip()
        Path(args.markdown).write_text(markdown(findings, os.environ.get("GITHUB_REPOSITORY", ""), sha))
    return 0


if __name__ == "__main__":
    sys.exit(main())
