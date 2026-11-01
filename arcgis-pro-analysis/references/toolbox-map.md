# ArcGIS Pro toolbox map

Verified against the current Pro tool reference. Tool names change between
releases; confirm in the version you are running before citing.

## Spatial Statistics toolbox

### Analyzing Patterns

| Tool | Question |
| --- | --- |
| Spatial Autocorrelation (Global Moran's I) | Is there clustering overall? |
| Incremental Spatial Autocorrelation | At what distance does clustering peak? |
| Multi-Distance Spatial Cluster Analysis (Ripley's K) | Clustering across a range of distances |

### Mapping Clusters

| Tool | Question | Supersedes |
| --- | --- | --- |
| Hot Spot Analysis (Getis-Ord Gi*) | Where are hot and cold spots? | — |
| Optimized Hot Spot Analysis | Same, with automatic scale selection | manual scale choice |
| Hot Spot Analysis Comparison | Did the pattern change between two layers? | eyeballing two maps |
| Cluster and Outlier Analysis (Anselin Local Moran's I) | Clusters and spatial outliers together | — |
| Optimized Outlier Analysis | Same, with automatic scale and correction | manual scale choice |
| Spatial Outlier Detection | Global or local point outliers | ad hoc z-scores |
| Density-based Clustering | DBSCAN, HDBSCAN, OPTICS; optional time | — |
| Multivariate Clustering | Attribute-space groups | legacy Grouping Analysis |
| Spatially Constrained Multivariate Clustering | Contiguous groups | legacy Grouping Analysis |
| Build Balanced Zones | Contiguous zones from criteria | manual regionalization |
| Calculate Composite Index | Combine variables into one index | ad hoc weighted sums |
| Similarity Search | Most similar candidate features | — |

### Modeling Spatial Relationships

| Tool | Use |
| --- | --- |
| Ordinary Least Squares (OLS) | Global baseline; always run first |
| Exploratory Regression | All-subsets search with criteria |
| Generalized Linear Regression (GLR) | Continuous, binary, count outcomes |
| Geographically Weighted Regression (GWR) | Local coefficients |
| Multiscale GWR (MGWR) | Variable-specific bandwidths |
| Spatial Autoregression | Global spatial lag/error model |
| Forest-based and Boosted Classification and Regression | Random forest, XGBoost |
| Presence-only Prediction | MaxEnt |
| Causal Inference Analysis | Exposure effect with confounders |
| Colocation Analysis | Local association between two point categories |
| Bivariate Spatial Association (Lee's L) | Spatial association between two continuous variables |
| Local Bivariate Relationships | How a relationship varies locally |
| Evaluate Predictions with Cross-validation | K-fold or spatial K-fold metrics |
| Evaluate Variable Influence for Predictions | Partial dependence from a `.ssm` |
| Prepare Data for Prediction | Train/test split, thinning, balancing |
| Generate Spatial Weights Matrix | `.swm` creation |
| Generate Network Spatial Weights | `.swm` from a network |

### Utilities and measuring distributions

Mean center, median center, directional distribution, standard distance,
linear directional mean, collect events, export feature attributes to ASCII.

## Spatial Analyst

| Task | Tool |
| --- | --- |
| Watershed delineation | Hydrology toolset: Fill, Flow Direction, Flow Accumulation, Watershed |
| Stream network | Derive Stream As Line / Raster, Stream Order, Stream to Feature |
| Depression handling | Fill, Generate Breach Lines, Locate Depressions |
| Stage-volume | Storage Capacity |
| Overlay | Weighted Overlay, Weighted Sum, Raster Calculator |
| Zonal summary | Zonal Statistics, Zonal Statistics as Table, Tabulate Area |
| Distance surfaces | Euclidean Distance, Cost Distance, Path Distance |
| Surface | Slope, Aspect, Curvature, Hillshade |

## Suitability

| Approach | Where |
| --- | --- |
| Suitability Modeler | Analysis ribbon; criteria, transform, influence, weighted overlay, locate |
| Weighted Overlay | Spatial Analyst, Overlay (integer reclassified inputs) |
| Weighted Sum | Spatial Analyst, Overlay (continuous inputs) |
| Calculate Composite Index | Spatial Statistics, Mapping Clusters |

## Artifacts to archive

| File | Produced by | Why it matters |
| --- | --- | --- |
| `.swm` | Generate Spatial Weights Matrix | The weights are the model; without the file the result is unreproducible |
| `.ssm` | Forest-based, GLR, Presence-only | Trained model; needed for prediction and variable influence |
| `.aprx` | Project | Layout and data sources, not analysis logic |
| Geodatabase | All tools | Feature classes and tables with metadata |
| Tool messages | Every run | Parameters, warnings, diagnostics |

## Scripting pattern

```python
import arcpy
import json
from datetime import datetime, timezone

info = arcpy.GetInstallInfo()
log = {
    "tool": "Hot Spot Analysis (Getis-Ord Gi*)",
    "pro_version": info["Version"],
    "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "parameters": {
        "input": "analysis/hotspots.gdb/incidents",
        "field": "rate_per_1000",
        "conceptualization": "FIXED_DISTANCE_BAND",
        "distance_band": 1200,
        "row_standardization": True,
        "fdr": True,
    },
}

arcpy.stats.HotSpots(
    Input_Feature_Class=log["parameters"]["input"],
    Input_Field=log["parameters"]["field"],
    Conceptualization="FIXED_DISTANCE_BAND",
    Distance_Band=1200,
    Standardization="ROW",
    Apply_FDR_Correction="FDR",
    Output_Feature_Class="analysis/hotspots.gdb/hotspots",
)

with open("analysis/arcgis/tool-log.json", "w", encoding="utf-8") as fh:
    json.dump(log, fh, indent=2)
```

Write the log in the same script that runs the tool. A log written afterwards
from memory is a reconstruction, not a record.

## Version notes

- Newer releases add tools rather than renaming existing ones; check the
  toolbox history page for your version.
- `Spatial Autoregression` gives global SAR/SEM without leaving Pro.
- `Evaluate Predictions with Cross-validation` supports spatial K-fold, which
  is the correct validation for autocorrelated data.
- Tool availability depends on licence level and extensions; record both.
