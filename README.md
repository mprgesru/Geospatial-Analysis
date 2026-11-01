# Geospatial Analysis skills

OpenCode skills for spatial, geostatistical, and reproducible research
analysis. Each skill is a self-contained directory: `SKILL.md` plus optional
`scripts/` and `references/`.

Fifteen skills, in the order a study uses them:

| Skill | Purpose |
| --- | --- |
| `spatial-analysis-plan` | Fix estimand, support, CRS, weights, and validation before modeling |
| `spatial-data-contract` | Audit and freeze inputs; CRS, geometry, sentinels, provenance |
| `geostatistical-diagnostics` | Moran's I, variograms, anisotropy, leak-proof validation |
| `hotspot-analysis` | Getis-Ord Gi*, scale choice, FDR, period comparison |
| `spatial-outlier-analysis` | Attribute vs spatial outliers vs clusters, LISA, DBSCAN |
| `spatial-regression` | SAR/SEM/SDM/SLX, direct and indirect effects, GWR/MGWR |
| `weighted-regression` | GWR/MGWR bandwidths, local collinearity, weighted surfaces |
| `kriging-interpolation` | Ordinary/universal/indicator/block kriging with uncertainty |
| `point-pattern-analysis` | CSR tests, Ripley's K/L with Monte Carlo envelopes |
| `site-suitability` | Constraints vs factors, weights, weighted overlay, sensitivity |
| `flood-inundation` | DEM conditioning, HAND, stage and hydrodynamic scenarios |
| `map-figures` | Publication cartography and uncertainty panels |
| `spatial-reporting` | Methods, results, checklist, data availability |
| `reproducible-pipeline` | One-command rebuild, pinned environment, run manifest |
| `arcgis-pro-analysis` | Current Pro tools, `.swm`/`.ssm` artifacts, ArcPy logging |

## Use from OpenCode

### Option A: clone and point at the directory

```bash
git clone https://github.com/mprgesru/Geospatial-Analysis.git
```

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "skills": ["/absolute/path/to/Geospatial-Analysis"]
}
```

Or vendor it as a submodule so the commit is pinned:

```bash
git submodule add https://github.com/mprgesru/Geospatial-Analysis.git skills/geospatial
```

### Option B: HTTP catalog, pinned to a tag

```jsonc
{
  "skills": [
    "https://raw.githubusercontent.com/mprgesru/Geospatial-Analysis/v1.0.1/"
  ]
}
```

`index.json` lists every file per skill. Pin a tag rather than `main` so the
skills cannot change between analysis and submission.

## Add or edit a skill

1. Create or edit `<skill-id>/SKILL.md` with `name` and `description` frontmatter.
2. Regenerate the catalog:

```bash
python build_catalog.py
```

3. Commit both the skill and `index.json`.

The `version` in `index.json` is a content hash, so it changes automatically
and clients never serve stale files. CI can enforce this:

```bash
python build_catalog.py --check
```

## Conventions

- One directory per skill; the directory name is the skill ID (lowercase
  kebab-case, case-sensitive).
- A skill directory must be self-contained. Relative paths resolve from the
  directory containing `SKILL.md`, so do not import from `../..`.
- Keep long references in `references/` and runnable code in `scripts/`. Only
  the `SKILL.md` body is loaded on demand.
- No secrets, keys, or personal data in this repository.

## Verification

The scripts were tested on synthetic data before publication:

| Script | Check |
| --- | --- |
| `spatial-data-contract/scripts/audit_geodata.py` | flags sentinels, duplicate geometry, missing CRS |
| `geostatistical-diagnostics/scripts/spatial_structure.py` | Moran's I and variogram on a known smooth field |
| `hotspot-analysis/scripts/getis_ord.py` | planted hotspot recovered: 27 hot, 0 cold, max z = 13.3 |
| `spatial-outlier-analysis/scripts/local_moran.py` | planted cluster and outlier recovered: 15 HH, 1 HL |
| `kriging-interpolation/scripts/ok_kriging.py` | exact interpolation at data points with zero nugget |
| `point-pattern-analysis/scripts/ripley_k.py` | uniform p = 0.60 vs clustered p = 0.005 |
| `reproducible-pipeline/scripts/run_manifest.py` | detects a changed output hash |
| `spatial-reporting/scripts/check_deliverables.py` | blocks on a FAIL verdict |

The Local Moran analytical variance was checked against 40,000 simulated
randomizations: formula/simulated variance ratio 0.994.

## Licence

Add a licence before accepting contributions. Until then, all rights reserved
by the author.
