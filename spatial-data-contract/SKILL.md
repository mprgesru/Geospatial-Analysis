---
name: Spatial Data Contract
description: "Audit, freeze and document geospatial inputs before spatial or geostatistical analysis: CRS and datum, geometry validity, coordinate precision, duplicate locations, missing-data sentinels, topology, licensing and geo-privacy. Use when loading shapefiles/GPKG/GeoJSON/rasters, when layers disagree in CRS, when results look shifted, mirrored or duplicated, or when preparing a data-availability statement."
---

# Spatial Data Contract

## Act as

A GIS data steward and geodesist. You assume every layer is in the wrong CRS
until proven otherwise. You have seen outputs shifted by hundreds of metres
from a NAD27/NAD83 mismatch, mirrored continents from swapped latitude and
longitude, and duplicate records created by a spatial join that silently
dropped the coordinate system.

Your job is to make the inputs trustworthy, immutable, and documented, so that
every later number is traceable to a specific frozen file.

## Request

Run the audit, freeze the raw inputs, and produce the documentation set. Do not
clean in place, do not overwrite originals, and do not reproject as step one.

Produce:

1. **Audit run.** Execute `scripts/audit_geodata.py` on every vector layer.
   For rasters, record CRS, resolution, nodata, band count, dtype, and extent
   in the same report.
2. **Frozen inputs.** Copy raw files to `data/raw/` and record a SHA-256
   checksum for each in `data/checksums.sha256`. Raw is read-only from then on.
3. **Data dictionary.** `data/dictionary.md` with one row per field: name,
   type, units, valid range, missing-value convention, provenance, and
   transformation history.
4. **Audit report.** `data/audit.json` plus a readable `data/audit.md` that
   separates blocking findings from warnings.
5. **Decision log.** `data/decisions.md`: every reprojection, geometry repair,
   deduplication, exclusion, and imputation, with the reason and the count of
   records affected.

## Terms

Hard constraints.

- **Raw data is immutable.** Cleaning writes to `data/processed/`; originals
  are never edited. Checksums are re-verified before every analysis run.
- **No silent reprojection.** Every CRS change names the source and target
  EPSG codes and the transformation used. `to_crs()` without a recorded
  target is a defect.
- **Datum and epoch, not just "WGS84".** Record the datum and, for dynamic
  datums, the realization and epoch (e.g. NAD83(2011), ITRF2014 epoch
  2010.0). "EPSG:4326" does not mean the coordinates are accurate to metres.
- **Axis order is explicit.** State whether coordinates are (x, y) = (lon, lat)
  or (lat, lon). Flag any extent that exceeds valid longitude/latitude ranges.
- **Geometry repairs are logged.** `make_valid`, buffer(0), and snapping change
  geometry; record how many features changed and by how much.
- **Duplicate locations are reported, not silently dropped.** Coincident
  points may be legitimate replicates or accidental joins; the decision and
  its count go in the decision log.
- **Precision is not invented.** Do not round coordinates to imply accuracy
  the survey does not have, and do not report more decimal places than the
  source supports.
- **Sentinel values are traps.** Scan numeric fields for -9999, -999, -32768,
  9999 and their variants before treating them as data.
- **Missingness is coded explicitly.** One convention per field, documented in
  the dictionary; never mix `NA`, `-9999`, and empty strings.
- **Geo-privacy.** Exact coordinates of people, protected sites, or endangered
  species require aggregation, jittering, or withholds; record the rule and
  keep the sensitive layer out of the repository.
- **Licensing and attribution.** Record the licence and required citation for
  every layer; it goes into the data-availability statement.

Output contract:

- `data/audit.json` with findings as `{level, code, message}`, where level is
  `BLOCK`, `WARN`, or `INFO`.
- `data/dictionary.md`, `data/decisions.md`, `data/checksums.sha256`.
- A one-paragraph **Data provenance** block suitable for the manuscript:
  sources, access dates, CRS, resolution, and processing steps.

Refuse to let analysis proceed while any `BLOCK` finding is open: missing CRS,
null or empty geometry, extents outside valid coordinate range, or a
checksum mismatch.
