# Sources

Full citations for every dataset used in Project 007. See `DATA_DICTIONARY.md` for how each indicator was used and its specific limitations, and `DATA_COVERAGE.md` for country/year coverage detail.

## Primary Source: World Bank Open Data

**Publisher:** World Bank | **Access:** `api.worldbank.org/v2` (public REST API, no authentication required) | **License:** CC-BY 4.0 (redistribution permitted) | **Date accessed:** 2026-08-29

World Bank was selected as the sole quantitative source for the core Country x Year panel after evaluating it against IMF and OECD (see Notebook 01 for the full comparison). Rationale: (1) it directly publishes a genuine consumer-spending indicator (Household Final Consumption Expenditure) with 217-economy, 1960s-present coverage; the other Tier-1 sources either lack this indicator or have materially narrower coverage; (2) using one consistent source for every indicator avoids cross-source definitional mismatches; (3) simple, stable, keyless REST API supports full reproducibility.

| Indicator code | Description | Frequency | Coverage |
|---|---|---|---|
| `NY.GDP.MKTP.CD` | GDP (current US$) | Annual | 1960–2023 |
| `NY.GDP.PCAP.CD` | GDP per capita (current US$) | Annual | 1960–2023 |
| `NY.GDP.PCAP.PP.CD` | GDP per capita, PPP (current international $) | Annual | 1990–2023 |
| `SP.POP.TOTL` | Population, total | Annual | 1960–2023 |
| `NE.CON.PRVT.CD` | Households and NPISHs final consumption expenditure (current US$) | Annual | 1960–2023 |
| `NE.CON.PRVT.KD` | Households and NPISHs final consumption expenditure (constant 2015 US$) | Annual | 1960–2023 |
| `NE.CON.PRVT.PC.KD` | Households final consumption expenditure per capita (constant 2015 US$) | Annual | 1960–2023 |
| `NE.CON.PRVT.ZS` | Households final consumption expenditure (% of GDP) | Annual | 1960–2023 |
| `FP.CPI.TOTL.ZG` | Inflation, consumer prices (annual %) | Annual | 1960–2023 |
| `SL.UEM.TOTL.ZS` | Unemployment, total (% of total labor force) | Annual | 1991–2023 |
| `SP.URB.TOTL.IN.ZS` | Urban population (% of total population) | Annual | 1960–2023 |
| `IT.NET.USER.ZS` | Individuals using the Internet (% of population) | Annual | 1990–2023 |
| `SP.POP.65UP.TO.ZS` | Population ages 65 and above (% of total) | Annual | 1960–2023 |
| `SP.POP.DPND` | Age dependency ratio (% of working-age population) | Annual | 1960–2023 |
| `dig.acc` | Digitally enabled account (% age 15+) | Every 3 years (Global Findex survey) | 2011, 2014, 2017, 2021, 2024 |
| `FX.OWN.TOTL.ZS` | Account ownership at a financial institution or mobile-money provider (% age 15+) | Every 3 years (Global Findex survey) | 2011, 2014, 2017, 2021, 2024 |

URL pattern used: `https://api.worldbank.org/v2/country/all/indicator/{code}?format=json&date=2013:2023&per_page=20000`

## Governance Indicators (added v2)

**Publisher:** World Bank, Worldwide Governance Indicators (WGI) project | **Access:** same `api.worldbank.org/v2` REST API | **License:** CC-BY 4.0 | **Date accessed:** 2026-08-29

Added to power the Market Attractiveness Index's Market Stability pillar (see `MARKET_ATTRACTIVENESS_METHODOLOGY.md`), closing the gap documented in `LIMITATIONS.md` item 7. Each indicator is a percentile rank (0–100) against all countries in the WGI's own global sample for that year.

| Indicator code | Description | Frequency | Coverage |
|---|---|---|---|
| `GOV_WGI_PV.SC` | Political Stability and Absence of Violence/Terrorism: Percentile Rank | Annual | 2013–2023 |
| `GOV_WGI_RL.SC` | Rule of Law: Percentile Rank | Annual | 2013–2023 |
| `GOV_WGI_RQ.SC` | Regulatory Quality: Percentile Rank | Annual | 2013–2023 |

