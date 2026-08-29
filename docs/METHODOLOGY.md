# Methodology

## Research Design

This project runs a fixed analytical funnel: **Data Acquisition → Data Engineering → Exploratory Analysis → Regional Comparison → Spending-Relationship Analysis → Market Segmentation → Market Attractiveness → Strategic Translation**, implemented as `src/` scripts (the reproducible source of truth) and mirrored narratively in `notebooks/01`–`07` (the walkthrough).

## Analytical Grain

**Country × Year**, 2013–2023, from a single primary source (World Bank Open Data). One source was used deliberately — see `docs/SOURCES.md` for the evaluation of alternatives — to avoid the definitional and methodological mismatches that arise when blending national-accounts figures from different agencies.

## Regional Classification

The brief's 8-region framework has no single official source. This project builds it from the **UN M49 standard** (an authoritative, publicly documented geographic classification), mapping UN sub-regions to the 8 Project 007 regions with a transparent, mostly-mechanical rule, plus three explicitly documented manual overrides where UN M49 diverges from standard market-research convention (full detail: `data/processed/REGION_MAPPING.csv`, Notes column, and Notebook 02).

## Currency & Comparability

Per Section 8 of the brief, this project distinguishes carefully between value bases:

| Use case | Column used | Why |
|---|---|---|
| Cross-country income/spending level comparison | `gdp_per_capita_ppp_current_intl`, or nominal per-capita when PPP unavailable | PPP adjusts for local price-level differences, which is essential for a valid cross-country comparison |
| Growth / CAGR / trend calculations | `household_consumption_expenditure_constant_2015_usd` (and its per-capita form) | Constant-price (real) series isolate volume growth from inflation and exchange-rate movements — nominal-USD growth would conflate a market's real growth with currency depreciation/appreciation against the dollar (see `LIMITATIONS.md` for a concrete example: Japan's nominal-USD consumption fell 2013–2023 largely due to yen depreciation, not falling real demand) |
| Regional/global spending totals and shares | `household_consumption_expenditure_current_usd` (nominal) | Necessary for a like-for-like sum of "how much is spent," but read with the caveat that exchange-rate movements affect the USD total independent of local spending behaviour |

**No analysis in this project compares nominal-USD levels across countries without noting this caveat**, and no growth or CAGR figure anywhere in this project is computed on a nominal basis.

## Derived Metrics

- **YoY real growth**: `pct_change()` of the constant-2015-USD consumption series, per country
- **CAGR (2013–2023)**: computed per country between its first and last available year in that window (not always exactly 2013/2023 — the actual years used are stored in `cagr_start_year`/`cagr_end_year`)
- **Global / regional consumption share**: each country's nominal consumption expenditure divided by the global (or regional) total, both computed from each country's own latest available year
- **Per-capita cross-check**: an independently computed `consumption / population` figure is included alongside World Bank's own per-capita series as a sanity check (see Notebook 02 / `DATA_DICTIONARY.md`)

## Statistical Methods

- **Descriptive statistics**: mean, median, percentiles, and distribution shape (Notebook 03)
- **Correlation**: Pearson r with p-values, computed pairwise on available (non-missing) data for each pair — sample size `n` is reported for every correlation, since it varies by indicator completeness (Notebook 05, `outputs/tables/correlation_analysis.csv`). **No correlation in this project is interpreted as causal** — see `LIMITATIONS.md`.
- **Segmentation**: K-Means clustering on standardised (z-scored) variables, with **k selected by comparing silhouette scores for k=3 through k=7** rather than assumed in advance (k=4 was selected). PCA (2 components, 73% of variance) used for visualisation only, not for clustering itself. Full detail: Notebook 06.
- **Market attractiveness composite**: see `MARKET_ATTRACTIVENESS_METHODOLOGY.md` for the full write-up (weighting, normalisation, and sensitivity analysis).

## Reproducibility

Every number in this project traces back to a script in `src/` that can be re-run against the committed raw data (or re-fetched live from the World Bank API) — see the root `README.md`'s "Reproducibility" section for exact commands. No manual/undocumented data edits were made anywhere in the pipeline.
