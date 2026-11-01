#!/usr/bin/env python3
"""Regenerate index.json from the skill directories in this repository.

Every top-level directory containing SKILL.md is one catalog entry. The
`version` field is a short content hash, so it changes automatically whenever
any file in the skill changes, and clients never serve a stale copy.

Usage:
    python build_catalog.py [--base-url URL] [--check]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKIP = {".git", ".github", "__pycache__", ".venv", "node_modules"}


def skill_dirs() -> list[Path]:
    found = []
    for path in sorted(ROOT.iterdir()):
        if not path.is_dir() or path.name in SKIP or path.name.startswith("."):
            continue
        if (path / "SKILL.md").is_file():
            found.append(path)
    return found


def files_of(directory: Path) -> list[str]:
    files = []
    for path in sorted(directory.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(directory)
        if any(part in SKIP for part in rel.parts):
            continue
        files.append(rel.as_posix())
    return files


def content_version(directory: Path, files: list[str]) -> str:
    digest = hashlib.sha256()
    for name in files:
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        digest.update((directory / name).read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()[:12]


def build() -> dict:
    entries = []
    for directory in skill_dirs():
        files = files_of(directory)
        entries.append(
            {
                "name": directory.name,
                "version": content_version(directory, files),
                "files": files,
            }
        )
    return {"skills": entries}


def main() -> int:
    parser = argparse.ArgumentParser(description="Rebuild index.json from skill directories.")
    parser.add_argument("--base-url", default="", help="documentation only; not stored in index.json")
    parser.add_argument("--check", action="store_true", help="fail if index.json is out of date")
    args = parser.parse_args()

    catalog = build()
    rendered = json.dumps(catalog, indent=2) + "\n"
    target = ROOT / "index.json"

    if args.check:
        current = target.read_text(encoding="utf-8") if target.exists() else ""
        if current != rendered:
            print("index.json is out of date; run python build_catalog.py")
            return 1
        print(f"index.json is current ({len(catalog['skills'])} skills)")
        return 0

    target.write_text(rendered, encoding="utf-8")
    print(f"wrote {target} with {len(catalog['skills'])} skills")
    for entry in catalog["skills"]:
        print(f"  {entry['name']:28} v{entry['version']}  ({len(entry['files'])} files)")

    if args.base_url:
        print(f"\ncatalog base URL: {args.base_url.rstrip('/')}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
