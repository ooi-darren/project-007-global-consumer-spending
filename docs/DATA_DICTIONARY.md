# Data Dictionary

Defines every column in `data/processed/master_consumer_spending.csv` and `data/processed/latest_year_snapshot.csv`. Every figure originates from the World Bank Open Data API (see `SOURCES.md`) and is classified **PUBLIC** — fetched and read directly this project, with no third-party or estimated figures in the core panel.

## Identifier columns

| Column | Type | Description |
|---|---|---|
| `ISO3` | string | ISO 3166-1 alpha-3 country code |
| `Country` | string | Country/economy name, as published by World Bank |
| `Year` | int | Calendar year of the observation |
| `Project_007_Region` | string | This project's 8-region classification — see `REGION_MAPPING.csv` and `docs/METHODOLOGY.md` |
| `Official_Region` | string | World Bank's own regional classification (7 regions) |
| `Sub_Region` | string | UN M49 sub-region |

## Economic & demographic indicators

| Column | Unit | World Bank code | Notes |
|---|---|---|---|
| `population_total` | persons | `SP.POP.TOTL` | |
| `urban_population_pct` | % of total population | `SP.URB.TOTL.IN.ZS` | |
| `population_65_plus_pct` | % of total population | `SP.POP.65UP.TO.ZS` | |
| `age_dependency_ratio_pct` | % of working-age population | `SP.POP.DPND` | Ratio of dependents (0–14 and 65+) to working-age population (15–64) |
| `gdp_current_usd` | current US$ | `NY.GDP.MKTP.CD` | Nominal, not inflation- or PPP-adjusted — do not use for cross-country comparison; see `LIMITATIONS.md` |
| `gdp_per_capita_current_usd` | current US$ | `NY.GDP.PCAP.CD` | Nominal |
| `gdp_per_capita_ppp_current_intl` | current international $ | `NY.GDP.PCAP.PP.CD` | PPP-adjusted — the preferred column for cross-country income comparisons |
| `inflation_cpi_annual_pct` | % | `FP.CPI.TOTL.ZG` | |
| `unemployment_pct_of_labor_force` | % | `SL.UEM.TOTL.ZS` | ILO-modelled estimate |
| `internet_users_pct_of_population` | % | `IT.NET.USER.ZS` | |

## Consumer spending indicators (the core variable of interest)

| Column | Unit | World Bank code | Notes |
|---|---|---|---|
| `household_consumption_expenditure_current_usd` | current US$ | `NE.CON.PRVT.CD` | **This is "consumer spending"** — Households and NPISHs (non-profit institutions serving households) final consumption expenditure. Nominal; do not compare across countries without considering exchange rates — see `LIMITATIONS.md`. |
| `household_consumption_expenditure_constant_2015_usd` | constant 2015 US$ | `NE.CON.PRVT.KD` | Inflation-adjusted (real) — used for all growth/CAGR calculations in this project |
| `household_consumption_expenditure_per_capita_constant_2015_usd` | constant 2015 US$ | `NE.CON.PRVT.PC.KD` | Real, per-capita — the primary comparison metric used across most charts |
| `consumption_per_capita_check_usd` | current US$ | *derived* | `household_consumption_expenditure_current_usd / population_total`, computed independently by this project as a cross-check on the World Bank per-capita series (nominal, so will not numerically match the constant-USD column above — that is expected, not an error) |
| `household_consumption_pct_of_gdp` | % of GDP | `NE.CON.PRVT.ZS` | |
| `consumption_growth_yoy_real_pct` | % | *derived* | Year-over-year % change in `household_consumption_expenditure_constant_2015_usd`, per country |
| `consumption_cagr_2013_2023_real_pct` | % | *derived* | Compound annual growth rate of real consumption between the first and last available year for that country in the 2013–2023 window (not always exactly 2013 and 2023 — see `cagr_start_year`/`cagr_end_year`) |
| `cagr_start_year` / `cagr_end_year` | year | *derived* | The actual first/last year used in that country's CAGR calculation — stated explicitly because not every country has full 2013 and 2023 data |

## Snapshot-only columns (in `latest_year_snapshot.csv`)

| Column | Unit | Notes |
|---|---|---|
| `global_consumption_share_pct` | % | This country's consumption expenditure as a share of the global total across all 182 countries in the snapshot |
| `regional_consumption_share_pct` | % | This country's consumption expenditure as a share of its own Project_007_Region's total |

## Supplementary (not in the master panel — separate files, `data/raw/worldbank/`)

| File | Description | Coverage caveat |
|---|---|---|
| `digitally_enabled_account_pct.csv` | Global Findex: % of population 15+ with a digitally-enabled financial account | Survey years only (2011/2014/2017/2021/2024); sparse — 108 non-null country-year observations across the full 2011–2024 window |
| `account_ownership_pct.csv` | Global Findex: % of population 15+ with any financial account | Survey years only; 804 non-null observations |
| `political_stability_score.csv` | WGI: Political Stability and Absence of Violence, percentile rank (0–100) | Annual, 2013–2023, ~207 countries — added v2, see `SOURCES.md` |
| `rule_of_law_score.csv` | WGI: Rule of Law, percentile rank (0–100) | Annual, 2013–2023, ~207 countries — added v2 |
| `regulatory_quality_score.csv` | WGI: Regulatory Quality, percentile rank (0–100) | Annual, 2013–2023, ~207 countries — added v2 |

## Supplementary: category-level spending (added v2, `data/processed/category_spending_shares_oecd.csv`)

**Previously descoped, resolved in v2** — see `LIMITATIONS.md` item 1 and `SOURCES.md` for the full API fix. This file is a **separate, narrower-coverage layer (36 countries)**, deliberately not merged into `master_consumer_spending.csv` or `latest_year_snapshot.csv`, since blending a 36-country layer into a 182-country panel would either silently null out 146 countries or invite a misleading impression of global coverage.

| Column | Unit | Notes |
|---|---|---|
| `ISO3` | string | ISO 3166-1 alpha-3 code |
| `Year` | int | Each country's own latest year with a *complete* 12-category breakdown (not necessarily the same year across countries — see the "latest year" selection logic in `src/data_collection/oecd_categories.py`, which deliberately picks the latest **complete** year, not just the latest year with any data, after an earlier version of this script left 11 countries with a total but no category detail) |
| `{category}_share_pct` (12 columns: `food`, `alcohol`, `clothing`, `housing`, `household`, `health`, `transport`, `communication`, `recreation`, `education`, `restaurants`, `other`) | % of total household consumption expenditure | COICOP top-level purpose categories; each country's 12 shares sum to approximately 100% (94.6–102.2% across the 36 countries — the deviation from an exact 100% reflects OECD's own published rounding/residual items, not a processing error) |

## What is deliberately NOT in this dataset

- **Global category-level spending for all 182 countries**: no free, redistributable, cross-country-comparable source covering anywhere close to 182 countries was found even after resolving the OECD API (OECD's own coverage tops out around 38 economies). The 36-country supplementary layer above is the closest available substitute; it is not blended into the main panel. See `LIMITATIONS.md` item 1.
- **Voice & Accountability, Government Effectiveness, and Control of Corruption** (3 of WGI's 6 governance dimensions) — only the 3 most directly "stability"-relevant dimensions were pulled for the Market Attractiveness Index; the other 3 speak to related but distinct questions and were left for a future version. See `SOURCES.md`.
