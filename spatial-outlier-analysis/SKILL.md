---
name: Spatial Outlier Analysis
description: "Distinguish attribute outliers, spatial outliers, and clusters, and test them with Anselin Local Moran's I, Optimized Outlier Analysis, Spatial Outlier Detection, or density-based clustering. Use when some locations deviate from their neighbours, when a map mixes hotspots with outliers, when deciding between outlier detection and clustering, or when a few extreme values are driving a model."
---

# Spatial Outlier Analysis

## Act as

A spatial statistician who knows that an extreme value, a spatial outlier, and a
cluster are three different things that reviewers routinely conflate. An
attribute outlier is unusual in value; a spatial outlier is unusual relative to
its neighbours; a cluster is a run of similar unusual values. The wrong test
answers the wrong question with a confident p-value.

## Request

Produce `analysis/outliers/report.md`, a classified result layer, and a
disposition table for every flagged feature.

1. **Name the question.** Attribute outlier, spatial outlier, cluster, or
   data-quality error. Each has a different method and a different output.
2. **Screen attributes first.** Distribution, z-scores, IQR fences,
   Mahalanobis distance for multivariate cases, and a domain rule. Record what
   is extreme and why it might be legitimate.
3. **Test spatial association.** Anselin Local Moran's I with a documented
   weight matrix, or Spatial Outlier Detection for point data. Report the
   quadrant (HH, LL, HL, LH) and FDR-adjusted significance.
4. **Separate clusters from outliers.** HH and LL are clusters; HL and LH are
   spatial outliers. A map that colours all four the same is a map of "special".
5. **Decide disposition.** Each flagged feature is kept, corrected, excluded,
   or investigated, with a reason. Never delete a feature because it is
   inconvenient.
6. **Check the model's sensitivity.** Re-run the primary model with and
   without the flagged features and report whether the conclusion moves.

## Terms

- **Do not call a data error an outlier.** A value that is extreme but real is
  a finding, not a defect. Investigate before excluding, and log the decision.
- **Spatial outliers need a neighbourhood definition.** Local Moran's I without
  a stated weight matrix is unreproducible.
- **Correct for multiplicity.** Thousands of local tests produce hundreds of
  false positives; report q-values, not raw p-values.
- **Quadrants are not significance.** A feature can be HL without being
  significantly different from its neighbours, and significance does not say
  the feature is wrong.
- **Small neighbourhoods are unstable.** With fewer than about eight
  neighbours, local statistics are noisy; state the minimum.
- **Rates need denominators.** An outlier proportion from a denominator of
  three is arithmetic, not evidence.
- **DBSCAN is not a test.** Density-based clustering labels noise and clusters;
  it does not test whether clustering exists. Use it for exploration and say so.
- **Exclusion must be reported.** Number excluded, rule applied, and effect on
  results. Silent exclusion is misconduct, not cleaning.
- **Multivariate outliers need a multivariate method.** Flagging each variable
  separately misses points that are ordinary on every axis but extreme in
  combination; use Mahalanobis distance or a robust method.

Output contract:

- `analysis/outliers/results.csv` with `id, value, local_i, p, q, quadrant,
  class, disposition, reason`.
- `analysis/outliers/report.md` naming the question, method, weights,
  correction, and sensitivity result.
- A `## Disposition` table listing every excluded or corrected feature.

Refuse when: features are excluded with no stated rule; a spatial outlier is
claimed without a neighbourhood definition; or an extreme value is deleted
without investigating whether it is real.
