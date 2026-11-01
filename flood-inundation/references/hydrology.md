# Flood modelling reference

## Terrain preparation

| Step | Tool (ArcGIS Pro) | Notes |
| --- | --- | --- |
| Project and mosaic | Project Raster, Mosaic to New Raster | One CRS, one cell size, one datum |
| Remove surface features | Classify LAS, LAS to Raster (bare earth) | Buildings and canopy block flow |
| Fill sinks | Fill | Flattens real depressions; record the change |
| Breach instead of fill | Generate Breach Lines | Preferred where depressions are real |
| Validate flow | Validate Flow Direction | Finds loops before they ruin accumulation |
| Continuous flow | Derive Continuous Flow | No prior filling required; newer alternative |

Record: DEM source, acquisition year, cell size, vertical accuracy, datum, and
the conditioning method. These belong in the methods paragraph, not a
footnote.

## Routing

| Choice | When | Cost |
| --- | --- | --- |
| D8 | Simple, well-defined channels | Single-direction flow on hillslopes |
| MFD | Diffuse flow, flat terrain | Disperses accumulation |
| DINF | Flow direction as an angle | Better on hillslopes, harder to summarize |

Stream threshold: state the accumulation value used to define a channel
(for example, 1% of maximum accumulation) and why.

## Bathtub inundation

```
depth   = water_surface_elevation − DEM
extent  = depth > 0 AND connected to the water source
```

Connectivity is the step that separates a credible map from a puddle detector.
Implement it as a region group or flood fill seeded from the river, reservoir,
or sea boundary, then keep only connected components. Without it, every
depression in the DEM floods.

Limitations: flat water surface, no velocity, no timing, no backwater, no
bridge hydraulics. Acceptable for screening and for large, flat floodplains
with slow rise; not acceptable for flash floods or hazard mapping that needs
velocity.

## HAND

Height above nearest drainage: for each cell, elevation minus the elevation of
the stream cell it drains to.

```
HAND = DEM − elevation_of_nearest_stream_cell_along_flow_path
```

Then a stage `h` inundates cells with `HAND < h`, subject to connectivity.
HAND is fast and works well in humid regions with a clear drainage network; it
is weaker in flat or arid terrain where the channel network is ambiguous.

Implementation: Arc Hydro (HAND tools), WhiteboxTools, TauDEM, or a custom
script using flow direction and a stream raster. ArcGIS Pro's Hydrology toolset
provides the inputs (`Flow Direction`, `Flow Accumulation`, `Derive Stream As
Raster`) but not a single HAND tool.

## Hydrodynamic modelling

Use when the question involves velocity, arrival time, hazard class, bridges,
culverts, or backwater:

- HEC-RAS 2D (free, widely accepted), TUFLOW, LISFLOOD-FP, MIKE.
- Required inputs: terrain, roughness (Manning's n by land cover), boundary
  conditions (flow hydrograph or stage), structures, and a computational mesh.
- Calibration against a gauged event; validation against an independent one.
- Report mesh resolution, timestep, roughness table, and boundary conditions.

## Validation

| Observed data | Metric | Caveat |
| --- | --- | --- |
| Satellite flood mask (Sentinel-1/2) | IoU, F1, omission/commission | Timing and vegetation confuse SAR |
| High-water marks | Vertical error at points | Sparse, and marks settle after the peak |
| Gauge records | Stage time series | Point validation, not spatial |
| Insurance claims | Hit rate by polygon | Reporting bias |
| Regulatory maps | Agreement | They may share the same assumptions |

Report the event date and the model scenario it corresponds to. Validating a
100-year map against a 10-year observed flood measures nothing.

## Uncertainty

- DEM vertical error: propagate by Monte Carlo (`DEM + N(0, σ)`).
- Roughness: sample Manning's n within a plausible range.
- Boundary conditions: ensemble of hydrographs or stages.
- Structures: test with bridges open, blocked, and removed.

Report a probability of inundation per cell from the ensemble, not a single
line. A deterministic boundary presented without uncertainty invites
overconfidence.

## Exposure

```python
# Zonal statistics by depth band, then summarize by asset class
arcpy.sa.ZonalStatisticsAsTable(
    in_zone_data="buildings", zone_field="class",
    in_value_raster="depth_100yr.tif", out_table="exposure.dbf",
    statistics_type="MAXIMUM",
)
```

Depth-damage curves need depth, not just extent. Report counts by depth band
(0–0.5 m, 0.5–1 m, 1–2 m, > 2 m) and the curve source.

## Scenario naming

`extent_<return_period>_<scenario>_<datum>_<model_version>.tif`

Example: `extent_100yr_baseline_navd88_hecras-v6.4.tif`. A filename that does
not name the scenario will eventually be mislabelled in a figure.
