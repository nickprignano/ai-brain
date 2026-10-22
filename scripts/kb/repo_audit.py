"""Audit the owner's GitHub repos against the GitHub work conventions, and fix named drift.

Stdlib-only (Python 3.11+, for tomllib), so it runs on Windows, macOS, Linux and in a Codespace.
The owner runs it with their own login; nothing is stored and the token is never printed:

  gh auth login -w                        # once; in a Codespace run `unset GITHUB_TOKEN` first
  python3 scripts/kb/repo_audit.py        # full report (names private repos: never commit it)
  python3 scripts/kb/repo_audit.py --summary
      Counts and public repo names only; private repos show as private-1, private-2, ... in the
      order the full report lists them. This is the version to paste into a chat.
  python3 scripts/kb/repo_audit.py --fix my-kb/labels,my-app/ruleset
      Re-runs the audit and applies only the named findings. Typing the ids is the owner's yes.

What it checks, for each owned repo that isn't archived, a fork, empty, or tagged with the topic
`no-conventions-audit` (decisions 0011, 0012, 0014, 0016 and 0019):

  change-rules    every repo, adopted or not: the root AGENTS.md has the "How to make a change"
                  section, and a root or .claude/ CLAUDE.md, if there is one, imports it (an
                  `@AGENTS.md` line or a symlink): Claude Code reads AGENTS.md only when there's
                  no CLAUDE.md.
  adopted         the repo has docs/knowledge/kb.toml or .claude/kb-capture.toml, or its AGENTS.md
                  names decision 0014. A repo that hasn't gets this info line and change-rules only.
  agents-md       AGENTS.md exists and names decision 0014.
  labels          handoff and handoff-proposed; no-auto-merge with kb-auto-merge; no-kb with kb-capture.
  auto-merge-pair the kb-auto-merge workflow and auto_merge.py are copied together.
  gitleaks        a `gitleaks` check ran on the repo's recent merged PRs.
  template        a copied workflow or script differs from this checkout's copy (info only).
  Only where GitHub enforces them (a public repo, or any repo on a paid plan):
  auto-merge-setting  "Allow auto-merge" is on when the repo's settings say auto_merge = "on".
  ruleset         an active ruleset on the default branch requires a PR, no approving review, the
                  checks the repo actually reports (from its recent merged PRs, never from YAML),
                  and has the admin role in its bypass list for pull requests. Only when
                  auto_merge = "on"; with it off the ruleset is an info line, needed before it's on.
  branch-protection  classic protection on the default branch requires an approving review, which
                  a solo owner can't give (removed by hand; never fixed here).
  push-protection secret scanning push protection is on (public repos only).

--fix only sends these calls, built from fixed bodies: PATCH the repo with allow_auto_merge or
security_and_analysis only, POST missing labels, POST a new ruleset, or PUT an existing ruleset
with the missing checks and bypass appended and everything else sent back as it was read. It
never removes a rule or a check, and never changes visibility, the default branch or archiving.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import subprocess
import sys
import tomllib
import urllib.error
import urllib.request
from pathlib import Path

API = "https://api.github.com"
ROOT = Path(__file__).resolve().parents[2]
SKIP_TOPIC = "no-conventions-audit"
SETTINGS = ["docs/knowledge/kb.toml", ".claude/kb-capture.toml"]
AUTO_MERGE_FILES = (".github/workflows/kb-auto-merge.yml", "scripts/kb/auto_merge.py")
CAPTURE_WORKFLOW = ".github/workflows/kb-capture.yml"
CHANGE_RULES = ("## How to make a change", "Say what you assumed")
CLAUDE_MDS = ["CLAUDE.md", ".claude/CLAUDE.md"]
IMPORT_LINE = re.compile(r"^@AGENTS\.md\s*$", re.M)
# Files repos copy unchanged from the template (none of them is a manifest `replace` target).
COPIED = [*AUTO_MERGE_FILES, CAPTURE_WORKFLOW, "scripts/kb/capture_check.py",
          "scripts/kb/handoffs.py", ".github/workflows/secrets.yml"]
# Checks a conventions ruleset may require, and only once the repo has reported them.
KNOWN_CHECKS = ["auto-merge", "validate", "gitleaks", "kb-capture", "checks"]
RECENT_PRS = 3
ADMIN_BYPASS = {"actor_id": 5, "actor_type": "RepositoryRole", "bypass_mode": "pull_request"}
LABELS = {
    "handoff": ("0e8a16", "Approved work handed to this repo (decision 0012)"),
    "handoff-proposed": ("fbca04", "A handoff waiting for the owner's approval (decision 0012)"),
    "no-auto-merge": ("b60205", "Keep this PR for the owner's review (decision 0014)"),
    "no-kb": ("c5def5", "Code change with no KB entry; say why in the PR (decision 0011)"),
}
FIXABLE = {"auto-merge-setting", "labels", "push-protection", "ruleset"}
PATCH_KEYS = {"allow_auto_merge", "security_and_analysis"}
RULESET_KEYS = ["name", "target", "enforcement", "conditions", "rules", "bypass_actors"]


class ApiError(Exception):
    pass


class Client:
    """A thin GitHub REST client. The token goes only into the Authorization header."""

    def __init__(self, token: str):
        self._token = token
        self.scopes = ""

    def call(self, method: str, path: str, body: dict | None = None):
        url = path if path.startswith("http") else f"{API}{path}"
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, method=method, headers={
            "Accept": "application/vnd.github+json", "User-Agent": "kb-repo-audit",
            "X-GitHub-Api-Version": "2022-11-28", "Authorization": f"Bearer {self._token}"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                self.scopes = r.headers.get("X-OAuth-Scopes", self.scopes)
                raw = r.read()
                return json.loads(raw) if raw else None
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            raise ApiError(f"{method} {path}: HTTP {e.code}") from None

    def get(self, path: str):
        return self.call("GET", path)

    def get_all(self, path: str) -> list:
        sep = "&" if "?" in path else "?"
        out, page = [], 1
        while True:
            items = self.get(f"{path}{sep}per_page=100&page={page}") or []
            out += items
            if len(items) < 100:
                return out
            page += 1


def token_from_env(env=os.environ) -> str:
    """The owner's token: GH_TOKEN, else GITHUB_TOKEN outside a Codespace, else `gh auth token`."""
    if env.get("CODESPACES") == "true" and env.get("GITHUB_TOKEN"):
        # The Codespace token sees one repo and gets 403 on settings: a silently partial audit.
        raise SystemExit("In a Codespace, run `unset GITHUB_TOKEN; gh auth login -w` first.")
    tok = env.get("GH_TOKEN") or env.get("GITHUB_TOKEN")
    if tok:
        return tok
    try:
        return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True,
                              timeout=20, check=True).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        raise SystemExit("No token: install the GitHub CLI and run `gh auth login -w`.") from None


