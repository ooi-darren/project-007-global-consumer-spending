# Data Coverage

Stated plainly, per Section 7 of the project brief: this document is the honest account of what is and isn't covered, not a marketing summary.

## Headline Numbers

- **217** economies in World Bank's country list (excluding World Bank's own aggregate/regional rows)
- **182** of those (84%) have at least one year of consumer-spending data in the 2013–2023 window and form the analytical sample used throughout this project
- **35** economies (16%) have zero consumer-spending observations in this window and are excluded from every spending-based chart, table, and analysis — full list below
- **2013–2023** is the panel window (11 years); most cross-sectional comparisons use each country's most recent available year within that window, not a fixed year

## Coverage by Project 007 Region

| Region | Countries in snapshot |
|---|---|
| Africa | 50 |
| Europe | 46 |
| Latin America | 25 |
| South & Southeast Asia | 18 |
| Middle East | 18 |
| Oceania | 15 |
| East Asia | 6 |
| North America | 4 |

## Data Recency (Which Year Each Country's Snapshot Value Actually Comes From)

World Bank data has genuine reporting lags for some countries. This project uses "latest available year per country" rather than a fixed year, and states exactly which year that was:

| Year used | Number of countries |
|---|---|
| 2023 | 171 |
| 2022 | 6 |
| 2020 | 1 |
| 2018 | 2 |
| 2016 | 1 |
| 2015 | 1 |

94% of the sample (171/182) reflects 2023 data; the remaining 6% reflects the most recent year each of those countries has actually reported, stated explicitly per-country in `latest_year_snapshot.csv`'s `Year` column rather than hidden.

## The 35 Excluded Countries

These economies have **no** household consumption expenditure figure in World Bank's database for any year 2013–2023, and are therefore absent from every spending-based analysis in this project (they still appear, where relevant, in `REGION_MAPPING.csv`, since the mapping itself doesn't depend on spending data):

Andorra, Antigua and Barbuda, Barbados, British Virgin Islands, Cayman Islands, Channel Islands, Dominica, **Eritrea**, Gibraltar, Grenada, Guyana, Isle of Man, Jamaica, **Jordan**, Korea (Dem. People's Rep. — North Korea), **Liberia**, Liechtenstein, Micronesia (Fed. Sts.), Monaco, **Myanmar**, Naoero (Nauru), **Nigeria**, Papua New Guinea, Sint Maarten, **South Sudan**, St. Kitts and Nevis, St. Lucia, St. Martin, St. Vincent and the Grenadines, Suriname, Trinidad and Tobago, Turkmenistan, Turks and Caicos Islands, Tuvalu, **Venezuela**.

Two patterns are worth naming explicitly (bolded above):
1. **Small states and territories** (many Caribbean and Pacific microstates, European microstates) — these often don't produce full System of National Accounts detail at all, a genuine capacity issue for very small statistical offices, not a World Bank omission.
2. **Countries with known, well-documented national-accounts reporting difficulties** — Nigeria (Africa's largest economy by GDP), Venezuela, Myanmar, South Sudan, Eritrea, North Korea, Liberia, and Jordan's consumption series specifically. These are analytically significant gaps (Nigeria in particular is a large omission from the Africa region total) and are named here rather than left as a silent absence.

## Indicator-Level Completeness (2023, all 217 economies, before the consumption-data filter)

| Indicator | % of countries with a 2023 value |
|---|---|
| Population, urbanisation, age structure | 100% |
| GDP (current USD) | 94% |
| GDP per capita, PPP | 91% |
| Unemployment | 85% |
| Internet users | 83% |
| Inflation (CPI) | 81% |
| Consumption % of GDP | 79% |
| Consumption, current USD | 79% |
| Consumption per capita, constant USD | 75% |

Consumption-related indicators are consistently the least complete — expected, since household consumption expenditure requires more detailed national accounts work than population or urbanisation figures, which every statistical office can produce.

## Segmentation & Attractiveness Sub-Samples

- **Market attractiveness ranking**: all 182 countries in the snapshot (each pillar scored independently; a country missing one pillar is scored on the remaining pillars — see `MARKET_ATTRACTIVENESS_METHODOLOGY.md`)
- **K-Means segmentation**: 146 of 182 countries (80%) — the 36 excluded are missing at least one of the six clustering variables (most commonly inflation or internet penetration) and were not imputed
