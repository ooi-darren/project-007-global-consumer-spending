# Sources

Full citations for every dataset used in Project 007. See `DATA_DICTIONARY.md` for how each indicator was used and its specific limitations, and `DATA_COVERAGE.md` for country/year coverage detail.

## Primary Source: World Bank Open Data

**Publisher:** World Bank | **Access:** `api.worldbank.org/v2` (public REST API, no authentication required) | **License:** CC-BY 4.0 (redistribution permitted) | **Date accessed:** 2026-08-29

World Bank was selected as the sole quantitative source for the core Country x Year panel after evaluating it against IMF and OECD (see Notebook 01 for the full comparison). Rationale: (1) it directly publishes a genuine consumer-spending indicator (Household Final Consumption Expenditure) with 217-economy, 1960s-present coverage — the other Tier-1 sources either lack this indicator or have materially narrower coverage; (2) using one consistent source for every indicator avoids cross-source definitional mismatches; (3) simple, stable, keyless REST API supports full reproducibility.

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

## Regional Classification Source

**Publisher:** UN Statistics Division (UN M49 standard), via the [ISO-3166-Countries-with-Regional-Codes](https://github.com/lukes/ISO-3166-Countries-with-Regional-Codes) public compilation | **License:** Public domain / MIT (compilation) | **Date accessed:** 2026-08-29

Provides authoritative Region/Sub-region classification per ISO3 code, used as the base geography for `REGION_MAPPING.csv`. Full mapping methodology and documented overrides: see `data/processed/REGION_MAPPING.csv` and Notebook 02.

## Geographic Boundary Data (for choropleth map)

**Publisher:** Natural Earth (public domain, no attribution required) | **Source file:** `ne_110m_admin_0_countries.geojson`, retrieved via the community-maintained mirror at `github.com/nvkelso/natural-earth-vector` | **Date accessed:** 2026-08-29

## Sources Evaluated but Not Used for the Core Panel

- **IMF World Economic Outlook database** — evaluated; does not publish a direct household consumption expenditure series with comparable global coverage in its core public tables. Not used as primary source; a future version could incorporate IMF's fiscal/current-account data for additional cross-validation (see README "Recommended Improvements").
- **OECD SDMX API** — evaluated for COICOP category-level household spending data (Section 10 of the original brief). OECD does publish this, but only for ~38 member/partner countries, and its SDMX API requires exact multi-dimension query keys that could not be reliably constructed within this project's time budget. **Category-level spending analysis was descoped as a result** — see `LIMITATIONS.md` for the full reasoning. This is a documented scope decision, not an oversight.
- **Global Findex digital-payment-specific indicators** beyond the two collected — Findex has thousands of granular indicator variants (by sex, age, education, income quintile); only the two most decision-relevant top-line indicators were collected to keep the digital-readiness layer focused rather than exhaustive.