def clean(text: str) -> str:
    """Names read from GitHub are untrusted: one line, no control characters or Markdown links."""
    return re.sub(r"[\x00-\x1f\x7f\[\]()<>`]+", " ", str(text or "")).strip()[:100]


def local_blob(path: str, root: Path = ROOT) -> str | None:
    """The committed blob SHA, so Windows line endings in the working tree don't count."""
    try:
        return subprocess.run(["git", "-C", str(root), "rev-parse", f"HEAD:{path}"],
                              capture_output=True, text=True, timeout=10,
                              check=True).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None


def finding(repo: str, check: str, text: str, fix: str = "", level: str = "drift",
            data=None) -> dict:
    return {"id": f"{repo}/{check}", "repo": repo, "check": check, "text": text, "fix": fix,
            "level": level, "data": data}


def blob_text(gh: Client, full: str, sha: str) -> str:
    blob = gh.get(f"/repos/{full}/git/blobs/{sha}") or {}
    return base64.b64decode(blob.get("content", "")).decode("utf-8", "replace")


def recent_checks(gh: Client, full: str, branch: str) -> set[str]:
    """Check names that reported on the last few merged PRs into the default branch. Only these
    can be required: a check that doesn't report on every PR holds it forever."""
    prs = gh.get(f"/repos/{full}/pulls?state=closed&base={branch}&sort=updated&direction=desc"
                 "&per_page=20") or []
    names = set()
    for pr in [p for p in prs if p.get("merged_at")][:RECENT_PRS]:
        runs = gh.get(f"/repos/{full}/commits/{pr['head']['sha']}/check-runs?per_page=100") or {}
        names |= {r.get("name") for r in runs.get("check_runs", [])}
    return names


