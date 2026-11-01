# Local Moran's I and outlier methods

## Three different questions

| Question | Method | Output |
| --- | --- | --- |
| Is this value unusual in the distribution? | z-score, IQR, Mahalanobis | attribute outlier |
| Is this value unusual given its neighbours? | Anselin Local Moran's I, Spatial Outlier Detection | spatial outlier |
| Do unusual values occur together? | Local Moran HH/LL, Getis-Ord Gi*, scan statistic | cluster |

A feature can be an attribute outlier and not a spatial outlier (extreme, but
surrounded by similar extremes), and vice versa.

## Statistic

```
I_i = ( z_i / m2 ) · Σ_j w_ij z_j
```

where `z = x − x̄`, `m2 = Σ z_j² / n`, and `w_ij` is a row-standardised weight.

| Quadrant | `z_i` | neighbour lag | Meaning |
| --- | --- | --- | --- |
| HH | + | + | high-high cluster |
| LL | − | − | low-low cluster |
| HL | + | − | high outlier among low values |
| LH | − | + | low outlier among high values |

Significance has two routes:

1. **Normal approximation** (Anselin 1995), used by GeoDa, ArcGIS Pro, and
   `scripts/local_moran.py`. Uses the randomization null with a kurtosis term
   `b2 = m4/m2²`:

   ```
   E[I_i]  = -w_i. / (n - 1)
   Var[I_i] = w_i(2)(n - b2)/(n - 1)
            + ((w_i.² - w_i(2))(2b2 - n)) / ((n - 1)(n - 2))
            - w_i.² / (n - 1)²
   ```

   The variance goes non-positive for extremely heavy tails; treat those
   p-values as unreliable and fall back to permutation.

2. **Conditional permutation**: hold `z_i` fixed and reassign the remaining
   values. This null is narrower than total randomization, and the p-value is
   floored at `1/(perms + 1)`. That floor is a real constraint: with 999
   permutations the smallest possible q across 500 features is
   `0.001 × 500 = 0.5`, so nothing can survive FDR. Use 10,000 or more if you
   take this route.

## Multiplicity

Local Moran produces one test per feature. Apply Benjamini-Hochberg and report
q-values. ArcGIS Pro's Cluster and Outlier Analysis applies FDR by default in
recent versions; confirm the setting rather than assuming.

## ArcGIS Pro

| Task | Tool | Notes |
| --- | --- | --- |
| Clusters and spatial outliers with chosen weights | Cluster and Outlier Analysis (Anselin Local Moran's I) | Outputs `COType`: HH, LL, HL, LH, Not Significant |
| Automatic scale and correction | Optimized Outlier Analysis | Picks aggregation and scale; report the parameters |
| Point outliers, global or local | Spatial Outlier Detection | Newer tool; point features only |
| Dense clusters with noise | Density-based Clustering (DBSCAN, HDBSCAN, OPTICS) | Exploration, not inference |
| Multivariate similarity | Multivariate Clustering, Similarity Search | Attribute space, not spatial outliers |

`COType` values are the classification; the z-score and p-value fields are the
evidence. Keep both in the attribute table.

## Python (PySAL)

```python
from libpysal.weights import KNN
from esda import Moran_Local

w = KNN.from_array(coords, k=8)
w.transform = "r"

lm = Moran_Local(y, w, permutations=999, seed=12345, keep_simulations=True)
q = lm.p_sim  # adjust with statsmodels or a BH implementation before reporting
```

`lm.q` gives the quadrant (1 = HH, 2 = LH, 3 = LL, 4 = HL in PySAL's coding);
check the documentation for your version rather than assuming the order.

## R (spdep)

```r
library(spdep)
nb <- knn2nb(knearneigh(coords, k = 8))
lw <- nb2listw(nb, style = "W", zero.policy = TRUE)

lm <- localmoran(y, lw, p.adjust.method = "BH")
```

## Robust alternatives

- **Mahalanobis distance** for multivariate attribute outliers; report the
  covariance estimate and the chi-square threshold.
- **Isolation forest** or **LOF** for high-dimensional attribute screening.
- **Empirical Bayes smoothing** before flagging rates from small denominators.
- **Robust regression residuals** to find features the model cannot explain,
  then test whether those residuals are spatially clustered.

## Reporting template

> Spatial outliers were identified with Anselin's Local Moran's I using
> queen contiguity (row-standardised, 4 isolates) and 999 conditional
> permutations. p-values were adjusted with Benjamini-Hochberg. HH and LL
> features with q < 0.05 were classified as clusters; HL and LH features as
> spatial outliers. Of 812 features, 34 were HH, 21 LL, 9 HL and 6 LH. Removing
> the 15 outliers changed the coefficient on X from 0.42 (95% CI 0.31–0.53) to
> 0.39 (0.28–0.50); the conclusion was unchanged.
