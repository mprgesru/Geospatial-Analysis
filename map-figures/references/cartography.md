# Cartography reference

## Decision table

| Question | Answer |
| --- | --- |
| Counts or rates? | Rates for choropleth. Counts need proportional symbols or a note. |
| Sequential or diverging? | Diverging only with a meaningful midpoint. |
| How many classes? | 5–7 for print; more than 7 is unreadable. |
| Which breaks? | Quantile for skewed rates, natural breaks for clusters, equal interval for comparison across maps, fixed thresholds for policy. |
| Point or areal uncertainty? | Prediction variance for points; interval width or classification stability for areas. |
| Vector or raster? | Vector for polygons and lines; 300–600 dpi raster for continuous surfaces. |

## Colour

- Sequential: `viridis`, `cividis`, `magma`, or a single-hue ramp.
- Diverging: `RdBu` or `BrBG`, centred on zero or a stated threshold.
- Qualitative: ColourBrewer `Set2` or `Dark2`, maximum about 8 categories.
- Avoid red-green pairs entirely; deuteranopia is common.
- Test in grayscale: if two classes collapse, change the ramp or add hatching.

## Python (matplotlib + geopandas)

```python
import matplotlib.pyplot as plt
import geopandas as gpd

fig, ax = plt.subplots(figsize=(7, 5), dpi=300)
gdf.plot(
    column="rate_per_1000",
    scheme="quantiles",
    k=5,
    cmap="viridis",
    legend=True,
    legend_kwds={"title": "Rate per 1,000", "fmt": "{:.1f}"},
    edgecolor="white",
    linewidth=0.3,
    ax=ax,
)
ax.set_axis_off()
ax.set_title("Incidence rate by district, 2024")
ax.annotate("EPSG:32633 · Source: ...", xy=(0.01, 0.01), xycoords="axes fraction", fontsize=6)
fig.savefig("outputs/figures/incidence.pdf", bbox_inches="tight")
```

Add a scale bar with `matplotlib_map_utils` or a manual line plus text; add a
north arrow only when the map is north-up. For an uncertainty companion,
repeat the panel with `column="variance"` and the same extent.

## R (ggplot2 + sf)

```r
library(ggplot2)
library(sf)

ggplot(d) +
  geom_sf(aes(fill = rate_per_1000), colour = "white", linewidth = 0.2) +
  scale_fill_viridis_c(name = "Rate per 1,000") +
  coord_sf(crs = 32633, datum = NA) +
  labs(title = "Incidence rate by district, 2024",
       caption = "EPSG:32633. Source: ...") +
  theme_void(base_size = 8)
```

Use `classInt::classIntervals()` for breaks and `scale_fill_manual()` when the
breaks must be fixed across panels.

## Export

| Output | Format | Setting |
| --- | --- | --- |
| Journal submission | PDF or SVG | Fonts embedded, no transparency flattening |
| Preprint | PNG | 300 dpi minimum |
| Presentation | PNG | 150 dpi, larger fonts |
| Colour proof | Grayscale PNG | Verify class separation |

Figure width for a two-column journal is typically 85 mm (single) or 170 mm
(double). Set the figure size in inches at final width and keep font sizes at
7–9 pt so the typesetter does not rescale the text.

## Caption template

> **Figure N.** *Quantity* in *units* across *study area*, *year*, classified
> by *method* with *k* classes. *Uncertainty* is shown in panel B as
> *variance / interval width*. Projection EPSG:*code*; scale bar in km.
> Source: *dataset*.

Every placeholder must be filled. A caption with "various" or "see text" is
incomplete.
