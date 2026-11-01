#!/usr/bin/env python3
"""Audit a vector layer against the spatial data contract.

Usage:
    python audit_geodata.py <layer> [--layer NAME] [--json PATH]

Writes human-readable findings to stdout and, optionally, JSON to PATH.
Exit codes: 0 = no blocking findings, 1 = blocking findings, 2 = unreadable input.

Requires: geopandas, shapely (present in the analysis environment).
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter

SENTINELS = {-99999.0, -99999, -9999.0, -9999, -999.0, -999, -32768.0, -32768, 9999.0, 9999}
TEXT_SENTINELS = {"NA", "N/A", "null", "NULL", "None", "NaN", "nan", "-"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit a vector layer against the spatial data contract.")
    parser.add_argument("layer", help="path to a vector dataset")
    parser.add_argument("--layer", dest="layer_name", default=None, help="layer name inside a multi-layer source")
    parser.add_argument("--json", dest="json_path", default=None, help="write findings as JSON here")
    args = parser.parse_args()

    try:
        import geopandas as gpd
    except ImportError as exc:
        print(f"missing dependency: {exc}", file=sys.stderr)
        return 2

    try:
        if args.layer_name:
            gdf = gpd.read_file(args.layer, layer=args.layer_name)
        else:
            gdf = gpd.read_file(args.layer)
    except Exception as exc:
        print(f"could not read {args.layer}: {exc}", file=sys.stderr)
        return 2

    findings: list[dict[str, str]] = []

    def add(level: str, code: str, message: str) -> None:
        findings.append({"level": level, "code": code, "message": message})

    add("INFO", "features", f"{len(gdf)} features, {len(gdf.columns)} attributes")

    # --- coordinate reference system -------------------------------------
    if gdf.crs is None:
        add("BLOCK", "no_crs", "No CRS declared; coordinates have no defined meaning.")
    else:
        epsg = gdf.crs.to_epsg()
        add("INFO", "crs", f"{gdf.crs.name} | EPSG:{epsg if epsg is not None else 'unknown'}")
        if gdf.crs.is_geographic:
            add("WARN", "geographic_crs",
                "Angular coordinates: project before any distance, area, buffer, or variogram computation.")
        if epsg is None:
            add("WARN", "crs_no_epsg", "CRS has no EPSG code; record the full WKT and its provenance.")

    # --- geometry ---------------------------------------------------------
    if "geometry" in gdf:
        types = Counter(gdf.geom_type.dropna())
        add("INFO", "geometry_types", ", ".join(f"{k}={v}" for k, v in sorted(types.items())))

        missing = int(gdf.geometry.isna().sum())
        if missing:
            add("BLOCK", "null_geometry", f"{missing} features have no geometry.")

        present = gdf.geometry.dropna()
        empty = int(present.is_empty.sum())
        if empty:
            add("WARN", "empty_geometry", f"{empty} features have empty geometry.")

        invalid = sum(1 for geom in present if not geom.is_valid)
        if invalid:
            add("WARN", "invalid_geometry",
                f"{invalid} invalid geometries; repair with make_valid and log every change.")

        try:
            dup_geom = int(present.to_wkb().duplicated().sum())
        except Exception:
            dup_geom = int(present.astype(str).duplicated().sum())
        if dup_geom:
            add("WARN", "duplicate_geometry", f"{dup_geom} duplicate geometries (identical WKB).")

        points = [
            (round(g.x, 9), round(g.y, 9))
            for g in present
            if g.geom_type == "Point"
        ]
        if points:
            dup_xy = len(points) - len(set(points))
            if dup_xy:
                add("WARN", "duplicate_coordinates",
                    f"{dup_xy} coincident point locations; confirm replicates before deduplication.")

    # --- extent and axis order -------------------------------------------
    try:
        minx, miny, maxx, maxy = gdf.total_bounds
        add("INFO", "extent_native", f"x {minx:.4f}..{maxx:.4f}, y {miny:.4f}..{maxy:.4f} (native CRS)")
        if gdf.crs is not None and gdf.crs.is_geographic:
            if maxx > 180 or maxy > 90:
                add("BLOCK", "axis_order",
                    "Geographic extent exceeds valid longitude/latitude ranges; likely swapped axes or wrong CRS.")
        if gdf.crs is not None and not gdf.crs.is_geographic:
            try:
                b = gdf.to_crs(4326).total_bounds
                add("INFO", "extent_wgs84",
                    f"lon {b[0]:.4f}..{b[2]:.4f}, lat {b[1]:.4f}..{b[3]:.4f}")
            except Exception as exc:
                add("WARN", "reproject_failed", f"could not reproject to EPSG:4326: {exc}")
    except Exception as exc:
        add("WARN", "extent_unavailable", f"could not compute extent: {exc}")

    # --- attributes -------------------------------------------------------
    for col in gdf.columns:
        if col == gdf.geometry.name:
            continue
        series = gdf[col]
        n_missing = int(series.isna().sum())
        if n_missing:
            add("INFO", "missing_values", f"{col}: {n_missing} null values.")

        if str(series.dtype).startswith(("int", "float")):
            hits = int(series.isin(SENTINELS).sum())
            if hits:
                add("WARN", "sentinel_values",
                    f"{col}: {hits} values look like missing-data sentinels (-9999 etc.).")
        elif series.dtype == object:
            hits = int(series.astype(str).str.strip().isin(TEXT_SENTINELS).sum())
            if hits:
                add("WARN", "text_sentinels", f"{col}: {hits} values look like text missing markers.")

    # --- report -----------------------------------------------------------
    order = {"BLOCK": 0, "WARN": 1, "INFO": 2}
    findings.sort(key=lambda f: order[f["level"]])

    blocking = sum(1 for f in findings if f["level"] == "BLOCK")
    warnings = sum(1 for f in findings if f["level"] == "WARN")

    for f in findings:
        print(f"[{f['level']:5}] {f['code']}: {f['message']}")

    print(f"\n{blocking} blocking finding(s), {warnings} warning(s), {len(findings)} total.")

    if args.json_path:
        with open(args.json_path, "w", encoding="utf-8") as fh:
            json.dump({"layer": args.layer, "findings": findings}, fh, indent=2)
        print(f"wrote {args.json_path}")

    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())
