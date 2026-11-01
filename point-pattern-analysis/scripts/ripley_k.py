#!/usr/bin/env python3
"""Ripley's K/L against complete spatial randomness, with Monte Carlo envelopes.

Usage:
    python ripley_k.py events.gpkg [--window boundary.gpkg] [--sims 999]
                        [--r-max auto] [--seed 0] [--out envelope.csv]

The estimator is the raw (uncorrected) K. Because the simulated CSR patterns
are generated in the same window and scored with the same estimator, the
comparison is valid; the raw estimator alone is biased near edges, which is
why the absolute K values are not reported as truth.

Requires numpy, geopandas, shapely.
"""

from __future__ import annotations

import argparse
import csv
import sys

import numpy as np


def read_events(path: str, layer: str | None):
    import geopandas as gpd

    gdf = gpd.read_file(path, layer=layer) if layer else gpd.read_file(path)
    if gdf.crs is None:
        raise SystemExit("layer has no CRS; fix the data contract first")
    if gdf.crs.is_geographic:
        gdf = gdf.to_crs(gdf.estimate_utm_crs())
    gdf = gdf[gdf.geometry.notna()]
    coords = np.column_stack([gdf.geometry.x.to_numpy(), gdf.geometry.y.to_numpy()])
    return coords, gdf.crs


def read_window(path: str, layer: str | None, coords: np.ndarray, crs, mode: str):
    import geopandas as gpd
    from shapely.geometry import MultiPoint, box

    if path:
        win = gpd.read_file(path, layer=layer) if layer else gpd.read_file(path)
        if win.crs is None:
            raise SystemExit("window layer has no CRS")
        win = win.to_crs(crs)
        geom = win.geometry.union_all()
        return geom, "explicit window"

    if mode == "hull":
        hull = MultiPoint(coords).convex_hull
        return hull, "convex hull (distorts the null; supply the real window)"

    minx, miny = coords.min(axis=0)
    maxx, maxy = coords.max(axis=0)
    return box(minx, miny, maxx, maxy), "bounding box (conservative; supply the real window)"


def distances(a: np.ndarray, b: np.ndarray | None = None) -> np.ndarray:
    if b is None:
        b = a
    diff = a[:, None, :] - b[None, :, :]
    return np.hypot(diff[..., 0], diff[..., 1])


def k_function(d: np.ndarray, radii: np.ndarray, area: float) -> np.ndarray:
    n = d.shape[0]
    out = np.empty(len(radii))
    np.fill_diagonal(d, np.inf)
    for i, r in enumerate(radii):
        out[i] = area * np.count_nonzero(d <= r) / (n * (n - 1))
    return out


def simulate(n: int, window, bounds, rng) -> np.ndarray:
    minx, miny, maxx, maxy = bounds
    points = []
    total = 0
    while len(points) < n:
        need = max(64, (n - len(points)) * 4)
        cand = np.column_stack(
            [rng.uniform(minx, maxx, need), rng.uniform(miny, maxy, need)]
        )
        from shapely import contains_xy

        inside = contains_xy(window, cand[:, 0], cand[:, 1])
        points.extend(cand[inside])
        total += need
        if total > 200 * n:
            raise SystemExit("rejection sampling failed; check the window geometry")
    return np.asarray(points[:n])


def main() -> int:
    parser = argparse.ArgumentParser(description="Ripley's K/L with Monte Carlo envelope.")
    parser.add_argument("events")
    parser.add_argument("--window", default=None, help="polygon file defining the study window")
    parser.add_argument("--window-layer", default=None)
    parser.add_argument("--window-mode", default="bbox", choices=["bbox", "hull"],
                        help="fallback window when --window is omitted")
    parser.add_argument("--sims", type=int, default=999)
    parser.add_argument("--r-max", type=float, default=0.0, help="maximum r; default = quarter of the shortest side")
    parser.add_argument("--steps", type=int, default=20)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out", default="envelope.csv")
    args = parser.parse_args()

    coords, crs = read_events(args.events, None)
    n = len(coords)
    if n < 20:
        raise SystemExit(f"only {n} events; too few for a stable K function")

    window, window_note = read_window(args.window, args.window_layer, coords, crs, args.window_mode)
    area = float(window.area)
    minx, miny, maxx, maxy = window.bounds
    shortest = min(maxx - minx, maxy - miny)
    r_max = args.r_max if args.r_max > 0 else 0.25 * shortest

    radii = np.linspace(r_max / args.steps, r_max, args.steps)
    d_obs = distances(coords)
    k_obs = k_function(d_obs, radii, area)
    l_obs = np.sqrt(k_obs / np.pi) - radii

    dup = int(np.count_nonzero(np.triu(d_obs == 0, 1)))
    if dup:
        print(f"# warning: {dup} coincident event pairs; they inflate clustering near r = 0", file=sys.stderr)

    rng = np.random.default_rng(args.seed)
    sims = args.sims
    if n > 800:
        sims = min(sims, 199)
        print(f"# warning: large n; reduced simulations to {sims}", file=sys.stderr)

    l_sim = np.empty((sims, len(radii)))
    for s in range(sims):
        pts = simulate(n, window, (minx, miny, maxx, maxy), rng)
        k = k_function(distances(pts), radii, area)
        l_sim[s] = np.sqrt(k / np.pi) - radii

    lo = np.quantile(l_sim, 0.025, axis=0)
    hi = np.quantile(l_sim, 0.975, axis=0)

    # Global test: maximum absolute deviation of L from the CSR expectation (zero).
    t_obs = float(np.max(np.abs(l_obs)))
    t_sim = np.max(np.abs(l_sim), axis=1)
    p_global = float((1 + np.count_nonzero(t_sim >= t_obs)) / (sims + 1))

    print(f"# events: {n}   window: {window_note}")
    print(f"# window area: {area:.1f}   r range: {radii[0]:.1f} to {radii[-1]:.1f}   simulations: {sims}   seed: {args.seed}")
    print(f"# global p (max |L| deviation): {p_global:.4f}")

    with open(args.out, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["r", "k_obs", "l_obs", "l_lo", "l_hi", "sims"])
        for r, k, l, a, b in zip(radii, k_obs, l_obs, lo, hi):
            writer.writerow([f"{r:.3f}", f"{k:.3f}", f"{l:.4f}", f"{a:.4f}", f"{b:.4f}", sims])

    print(f"# wrote {args.out}")
    print("\n# r range where the observed L leaves the envelope is the range of evidence.")
    print("# a single p-value with no r range is an incomplete result")
    return 0


if __name__ == "__main__":
    sys.exit(main())
