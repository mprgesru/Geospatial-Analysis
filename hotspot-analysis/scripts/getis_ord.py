#!/usr/bin/env python3
"""Getis-Ord Gi* with k-nearest-neighbour weights and Benjamini-Hochberg FDR.

Usage:
    python getis_ord.py points.gpkg --field rate --k 8 [--sims 999] [--out results.csv]

Gi* includes the feature itself in its neighbourhood (w_ii = 1). p-values are
two-sided from the normal approximation. q-values are Benjamini-Hochberg over
all features.

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

    if not gdf.geom_type.isin(["Point", "MultiPoint"]).all():
        print("# note: non-point geometry; using representative points", file=sys.stderr)
        geom = gdf.geometry.representative_point()
    else:
        geom = gdf.geometry

    coords = np.column_stack([geom.x.to_numpy(), geom.y.to_numpy()])
    values = gdf[field].to_numpy(dtype=float)
    return coords, values, gdf


def knn_weights(coords: np.ndarray, k: int) -> np.ndarray:
    n = len(coords)
    k = min(k, n - 1)
    diff = coords[:, None, :] - coords[None, :, :]
    dist = np.hypot(diff[..., 0], diff[..., 1])
    np.fill_diagonal(dist, np.inf)
    idx = np.argpartition(dist, k - 1, axis=1)[:, :k]
    w = np.zeros((n, n))
    w[np.repeat(np.arange(n), k), idx.ravel()] = 1.0
    w = np.maximum(w, w.T)
    np.fill_diagonal(w, 1.0)  # Gi* includes the feature itself
    return w


def gi_star(values: np.ndarray, w: np.ndarray) -> np.ndarray:
    n = len(values)
    mean = values.mean()
    sd = sqrt(max(np.mean(values ** 2) - mean ** 2, 0.0))
    if sd == 0:
        return np.zeros(n)
    row_sums = w.sum(axis=1)
    w_sq_sums = (w ** 2).sum(axis=1)
    local_sum = w @ values
    denominator = sd * np.sqrt((n * w_sq_sums - row_sums ** 2) / (n - 1))
    denominator = np.where(denominator == 0, np.nan, denominator)
    return (local_sum - mean * row_sums) / denominator


def bh_qvalues(p: np.ndarray) -> np.ndarray:
    n = len(p)
    order = np.argsort(p)
    ranked = p[order] * n / np.arange(1, n + 1)
    ranked = np.minimum.accumulate(ranked[::-1])[::-1]
    q = np.empty(n)
    q[order] = np.clip(ranked, 0.0, 1.0)
    return q


def classify(q: np.ndarray, z: np.ndarray) -> list[str]:
    labels = []
    for qi, zi in zip(q, z):
        if np.isnan(qi) or qi >= 0.10:
            labels.append("Not Significant")
            continue
        level = "99" if qi < 0.01 else ("95" if qi < 0.05 else "90")
        labels.append(f"Hot {level}" if zi > 0 else f"Cold {level}")
    return labels


def main() -> int:
    parser = argparse.ArgumentParser(description="Getis-Ord Gi* with FDR correction.")
    parser.add_argument("layer")
    parser.add_argument("--field", required=True)
    parser.add_argument("--layer", dest="layer_name", default=None)
    parser.add_argument("--k", type=int, default=8)
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    coords, values, gdf = read_features(args.layer, args.field, args.layer_name)
    n = len(values)
    if n < 10:
        raise SystemExit(f"only {n} features; too few for a local statistic")

    if (values < 0).any():
        print("# warning: negative values; Gi* assumes a non-negative attribute", file=sys.stderr)

    w = knn_weights(coords, args.k)
    z = gi_star(values, w)
    p = np.array([erfc(abs(zi) / sqrt(2.0)) for zi in z])
    q = bh_qvalues(p)
    labels = classify(q, z)

    n_sig = sum(1 for label in labels if label != "Not Significant")
    n_expected = 0.05 * n
    hot = sum(1 for label in labels if label.startswith("Hot"))
    cold = sum(1 for label in labels if label.startswith("Cold"))

    print(f"# features: {n}   k = {args.k} (self included)   FDR = Benjamini-Hochberg")
    print(f"# significant at q < 0.05: {n_sig}   expected false positives at p < 0.05 before correction: {n_expected:.1f}")
    print(f"# hot: {hot}   cold: {cold}")
    print("# a z-score is not an effect size; report the underlying values too")

    if args.out:
        with open(args.out, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(["x", "y", "value", "gi_z", "p", "q", "class"])
            xs = gdf.geometry.representative_point().x.to_numpy()
            ys = gdf.geometry.representative_point().y.to_numpy()
            for i in range(n):
                writer.writerow([
                    f"{xs[i]:.3f}", f"{ys[i]:.3f}", f"{values[i]:.6f}",
                    f"{z[i]:.4f}", f"{p[i]:.6f}", f"{q[i]:.6f}", labels[i],
                ])
        print(f"# wrote {args.out}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