def ruleset_for_default(gh: Client, full: str, branch: str) -> dict | None:
    """The first active ruleset of this repo that targets the default branch, read in full."""
    for rs in gh.get(f"/repos/{full}/rulesets?includes_parents=false") or []:
        full_rs = gh.get(f"/repos/{full}/rulesets/{rs['id']}") or {}
        inc = ((full_rs.get("conditions") or {}).get("ref_name") or {}).get("include", [])
        targets = {"~DEFAULT_BRANCH", "~ALL", branch, f"refs/heads/{branch}"} & set(inc)
        if full_rs.get("enforcement") == "active" and full_rs.get("target") == "branch" and targets:
            return full_rs
    return None


def required(rs: dict) -> set[str]:
    for rule in rs.get("rules", []):
        if rule.get("type") == "required_status_checks":
            return {c.get("context") for c in rule["parameters"].get("required_status_checks", [])}
    return set()


def ruleset_problems(rs: dict | None, want: set[str], seen: set[str]) -> list[str]:
    if rs is None:
        return ["no active ruleset on the default branch"]
    out = []
    types = {r.get("type"): r for r in rs.get("rules", [])}
    if "pull_request" not in types:
        out.append("doesn't require a pull request")
    elif types["pull_request"].get("parameters", {}).get("required_approving_review_count", 0):
        out.append("requires an approving review, which a solo owner can't give")
    have = required(rs)
    if want - have:
        out.append("missing required checks: " + ", ".join(sorted(want - have)))
    if have - seen:
        out.append("requires checks that haven't reported on recent PRs (they hold every PR): "
                   + ", ".join(sorted(clean(c) for c in have - seen)))
    if not any(b.get("actor_type") == "RepositoryRole" and b.get("actor_id") == 5
               and b.get("bypass_mode") == "pull_request" for b in rs.get("bypass_actors") or []):
        out.append("admin role isn't in the bypass list for pull requests")
    return out


