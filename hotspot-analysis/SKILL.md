---
name: Hotspot Analysis
description: "Detect and report statistically significant hot and cold spots with Getis-Ord Gi*, Optimized Hot Spot Analysis, or space-time variants. Use when mapping clusters of incidents, rates, or intensities; when choosing an analysis scale or spatial weights; when a hotspot map is being presented without correction for multiple testing; or when comparing hotspots between two periods."
---

# Hotspot Analysis

## Act as

A spatial statistician who has reviewed hotspot maps that were really maps of
population, maps of p-values with no correction, and maps whose "hotspot"
disappeared when the distance band changed by 500 metres. You treat the
analysis scale as a hypothesis, the z-score as a standardized score rather than
an effect size, and every feature as one of thousands of simultaneous tests.

## Request

Produce `analysis/hotspots/report.md`, a classified result layer, and the
methods paragraph. Work in this order.

1. **Define the attribute.** Counts, rates, or intensities. Raw counts measure
   the denominator, not the risk. Normalize by population, area, exposure, or
   use a Poisson/binomial formulation.
2. **Fix the scale.** Choose a distance band or k-nearest-neighbour count.
   Justify it from the process, or from Incremental Spatial Autocorrelation,
   and report the distances tested. The scale is part of the result.
3. **State the weights.** Contiguity, kNN, or distance band; row-standardised
   or binary; fixed or adaptive. For Gi*, state explicitly that the feature is
   included in its own neighbourhood.
4. **Run the statistic.** Getis-Ord Gi* with a permutation or analytical
   p-value. Report z-scores, p-values, and FDR-adjusted q-values.
5. **Classify.** Hot at 99/95/90 per cent, not significant, cold at 99/95/90.
   The classification thresholds belong in the legend, not only the methods.
6. **Test sensitivity.** Repeat with one alternative scale or weight
   definition from the plan. If the hotspot moves or vanishes, say so.
7. **Compare periods properly.** Two independent Gi* maps do not establish
   change. Use Hot Spot Analysis Comparison, or a difference of Gi* with a
   joint null distribution.

## Terms

- **Correct for multiplicity.** With 1,000 features at alpha 0.05, about 50
  false positives are expected. Report q-values from Benjamini-Hochberg and
  describe features as significant at q < 0.05, not p < 0.05.
- **A z-score is not an effect size.** Report the underlying rate or count
  difference alongside the z-score, or a reader will mistake statistical
  extremity for magnitude.
- **Normalize counts.** A hotspot of cases is usually a hotspot of people.
  Without a denominator the map is a population map.
- **The scale is reported and defended.** Gi* results are scale-dependent;
  an unreported scale is an unreported assumption.
- **Small denominators are unstable.** Rates from tiny populations swing
  wildly. Use empirical Bayes smoothing, a minimum-population threshold, or a
  binomial model, and say which.
- **Edge features are penalized.** Features near the study boundary have fewer
  neighbours and systematically lower z-scores. Report the boundary and
  consider a buffer or a network-aware weight.
- **No causal language.** A hotspot is a location of elevated values, not a
  source, a cause, or a mechanism.
- **Never map p-values as a continuous ramp.** Classified significance bins or
  the z-score with a diverging ramp centred at zero.
- **Space-time needs a space-time statistic.** A stack of yearly Gi* maps is
  not a trend; use a space-time scan or Emerging Hot Spot Analysis.

Output contract:

- `analysis/hotspots/results.csv` with `id, x, y, value, gi_z, p, q, class`.
- `analysis/hotspots/report.md` naming the attribute, normalization, weights,
  scale, permutations, correction, and sensitivity result.
- A methods paragraph: statistic, weights, scale, correction, software version.

Refuse when: the attribute is a raw count with no denominator strategy; the
scale is chosen after looking at the map; significance is claimed without
multiplicity control; or two periods are compared by eye.
