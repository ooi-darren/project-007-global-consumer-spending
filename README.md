# Project 007 — Global Consumer Spending Intelligence

<img src="./outputs/figures/01_global_spending_map.png" width="800" alt="Global map of consumer spending per capita, concentrated in North America, Europe, and wealthy East Asia/Gulf states">

**Part of a [7-case-study portfolio](https://github.com/ooi-darren)** — the first to move beyond a single country into a genuinely global panel.

## Executive Summary

This project builds and analyses a 182-country, 11-year (2013–2023) consumer-spending intelligence panel from World Bank Open Data, to test whether — and how — consumer spending behaviour actually differs across global regions, rather than assuming the answer. It finds that market **size** and market **growth** are almost unrelated (the countries with the biggest consumer markets are rarely the fastest-growing ones), that income remains the single strongest predictor of spending levels (r=0.88), that digital penetration now behaves more like a marker of market maturity than a growth driver, and that a data-driven clustering of 146 countries produces four distinct, interpretable market archetypes — including a small but real "crisis markets" segment (Argentina, Lebanon) that conventional attractiveness scoring would otherwise misread as moderately attractive. A transparent, sensitivity-tested market attractiveness index ranks 182 countries; the United States tops it by a wide margin, driven overwhelmingly by scale rather than growth.

## Research Question

**How does consumer spending behaviour differ across global regions, and what economic, demographic, and technological factors help explain these differences?**

Eleven secondary questions (market size, growth, income relationship, inflation, spending composition, digitalisation, demographics, market maturity, and strategic implications) are addressed directly in Notebooks 03–07 — see **Key Findings** below for the answers this project actually found, not assumed.

## Why This Research Matters

Businesses evaluating international expansion routinely rely on qualitative or anecdotal claims about "emerging market growth" or "mature market saturation." This project tests those claims against 182 countries' worth of actual, publicly sourced economic data, using a transparent, reproducible methodology — the kind of evidence base a strategy or consumer-intelligence team would need before a real market-entry recommendation, not a dashboard of unexamined numbers.

## Global Research Coverage

- **182 countries** with usable consumer-spending data (of 217 World Bank economies evaluated — 84% coverage; see `docs/DATA_COVERAGE.md` for exactly which 35 were excluded and why)
- **11 years** (2013–2023) per country where available
- **8 project regions**, built from the UN M49 standard with three documented overrides (`data/processed/REGION_MAPPING.csv`)
- **14 core indicators** per country-year: population, GDP (nominal and PPP), consumer spending (nominal, real, per-capita, % of GDP), inflation, unemployment, urbanisation, internet penetration, age structure — all from a single primary source (World Bank) to avoid cross-source definitional mismatches

## Research Framework

```
Data Acquisition (World Bank API)
        │
Data Engineering (region mapping, cleaning, derived metrics — CAGR, growth, shares)
        │
Exploratory Analysis (distributions, outliers)
        │
Regional Analysis (size, growth, trends by region)
        │
Spending-Relationship Analysis (income, inflation, digitalisation — correlation only)
        │
Market Segmentation (K-Means, k selected by silhouette score)
        │
Market Attractiveness (transparent composite index, sensitivity-tested)
        │
Strategic Translation (DATA → INSIGHT → BUSINESS IMPLICATION → STRATEGIC CONSIDERATION)
```

## Data Sources

**Primary source: World Bank Open Data** (`api.worldbank.org`, CC-BY 4.0, no authentication required) — selected after evaluating IMF and OECD specifically because it is the only Tier-1 source with a direct household-consumption-expenditure indicator at 180+ country coverage. Full evaluation and citations: [`docs/SOURCES.md`](docs/SOURCES.md).

**Regional classification**: UN M49 standard, via the ISO-3166-Countries-with-Regional-Codes public compilation.

**Geographic boundaries** (for the choropleth map): Natural Earth (public domain).

Category-level (COICOP) spending was evaluated (OECD, ~38 countries) and **descoped** for this version — see [`docs/LIMITATIONS.md`](docs/LIMITATIONS.md) for why, and what a future version would need.

## Methodology

Full write-up: [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md). In brief: real (constant-2015-USD) series are used for every growth/CAGR calculation, to isolate volume growth from inflation and exchange-rate effects; PPP-adjusted GDP per capita is used for income comparisons; nominal-USD is used only for market-size totals (with the exchange-rate caveat stated explicitly). Correlation analysis never claims causation. Market segmentation uses K-Means with k chosen by silhouette score, not assumed. The market attractiveness index uses equal-weighted, min-max normalised pillars with a documented sensitivity check (Spearman ρ=0.985 against a growth-double-weighted alternative).

## Key Findings

**1. Market size and market growth are nearly unrelated.** North America holds ~34% of global consumer spending with median real CAGR of only ~1.6%; South & Southeast Asia holds ~8% of global spending but is growing at median ~4.6% — more than double North America's rate, from a much smaller base.

**2. Income is the strongest single predictor of spending levels (r=0.88, n=166).** GDP per capita (PPP) and consumption per capita move together closely across the full country sample — the expected relationship, and a useful sanity check that the underlying data behaves as economic theory predicts.

**3. Digitalisation now reads as a maturity marker, not a growth driver.** Internet penetration correlates positively with spending *level* (r=0.61) but *negatively* with spending *growth* (r=-0.22) — already-online markets are typically large and mature, not fast-growing.

**4. Inflation shows no simple linear relationship with real spending growth at the country-year level** (r=-0.08, not statistically significant, n=153, p=0.31) — a genuinely "no relationship found" result, reported as such rather than forced into a narrative.

**5. Four data-driven market segments emerge from clustering** (see below) — including a real, small "crisis markets" cluster (Argentina, Lebanon) that ordinary attractiveness metrics would otherwise misread.

**6. The market attractiveness ranking is dominated by the United States** (score 90.1, next-highest Switzerland at 65.3) — almost entirely a market-size effect, not a growth or per-capita-spending effect; see the Market Attractiveness section below.

## Global Consumer Spending Landscape

| Region | Countries | Global spending share | Median real CAGR 2013–23 | Median spending/capita (constant 2015 USD) |
|---|---|---|---|---|
| North America | 4 | 33.9% | 1.6% | $35,995 |
| Europe | 46 | 23.9% | 2.4% | $10,845 |
| East Asia | 6 | 18.3% | 2.0% | $18,604 |
| South & Southeast Asia | 18 | 8.0% | **4.6%** (fastest) | $2,106 |
| Latin America | 25 | 7.5% | 2.6% | $5,192 |
| Middle East | 18 | 3.9% | 2.8% | $7,314 |
| Africa | 50 | 2.8% | 3.7% | $996 (lowest) |
| Oceania | 15 | 1.8% | 2.4% | $7,842 |

Full regional profile table: `outputs/tables/regional_profiles.csv`.

## Regional Consumer Profiles

Condensed here; the full economic / consumer / digital / demographic / behavioural-interpretation profile for every region is built directly from the tables above and Notebooks 03–05. Two illustrative examples:

**North America** — Economic: highest income and spending base globally. Consumer: largest absolute market (33.9% of global spending) but slowest-growing among major regions (1.6% median CAGR) — a mature, scale market. Digital: near-universal internet penetration. *Behavioural interpretation (evidence-consistent, not directly measured): premiumisation and convenience are more likely purchase drivers than price in an already-saturated, high-income, highly-digital market.*

**South & Southeast Asia** — Economic: low-to-middle income base. Consumer: smallest of the fast-growing regions by absolute share (8.0%) but fastest median growth (4.6%) of any region. Digital: internet penetration still has meaningfully more room to expand than in mature regions. *Behavioural interpretation: a market still building its digital and retail infrastructure, where price sensitivity is likely to remain a stronger purchase driver than in mature markets, alongside rapid genuine volume growth.*

## Consumer Market Segmentation

K-Means clustering (k=4, selected by silhouette score across k=3–7) on 146 countries with complete data across six standardised variables produced four distinct, interpretable archetypes:

| Segment | n | Median GDP/capita (PPP) | Median spending/capita (real) | Median real CAGR | Example markets |
|---|---|---|---|---|---|
| **Mature High-Spending Markets** | 35 | $71,624 | $22,906 | 2.1% | US, Switzerland, Singapore, Japan, UK |
| **Emerging Upper-Middle Markets** | 55 | $25,200 | $5,312 | 2.7% | China, Malaysia, Mexico, Brazil, Poland |
| **Lower-Spending Developing Markets** | 54 | $6,239 | $1,332 | **4.3%** (fastest) | India, Indonesia, Vietnam, Kenya, most of Sub-Saharan Africa |
| **Crisis / High-Inflation Markets** | 2 | $21,416 | $7,705 | **-0.4%** (only negative) | Argentina, Lebanon |

Full segment interpretation and methodology: Notebook 06, `docs/METHODOLOGY.md`.

## Market Attractiveness

Transparent, four-pillar (Market Size, Market Growth, Spending Power, Digital Readiness), equal-weighted, min-max-normalised composite score across all 182 countries. Full methodology, including the sensitivity check: [`MARKET_ATTRACTIVENESS_METHODOLOGY.md`](MARKET_ATTRACTIVENESS_METHODOLOGY.md).

**Top 10:** United States (90.1), Switzerland (65.3), Norway (63.2), Luxembourg (63.0), Australia (60.7), Iceland (59.5), United Kingdom (59.3), United Arab Emirates (58.7), Qatar (57.6), Hong Kong SAR (57.5).

The ranking is dominated by scale — the US score is driven overwhelmingly by market size, not growth or per-capita spending, which is itself an important finding: a naive "top market" list built on this composite will structurally favour large mature economies over genuinely high-growth smaller ones, exactly the kind of distortion Section 14 of the original brief warns a composite score can introduce if not read carefully. Full ranking: `outputs/tables/market_attractiveness_ranking.csv`.

## Strategic Implications

Full DATA → INSIGHT → BUSINESS IMPLICATION → STRATEGIC CONSIDERATION write-ups for three major findings are in **Notebook 07**. Summary:

1. **Scale markets and growth markets require different playbooks** — market size and growth are nearly uncorrelated, so a single global entry strategy is unlikely to serve both large mature markets and small high-growth ones well.
2. **Digital-first entry is table stakes in mature/emerging-upper-middle markets, but digital-infrastructure investment itself may be the bigger near-term opportunity in the fastest-growing (Lower-Spending Developing) segment**, where internet penetration still has substantial room to expand.
3. **Macro instability can invalidate standard attractiveness signals entirely** — Argentina and Lebanon score moderately on demographic/digital fundamentals despite active currency crises, illustrating why a real capital-allocation screen needs macro stability as a gating filter, not just one averaged input.

## Visualisations

12 required visualisations, `outputs/figures/`:

1. Global consumer spending per capita (choropleth map)
2. Consumer spending by region
3. Consumer spending per capita, top 20 markets
4. Consumer spending growth by region (distribution)
5. Regional spending trends, indexed 2013=100
6. Consumption as % of GDP by region (category-composition substitute — see Limitations)
7. Income vs. consumer spending
8. Inflation vs. spending growth
9. Digitalisation vs. spending
10. Country segmentation (K-Means, PCA-visualised)
11. Market attractiveness matrix (growth × spending power × market-size bubble)
12. Regional comparison dashboard (4-panel)

## Limitations

Full document: [`docs/LIMITATIONS.md`](docs/LIMITATIONS.md). Headline items: category-level spending was descoped (no free cross-country source); 35 of 217 countries (including Nigeria) have no consumption data and are excluded; regional classification is a documented judgment call, not an official standard; all correlations are explicitly non-causal; the market-attractiveness weighting is a stated simplification, not an optimum.

## Reproducibility

```bash
pip install -r requirements.txt

# 1. Pull raw data from World Bank + build region mapping
python src/data_collection/world_bank.py
python src/data_collection/build_region_mapping.py

# 2. Build the master analytical dataset
python src/cleaning/build_master_dataset.py

# 3. Run the analysis layer
python src/analysis/regional_analysis.py
python src/analysis/segmentation.py
python src/analysis/market_attractiveness.py

# 4. Generate all 12 visualisations
python src/visualisation/make_charts.py

# 5. Walk through the narrative notebooks
jupyter notebook notebooks/
```

All raw and processed data is committed to this repository (World Bank's CC-BY 4.0 licence permits redistribution), so steps 2–5 can be run directly without re-fetching from the API.

## Project Structure

```
project-007-global-consumer-spending/
├── README.md
├── MARKET_ATTRACTIVENESS_METHODOLOGY.md
├── data/
│   ├── raw/            # World Bank API pulls, unmodified
│   ├── processed/       # master_consumer_spending.csv, latest_year_snapshot.csv, REGION_MAPPING.csv
│   └── external/         # UN M49 region reference, Natural Earth boundaries
├── notebooks/            # 01-07, narrative walkthrough of the src/ pipeline
├── src/
│   ├── data_collection/  # World Bank API client, region mapping builder
│   ├── cleaning/          # master dataset builder
│   ├── analysis/           # regional, segmentation, market attractiveness
│   └── visualisation/      # house chart style + all 12 chart builders
├── outputs/
│   ├── figures/            # 12 PNG visualisations
│   └── tables/               # regional profiles, correlations, segmentation, rankings
├── docs/
│   ├── DATA_DICTIONARY.md
│   ├── DATA_COVERAGE.md
│   ├── METHODOLOGY.md
│   ├── SOURCES.md
│   └── LIMITATIONS.md
├── requirements.txt
├── LICENSE
└── .gitignore
```

## Sources

Full citations: [`docs/SOURCES.md`](docs/SOURCES.md).

## Author

Darren Ooi — [LinkedIn](https://www.linkedin.com/in/darrenooizhixian)
