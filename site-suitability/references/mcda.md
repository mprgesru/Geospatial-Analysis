# Multi-criteria suitability reference

## Structure

```
Decision
├── Constraints (binary masks)     water, protected areas, slope > 25%, zoning
├── Factors (continuous scores)    distance to road, soil, population, cost
│   ├── standardize to 0–1
│   ├── weight (sum = 1)
│   └── combine
└── Sensitivity + validation
```

## Standardization functions

| Intent | Function | Notes |
| --- | --- | --- |
| Higher is better | `(x − min) / (max − min)` | Sensitive to outliers; consider percentiles |
| Lower is better | `1 − (x − min) / (max − min)` | Distance to a nuisance |
| Ideal range | `1 − |x − c| / r` | Triangular; state centre `c` and radius `r` |
| Categorical | Score table | Ordinal classes keep their order; nominal classes do not |
| Threshold | Step function | Only when a real policy threshold exists |

Record the minimum and maximum used. If they come from the observed data, the
scores are not comparable across study areas.

## Weights

**Equal weights** are a legitimate, transparent default. Say so.

**AHP** (analytic hierarchy process):

1. Build a pairwise comparison matrix `A` with Saaty's 1–9 scale.
2. Weights are the principal eigenvector, normalized to sum to 1.
3. Consistency index `CI = (λmax − n) / (n − 1)`.
4. Consistency ratio `CR = CI / RI`, with `RI` from Saaty's table
   (n = 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45).
5. Accept `CR < 0.10`; otherwise revise the judgements.

Report the matrix or at least the weights and CR. AHP is a formalization of
opinion, not evidence of truth.

## Combining

```
score = Σ (weight_i × factor_i)        over factors
score = score × constraint_mask        constraints applied last
```

Order matters: apply the mask after weighting so the score surface remains
comparable inside the feasible area.

## ArcGIS Pro

| Approach | Where | Notes |
| --- | --- | --- |
| Suitability Modeler | Analysis ribbon (Spatial Analyst) | Criteria, transform, influence, weighted overlay, and a Locate mode; keeps the model editable |
| Weighted Overlay | Spatial Analyst, Overlay toolset | Requires integer reclassified rasters; less transparent than the Modeler |
| Weighted Sum | Spatial Analyst, Overlay toolset | Continuous inputs; weights assigned directly |
| Raster Calculator | Spatial Analyst | Full control; best for reproducibility with a saved expression |
| Calculate Composite Index | Spatial Statistics, Mapping Clusters | Combines variables into one index from polygon attributes |

The Suitability Modeler is preferable when the model will be revised, because
the criteria, transforms, and weights remain visible and editable. Export the
final model settings into the methods text regardless of tool.

## Sensitivity

| Method | What it shows |
| --- | --- |
| Equal weights | How much the ranking depends on the weights at all |
| One-at-a-time ±20% | Which criterion the result is most sensitive to |
| Monte Carlo over weight ranges | Distribution of rank for each candidate site |
| Alternative standardization | Whether breakpoints drive the result |

Report the area or the share of top-ranked sites that change class. "The
northern site remains in the top decile under 90% of weight draws" is a result;
a second map in the supplement is not.

## Validation

- **Known sites**: AUC or hit rate against existing facilities or observed use.
- **Expert ranking**: Spearman correlation with an independent ranking.
- **Outcome data**: logistic regression of observed occurrence on the
  suitability score.
- **Null model**: compare with a random score surface; a good-looking map can
  still be no better than chance.

Report the validation sample size and whether it was used to tune the model.

## Worked table

| Factor | Direction | Transform | Breakpoints | Weight | Source |
| --- | --- | --- | --- | --- | --- |
| Slope | lower better | linear decreasing | 0–25% | 0.25 | DEM |
| Distance to road | lower better | linear decreasing | 0–2,000 m | 0.20 | Roads |
| Soil drainage | higher better | categorical | classes 1–5 | 0.25 | Soil survey |
| Population density | higher better | quantile | 5 classes | 0.20 | Census |
| Protected areas | constraint | mask | — | — | WDPA |
| Flood zone | constraint | mask | 100-year | — | Regulatory map |
