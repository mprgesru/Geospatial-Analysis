# Pipeline reference

## Layout

```
project/
├── data/
│   ├── raw/                 read-only, checksummed
│   ├── processed/           derived, disposable
│   └── checksums.sha256
├── analysis/
│   ├── plan.md
│   ├── diagnostics/
│   └── models/
├── outputs/
│   ├── tables/
│   └── figures/
├── manuscript/
├── run_all.py
├── run_manifest.json
└── requirements.txt
```

## run_all.py skeleton

```python
#!/usr/bin/env python3
"""Rebuild every table, figure and number from data/raw."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SEEDS = {"screen": 20261102, "kriging": 20261102, "figures": None}

STAGES = [
    "scripts/01_audit.py",
    "scripts/02_screen.py",
    "scripts/03_model.py",
    "scripts/04_validate.py",
    "scripts/05_figures.py",
    "scripts/06_report.py",
]


def verify_raw() -> None:
    listing = ROOT / "data" / "checksums.sha256"
    for line in listing.read_text().splitlines():
        if not line.strip():
            continue
        expected, name = line.split(maxsplit=1)
        target = ROOT / "data" / "raw" / name.lstrip("*")
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual != expected:
            sys.exit(f"raw input changed: {name}")
    print("raw inputs verified")


def main() -> int:
    verify_raw()
    for stage in STAGES:
        print(f"== {stage}")
        result = subprocess.run([sys.executable, stage], cwd=ROOT)
        if result.returncode != 0:
            sys.exit(f"stage failed: {stage}")
    print(json.dumps(SEEDS, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

## Makefile equivalent

```make
.PHONY: all verify clean

all: verify
	python scripts/01_audit.py
	python scripts/02_screen.py
	python scripts/03_model.py
	python scripts/04_validate.py
	python scripts/05_figures.py
	python scripts/06_report.py

verify:
	sha256sum -c data/checksums.sha256

clean:
	rm -rf outputs analysis/diagnostics
```

## Environment pinning

Python:

```
python -m pip freeze > requirements.txt
python -m pip install -r requirements.txt
```

Prefer a lock with hashes (`uv pip compile`, `pip-tools`) and record the
platform, because GDAL-linked packages can differ across operating systems.

R:

```r
renv::init()
renv::snapshot()
```

## Determinism checklist

- [ ] One seed per stochastic stage, read from one config, not scattered.
- [ ] `PYTHONHASHSEED` set if any stage depends on set or dict order.
- [ ] No timestamps inside result tables or figures.
- [ ] Floating point formatted consistently (for example 6 decimals) at write
      time, not by the plotting library.
- [ ] No dependence on file iteration order; sort paths.
- [ ] Parallel stages write disjoint files, or reduce deterministically.
- [ ] A second run reproduces every hash in `run_manifest.json`.

## What a reviewer means by "reproducible"

1. The data are available, or the reason they are not is stated.
2. The code runs from a clean environment with one command.
3. The environment is pinned.
4. The outputs match the reported numbers.
5. The commit cited matches the code that produced the results.

Meeting four of five is not reproducibility; it is a best effort.
