# Diagnostic reference

## Global autocorrelation

| Statistic | Sensitive to | Use when |
| --- | --- | --- |
| Moran's I | Global similarity, high leverage from extreme values | Standard first screen for a continuous variable |
| Geary's C | Local differences, better for abrupt boundaries and outliers | Moran's I is inflated by a few extreme values |
| Getis-Ord General G | Concentration of high values | You care about hotspots of magnitude, not similarity |

Report the weight definition with the statistic. Moran's I under binary kNN and
under row-standardised kNN are different statistics on the same data.

Expected value under no autocorrelation: `E[I] = -1/(n-1)`. For n = 100 that is
-0.0101, not zero; do not describe a value of -0.01 as "slightly positive".

## Local indicators

LISA (local Moran) produces one statistic per unit. With 2,000 units and
alpha = 0.05, about 100 false positives are expected. Apply Benjamini-Hochberg
FDR control and report:

- the number of significant units before and after correction;
- the number expected by chance;
- the weight matrix used (LISA is more sensitive to weights than global I).

Local statistics also suffer from the multiple-comparison and
conditional-permutation problems; state which permutation scheme was used.

## Variogram conventions

- **Bin width**: at least the minimum inter-point spacing, ideally several times it.
- **Maximum lag**: no more than half the maximum separation. Beyond that, pairs
  come from opposite corners and the estimate is unstable.
- **Pairs per bin**: at least 30, preferably 100. Report the counts.
- **Nugget**: measurement error plus variation below the sampling support.
  A large nugget ratio (> 0.5) means most variance is unresolved.
- **Range**: the distance parameter, not the distance at which the model reaches
  the sill. For exponential, practical range is about 3 x range. State which is
  reported.
- **Anisotropy**: compute directional variograms at 0, 45, 90, 135 degrees with
  a tolerance of about 22.5 degrees. Geometric anisotropy is handled by
  transforming coordinates; zonal anisotropy needs a different model.

## Validation

| Method | Leaves out | Good for | Failure mode |
| --- | --- | --- | --- |
| Leave-one-out | 1 point | Small n, smooth fields | Optimistic under strong local correlation |
| Random k-fold | Random points | Non-spatial data only | Leakage; near-perfect scores |
| Spatial block | Contiguous blocks | Honest map accuracy | Block size must exceed the range |
| Buffered LOO | 1 point + neighbours within range | Honest point accuracy | Expensive; report the buffer width |

For each, report: fold geometry, minimum train/test separation, and whether it
exceeds the fitted range.

Standardized RMSE = sqrt(mean((z - ẑ)² / σ̂²)). Values near 1 mean the kriging
variance is honest; below 1 means it is too wide, above 1 too narrow.

## Back-transformation

If the model is fitted to `log(z)`, the predicted mean on the original scale is
not `exp(ẑ)`. For ordinary kriging with log-normal errors:

```
E[Z] = exp(ẑ + σ̂²/2)
```

Report accuracy on both scales, and state whether the back-transformed
prediction intervals are approximate.

## Software

- R: `gstat` (variogram, kriging), `spdep` (Moran, LISA, spatial regression),
  `sf`, `terra`, `automap`.
- Python: `libpysal` + `esda` (weights, Moran, LISA), `scikit-gstat` or
  `GSTools` (variogram, kriging), `pykrige` (kriging), `geopandas`, `rasterio`.

Current environment has geopandas, shapely, pyproj, numpy, pandas. Missing:
`matplotlib`, `libpysal`, `esda`, `scikit-gstat`, `pykrige`, `rasterio`.
Install with:

```
python -m pip install matplotlib libpysal esda scikit-gstat pykrige rasterio
```