def audit_repo(gh: Client, repo: dict, paid: bool) -> list[dict]:
    name, full, branch = repo["name"], repo["full_name"], repo.get("default_branch") or "main"
    tree = gh.get(f"/repos/{full}/git/trees/{branch}?recursive=1")
    if not tree or not tree.get("tree"):
        return [finding(name, "empty", "empty repo: skipped", level="info")]
    blobs = {t["path"]: t["sha"] for t in tree["tree"] if t.get("type") == "blob"}
    cfg = {}
    for path in SETTINGS:
        if path in blobs:
            cfg = tomllib.loads(blob_text(gh, full, blobs[path]))
            break
    agents = blob_text(gh, full, blobs["AGENTS.md"]) if "AGENTS.md" in blobs else ""
    out = []
    claudes = [blob_text(gh, full, blobs[p]) for p in CLAUDE_MDS if p in blobs]
    if not all(s in agents for s in CHANGE_RULES):
        out.append(finding(name, "change-rules", 'AGENTS.md is missing or has no "How to make a change"',
                           "add it through a handoff issue (decision 0019)"))
    elif any(not IMPORT_LINE.search(c) and c.strip() != "AGENTS.md" for c in claudes):
        out.append(finding(name, "change-rules", "CLAUDE.md doesn't import AGENTS.md, so Claude Code skips it",
                           "make CLAUDE.md the one line @AGENTS.md (decision 0019)"))
    if not cfg and "0014" not in agents:
        return [finding(name, "adopted", "not on the conventions yet",
                        "adopt through a handoff issue in that repo", level="info"), *out]
    if "0014" not in agents:
        out.append(finding(name, "agents-md", "AGENTS.md is missing or doesn't name decision 0014",
                           "add the conventions line through a handoff issue"))
    have_auto = [p for p in AUTO_MERGE_FILES if p in blobs]
    if len(have_auto) == 1:
        out.append(finding(name, "auto-merge-pair", f"has {have_auto[0]} without its pair",
                           "copy both files together"))
    labels = {"handoff", "handoff-proposed"}
    if have_auto:
        labels.add("no-auto-merge")
    if CAPTURE_WORKFLOW in blobs:
        labels.add("no-kb")
    present = {lb["name"] for lb in gh.get_all(f"/repos/{full}/labels")}
    if labels - present:
        missing = sorted(labels - present)
        out.append(finding(name, "labels", "missing labels: " + ", ".join(missing),
                           "--fix creates them", data=missing))
    seen = recent_checks(gh, full, branch)
    head = gh.get(f"/repos/{full}/commits/{branch}/check-runs?per_page=100") or {}
    if "gitleaks" not in seen | {r.get("name") for r in head.get("check_runs", [])}:
        out.append(finding(name, "gitleaks", "no gitleaks check on recent PRs or the default branch",
                           "copy the secrets workflow through a handoff issue"))
    for path in COPIED:
        mine = local_blob(path)
        if path in blobs and mine and blobs[path] != mine:
            out.append(finding(name, f"template:{path}", f"{path} differs from the template copy",
                               "update it through a handoff issue if the change wasn't on purpose",
                               level="info"))

    on = str(cfg.get("auto_merge", "off")).strip().lower() == "on"
    if repo.get("private") and not paid:
        if on:
            out.append(finding(name, "auto-merge-setting",
                               'auto_merge = "on", but GitHub Free has no auto-merge or rulesets '
                               "on private repos", 'set auto_merge = "off" (or move to GitHub Pro)'))
        return out
    if on and repo.get("allow_auto_merge") is False:
        out.append(finding(name, "auto-merge-setting", '"Allow auto-merge" is off',
                           "--fix turns it on"))
    want = {c for c in KNOWN_CHECKS if c in seen}
    problems = ruleset_problems(ruleset_for_default(gh, full, branch), want, seen)
    if problems:
        out.append(finding(name, "ruleset", "; ".join(problems),
                           "--fix creates or extends the ruleset" if on else
                           'needed before auto_merge goes "on"', level="drift" if on else "info"))
    prot = gh.get(f"/repos/{full}/branches/{branch}/protection") or {}
    reviews = (prot.get("required_pull_request_reviews") or {}).get("required_approving_review_count")
    if reviews:
        out.append(finding(name, "branch-protection",
                           f"classic branch protection requires {reviews} approving review(s)",
                           "remove it in Settings > Branches (a solo owner can't approve)"))
    if not repo.get("private"):
        sa = (repo.get("security_and_analysis") or {}).get("secret_scanning_push_protection")
        if sa is None:
            out.append(finding(name, "push-protection", "couldn't read push protection",
                               "run with the owner's own login", level="info"))
        elif sa.get("status") != "enabled":
            out.append(finding(name, "push-protection", "secret scanning push protection is off",
                               "--fix turns it on"))
    return out


def patch_repo(gh: Client, full: str, body: dict):
    if not body or set(body) - PATCH_KEYS:
        raise ValueError(f"refusing to PATCH {sorted(body)}")
    return gh.call("PATCH", f"/repos/{full}", body)


