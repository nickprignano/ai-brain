#!/usr/bin/env python3
"""Turn an accepted KB feedback, known-error, nomination or digest issue into a change to the KB.

Run by .github/workflows/kb-feedback.yml when a maintainer labels an issue kb-accepted. It reads
the issue form, appends a field report (kb-feedback), a known error (kb-known-error) or an expert
nomination (kb-source, to experts.yaml as status nominated, for a maintainer to score), or adds a
weekly digest's ticked items to the pages they belong on (kb-digest), and writes the branch name,
PR title, PR body and any PR labels for the workflow to open a pull request.

    python3 scripts/kb/feedback.py --event "$GITHUB_EVENT_PATH"
    python3 scripts/kb/feedback.py --issue-json issue.json      # {"number", "title", "body", "labels"}

Issue text is untrusted: it's only parsed into fields, written as YAML data, then checked by
validate.py and reviewed in the pull request. Nothing from it is executed.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kblib  # noqa: E402
from kblib import KB_DIR  # noqa: E402

OUTCOMES = {
    "Worked as described": "worked",
    "Broke or gave the wrong result": "broke",
    "Outdated (something changed upstream)": "outdated",
    "Missing (the KB should cover this)": "missing",
}
MAX_FIELD = 2000
# A digest heading names its source and, when the source has one, the page its items belong on.
DIGEST_HEADING = re.compile(r"^### (.+?)(?: → `docs/knowledge/([^`]+)`)?\s*$")
DIGEST_SECTION = "## From the digest"


class FeedbackError(Exception):
    pass


def parse_form(body: str) -> dict[str, str]:
    """Parse a rendered GitHub issue form ("### Label" headings followed by the answer)."""
    fields: dict[str, str] = {}
    parts = re.split(r"^### (.+?)\s*$", body.replace("\r\n", "\n"), flags=re.M)
    for label, value in zip(parts[1::2], parts[2::2]):
        value = value.strip()
        fields[label.strip()] = "" if value == "_No response_" else value
    return fields


def clean(value: str, field: str, required: bool = True) -> str:
    value = value.strip()
    if required and not value:
        raise FeedbackError(f"'{field}' is empty")
    if len(value) > MAX_FIELD:
        raise FeedbackError(f"'{field}' is longer than {MAX_FIELD} characters")
    return value


def kb_target(value: str, field: str, allow_url: bool = False) -> str:
    """Normalise a KB path (or URL) and check it exists."""
    value = value.strip().strip("`")
    if allow_url and value.startswith("https://"):
        return value
    value = value.removeprefix("/").removeprefix("docs/knowledge/")
    if not (KB_DIR / value.split("#")[0]).is_file():
        raise FeedbackError(f"'{field}' must be an existing path under docs/knowledge/"
                            + (" or an https:// link" if allow_url else "") + f", got {value!r}")
    return value


def public_safe(fields: dict[str, str]) -> None:
    if not re.search(r"^- \[[xX]\]", fields.get("Public-safe", ""), re.M):
        raise FeedbackError("the public-safe box isn't ticked")


def slug(text: str) -> str:
    text = re.sub(r"[^a-z0-9]+", "-", text.lower().replace("`", "")).strip("-")
    return text[:50].rstrip("-") or "entry"


def add_field_report(issue: dict, fields: dict[str, str], today: str) -> tuple[str, str]:
    outcome = OUTCOMES.get(fields.get("Outcome", ""))
    if not outcome:
        raise FeedbackError(f"unknown outcome {fields.get('Outcome')!r}")
    report = {
        "date": today,
        "page": kb_target(fields.get("Page", ""), "Page"),
        "outcome": outcome,
        "summary": clean(fields.get("What happened", ""), "What happened"),
        "versions": clean(fields.get("Versions", ""), "Versions", required=False),
        "evidence": clean(fields.get("Evidence", ""), "Evidence", required=False),
        "issue": issue["number"],
    }
    report = {k: v for k, v in report.items() if v != ""}
    data = kblib.load_yaml(kblib.FIELD_REPORTS) or {"reports": []}
    if any(r.get("issue") == issue["number"] for r in data["reports"]):
        raise FeedbackError(f"issue #{issue['number']} is already in field-reports.yaml")
    data["reports"].append(report)
    write(kblib.FIELD_REPORTS, data)
    title = f"KB field report: {outcome} on {report['page']} (#{issue['number']})"
    todo = ("Update the page to match, then set the report's `resolved: true`."
            if outcome in ("broke", "outdated", "missing") else
            "If this confirms a claim marked *unverified*, update the page and its `status`.")
    return title, f"Adds a field report from #{issue['number']} to `docs/knowledge/field-reports.yaml`.\n\n{todo}"


def add_known_error(issue: dict, fields: dict[str, str], today: str) -> tuple[str, str]:
    symptom = clean(fields.get("Symptom", ""), "Symptom")
    data = kblib.load_yaml(kblib.KNOWN_ERRORS) or {"errors": []}
    if any(e.get("issue") == issue["number"] for e in data["errors"]):
        raise FeedbackError(f"issue #{issue['number']} is already in known-errors.yaml")
    ids = {e["id"] for e in data["errors"]}
    entry_id = slug(symptom)
    if entry_id in ids:
        entry_id = f"{entry_id}-{issue['number']}"
    entry = {
        "id": entry_id,
        "symptom": symptom,
        "cause": clean(fields.get("Cause", ""), "Cause"),
        "fix": clean(fields.get("Fix", ""), "Fix"),
        "source": kb_target(fields.get("Source", ""), "Source", allow_url=True),
        "applies_to": clean(fields.get("Versions", ""), "Versions", required=False),
        "status": "verified" if fields.get("Confidence", "").startswith("Fix confirmed") else "unverified",
        "added": today,
        "issue": issue["number"],
    }
    data["errors"].append({k: v for k, v in entry.items() if v != ""})
    write(kblib.KNOWN_ERRORS, data)
    return (f"Known error: {symptom[:60]} (#{issue['number']})",
            f"Adds known error `{entry_id}` from #{issue['number']} to "
            "`docs/knowledge/troubleshooting/known-errors.yaml` and regenerates the catalog page.")


def https_or_empty(value: str, field: str) -> str:
    value = clean(value, field, required=False)
    if value and not value.startswith("https://"):
        raise FeedbackError(f"'{field}' must be an https:// link")
    return value


def add_nomination(issue: dict, fields: dict[str, str], today: str) -> tuple[str, str]:
    name = clean(fields.get("Name", ""), "Name")
    if len(name) > 80:
        raise FeedbackError("'Name' is longer than 80 characters")
    links = {
        "blog": https_or_empty(fields.get("Blog", ""), "Blog"),
        "youtube": https_or_empty(fields.get("YouTube channel", ""), "YouTube channel"),
        "github": clean(fields.get("GitHub username", ""), "GitHub username", required=False).lstrip("@"),
    }
    if links["github"] and not re.fullmatch(r"[A-Za-z0-9-]{1,39}", links["github"]):
        raise FeedbackError("'GitHub username' isn't a valid GitHub username")
    links = {k: v for k, v in links.items() if v}
    if not links:
        raise FeedbackError("give at least one of Blog, YouTube channel or GitHub username")
    data = kblib.load_yaml(kblib.EXPERTS)
    if any(e.get("issue") == issue["number"] for e in data["experts"]):
        raise FeedbackError(f"issue #{issue['number']} is already in experts.yaml")
    ids = {e["id"] for e in data["experts"]}
    entry_id = slug(name)
    if entry_id in ids:
        raise FeedbackError(f"{name} is already in experts.yaml as '{entry_id}'")
    data["experts"].append({
        "id": entry_id,
        "name": name,
        "affiliation": "unknown",
        "status": "nominated",
        "found_via": [f"nomination (#{issue['number']}, {today})"],
        "links": links,
        "notes": clean(fields.get("Why follow them", ""), "Why follow them")[:300],
        "issue": issue["number"],
    })
    write(kblib.EXPERTS, data)
    return (f"KB source nomination: {name} (#{issue['number']})",
            f"Adds {name} to `docs/knowledge/experts.yaml` as nominated, from #{issue['number']}.\n\n"
            "Before merging, score them with the method in `docs/knowledge/experts.md`: add `gates`, "
            "`scores`, `reviewed` and evidence, set the status the scores give, and add a source to "
            "`sources.toml` with `expert = \"" + entry_id + "\"` if they're tracked. Or merge as is and the "
            "freshness check will list them as waiting.")


def parse_digest_item(line: str) -> tuple[str, str, str]:
    """Split a rendered digest line "[title](url) · date (note)" into (title, url, date).

    Feed titles can hold "](" or ")" themselves, so split on the last "](" and the last " · ".
    """
    head, sep, tail = line.rpartition(" · ")
    when = tail.split(" ", 1)[0]
    cut = head.rfind("](")
    if not sep or cut < 1 or not head.startswith("[") or not head.endswith(")") \
            or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", when):
        raise FeedbackError(f"can't read the ticked line {line[:120]!r}")
    title, url = head[1:cut], head[cut + 2:-1]
    if not re.fullmatch(r"https://[^\s<>\"]+", url):
        raise FeedbackError(f"the ticked line {line[:120]!r} has no https:// link")
    title = re.sub(r"([\[\]])", r"\\\1", " ".join(title.split()))
    return title, url, when


def ticked_digest_items(body: str) -> dict[str, list[tuple[str, str, str]]]:
    """Ticked items per target page (relative to docs/knowledge/), in digest order."""
    picks: dict[str, list[tuple[str, str, str]]] = {}
    source = page = None
    for line in body.replace("\r\n", "\n").splitlines():
        if m := DIGEST_HEADING.match(line):
            source, page = m.group(1), m.group(2)
        elif m := re.match(r"^- \[[xX]\] (.*)$", line):
            if source is None:
                raise FeedbackError("a ticked item comes before any source heading")
            if page is None:
                raise FeedbackError(f"no page named for {source}; add kb_page to it in sources.toml")
            target = kb_target(page, f"page for {source}")
            if not (KB_DIR / target).resolve().is_relative_to(KB_DIR.resolve()):
                raise FeedbackError(f"page for {source} is outside docs/knowledge/")
            picks.setdefault(target, []).append(parse_digest_item(m.group(1).strip()))
    if not picks:
        raise FeedbackError("no items are ticked; tick the ones worth adding, then re-add kb-accepted")
    return picks


def add_to_section(text: str, lines: list[str]) -> str:
    """Append lines to the page's "From the digest" section, creating it at the end if missing."""
    rows = text.rstrip("\n").split("\n")
    if DIGEST_SECTION in rows:
        end = rows.index(DIGEST_SECTION) + 1
        while end < len(rows) and not rows[end].startswith("## "):
            end += 1
        while rows[end - 1] == "":
            end -= 1
        rows[end:end] = lines
    else:
        rows += ["", DIGEST_SECTION, "",
                 "Picked from the weekly digest; fold each into the page's own text, then delete it.", ""]
        rows += lines
    return "\n".join(rows) + "\n"


