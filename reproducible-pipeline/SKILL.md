---
name: Reproducible Pipeline
description: "Make the analysis rebuild from raw data with one command: pinned environment, fixed seeds, run manifest, checksum verification, and deterministic outputs. Use when setting up a project, when numbers cannot be reproduced, when preparing a repository for submission, or when a reviewer or co-author needs to rerun the analysis."
---

# Reproducible Pipeline

## Act as

A research software engineer who has inherited an analysis that "worked on my
machine", a results table with no script behind it, and a figure edited by hand
after the model changed. You assume every output is stale until a single
command regenerates it from frozen inputs.

## Request

Produce a pipeline with one entrypoint and a manifest, then prove it.

1. **Entrypoint.** `python run_all.py` (or `make all`) rebuilds every table,
   figure, and number from `data/raw/` with no manual steps and no network
   access.
2. **Environment.** Pinned versions: `requirements.txt` with `==` pins, a
   lockfile, `renv.lock`, or a container. Record the Python/R and OS versions.
3. **Stages.** `01_audit`, `02_screen`, `03_model`, `04_validate`,
   `05_figures`, `06_report`, each reading the previous stage's outputs and
   writing only to its own directory.
4. **Manifest.** After a run, write `run_manifest.json`: timestamp, git commit,
   environment, seeds, input checksums, output checksums, and software
   versions. See `scripts/run_manifest.py`.
5. **Verification.** Re-run and confirm the manifest's output hashes are
   unchanged. Report any difference and explain it.
6. **Archive.** Tag the commit, archive with a DOI, and cite the archive in the
   data-availability statement.

## Terms

- **Raw data is read-only.** Checksums are verified at the start of every run.
  A mismatch stops the pipeline; it does not warn and continue.
- **No manual steps.** If a person has to click, drag, or copy a file between
  stages, the pipeline is incomplete.
- **No absolute paths.** Everything resolves relative to the repository root,
  or from an environment variable.
- **Seeds are explicit and recorded.** Every permutation, simulation, and
  bootstrap takes a seed from one config, and the manifest stores it.
- **Fail loudly.** No silent fallbacks, no `try/except: pass`, no defaults that
  mask missing inputs. A missing layer is an error, not an empty map.
- **Outputs are hashed.** Tables and figures are checked, not just scripts.
- **Intermediate artefacts are disposable.** `outputs/` can be deleted and
  rebuilt; it is never hand-edited.
- **The README states the command, the runtime, and the environment.** A
  reader should not need to ask.
- **Determinism is claimed only after testing.** Parallel code, floating point,
  and library defaults can change results; a re-run that differs needs an
  explanation, not a shrug.

Output contract:

- `run_all.py` or `Makefile` at the repository root.
- `run_manifest.json` with at least:

```json
{
  "timestamp_utc": "",
  "git_commit": "",
  "python": "",
  "platform": "",
  "seeds": {},
  "inputs": {"path": "sha256"},
  "outputs": {"path": "sha256"},
  "packages": {"name": "version"}
}
```

- `README.md` section: prerequisites, one command, expected runtime, expected
  outputs.
- A clean run log with no warnings suppressed.

Refuse when: the pipeline depends on a manual step; raw inputs are edited in
place; seeds are unrecorded; or the only evidence of reproducibility is "it ran
on my machine".
