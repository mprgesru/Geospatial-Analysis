# Geographically weighted regression reference

## Before GWR: the global model

GWR only makes sense relative to OLS. Check:

| Diagnostic | Threshold | Action |
| --- | --- | --- |
| Jarque-Bera p | < 0.05 | Transform the dependent variable or use a GLM |
| Koenker BP p | < 0.05 | Heteroskedasticity; GWR may help, but report it |
| VIF | > 7.5 | Remove or combine collinear variables |
| Residual Moran's I | p < 0.05 | Spatial structure remains; GWR is a candidate |
| AICc | — | Baseline for comparing GWR |

## Kernel and bandwidth

| Kernel | When | Parameter |
| --- | --- | --- |
| Fixed Gaussian | Evenly distributed features | Distance in map units |
| Fixed bisquare | Evenly distributed, sharper cutoff | Distance in map units |
| Adaptive bisquare | Density varies (typical for points) | Number of neighbours |

Bandwidth selection in ArcGIS Pro: AICc (default recommendation), CV, or a
fixed value. Report which, and the search range. A bandwidth near the number of
features means the model is nearly global; a very small bandwidth means each
estimate rests on a handful of points.

Rule of thumb: the effective number of parameters should be well below `n`. If
it approaches `n`, the model is interpolating.

## Local collinearity

ArcGIS Pro reports the minimum, median, and maximum local condition number and
the percentage of features above 30. Above 30, local signs and magnitudes are
unstable and should not be interpreted. Options: drop a variable, combine
collinear variables into an index, or use MGWR.

## MGWR

MGWR gives each covariate its own bandwidth. It is the right tool when theory
suggests different processes operate at different scales (for example, a
regional policy variable and a local environmental exposure).

Requirements: enough observations per local neighbourhood, a global model that
is already well specified, and a willingness to report several bandwidths.
With fewer than a few hundred features, variable-specific bandwidths are
usually unstable.

## ArcGIS Pro

Geographically Weighted Regression (GWR) and Multiscale Geographically
Weighted Regression (MGWR) are in the Spatial Statistics toolbox, Modeling
Spatial Relationships toolset. Both require projected data.

Key parameters and outputs:

- Number of neighbours or distance band, plus kernel type.
- Bandwidth method: AICc, CV, or fixed.
- Optional prediction locations for out-of-sample prediction.
- Output fields include local coefficients, local standard errors, local R²,
  condition numbers, residuals, and predicted values.
- Messages and the generated PDF report carry AICc, R², adjusted R², effective
  number of parameters, and the condition-number summary.

```python
import arcpy

arcpy.stats.GeographicallyWeightedRegression(
    in_features="analysis_points",
    dependent_variable="rate",
    explanatory_variables=["income", "distance_to_road", "greenness"],
    out_features="outputs/gwr_features",
    number_of_neighbors=30,
    kernel_type="ADAPTIVE",
    bandwidth_method="AICc",
    coefficient_raster_workspace="outputs/gwr_rasters",
    scale_factor=1000,
)
```

Always run Ordinary Least Squares first; the GWR tool warns when the global
model is misspecified, and that warning is the most useful thing it produces.

## Python (mgwr)

```python
from mgwr.gwr import GWR, MGWR
from mgwr.sel_bw import Sel_BW

selector = Sel_BW(coords, y, X)
bandwidth = selector.search(criterion="AICc")
model = GWR(coords, y, X, bw=bandwidth).fit()

model.params      # local coefficients
model.bse         # local standard errors
model.localR2     # local R-squared
model.aicc        # model comparison
```

MGWR:

```python
selector = Sel_BW(coords, y, X, multi=True)
bandwidths = selector.search(criterion="AICc")
model = MGWR(coords, y, X, selector=selector).fit()
```

## R (spgwr, GWmodel)

```r
library(spgwr)
bw <- gwr.sel(y ~ x1 + x2, data = df,
              coords = cbind(df$x, df$y), adapt = TRUE)
fit <- gwr(y ~ x1 + x2, data = df,
           coords = cbind(df$x, df$y), bandwidth = bw,
           adapt = TRUE, hatmatrix = TRUE)
```

## Interpretation checklist

- [ ] Global OLS reported and compared.
- [ ] Bandwidth, kernel, and criterion stated.
- [ ] Effective parameters and AICc reported.
- [ ] Local condition numbers summarised.
- [ ] Coefficient surfaces shown with local standard errors, not t-values alone.
- [ ] Spatial cross-validation RMSE compared with OLS.
- [ ] Areas of instability described in the text.

## Weighted least squares is not GWR

If weights represent precision, population, or survey design rather than
geographic distance, use WLS:

```r
fit <- lm(y ~ x, data = df, weights = precision)
```

Do not label it geographically weighted. The two answer different questions.
