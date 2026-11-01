#!/usr/bin/env python3
"""Ordinary kriging with leave-one-out and spatial block validation.

Usage:
    python ok_kriging.py points.gpkg --field Z \
        --model exponential --nugget 0.1 --sill 4.2 --range 1200 \
        [--blocks 4] [--grid 120] [--out grid.csv]

Requires only numpy and geopandas. For universal, regression, indicator or
block kriging, use gstat (R) or scikit-gstat/GSTools; those variants are out of
scope for this screening implementation.

The variogram parameters must come from `geostatistical-diagnostics`; this
script deliberately does not fit them.
"""

from __future__ import annotations

import argparse
import csv
import sys

import numpy as np


def read_points(path: str, field: str, layer: str | None):
    import geopandas as gpd

    gdf = gpd.read_file(path, layer=layer) if layer else gpd.read_file(path)
    if field not in gdf.columns:
        raise SystemExit(f"field {field!r} not found; available: {list(gdf.columns)}")
    if gdf.crs is None:
        raise SystemExit("layer has no CRS; fix the data contract first")

    gdf = gdf[gdf[field].notna() & gdf.geometry.notna()].copy()
    if gdf.crs.is_geographic:
        gdf = gdf.to_crs(gdf.estimate_utm_crs())

    coords = np.column_stack([gdf.geometry.x.to_numpy(), gdf.geometry.y.to_numpy()])
    z = gdf[field].to_numpy(dtype=float)
    return coords, z, gdf.crs


def pairwise(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    diff = a[:, None, :] - b[None, :, :]
    return np.hypot(diff[..., 0], diff[..., 1])


def gamma(h: np.ndarray, model: str, nugget: float, sill: float, rng: float) -> np.ndarray:
    h = np.asarray(h, dtype=float)
    partial = max(sill - nugget, 0.0)
    if model == "exponential":
        g = nugget + partial * (1.0 - np.exp(-h / rng))
    elif model == "spherical":
        ratio = np.minimum(h / rng, 1.0)
        g = nugget + partial * (1.5 * ratio - 0.5 * ratio ** 3)
        g = np.where(h >= rng, sill, g)
    elif model == "gaussian":
        g = nugget + partial * (1.0 - np.exp(-(h ** 2) / (rng ** 2)))
    else:
        raise SystemExit(f"unknown model {model!r}")
    return np.where(h == 0.0, 0.0, g)


def ok_predict(train_xy, train_z, target_xy, vario):
    n = len(train_z)
    a = gamma(pairwise(train_xy, train_xy), **vario)
    np.fill_diagonal(a, 0.0)
    system = np.ones((n + 1, n + 1))
    system[:n, :n] = a
    system[n, n] = 0.0

    b = gamma(pairwise(target_xy, train_xy), **vario).T
    rhs = np.vstack([b, np.ones((1, target_xy.shape[0]))])

    solution = np.linalg.solve(system, rhs)
    weights = solution[:n, :]
    mu = solution[n, :]

    prediction = weights.T @ train_z
    variance = np.sum(weights * b, axis=0) + mu
    return prediction, np.maximum(variance, 0.0)


def loo(coords, z, vario):
    n = len(z)
    if n > 400:
        raise SystemExit(
            f"{n} points is too many for exact leave-one-out here; use spatial blocks "
            "or raise the cap deliberately in the script"
        )
    errors = np.empty(n)
    for i in range(n):
        mask = np.ones(n, dtype=bool)
        mask[i] = False
        pred, _ = ok_predict(coords[mask], z[mask], coords[i : i + 1], vario)
        errors[i] = z[i] - pred[0]
    return errors


def block_cv(coords, z, vario, blocks: int):
    minx, miny = coords.min(axis=0)
    maxx, maxy = coords.max(axis=0)
    ix = np.clip(((coords[:, 0] - minx) / (maxx - minx + 1e-12) * blocks).astype(int), 0, blocks - 1)
    iy = np.clip(((coords[:, 1] - miny) / (maxy - miny + 1e-12) * blocks).astype(int), 0, blocks - 1)
    fold = iy * blocks + ix

    errors, separations = [], []
    for f in np.unique(fold):
        test = fold == f
        train = ~test
        if test.sum() == 0 or train.sum() < 10:
            continue
        pred, _ = ok_predict(coords[train], z[train], coords[test], vario)
        errors.extend(z[test] - pred)
        d = pairwise(coords[test], coords[train])
        separations.append(float(d.min()))
    return np.array(errors), separations


def metrics(errors: np.ndarray) -> dict:
    e = np.asarray(errors, dtype=float)
    return {
        "n": int(e.size),
        "rmse": float(np.sqrt(np.mean(e ** 2))),
        "mae": float(np.mean(np.abs(e))),
        "bias": float(np.mean(e)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Ordinary kriging with spatial validation.")
    parser.add_argument("layer")
    parser.add_argument("--field", required=True)
    parser.add_argument("--layer", dest="layer_name", default=None)
    parser.add_argument("--model", default="exponential", choices=["exponential", "spherical", "gaussian"])
    parser.add_argument("--nugget", type=float, required=True)
    parser.add_argument("--sill", type=float, required=True)
    parser.add_argument("--range", dest="rng", type=float, required=True)
    parser.add_argument("--blocks", type=int, default=4)
    parser.add_argument("--grid", type=int, default=0, help="write an N x N prediction grid")
    parser.add_argument("--out", default="grid.csv")
    args = parser.parse_args()

    coords, z, crs = read_points(args.layer, args.field, args.layer_name)
    vario = {
        "model": args.model,
        "nugget": args.nugget,
        "sill": args.sill,
        "rng": args.rng,
    }

    print(f"# units: {crs.to_string()}")
    print(f"# n = {len(z)}   variogram: {args.model}(nugget={args.nugget}, sill={args.sill}, range={args.rng})")
    if args.nugget > 0:
        print("# note: non-zero nugget, so predictions do not reproduce observations exactly")

    loo_err = loo(coords, z, vario)
    m = metrics(loo_err)
    print(f"\n# leave-one-out   n={m['n']}  RMSE={m['rmse']:.4f}  MAE={m['mae']:.4f}  bias={m['bias']:.4f}")

    cv_err, separations = block_cv(coords, z, vario, args.blocks)
    if cv_err.size:
        mb = metrics(cv_err)
        print(
            f"# spatial blocks   n={mb['n']}  RMSE={mb['rmse']:.4f}  "
            f"MAE={mb['mae']:.4f}  bias={mb['bias']:.4f}"
        )
        print(f"# min train/test separation: {min(separations):.1f} (should exceed the fitted range)")
        if min(separations) < args.rng:
            print("# WARNING: a fold is closer than the fitted range; the block size leaks")

    if args.grid:
        xs = np.linspace(coords[:, 0].min(), coords[:, 0].max(), args.grid)
        ys = np.linspace(coords[:, 1].min(), coords[:, 1].max(), args.grid)
        gx, gy = np.meshgrid(xs, ys)
        targets = np.column_stack([gx.ravel(), gy.ravel()])
        pred, var = ok_predict(coords, z, targets, vario)
        with open(args.out, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(["x", "y", "prediction", "variance"])
            for (x, y), p, v in zip(targets, pred, var):
                writer.writerow([f"{x:.3f}", f"{y:.3f}", f"{p:.6f}", f"{v:.6f}"])
        print(f"\n# wrote {args.grid * args.grid} predictions to {args.out}")
        print("# predictions outside the convex hull are extrapolation; mask them before mapping")

    return 0


if __name__ == "__main__":
    sys.exit(main())
