#!/usr/bin/env python3
"""Fast screening diagnostics for spatial dependence.

Computes Moran's I with k-nearest-neighbour weights and a permutation test,
then an experimental semivariogram with a grid-searched exponential fit.

Usage:
    python spatial_structure.py points.gpkg --field Z [--k 8] [--permutations 999]

This is a dependency-light screen, deliberately not a substitute for
PySAL/esda or gstat/GSTools. Reconcile before reporting. Requires numpy and
geopandas.
"""

from __future__ import annotations

import argparse
import sys

import numpy as np


def read_points(path: str, field: str, layer: str | None):
    import geopandas as gpd

    gdf = gpd.read_file(path, layer=layer) if layer else gpd.read_file(path)
    if field not in gdf.columns:
        raise SystemExit(f"field {field!r} not found; available: {list(gdf.columns)}")
    if gdf.crs is None:
        raise SystemExit("layer has no CRS; resolve this in the data contract first")

    gdf = gdf[gdf[field].notna() & gdf.geometry.notna()].copy()
    if len(gdf) < 8:
        raise SystemExit(f"only {len(gdf)} usable features; too few for a variogram")
    if gdf.crs.is_geographic:
        target = gdf.estimate_utm_crs()
        gdf = gdf.to_crs(target)
        print(f"# reprojected to {gdf.crs.to_string()} for metric distances", file=sys.stderr)

    coords = np.column_stack([gdf.geometry.x.to_numpy(), gdf.geometry.y.to_numpy()])
    z = gdf[field].to_numpy(dtype=float)
    return coords, z, gdf.crs


def distance_matrix(coords: np.ndarray) -> np.ndarray:
    diff = coords[:, None, :] - coords[None, :, :]
    return np.hypot(diff[..., 0], diff[..., 1])


def knn_weights(dist: np.ndarray, k: int) -> np.ndarray:
    n = dist.shape[0]
    k = min(k, n - 1)
    work = dist.copy()
    np.fill_diagonal(work, np.inf)
    idx = np.argpartition(work, k - 1, axis=1)[:, :k]
    w = np.zeros((n, n))
    w[np.repeat(np.arange(n), k), idx.ravel()] = 1.0
    return np.maximum(w, w.T)


def morans_i(z: np.ndarray, w: np.ndarray) -> float:
    dev = z - z.mean()
    s0 = w.sum()
    if s0 == 0:
        return float("nan")
    return float(len(z) / s0 * (dev @ w @ dev) / (dev @ dev))


def permutation_test(z: np.ndarray, w: np.ndarray, n_perm: int, seed: int) -> tuple[float, float]:
    observed = morans_i(z, w)
    expected = -1.0 / (len(z) - 1)
    rng = np.random.default_rng(seed)
    exceed = 0
    for _ in range(n_perm):
        permuted = rng.permutation(z)
        stat = morans_i(permuted, w)
        if abs(stat - expected) >= abs(observed - expected):
            exceed += 1
    p_value = (exceed + 1) / (n_perm + 1)
    return observed, float(p_value)


def experimental_variogram(dist: np.ndarray, z: np.ndarray, n_bins: int = 15):
    n = len(z)
    iu = np.triu_indices(n, 1)
    d = dist[iu]
    semivar = 0.5 * (z[iu[0]] - z[iu[1]]) ** 2

    max_lag = 0.5 * float(d.max())
    edges = np.linspace(0.0, max_lag, n_bins + 1)
    which = np.digitize(d, edges) - 1

    rows = []
    for b in range(n_bins):
        m = which == b
        if m.sum() < 30:
            continue
        rows.append(
            (
                float(edges[b]),
                float(edges[b + 1]),
                float(0.5 * (edges[b] + edges[b + 1])),
                int(m.sum()),
                float(semivar[m].mean()),
            )
        )
    return np.array(rows)


def fit_exponential(lag: np.ndarray, gamma: np.ndarray, pairs: np.ndarray):
    """Weighted grid search: gamma(h) = nugget + (sill - nugget)(1 - exp(-h/range))."""
    best_sse = np.inf
    best = (np.nan, np.nan, np.nan)
    g_max = float(gamma.max())

    for nugget in np.linspace(0.0, 0.9 * g_max, 19):
        for sill in np.linspace(max(nugget, float(gamma.min())), 1.2 * g_max, 19):
            for rng in np.geomspace(max(float(lag.min()), 1e-9), float(lag.max()) * 2.0, 40):
                model = nugget + (sill - nugget) * (1.0 - np.exp(-lag / rng))
                weights = pairs / (lag ** 2)
                sse = float(np.sum(weights * (gamma - model) ** 2))
                if sse < best_sse:
                    best_sse = sse
                    best = (float(nugget), float(sill), float(rng))
    return best


def main() -> int:
    parser = argparse.ArgumentParser(description="Screening diagnostics for spatial dependence.")
    parser.add_argument("layer")
    parser.add_argument("--field", required=True, help="numeric attribute to analyse")
    parser.add_argument("--layer", dest="layer_name", default=None)
    parser.add_argument("--k", type=int, default=8, help="neighbours for Moran's I weights")
    parser.add_argument("--permutations", type=int, default=999)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--bins", type=int, default=15)
    args = parser.parse_args()

    coords, z, crs = read_points(args.layer, args.field, args.layer_name)

    sentinels = {-99999.0, -9999.0, -999.0, -32768.0, 9999.0}
    n_sentinel = int(np.isin(z, list(sentinels)).sum())
    if n_sentinel:
        print(
            f"# warning: {n_sentinel} values match common missing-data sentinels; "
            "resolve through the data contract before interpreting these results",
            file=sys.stderr,
        )

    if len(z) > 4000:
        print(
            f"# warning: {len(z)} features; the dense distance matrix may need several GB",
            file=sys.stderr,
        )

    dist = distance_matrix(coords)
    w = knn_weights(dist, args.k)

    observed, p_value = permutation_test(z, w, args.permutations, args.seed)
    expected = -1.0 / (len(z) - 1)

    print(f"# units: {crs.to_string() if crs else 'unknown'}")
    print(f"# n = {len(z)}")
    print(f"# Moran's I (knn k={args.k}, binary, symmetrised, {args.permutations} permutations)")
    print(f"Morans_I        {observed:.4f}")
    print(f"expected_I      {expected:.4f}")
    print(f"p_two_sided     {p_value:.4f}")

    rows = experimental_variogram(dist, z, args.bins)
    if len(rows) < 3:
        print("\n# too few populated bins for a variogram fit; increase the extent or the bin count")
        return 0

    print("\n# experimental semivariogram")
    print(f"{'lag_lo':>12} {'lag_hi':>12} {'lag_mid':>12} {'pairs':>8} {'gamma':>12}")
    for lo, hi, mid, pairs, gamma in rows:
        print(f"{lo:12.1f} {hi:12.1f} {mid:12.1f} {int(pairs):8d} {gamma:12.4f}")

    nugget, sill, rng = fit_exponential(rows[:, 2], rows[:, 4], rows[:, 3])
    print("\n# exponential fit (weighted by pairs / lag^2)")
    print(f"nugget          {nugget:.4f}")
    print(f"sill            {sill:.4f}")
    print(f"range           {rng:.1f}")
    print(f"practical_range {3.0 * rng:.1f}   (3 x range, 95% of sill)")
    print(f"nugget_ratio    {nugget / sill if sill else float('nan'):.3f}")
    print("\n# screen only: confirm with PySAL/esda or gstat/GSTools before reporting")
    return 0


if __name__ == "__main__":
    sys.exit(main())
