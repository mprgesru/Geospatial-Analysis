# Spatial regression reference

## Decision path

```
OLS + robust SE
   └─ residual Moran's I
        ├─ not significant → stop. Use OLS. Say so.
        └─ significant
             ├─ LM-lag only        → SAR
             ├─ LM-error only      → SEM
             ├─ both               → robust LM
             │    ├─ robust lag    → SAR
             │    ├─ robust error  → SEM
             │    └─ neither       → SDM, then test down
             └─ coefficient drift → GWR / MGWR
```

## The four workhorse models

| Model | Equation | What it says |
| --- | --- | --- |
| SAR (lag) | `y = rho W y + X beta + e` | Outcome in one unit depends on neighbours' outcome |
| SEM (error) | `y = X beta + u`, `u = lambda W u + e` | Unobserved shocks are spatially correlated |
| SLX | `y = X beta + W X theta + e` | Covariates spill over; no feedback |
| SDM | `y = rho W y + X beta + W X theta + e` | Both; nests SAR and SLX |

SDM nests SAR (`theta = 0`) and SLX (`rho = 0`). Test down rather than choosing
by AIC alone; a likelihood ratio test with one restriction is cleaner.

## Direct and indirect effects

For SDM, the total effect of covariate `k` is not `beta_k`. With row-standardised
`W`:

```
S_k = (I - rho W)^-1 (beta_k I + theta_k W)
```

- **Direct** = mean of the diagonal of `S_k` (own unit plus feedback).
- **Indirect** = mean row sum off-diagonal (spillover to neighbours).
- **Total** = direct + indirect.

Compute confidence intervals by simulation: draw `rho`, `beta`, `theta` from
their sampling distribution, recompute `S_k`, and take empirical quantiles.
Reporting `beta` as "the effect" when `rho` is 0.4 understates it by roughly
`1/(1-rho)`.

## Python (PySAL)

```python
import numpy as np
from libpysal.weights import Queen, KNN
from spreg import OLS, ML_Lag, ML_Error
from libpysal.weights import lag_spatial

w = Queen.from_dataframe(gdf, use_index=True)
w.transform = "r"

ols = OLS(y, X, w=w, spat_diag=True, moran=True)
sar = ML_Lag(y, X, w=w)
sem = ML_Error(y, X, w=w)

# SDM = SAR + lagged covariates
X_sdm = np.hstack([X, lag_spatial(w, X)])
sdm = ML_Lag(y, X_sdm, w=w)
```

`spreg` reports `pr2` (pseudo R2), log-likelihood, AIC, and the spatial
parameter. Check `ols.moran_res` for residual autocorrelation.

## R (spdep)

```r
library(spdep)
nb  <- poly2nb(shp, queen = TRUE)
lw  <- nb2listw(nb, style = "W", zero.policy = TRUE)

ols <- lm(y ~ x, data = df)
lm.morantest(ols, lw)
lm.LMtests(ols, lw, test = "all")

sar <- lagsarlm(y ~ x, data = df, listw = lw)
sem <- errorsarlm(y ~ x, data = df, listw = lw)
sdm <- lagsarlm(y ~ x, data = df, listw = lw, type = "mixed")

summary(impacts(sdm, listw = lw, R = 1000), zstats = TRUE)
```

## GWR and MGWR

```python
from mgwr.gwr import GWR
from mgwr.sel_bw import Sel_BW

bw = Sel_BW(coords, y, X).search(criterion="AICc")
model = GWR(coords, y, X, bw=bw).fit()
```

```r
library(spgwr)
bw <- gwr.sel(y ~ x, data = df, coords = cbind(df$x, df$y), gweight = gwr.Gauss)
fit <- gwr(y ~ x, data = df, coords = cbind(df$x, df$y),
           bandwidth = bw, gweight = gwr.Gauss, hatmatrix = TRUE)
```

Rules for GWR:

- Report the bandwidth in map units and the kernel.
- Check local collinearity: `mgwr` exposes local condition numbers; above ~30
  is unstable.
- Local coefficients are correlated across units; a map of local t-values is
  not a significance map.
- MGWR only when you have enough observations per local neighbourhood,
  typically several hundred.

## Common reviewer objections

| Objection | Answer |
| --- | --- |
| "Your residuals are autocorrelated." | Report residual Moran's I before and after; if it remains, the mean model is wrong. |
| "Your weights are arbitrary." | Justify from process; report one planned alternative and the sensitivity result. |
| "You interpret beta as an effect." | Use the direct/indirect decomposition. |
| "A spatial lag absorbs your treatment." | Show the model without the lag and discuss identification. |
| "GWR coefficients are overinterpreted." | Report bandwidth, collinearity, and uncertainty; avoid local significance maps. |
