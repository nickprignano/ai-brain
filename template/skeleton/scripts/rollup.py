"""Write the weekly roll-up from the public hub knowledge base, as Markdown on stdout.

    GITHUB_TOKEN=... python3 scripts/rollup.py [--days 8] [--monthly]

Reads only the public hub named in hub.toml: its recent kb-digest and kb-freshness issues, and recent
commits to its decisions folder, field reports and known errors. With --monthly it also appends
the output of this repo's own scripts/stale_check.py. Nothing is sent anywhere; the workflow posts the output as an
issue in this repo. The token is optional (the hub is public) and only raises the rate limit.
Self-contained on purpose: the same file runs in every private layer built from this kit.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tomllib
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SETTINGS = ROOT / "hub.toml"
API = "https://api.github.com"


def stale_report() -> str:
    run = subprocess.run([sys.executable, str(ROOT / "scripts" / "stale_check.py")],
                         capture_output=True, text=True, cwd=ROOT)
    return (run.stdout + run.stderr).strip()


def get(path: str, params: dict | None = None) -> list | dict:
    url = f"{API}{path}" + (f"?{urllib.parse.urlencode(params)}" if params else "")
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "private-layer-rollup"}
    if os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as r:
        return json.load(r)


def issues(repo: str, label: str, since: str) -> list[str]:
    found = get(f"/repos/{repo}/issues", {"labels": label, "state": "all", "since": since, "per_page": 20})
    return [f"- [ ] [{i['title']}]({i['html_url']})" for i in found if "pull_request" not in i]


def commits(repo: str, path: str, since: str) -> list[str]:
    found = get(f"/repos/{repo}/commits", {"path": path, "since": since, "per_page": 20})
    return [f"- [ ] [{c['commit']['message'].splitlines()[0]}]({c['html_url']})" for c in found]


def render(cfg: dict, days: int, monthly: bool, fetch=None, stale=None) -> str:
    repo, kb = cfg["hub_repo"], cfg.get("hub_kb_path", "docs/knowledge").strip("/")
    since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    fetch = fetch or {"issues": issues, "commits": commits}
    sections = [
        ("Weekly digest", fetch["issues"](repo, "kb-digest", since)),
        ("Freshness", fetch["issues"](repo, "kb-freshness", since)),
        ("Decisions", fetch["commits"](repo, f"{kb}/decisions", since)),
        ("Field reports", fetch["commits"](repo, f"{kb}/field-reports.yaml", since)),
        ("Known errors", fetch["commits"](repo, f"{kb}/troubleshooting/known-errors.yaml", since)),
    ]
    out = [f"From the hub, the last {days} days. Tick an item that's worth a pattern note.", ""]
    for title, items in sections:
        out += [f"## {title}", "", *(items or ["Nothing new."]), ""]
    if monthly:
        out += ["## This repo's notes", "", "```", (stale or stale_report)(), "```", ""]
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--days", type=int, default=8)
    ap.add_argument("--monthly", action="store_true", help="also list this repo's stale notes")
    args = ap.parse_args()
    with SETTINGS.open("rb") as f:
        cfg = tomllib.load(f)
    if cfg["hub_repo"].startswith("<"):
        print("Set hub_repo in hub.toml first.", file=sys.stderr)
        return 1
    print(render(cfg, args.days, args.monthly))
    return 0


if __name__ == "__main__":
    sys.exit(main())