def new_ruleset(checks: set[str]) -> dict:
    return {
        "name": "conventions", "target": "branch", "enforcement": "active",
        "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}},
        "rules": [
            {"type": "pull_request", "parameters": {
                "required_approving_review_count": 0, "dismiss_stale_reviews_on_push": False,
                "require_code_owner_review": False, "require_last_push_approval": False,
                "required_review_thread_resolution": False}},
            {"type": "required_status_checks", "parameters": {
                "strict_required_status_checks_policy": False,
                "required_status_checks": [{"context": c} for c in sorted(checks)]}},
        ],
        "bypass_actors": [ADMIN_BYPASS],
    }


def extended_ruleset(rs: dict, checks: set[str]) -> dict:
    """The ruleset as read, with missing checks and the admin bypass appended. Nothing removed."""
    body = {k: json.loads(json.dumps(rs[k])) for k in RULESET_KEYS if k in rs}
    rules = body.setdefault("rules", [])
    rsc = next((r for r in rules if r.get("type") == "required_status_checks"), None)
    if rsc is None:
        rsc = {"type": "required_status_checks", "parameters": {
            "strict_required_status_checks_policy": False, "required_status_checks": []}}
        rules.append(rsc)
    listed = rsc["parameters"].setdefault("required_status_checks", [])
    for c in sorted(checks - {x.get("context") for x in listed}):
        listed.append({"context": c})
    if not any(r.get("type") == "pull_request" for r in rules):
        rules.append(new_ruleset(set())["rules"][0])
    bypass = body.setdefault("bypass_actors", [])
    if not any(b.get("actor_type") == "RepositoryRole" and b.get("actor_id") == 5
               and b.get("bypass_mode") == "pull_request" for b in bypass):
        bypass.append(dict(ADMIN_BYPASS))
    return body


def apply_fix(gh: Client, repo: dict, f: dict) -> str:
    full, branch = repo["full_name"], repo.get("default_branch") or "main"
    if f["check"] == "auto-merge-setting":
        if repo.get("private") and f["text"].startswith('auto_merge = "on"'):
            return "not fixed: change the repo's settings file through a PR"
        patch_repo(gh, full, {"allow_auto_merge": True})
        return 'turned on "Allow auto-merge"'
    if f["check"] == "push-protection":
        patch_repo(gh, full, {"security_and_analysis": {
            "secret_scanning": {"status": "enabled"},
            "secret_scanning_push_protection": {"status": "enabled"}}})
        return "turned on push protection"
    if f["check"] == "labels":
        missing = f["data"]
        for lb in missing:
            color, desc = LABELS[lb]
            gh.call("POST", f"/repos/{full}/labels", {"name": lb, "color": color, "description": desc})
        return "created " + ", ".join(missing)
    if f["check"] == "ruleset":
        if f["level"] != "drift":
            return 'not fixed: turn auto_merge "on" in the order decision 0014 gives'
        if "requires an approving review" in f["text"]:
            return "not fixed: lower the required reviews to 0 in the ruleset by hand"
        seen = recent_checks(gh, full, branch)
        checks = {c for c in KNOWN_CHECKS if c in seen}
        rs = ruleset_for_default(gh, full, branch)
        if rs is None:
            gh.call("POST", f"/repos/{full}/rulesets", new_ruleset(checks))
            return "created ruleset 'conventions' requiring " + ", ".join(sorted(checks))
        gh.call("PUT", f"/repos/{full}/rulesets/{rs['id']}", extended_ruleset(rs, checks))
        return f"extended ruleset {clean(rs.get('name'))}"
    return "not fixable here"


