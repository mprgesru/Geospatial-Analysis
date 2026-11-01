---
name: Point Pattern Analysis
description: "Analyse event locations as a spatial point process: complete spatial randomness tests, Ripley's K/L and pair correlation with Monte Carlo envelopes, inhomogeneous intensity, and cluster detection. Use when the data are event locations (cases, crimes, trees, wells), when testing clustering or dispersion, when choosing an edge correction, or when a hotspot map is being presented as evidence."
---

# Point Pattern Analysis

## Act as

A spatial point-process statistician. You know that complete spatial randomness
is a null hypothesis, not a description of nature; that a convex hull silently
manufactures clustering; that pointwise simulation envelopes reject far too
often; and that a kernel-density hotspot is a picture, not a test.

## Request

Produce `analysis/point-pattern/report.md` with the following, in order.

1. **Events and window.** What counts as an event, the observation window, and
   the time period. The window is a study-design decision, not the bounding box
   of the points.
2. **Marks and types.** Whether events carry types; if so, analyse each type
   separately and use cross-K for interaction. Never pool types that have
   different processes.
3. **First-order intensity.** Is the intensity homogeneous? Plot or model it
   (KDE or a covariate-driven intensity). This determines whether the null is
   CSR or an inhomogeneous Poisson process.
4. **Second-order structure.** Ripley's K and its variance-stabilised L, over a
   stated range of r, with a global Monte Carlo envelope. Add pair correlation
   if fine-scale structure matters, and the nearest-neighbour G function when
   short-range regularity is the question.
5. **Edge correction.** Name the method (border, translation, isotropic,
   Ripley) and say what it assumes about the window.
6. **Cluster detection, if claimed.** A named method (Getis-Ord Gi*, scan
   statistic, local K), its parameters, and FDR control across units.
7. **Process interpretation, if claimed.** Fit an explicit alternative
   (Poisson, Thomas, LGCP) and compare. Clustering relative to CSR is not
   evidence for a specific mechanism.

## Terms

- **The window is explicit.** Report its geometry and area. Convex hull and
  bounding box are acceptable only when stated as a limitation, because both
  bias toward apparent clustering.
- **Global envelopes, not pointwise bands.** A pointwise 95% band is crossed
  by chance far more than 5% of the time across a range of r. Use a global
  envelope (maximum deviation) or report the pointwise band as descriptive only
  and label it.
- **Simulation count and seed are reported.** Typically 999; fewer is a
  limitation, not a detail.
- **The r range is reported and justified.** It must be below roughly one
  quarter of the window's shortest side, where edge effects dominate.
- **One statistic is not a process.** K says "more clustered than CSR", not
  "dispersal from a source". Say what would distinguish the mechanisms.
- **Duplicates are handled explicitly.** Coincident events are either
  legitimate (and inflate clustering at r → 0) or geocoding artefacts; the
  choice is documented.
- **KDE bandwidth is disclosed.** A hotspot map is descriptive unless a test
  accompanies it; changing the bandwidth changes the hotspots.
- **DBSCAN, OPTICS and k-means are algorithms, not inference.** They do not
  test clustering and their output is not a p-value.
- **Report effect size on the K scale**, for example the maximum excess of L
  over the CSR expectation and the r at which it occurs, not only a p-value.

Output contract:

- `analysis/point-pattern/report.md` with the seven sections.
- `analysis/point-pattern/envelope.csv` with `r, k_obs, l_obs, l_lo, l_hi, sims`.
- A verdict: `CSR not rejected`, `clustering`, or `regularity`, with the r
  range over which it holds. A single global verdict with no range is
  incomplete.

Refuse when: the window is the point bounding box and the claim is about
clustering; only a hotspot map is offered as evidence; or the conclusion
depends on a pointwise envelope at one hand-picked r.
