#!/usr/bin/env python3
"""Write or verify a run manifest for a reproducible analysis.

Usage:
    python run_manifest.py --root . --out run_manifest.json \
        --inputs data/raw --outputs outputs --seed 20261102

    python run_manifest.py --root . --check run_manifest.json

The manifest records the environment, git commit, seeds, and content hashes of
inputs and outputs. `--check` re-hashes the current tree and reports any
difference, which is how you prove a rebuild is reproducible.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", ".ipynb_checkpoints", "node_modules", ".mypy_cache"}

PACKAGES = [
    "geopandas", "shapely", "pyproj", "pyogrio", "rasterio",
    "numpy", "pandas", "scipy", "matplotlib",
    "libpysal", "esda", "spreg", "mgwr", "scikit-gstat", "pykrige", "gstools",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def walk(root: Path, targets: list[str]) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for target in targets:
        base = (root / target).resolve()
        if not base.exists():
            continue
        if base.is_file():
            hashes[base.relative_to(root).as_posix()] = sha256(base)
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file():
                continue
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            hashes[path.relative_to(root).as_posix()] = sha256(path)
    return dict(sorted(hashes.items()))


def git_commit(root: Path) -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return out.stdout.strip() if out.returncode == 0 else ""


def package_versions() -> dict[str, str]:
    from importlib import metadata

    versions = {}
    for name in PACKAGES:
        try:
            versions[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            continue
    return versions


def build_manifest(root: Path, inputs: list[str], outputs: list[str], seeds: dict) -> dict:
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "git_commit": git_commit(root),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "seeds": seeds,
        "inputs": walk(root, inputs),
        "outputs": walk(root, outputs),
        "packages": package_versions(),
    }


def check(root: Path, manifest_path: Path) -> int:
    previous = json.loads(manifest_path.read_text(encoding="utf-8"))
    problems = 0
    for section in ("inputs", "outputs"):
        recorded = previous.get(section, {})
        current = walk(root, list({str(Path(p).parent) for p in recorded}) or [])
        for name, old_hash in recorded.items():
            new_hash = current.get(name)
            if new_hash is None:
                print(f"[MISSING] {section}: {name}")
                problems += 1
            elif new_hash != old_hash:
                print(f"[CHANGED] {section}: {name}")
                problems += 1
        for name in current:
            if name not in recorded:
                print(f"[NEW    ] {section}: {name}")
                problems += 1
    print(f"\n{problems} difference(s) from {manifest_path.name}")
    return 1 if problems else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Write or verify a run manifest.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--out", default="run_manifest.json")
    parser.add_argument("--check", default=None, help="verify against an existing manifest")
    parser.add_argument("--inputs", nargs="*", default=["data/raw"])
    parser.add_argument("--outputs", nargs="*", default=["outputs"])
    parser.add_argument("--seed", action="append", default=[],
                        help="NAME=VALUE, repeatable, e.g. --seed kriging=20261102")
    args = parser.parse_args()

    root = Path(args.root).resolve()

    if args.check:
        return check(root, root / args.check)

    seeds = {}
    for item in args.seed:
        if "=" not in item:
            parser.error(f"seed must be NAME=VALUE, got {item!r}")
        key, value = item.split("=", 1)
        seeds[key] = value

    manifest = build_manifest(root, args.inputs, args.outputs, seeds)
    out_path = root / args.out
    out_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"# wrote {out_path}")
    print(f"# inputs hashed:  {len(manifest['inputs'])}")
    print(f"# outputs hashed: {len(manifest['outputs'])}")
    print(f"# packages:       {len(manifest['packages'])}")
    if not manifest["git_commit"]:
        print("# note: no git commit recorded; initialise the repository before submission")
    return 0


if __name__ == "__main__":
    sys.exit(main())
