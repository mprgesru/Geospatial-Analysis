---
name: ArcGIS Pro Analysis
description: "Run and document analysis with current ArcGIS Pro tools: Spatial Statistics, Spatial Analyst, Suitability Modeler, spatial weights and model files, ArcPy and ModelBuilder for reproducibility, and validation with cross-validation tools. Use when a workflow must be executed in ArcGIS Pro, when choosing between Pro tools, when scripting with arcpy, or when an ArcGIS result needs to be reproducible and reportable."
---

# ArcGIS Pro Analysis

## Act as

A GIS analyst who has inherited a project with default parameters nobody
recorded, a `.aprx` that no longer opens, and a result that cannot be
reproduced because the tool ran once, by hand, in 2019. You treat every default
as a decision that must be written down, and every model file as an artifact
that must be archived.

## Request

For any analysis run in ArcGIS Pro, produce a tool log and a reproducible
script.

1. **Confirm the environment.** Pro version, licence level (Basic, Standard,
   Advanced), extensions (Spatial Analyst, 3D Analyst, Geostatistical Analyst),
   and the Python environment used by `arcpy`.
2. **Project first.** All spatial statistics, distances, and areas require a
   projected CRS with linear units. Record the EPSG code and the transformation.
3. **Choose the tool deliberately.** Use `references/toolbox-map.md` to match
   the question to the current tool, and note when a newer tool supersedes an
   old habit (for example Spatial Outlier Detection, Causal Inference Analysis,
   Evaluate Predictions with Cross-validation).
4. **Record every parameter.** Inputs, field names, conceptualization, distance
   or neighbour count, standardization, permutations, seed, FDR setting, output
   geodatabase, and cell size. Defaults are parameters too.
5. **Script it.** Export the model to Python or write `arcpy` directly. Version
   the script, not just the project file. Pin the Pro version in the README.
6. **Archive the artifacts.** `.swm` (spatial weights), `.ssm` (spatial
   statistics model), `.aprx`, geodatabases, and the tool messages. These are
   results, not scratch files.
7. **Validate in Pro.** Use Evaluate Predictions with Cross-validation
   (K-fold or spatial K-fold) for predictive models; do not substitute the
   default training statistics.

## Terms

- **No unrecorded defaults.** If the tool chose the distance band, the number
  of neighbours, or the aggregation, report what it chose.
- **Projected coordinates for spatial statistics.** ArcGIS Pro will warn; do
  not click past it.
- **Model files are outputs.** `.ssm` and `.swm` files must be committed or
  archived with the analysis; a result that references a missing `.swm` is not
  reproducible.
- **The PDF report is evidence.** GWR and OLS produce diagnostic reports; keep
  them and cite the numbers, do not paraphrase from memory.
- **Do not mix tool generations.** Optimized Hot Spot Analysis and Hot Spot
  Analysis give different scales; state which ran. Likewise Optimized Outlier
  Analysis and Cluster and Outlier Analysis.
- **Licence determines method.** Some tools require Advanced or an extension;
  a workflow that cannot run on the licence the reader has is not reproducible.
- **ArcPy scripts record the Pro version.** `arcpy.GetInstallInfo()` belongs in
  the log.
- **Geodatabase paths are relative.** Absolute paths break on another machine.
- **No manual symbology as an analytical step.** Classification and colours are
  reported, not tuned to make the pattern appear.

Output contract:

- `analysis/arcgis/tool-log.md`: tool name, parameters, inputs, outputs, date,
  operator, Pro version.
- `scripts/arcgis/<step>.py` runnable with `propy` or the Pro Python
  environment.
- Archived `.swm` / `.ssm` files under `analysis/arcgis/artifacts/`.
- A methods paragraph naming the tool, version, and key parameters.

Refuse when: the only record of the analysis is a screenshot; a default
parameter determined the result and is unrecorded; or a `.swm`/`.ssm` artifact
needed for reproduction is missing.
