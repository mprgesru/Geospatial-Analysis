# Spatial reporting checklist

Mark each item `satisfied`, `partial`, or `n/a`, and give the section that
satisfies it. A `partial` with an explanation is acceptable; a false
`satisfied` is a retraction risk.

## Design and question

| # | Item | Where |
| --- | --- | --- |
| 1 | Research question and spatial estimand stated | Methods ¶1 |
| 2 | Unit of analysis and support named | Methods |
| 3 | Sampling frame and selection mechanism described | Methods |
| 4 | Target of inference matches sampled support | Methods |
| 5 | Confirmatory analyses separated from exploratory | Methods, end |

## Data

| # | Item | Where |
| --- | --- | --- |
| 6 | Sources, access dates, licence | Data availability |
| 7 | Analysis CRS with EPSG code and projection property | Methods |
| 8 | Resolution or support size | Methods |
| 9 | Missing data, exclusions, and flow counts | Methods, figure |
| 10 | Geometry validation and repairs logged | Supplement |
| 11 | Geo-privacy measures stated | Data availability |

## Spatial structure

| # | Item | Where |
| --- | --- | --- |
| 12 | Weight matrix construction, standardisation, isolates | Methods |
| 13 | Justification of weights from process, not fit | Methods |
| 14 | Variogram model, nugget, sill, range, with units | Methods |
| 15 | Maximum lag and binning rule | Supplement |
| 16 | Anisotropy tested | Supplement |
| 17 | Stationarity assumed and defended | Methods |

## Model

| # | Item | Where |
| --- | --- | --- |
| 18 | Estimator named (ML, GMM, Bayesian) | Methods |
| 19 | Covariates and functional form | Methods |
| 20 | Spatial parameter with standard error | Results |
| 21 | Direct, indirect, and total effects where relevant | Results |
| 22 | Multiplicity correction stated | Methods |
| 23 | Software and versions | Methods, end |

## Validation

| # | Item | Where |
| --- | --- | --- |
| 24 | Validation design named and fold geometry described | Methods |
| 25 | Minimum train/test separation versus fitted range | Methods |
| 26 | RMSE, MAE, bias, and standardized RMSE | Results |
| 27 | Interval coverage | Results or supplement |
| 28 | Baseline comparison | Results |
| 29 | Back-transformation correction if transformed | Methods |
| 30 | Residual spatial dependence reported | Results |

## Results and interpretation

| # | Item | Where |
| --- | --- | --- |
| 31 | Effect sizes with confidence intervals | Results |
| 32 | Uncertainty map or interval presented | Figures |
| 33 | Conclusions limited to the support and scale studied | Discussion |
| 34 | Alternative explanations for spatial pattern discussed | Discussion |
| 35 | Specific limitations, not generic ones | Discussion |

## Reproducibility and availability

| # | Item | Where |
| --- | --- | --- |
| 36 | Code repository and commit hash | Data availability |
| 37 | Environment pin or lockfile | Repository |
| 38 | Seeds recorded | Methods or supplement |
| 39 | One-command rebuild documented | Repository README |
| 40 | Raw data checksums | Repository |

## Figure checklist

| # | Item |
| --- | --- |
| 41 | CRS in every caption |
| 42 | Units in every legend |
| 43 | Class breaks and method stated |
| 44 | Scale bar in metric units |
| 45 | Uncertainty panel or a stated reason |
| 46 | Colour-blind-safe and grayscale-safe |
| 47 | No choropleth of raw counts |

## Common desk-reject triggers

- "Spatial analysis" with no weights or variogram reported.
- Accuracy claimed from random k-fold.
- A p-value map with no multiplicity correction.
- A kriged surface presented as if it reproduces observations.
- CRS omitted, or latitude/longitude used for distance.
- Data availability statement contradicted by the licence.
