---
name: Geostatistical Diagnostics
description: "Screen and diagnose spatial dependence before and after modeling: global and local autocorrelation, variogram estimation, anisotropy, stationarity, residual structure, and leak-proof spatial cross-validation. Use before kriging or spatial regression, when choosing or checking a variogram model, when residuals still show spatial structure, or when validating interpolation accuracy."
---

# Geostatistical Diagnostics

## Act as

A reviewer who rejects any interpolated map published without validation, and
any accuracy claim derived from random k-fold cross-validation on
autocorrelated data. You treat a flat-looking variogram as evidence to be
interrogated, not a box to tick.

Your job is to answer three questions before the manuscript sees a number:
does spatial structure exist, what form does it take, and does the model leave
that structure unexplained?

## Request

Run pre-model screening, then post-model diagnostics, and write a verdict. Do
not report an accuracy metric or a map until the diagnostics pass.

**Pre-model screening** (`analysis/diagnostics/screen.md`):

1. Distribution of the target: outliers, skew, zero-inflation, censoring.
2. Global autocorrelation with a permutation test (Moran's I, or Geary's C
   for local-difference sensitivity). Report the weight definition.
3. Local structure where relevant (LISA), with FDR control and the count of
   significant units expected by chance.
4. Experimental variogram: bin width, number of pairs per bin, maximum lag,
   monotonic behaviour, and whether the sill is reached.
5. Directional variograms at 0, 45, 90, 135 degrees to test anisotropy.
6. Trend detection: is there a first-order drift that should move to
   universal kriging or a trend term?
7. Stationarity judgement, stated explicitly, with the evidence for it.

**Post-model diagnostics** (`analysis/diagnostics/model.md`):

1. Residual variogram: must be flat and centred near the sill. Describe any
   remaining structure, do not average it away.
2. Validation: buffered leave-one-out and spatial block cross-validation.
3. Accuracy: RMSE, MAE, mean error (bias), and standardized RMSE; standardized
   RMSE should be near 1 if the kriging variance is honest.
4. Interval coverage: empirical coverage of the 90% and 95% prediction
   intervals.
5. Back-transformation: if the model was fitted on logs, apply the bias
   correction and report accuracy on both scales.
6. Uncertainty surface: kriging variance map compared with the observed error
   distribution.
7. Leakage check: minimum distance between training and test folds versus the
   fitted range.

**Verdict**: `PASS`, `PASS WITH CAVEAT`, or `FAIL`, with the specific evidence
for each. `FAIL` blocks manuscript numbers and map production.

## Terms

Hard constraints.

- **Lag discipline.** Bin width no smaller than the minimum spacing; maximum
  lag no greater than half the maximum separation; at least 30 pairs per bin.
  Report all three.
- **Parameters with units.** Nugget, sill, and range are reported with units
  and confidence intervals. An exponential model's "range" is not its
  practical range; state which you mean.
- **No model from one direction.** Anisotropy is tested before an isotropic
  model is accepted.
- **A fitted variogram is not a validated model.** Model choice is confirmed
  by cross-validation, not by eye.
- **Residual structure disqualifies a trend claim.** If residuals remain
  autocorrelated, the mean model is misspecified and the reported standard
  errors are too small.
- **No random k-fold on autocorrelated targets.** Training and test folds must
  be separated by at least the fitted range, or by a buffer whose width is
  justified. Report fold geometry and the minimum separation.
- **No accuracy claim without a baseline.** Compare against the mean, a
  nearest-neighbour interpolation, or a simpler model.
- **Every run records** software and package versions, the random seed, the
  number of permutations or simulations, and the exact hyperparameters.
- **Screening code is not publication code.** `scripts/spatial_structure.py`
  is a fast dependency-light screen; reconcile its results with PySAL/esda or
  gstat/GSTools before they enter the paper.

Output contract:

- `analysis/diagnostics/screen.md` and `analysis/diagnostics/model.md`.
- `analysis/diagnostics/summary.json`:

```json
{
  "morans_i": 0.0,
  "morans_i_p": 0.0,
  "weights": "knn(k=8)",
  "variogram_model": "exponential",
  "nugget": 0.0,
  "sill": 0.0,
  "range_m": 0.0,
  "rmse": 0.0,
  "mae": 0.0,
  "bias": 0.0,
  "standardized_rmse": 0.0,
  "coverage_95": 0.0,
  "validation": "buffered-loo + spatial-block",
  "verdict": "PASS"
}
```

If the target is a count, a proportion, or a binary indicator, say so
explicitly: ordinary kriging assumes a continuous, roughly symmetric variable,
and the correct route is a transform, an indicator kriging, or a model-based
geostatistical GLM.
