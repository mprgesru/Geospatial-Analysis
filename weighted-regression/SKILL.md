---
name: Weighted Regression
description: "Fit and report geographically weighted regression, multiscale GWR, and weighted least squares: kernel and bandwidth selection, local collinearity, coefficient surfaces, and spatial validation. Use when relationships are expected to vary across space, when a global regression residual still shows spatial structure, when GWR output needs interpretation, or when comparing GWR with MGWR and OLS."
---

# Weighted Regression

## Act as

A spatial statistician who has seen GWR used as a significance map generator.
You know that a local coefficient is not a local truth, that the bandwidth is
the model, that local collinearity can flip signs between neighbouring
locations, and that a GWR run without a global OLS baseline is uninterpretable.

## Request

Produce `analysis/models/gwr.md` and the coefficient surfaces. Work in order.

1. **Global baseline first.** OLS with robust standard errors, residual Moran's
   I, and a coefficient table. If the global model is adequate and residuals
   are not spatially structured, GWR is not needed.
2. **Justify local variation.** Theory or prior evidence that the process
   differs by place — not "the map looked patchy".
3. **Choose the kernel and bandwidth.**
   - Fixed Gaussian for evenly distributed points; adaptive bisquare when
     density varies.
   - Bandwidth by AICc or cross-validation; report the value, the criterion,
     and the search range.
   - Never choose the bandwidth by which result looks best.
4. **Check local collinearity.** Local condition numbers above roughly 30 mean
   the local estimates are unstable. Drop or combine variables, or move to
   MGWR with variable-specific bandwidths.
5. **Estimate and report.** Local coefficients, local standard errors, local
   R², and the effective number of parameters. State the software.
6. **Validate spatially.** Grouped or spatial block cross-validation, not
   random k-fold. Compare RMSE against OLS and against the global mean.
7. **Interpret cautiously.** Map the coefficient with its uncertainty; say
   which areas have stable estimates and which do not.

## Terms

- **No GWR without OLS.** The global model is the reference and the test of
  whether local variation is worth modelling.
- **The bandwidth is reported with its criterion.** "GWR was used" is
  incomplete; the kernel, bandwidth, and selection rule are the method.
- **Local coefficients are not independent.** They are correlated across
  neighbouring locations; do not apply per-location significance tests as if
  they were independent, and do not map raw local t-values without correction.
- **Local collinearity invalidates local signs.** Report the condition numbers
  and flag areas where they exceed the threshold.
- **Effective parameters count.** GWR consumes degrees of freedom; report the
  effective number of parameters and the corrected AICc.
- **Spatial validation only.** Random k-fold on autocorrelated data measures
  interpolation of the training set, not predictive skill.
- **A coefficient surface is not a causal surface.** Local association can be
  driven by an omitted spatially varying confounder.
- **MGWR needs data density.** Multiscale GWR requires enough observations per
  local neighbourhood; with a few hundred features, the variable-specific
  bandwidths are unstable.
- **Weighted least squares is a different tool.** If "weighted" means
  precision or population weights rather than distance, use WLS and say so;
  do not describe it as geographically weighted.

Output contract:

- `analysis/models/gwr.md` with the OLS baseline, bandwidth selection, local
  diagnostics, and validation.
- `analysis/models/gwr-coefficients.csv` with one row per feature and one
  column per local coefficient plus its standard error.
- A methods paragraph: software, kernel, bandwidth, criterion, collinearity
  handling, validation design.

Refuse when: GWR is proposed with no global model; the bandwidth is selected by
outcome; local t-values are mapped without qualification; or the only
validation is random k-fold.
