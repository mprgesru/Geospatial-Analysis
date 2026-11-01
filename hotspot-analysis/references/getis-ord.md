# Getis-Ord Gi* reference

## Statistic

For feature `i` with values `x_j` and weights `w_ij` (including `w_ii`):

```
Gi* = ( Σ_j w_ij x_j − X̄ Σ_j w_ij )
      / ( S · sqrt( (n Σ_j w_ij² − (Σ_j w_ij)²) / (n − 1) ) )
```

where `X̄ = Σ x_j / n` and `S = sqrt( Σ x_j² / n − X̄² )`.

- Gi* includes the feature itself (`w_ii = 1`).
- Gi excludes it. ArcGIS Pro and PySAL default to the star version.
- The z-score is standardized against a random-labelling null. It is not an
  effect size and does not scale with the magnitude of the local mean.
- p-values are two-sided from the standard normal, or from permutations.

## Choosing the scale

The analysis scale determines the answer. Three defensible routes:

1. **Process-based.** Dispersal distance, catchment radius, policing beat,
   travel time — preferably from the literature, fixed in the plan.
2. **Incremental Spatial Autocorrelation.** Run global Moran's I at a series of
   distances; pick the distance where autocorrelation peaks. This is
   data-driven, so label it exploratory and report the full curve.
3. **Optimized Hot Spot Analysis.** ArcGIS Pro estimates the scale from the
   data. Convenient, but the choice becomes invisible unless you report the
   parameters the tool selected.

Report: distance band or k, the range tested, and the metric.

## Multiplicity

Benjamini-Hochberg over all features:

```
q_(k) = min_{j >= k} ( p_(j) · n / j )
```

Report the number significant at q < 0.05 and the expected false positives
before correction. ArcGIS Pro's Hot Spot Analysis does not apply FDR by
default; use the `adjusted` p-values from PySAL or correct afterwards.

## ArcGIS Pro

| Task | Tool | Notes |
| --- | --- | --- |
| Fixed scale, analyst chooses weights | Hot Spot Analysis (Getis-Ord Gi*) | Set Conceptualization and Distance Band/Threshold |
| Automatic scale selection | Optimized Hot Spot Analysis | Inspects the data, picks aggregation and scale; report what it chose |
| Compare two result layers | Hot Spot Analysis Comparison | Tests similarity and association between two Gi* surfaces |
| Rates from small populations | Smooth or model first | Empirical Bayes smoothing or a binomial model; do not feed unstable proportions to Gi* |
| Space-time | Emerging Hot Spot Analysis (Space Time Pattern Mining) | Requires a space-time cube, not stacked maps |

Set `Apply False Discovery Rate Correction` when the tool offers it, and still
document it. Enable `Output Field` z-scores and p-values; do not rely on the
symbology alone.

## Python (PySAL)

```python
import numpy as np
from libpysal.weights import KNN
from esda import G_Local

w = KNN.from_array(coords, k=8)
w.transform = "r"

g = G_Local(y, w, star=True, permutations=999, seed=12345)
z, p = g.Z, g.p_sim
```

## R (spdep)

```r
library(spdep)
nb <- knn2nb(knearneigh(coords, k = 8))
lw <- nb2listw(nb, style = "W", zero.policy = TRUE)

g <- localG(y, lw)          # Gi* by default
p <- 2 * pnorm(-abs(g))
q <- p.adjust(p, method = "BH")
```

## Reporting template

> Hot spots were identified with the Getis-Ord Gi* statistic (ArcGIS Pro 3.x)
> using a fixed distance band of 1,200 m, row-standardised binary weights, and
> 999 permutations. Feature i was included in its own neighbourhood. p-values
> were adjusted for multiple testing with Benjamini-Hochberg; features with
> q < 0.05 were classified as hot or cold at the 95 per cent level. Results
> were sensitive to the distance band: at 800 m the eastern cluster was no
> longer significant.
