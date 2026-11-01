#!/usr/bin/env python3
"""Check that the analysis artefacts required for reporting exist and pass.

Usage:
    python check_deliverables.py [--root .] [--verify-checksums]

Exit codes: 0 = all required artefacts present and no FAIL verdict,
            1 = a required artefact is missing or a verdict is FAIL,
            2 = malformed input.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REQUIRED = [
    ("analysis/plan.md", "pre-specified analysis plan"),
    ("data/audit.json", "data-contract audit"),
    ("data/dictionary.md", "data dictionary"),
    ("data/checksums.sha256", "raw-data checksums"),
    ("analysis/diagnostics/screen.md", "pre-model diagnostics"),
    ("analysis/diagnostics/model.md", "post-model diagnostics"),
    ("analysis/diagnostics/summary.json", "diagnostics verdict"),
    ("manuscript/checklist.md", "reporting checklist"),
]

OPTIONAL = [
    ("manuscript/figures.md", "figure specification"),
    ("outputs/tables", "tables directory"),
    ("outputs/figures", "figures directory"),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_checksums(root: Path) -> list[str]:
    problems: list[str] = []
    listing = root / "data" / "checksums.sha256"
    if not listing.exists():
        return ["checksums file missing"]

    for line in listing.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            problems.append(f"malformed checksum line: {line!r}")
            continue
        expected, name = parts[0], parts[1].lstrip("*")
        target = root / name
        if not target.exists():
            target = root / "data" / "raw" / Path(name).name
        if not target.exists():
            problems.append(f"missing raw file: {name}")
            continue
        actual = sha256(target)
        if actual != expected:
            problems.append(f"checksum mismatch: {name}")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description="Check reporting deliverables.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--verify-checksums", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    failures = 0

    print(f"# deliverables under {root}\n")
    for rel, label in REQUIRED:
        path = root / rel
        ok = path.exists() and (path.stat().st_size > 0 if path.is_file() else True)
        print(f"[{'OK' if ok else 'MISSING':7}] {rel:45} {label}")
        failures += 0 if ok else 1

    for rel, label in OPTIONAL:
        path = root / rel
        if path.is_dir():
            ok = any(path.iterdir())
        else:
            ok = path.exists()
        print(f"[{'OK' if ok else 'absent ':7}] {rel:45} {label} (optional)")

    summary = root / "analysis" / "diagnostics" / "summary.json"
    verdict = None
    if summary.exists():
        try:
            data = json.loads(summary.read_text(encoding="utf-8"))
            verdict = data.get("verdict")
        except json.JSONDecodeError as exc:
            print(f"\nERROR: summary.json is not valid JSON: {exc}")
            failures += 1
        else:
            print(f"\n# diagnostics verdict: {verdict!r}")
            if str(verdict).upper().startswith("FAIL"):
                print("ERROR: diagnostics verdict is FAIL; manuscript numbers are blocked.")
                failures += 1

    audit = root / "data" / "audit.json"
    if audit.exists():
        try:
            findings = json.loads(audit.read_text(encoding="utf-8")).get("findings", [])
            blocking = [f for f in findings if f.get("level") == "BLOCK"]
            if blocking:
                print(f"ERROR: {len(blocking)} blocking data-contract finding(s).")
                failures += 1
        except json.JSONDecodeError:
            print("ERROR: audit.json is not valid JSON.")
            failures += 1

    if args.verify_checksums:
        problems = verify_checksums(root)
        if problems:
            print("\n# checksum verification")
            for problem in problems:
                print(f"  ERROR: {problem}")
            failures += len(problems)
        else:
            print("\n# checksum verification: all raw files match")

    print(f"\nfailures: {failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
