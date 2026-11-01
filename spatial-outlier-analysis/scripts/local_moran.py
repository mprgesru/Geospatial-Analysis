#!/usr/bin/env python3
"""Anselin Local Moran's I with analytical significance and FDR correction.

Usage:
    python local_moran.py features.gpkg --field value --k 8 [--out results.csv]

Weights are k-nearest-neighbour, row-standardised. Significance uses the
normal approximation (Anselin 1995), which is the same approach used by GeoDa
and ArcGIS Pro, and which permits FDR correction at large n. Two-sided p-values
are adjusted with Benjamini-Hochberg.

Why not permutation here: a permutation p-value is floored at 1/(perms+1).
With 999 permutations the smallest possible q across 500 features is
0.001 x 500 = 0.5, so nothing can survive FDR. Use 10,000+ permutations if you
prefer the permutation route.

Requires numpy and geopandas.
"""

from __future__ import annotations

import argparse
import csv
import sys
from math import erfc, sqrt

import numpy as np


def read_features(path: str, field: str, layer: str | None):
    import geopandas as gpd

    gdf = gpd.read_file(path, layer=layer) if layer else gpd.read_file(path)
    if field not in gdf.columns:
        raise SystemExit(f"field {field!r} not found; available: {list(gdf.columns)}")
    if gdf.crs is None:
        raise SystemExit("layer has no CRS; fix the data contract first")

    gdf = gdf[gdf[field].notna() & gdf.geometry.notna()].copy()
    if gdf.crs.is_geographic:
        gdf = gdf.to_crs(gdf.estimate_utm_crs())

    geom = gdf.geometry.representative_point()
    coords = np.column_stack([geom.x.to_numpy(), geom.y.to_numpy()])
    values = gdf[field].to_numpy(dtype=float)
    return coords, values


def knn_row_standardised(coords: np.ndarray, k: int) -> np.ndarray:
    n = len(coords)
    k = min(k, n - 1)
    diff = coords[:, None, :] - coords[None, :, :]
    dist = np.hypot(diff[..., 0], diff[..., 1])
    np.fill_diagonal(dist, np.inf)
    idx = np.argpartition(dist, k - 1, axis=1)[:, :k]
    w = np.zeros((n, n))
    w[np.repeat(np.arange(n), k), idx.ravel()] = 1.0
    row_sums = w.sum(axis=1, keepdims=True)
    return np.divide(w, row_sums, out=np.zeros_like(w), where=row_sums > 0)


def local_moran(values: np.ndarray, w: np.ndarray):
    n = len(values)
    z = values - values.mean()
    m2 = float(np.sum(z ** 2) / n)
    if m2 == 0:
        raise SystemExit("zero variance; nothing to test")

    lag = w @ z
    observed = (z / m2) * lag

    b2 = float(np.sum(z ** 4) / n / (m2 ** 2))  # kurtosis
    row_sums = w.sum(axis=1)
    squared_sums = (w ** 2).sum(axis=1)

    expected = -row_sums / (n - 1)
    variance = (
        squared_sums * (n - b2) / (n - 1)
        + ((row_sums ** 2 - squared_sums) * (2 * b2 - n)) / ((n - 1) * (n - 2))
        - (row_sums ** 2) / ((n - 1) ** 2)
    )

    unusable = variance <= 0
    if unusable.any():
        print(
            f"# warning: {int(unusable.sum())} features have non-positive analytical variance "
            "(heavy tails or degenerate weights); p-values there are unreliable and set to 1",
            file=sys.stderr,
        )
    safe = np.where(unusable, 1.0, variance)
    scores = (observed - expected) / np.sqrt(safe)
    p_values = np.array([erfc(abs(s) / sqrt(2.0)) for s in scores])
    p_values[unusable] = 1.0
    return z, lag, observed, scores, p_values


def bh_qvalues(p: np.ndarray) -> np.ndarray:
    n = len(p)
    order = np.argsort(p)
    ranked = p[order] * n / np.arange(1, n + 1)
    ranked = np.minimum.accumulate(ranked[::-1])[::-1]
    q = np.empty(n)
    q[order] = np.clip(ranked, 0.0, 1.0)
    return q


def quadrant(z: np.ndarray, lag: np.ndarray) -> list[str]:
    return [
        ("H" if zi >= 0 else "L") + ("H" if li >= 0 else "L")
        for zi, li in zip(z, lag)
    ]


def classify(quad: list[str], q: np.ndarray) -> list[str]:
    names = {
        "HH": "High-High Cluster",
        "LL": "Low-Low Cluster",
        "HL": "High-Low Outlier",
        "LH": "Low-High Outlier",
    }
    return [names[q_] if qi < 0.05 else "Not Significant" for q_, qi in zip(quad, q)]


def main() -> int:
    parser = argparse.ArgumentParser(description="Anselin Local Moran's I with FDR.")
    parser.add_argument("layer")
    parser.add_argument("--field", required=True)
    parser.add_argument("--layer", dest="layer_name", default=None)
    parser.add_argument("--k", type=int, default=8)
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    coords, values = read_features(args.layer, args.field, args.layer_name)
    n = len(values)
    if n < 20:
        raise SystemExit(f"only {n} features; too few for local statistics")

    w = knn_row_standardised(coords, args.k)
    z, lag, observed, scores, p = local_moran(values, w)
    q = bh_qvalues(p)
    quad = quadrant(z, lag)
    labels = classify(quad, q)

    counts: dict[str, int] = {}
    for label in labels:
        counts[label] = counts.get(label, 0) + 1

    print(f"# features: {n}   k = {args.k} (row-standardised)   significance: normal approximation   FDR: Benjamini-Hochberg")
    for label, count in sorted(counts.items(), key=lambda item: -item[1]):
        print(f"#   {label:22} {count}")
    print("# clusters are HH/LL; spatial outliers are HL/LH; significance uses q < 0.05")

    if args.out:
        with open(args.out, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(["x", "y", "value", "z", "lag", "local_i", "z_score", "p", "q", "quadrant", "class"])
            for i in range(n):
                writer.writerow([
                    f"{coords[i, 0]:.3f}", f"{coords[i, 1]:.3f}", f"{values[i]:.6f}",
                    f"{z[i]:.6f}", f"{lag[i]:.6f}", f"{observed[i]:.6f}",
                    f"{scores[i]:.4f}", f"{p[i]:.6f}", f"{q[i]:.6f}", quad[i], labels[i],
                ])
        print(f"# wrote {args.out}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
