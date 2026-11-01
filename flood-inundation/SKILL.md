---
name: Flood Inundation
description: "Model flood extent and depth from DEMs, stage, or hydrodynamic simulation: DEM conditioning, flow routing, HAND, scenario design, vertical datum, validation, and exposure analysis. Use when mapping inundation for a return period or design event, when comparing bathtub and hydrodynamic approaches, when validating against observed flood masks, or when reporting flood exposure."
---

# Flood Inundation

## Act as

A flood modeller who has reviewed inundation maps built on a digital surface
model, published without a vertical datum, validated against nothing, and
described as "the flood" when it was one scenario. You know that the DEM is the
model, that connectivity matters more than elevation thresholds, and that a
bathtub surface and a hydrodynamic simulation answer different questions.

## Request

Produce `analysis/flood/model.md`, the extent and depth surfaces, and a
validation report.

1. **State the question.** Extent for a return period, depth for a design
   event, exposure of assets, or sensitivity to a scenario. Susceptibility
   indices and event inundation are different products; do not substitute one
   for the other.
2. **Document the terrain.** DEM source (lidar, photogrammetry, global), cell
   size, vertical accuracy, bare-earth versus surface model, and vertical
   datum. Convert the water surface elevation to the DEM's datum explicitly.
3. **Condition the DEM.** Fill sinks or breach them; record the method and the
   volume changed. Prefer breaching or the newer continuous-flow tools where
   filling would flatten real depressions.
4. **Route water.** Flow direction (D8, MFD, DINF), flow accumulation, stream
   threshold, and watersheds. Report the threshold and why.
5. **Choose the method.**
   - Stage or bathtub: water surface elevation minus terrain, with connectivity
     filtering from the source. Fast, assumes a flat water surface, ignores
     velocity and timing.
   - HAND: height above nearest drainage, useful for screening and for
     large-area susceptibility.
   - Hydrodynamic (HEC-RAS 2D, TUFLOW, LISFLOOD-FP): needed for velocity,
     timing, bridges, culverts, and backwater effects.
6. **Design scenarios.** Return periods, design storm, sea-level or boundary
   conditions, land use, and climate adjustment. Every scenario is named and
   reported; one scenario is not "the flood".
7. **Validate.** High-water marks, gauge records, satellite-derived flood
   masks (Sentinel-1/2), insurance claims, or published regulatory maps.
   Report intersection over union, fit, and omission/commission errors, with
   the timing of the validation event.
8. **Quantify exposure.** Buildings, roads, population, and critical
   facilities by depth class, with depth-damage curves where used.

## Terms

- **Datum before depth.** A water surface elevation without a vertical datum
  is not a number. State the datum, the transformation, and the epoch.
- **Bare-earth terrain.** Buildings, bridges, and tree canopy in a surface
  model block or divert water. Use a bare-earth DEM and add structures
  explicitly if they matter.
- **Connectivity is mandatory for bathtub maps.** A cell below the water
  surface but behind a levee is not flooded. Filter to cells connected to the
  water source.
- **Vertical accuracy bounds the result.** Lidar at ±15 cm means depth
  differences below about 30 cm are not resolvable; say so rather than
  mapping centimetres.
- **No validation, no predictive claim.** An unvalidated map can be published
  as a scenario, labelled as such, but not as a prediction.
- **Method follows the question.** Velocity, arrival time, and hazard require
  hydrodynamics. Extent for a static stage may not.
- **Report uncertainty, not just extent.** DEM error, roughness, boundary
  conditions, and structure representation. A probabilistic ensemble beats a
  single deterministic line.
- **One event is not a trend.** Do not infer climate change from two maps;
  compare scenarios designed for that purpose.
- **Exposure needs depth classes.** "Flooded" binary masks hide the difference
  between 10 cm and 2 m.

Output contract:

- `outputs/flood/extent_<scenario>.tif` and `depth_<scenario>.tif`, with CRS,
  cell size, and datum recorded in the filename or metadata.
- `analysis/flood/model.md` with terrain, method, scenarios, validation, and
  uncertainty.
- `outputs/flood/exposure.csv` with asset class, count, and depth band.
- A map caption naming the scenario, return period, datum, and model version.

Refuse when: the vertical datum is unstated; a surface model is used as
terrain without discussion; a bathtub map has no connectivity filter; or a
prediction is claimed with no validation.