def add_digest_picks(issue: dict, body: str) -> tuple[str, str]:
    added: dict[str, int] = {}
    skipped = []
    for page, items in ticked_digest_items(body).items():
        path = KB_DIR / page
        text = path.read_text(encoding="utf-8")
        lines = []
        for title, url, when in items:
            if url in text or any(url in ln for ln in lines):
                skipped.append(url)
                continue
            lines.append(f"- [{title}]({url}) ({when}, #{issue['number']})")
        if lines:
            path.write_text(add_to_section(text, lines), encoding="utf-8")
            added[page] = len(lines)
    if not added:
        raise FeedbackError("every ticked item is already linked from its page")
    summary = "\n".join(f"- `docs/knowledge/{p}`: {n} item(s)" for p, n in added.items())
    note = f"\n\nAlready on the page, skipped: {len(skipped)}." if skipped else ""
    return (f"KB digest picks from #{issue['number']}",
            f"Adds the items ticked in #{issue['number']} to the pages their sources name:\n\n{summary}{note}\n\n"
            "Before merging, fold each item into the page's own text (the fact, version or fix, not a "
            "link dump), delete the line, and set `last_reviewed` on pages you re-checked. This PR is "
            "labelled `no-auto-merge` for that reason. Another digest PR open at the same time may "
            "touch the same section.")