Fetch script: `src/data_collection/governance_indicators.py`. Only 3 of WGI's 6 dimensions were pulled (the 3 most directly about "is this a stable place to do business": stability, rule of law, regulation), not Voice & Accountability, Government Effectiveness, or Control of Corruption, which speak to related but distinct questions and were left for a future version rather than folded in without a stated reason.

## Category-Level Spending Data (added v2, previously descoped)

**Publisher:** OECD, National Accounts (Household final consumption expenditure by COICOP purpose) | **Access:** `sdmx.oecd.org/public/rest/data/OECD.SDD.NAD,DSD_NAMAIN10@DF_TABLE5,1.0/` (SDMX REST API, no authentication) | **License:** OECD data is freely reusable with attribution | **Date accessed:** 2026-08-29

v1 evaluated this source and descoped it because the SDMX API's 12-dimension query key could not be reliably constructed by guessing. v2 resolved this by fetching the dataflow's DSD structure (`.../dataflow/OECD.SDD.NAD/DSD_NAMAIN10@DF_TABLE5/1.0?references=all`) and using the `.../availableconstraint/{key}?format=csvfile` endpoint to discover real, valid dimension-value combinations for a test country before building the full query, rather than guessing codes and hoping. Working key: `A.{ISO3}.S14..P31DC...{COICOP_CODE}.XDC.V.N.T0117` (frequency=Annual, sector=Households, transaction=Final consumption expenditure, unit=national currency, price base=Value, transformation=None, table=T0117). Fetch script: `src/data_collection/oecd_categories.py`.

Result: 36 countries with a complete 12-category COICOP breakdown, `data/processed/category_spending_shares_oecd.csv`. Validated by confirming each country's 12 category shares sum to approximately 100% of its reported total (range 94.6–102.2% across the 36 countries), internal consistency that would not hold if the query were pulling mismatched or partial data. This is a genuinely narrower-coverage supplementary layer (~38 economies), not a replacement for the 182-country main panel. See `LIMITATIONS.md` item 1.

## Regional Classification Source

**Publisher:** UN Statistics Division (UN M49 standard), via the [ISO-3166-Countries-with-Regional-Codes](https://github.com/lukes/ISO-3166-Countries-with-Regional-Codes) public compilation | **License:** Public domain / MIT (compilation) | **Date accessed:** 2026-08-29

Provides authoritative Region/Sub-region classification per ISO3 code, used as the base geography for `REGION_MAPPING.csv`. Full mapping methodology and documented overrides: see `data/processed/REGION_MAPPING.csv` and Notebook 02.

## Geographic Boundary Data (for choropleth map)

**Publisher:** Natural Earth (public domain, no attribution required) | **Source file:** `ne_110m_admin_0_countries.geojson`, retrieved via the community-maintained mirror at `github.com/nvkelso/natural-earth-vector` | **Date accessed:** 2026-08-29

## Sources Evaluated but Not Used for the Core Panel

- **IMF World Economic Outlook database**, evaluated; does not publish a direct household consumption expenditure series with comparable global coverage in its core public tables. Not used as primary source; a future version could incorporate IMF's fiscal/current-account data for additional cross-validation (see README "Recommended Improvements").
- **OECD SDMX API**: initially evaluated for COICOP category-level household spending data (Section 10 of the original brief) and descoped in v1 because its SDMX API requires exact multi-dimension query keys that could not be reliably constructed within v1's time budget. **Resolved in v2**. See "Category-Level Spending Data (added v2)" above and `LIMITATIONS.md` item 1 for the full before/after.
- **Global Findex digital-payment-specific indicators** beyond the two collected; Findex has thousands of granular indicator variants (by sex, age, education, income quintile); only the two most decision-relevant top-line indicators were collected to keep the digital-readiness layer focused rather than exhaustive.
