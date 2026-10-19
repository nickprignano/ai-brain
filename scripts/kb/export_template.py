"""Export this KB's machinery as the 2ndbrain template, following template/manifest.toml.

    python3 scripts/kb/export_template.py OUT_DIR

Copies the manifest's `include` paths, overlays the skeleton, applies each `replace` (one that no
longer matches fails the export, so a changed source line can't drift silently), regenerates the
skeleton's indexes and llms.txt with the exported build.py, and fails if any file still contains a
`forbid` string or the private layer (notes/, outbox/) holds anything but its empty templates. The template repo runs this on a checkout of this repo and opens a PR in itself.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "template" / "manifest.toml"


class ExportError(Exception):
    pass


def load_manifest(path: Path = MANIFEST) -> dict:
    with path.open("rb") as f:
        return tomllib.load(f)


def copy_included(manifest: dict, out: Path) -> None:
    exclude = {ROOT / e for e in manifest.get("exclude", [])}
    for pattern in manifest["include"]:
        matches = sorted(p for p in ROOT.glob(pattern) if p.is_file() and p not in exclude)
        if not matches:
            raise ExportError(f"include {pattern!r} matches nothing")
        for src in matches:
            dst = out / src.relative_to(ROOT)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)


def overlay_skeleton(manifest: dict, out: Path) -> None:
    skeleton = ROOT / manifest["skeleton"]
    for src in sorted(p for p in skeleton.rglob("*") if p.is_file()):
        dst = out / src.relative_to(skeleton)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def apply_replacements(manifest: dict, out: Path) -> None:
    for r in manifest.get("replace", []):
        path = out / r["file"]
        text = path.read_text(encoding="utf-8")
        found = text.count(r["find"])
        want = r.get("count", 1)
        if found != want:
            raise ExportError(f"{r['file']}: expected {want} match(es) of {r['find'][:60]!r}, found {found}")
        path.write_text(text.replace(r["find"], r["replace"]), encoding="utf-8")


def check_forbidden(manifest: dict, out: Path) -> None:
    exempt = set(manifest.get("forbid_exempt", []))
    hits = []
    for path in sorted(p for p in out.rglob("*") if p.is_file()):
        rel = path.relative_to(out).as_posix()
        if rel in exempt or "__pycache__" in rel:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        hits += [f"{rel}: {word!r}" for word in manifest["forbid"] if word in text]
    if hits:
        raise ExportError("content leaked into the template:\n  " + "\n  ".join(hits))


def check_private_layer_empty(out: Path) -> None:
    """The template's private layer ships empty: only `_template.md` files and the capture rules,
    index (with no entries) and instructions. Anything else would be someone's note."""
    notes, outbox = out / "notes", out / "outbox"
    hits = [p for p in sorted(notes.glob("*/**/*")) if p.is_file() and p.name != "_template.md"]
    hits += [p for p in sorted(outbox.glob("*")) if p.is_file() and p.name != "README.md"]
    index = notes / "index.md"
    if index.exists() and any(line.lstrip().startswith(("- ", "* ")) for line in index.read_text().splitlines()):
        hits.append(index)
    if hits:
        raise ExportError("the private layer must ship empty:\n  " + "\n  ".join(p.relative_to(out).as_posix() for p in hits))


def build(out: Path) -> None:
    result = subprocess.run([sys.executable, "scripts/kb/build.py"], cwd=out, capture_output=True, text=True)
    if result.returncode != 0:
        raise ExportError(f"build.py failed in the export:\n{result.stdout}{result.stderr}")


def export(out: Path, manifest: dict | None = None) -> None:
    manifest = manifest or load_manifest()
    if out.exists() and any(p.name != ".git" for p in out.iterdir()):
        # Keep the template repo's .git; replace everything else so removed files disappear too.
        for p in out.iterdir():
            if p.name == ".git":
                continue
            shutil.rmtree(p) if p.is_dir() else p.unlink()
    out.mkdir(parents=True, exist_ok=True)
    copy_included(manifest, out)
    overlay_skeleton(manifest, out)
    apply_replacements(manifest, out)
    build(out)
    for cache in out.rglob("__pycache__"):
        shutil.rmtree(cache)
    check_forbidden(manifest, out)
    check_private_layer_empty(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out", type=Path, help="directory to write the template into (a checkout of the template repo)")
    args = ap.parse_args()
    try:
        export(args.out.resolve())
    except ExportError as e:
        print(f"::error::{e}")
        return 1
    print(f"exported the template to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