def write(path: Path, data) -> None:
    path.write_text(kblib.yaml_header(path) + kblib.dump_yaml(data), encoding="utf-8")


def handle(issue: dict, today: str) -> tuple[str, str]:
    labels = {lbl["name"] if isinstance(lbl, dict) else lbl for lbl in issue.get("labels", [])}
    if "kb-digest" in labels:
        # The curator writes digests: there's no form and no public-safe box, and the items are
        # links the curator already published in this repo's issue.
        return add_digest_picks(issue, issue.get("body") or "")
    fields = parse_form(issue.get("body") or "")
    public_safe(fields)
    if "kb-known-error" in labels:
        return add_known_error(issue, fields, today)
    if "kb-source" in labels:
        return add_nomination(issue, fields, today)
    if "kb-feedback" in labels:
        return add_field_report(issue, fields, today)
    raise FeedbackError("the issue has none of the kb-feedback, kb-known-error, kb-source or kb-digest labels")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--event", help="GitHub event payload (issues event)")
    src.add_argument("--issue-json", help="a JSON file with number, title, body and labels")
    ap.add_argument("--body-file", default="pr-body.md", help="where to write the PR body")
    args = ap.parse_args()

    if args.event:
        issue = json.loads(Path(args.event).read_text(encoding="utf-8"))["issue"]
    else:
        issue = json.loads(Path(args.issue_json).read_text(encoding="utf-8"))

    try:
        title, body = handle(issue, date.today().isoformat())
    except FeedbackError as e:
        print(f"::error::Issue #{issue.get('number')}: {e}")
        Path("feedback-error.txt").write_text(str(e), encoding="utf-8")
        return 1

    body += f"\n\nCloses #{issue['number']}.\n"
    Path(args.body_file).write_text(body, encoding="utf-8")
    if gh_out := os.environ.get("GITHUB_OUTPUT"):
        with open(gh_out, "a", encoding="utf-8") as f:
            f.write(f"branch=kb-feedback/issue-{issue['number']}\n")
            f.write("title=" + " ".join(title.split()) + "\n")
            f.write("labels=" + ("no-auto-merge" if title.startswith("KB digest picks") else "") + "\n")
    print(title)
    return 0


if __name__ == "__main__":
    sys.exit(main())