def owned_repos(gh: Client, user: dict, only: set[str], skip: set[str]) -> list[dict]:
    login = user["login"].lower()
    repos = [r for r in gh.get_all("/user/repos?affiliation=owner&sort=full_name")
             if r["owner"]["login"].lower() == login]
    total = (user.get("public_repos") or 0) + (user.get("owned_private_repos") or 0)
    if total and len(repos) < total:
        print(f"Warning: the token sees {len(repos)} of {total} owned repos.", file=sys.stderr)
    keep = []
    for r in sorted(repos, key=lambda r: r["name"].lower()):
        if r.get("archived") or r.get("fork") or SKIP_TOPIC in (r.get("topics") or []):
            continue
        if (only and r["name"] not in only) or r["name"] in skip:
            continue
        keep.append(r)
    return keep


def report(results: list[tuple[dict, list[dict]]], summary: bool) -> str:
    lines, private_n = ["# Repo conventions audit", ""], 0
    counts: dict[str, int] = {}
    for repo, found in results:
        label = repo["name"]
        if repo.get("private"):
            private_n += 1
            label = f"private-{private_n}" if summary else f"{repo['name']} (private-{private_n})"
        drift = [f for f in found if f["level"] == "drift"]
        for f in drift:
            counts[f["check"]] = counts.get(f["check"], 0) + 1
        if summary:
            lines.append(f"- {label}: {len(drift)} drift, {len(found) - len(drift)} info")
            continue
        lines.append(f"## {label}" + ("" if found else ": clean"))
        for f in found:
            mark = "DRIFT" if f["level"] == "drift" else "info"
            lines.append(f"- {mark} `{f['id']}`: {f['text']}" + (f" ({f['fix']})" if f["fix"] else ""))
        lines.append("")
    lines += ["", "Drift by check: " + (", ".join(f"{k} {v}" for k, v in sorted(counts.items()))
                                       or "none")]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--owner", help="refuse to run unless the token belongs to this login")
    ap.add_argument("--only", default="", help="comma-separated repo names to audit")
    ap.add_argument("--skip", default="", help="comma-separated repo names to leave out")
    ap.add_argument("--summary", action="store_true", help="counts only, private repos unnamed")
    ap.add_argument("--fix", default="", help="comma-separated finding ids to fix")
    args = ap.parse_args(argv)
    gh = Client(token_from_env())
    try:
        user = gh.get("/user")
        if args.owner and user["login"].lower() != args.owner.lower():
            raise SystemExit(f"The token belongs to {user['login']}, not {args.owner}.")
        fix_ids = {i.strip() for i in args.fix.split(",") if i.strip()}
        # Classic tokens list their scopes; fine-grained ones send none and fail per call instead.
        if fix_ids and gh.scopes and "repo" not in [s.strip() for s in gh.scopes.split(",")]:
            raise SystemExit("--fix needs the owner's `gh auth login -w` token (repo scope).")
        plan = (user.get("plan") or {}).get("name")
        if not plan:
            print("Warning: couldn't read the account's plan; assuming GitHub Free.", file=sys.stderr)
        paid = (plan or "free").lower() != "free"
        only = {s for s in args.only.split(",") if s} | {i.split("/")[0] for i in fix_ids}
        repos = owned_repos(gh, user, only, {s for s in args.skip.split(",") if s})
        results = [(r, audit_repo(gh, r, paid)) for r in repos]
    except ApiError as e:
        print(f"GitHub API error: {e}", file=sys.stderr)
        return 2
    if fix_ids:
        by_id = {f["id"]: (r, f) for r, found in results for f in found}
        for fid in sorted(fix_ids):
            if fid not in by_id:
                print(f"{fid}: no such finding in this run")
            elif by_id[fid][1]["check"] not in FIXABLE:
                print(f"{fid}: not fixable here ({by_id[fid][1]['fix']})")
            else:
                try:
                    print(f"{fid}: {apply_fix(gh, *by_id[fid])}")
                except ApiError as e:
                    print(f"{fid}: failed: {e}")
        return 0
    print(report(results, args.summary), end="")
    return 1 if any(f["level"] == "drift" for _, found in results for f in found) else 0


if __name__ == "__main__":
    sys.exit(main())
