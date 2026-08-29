# Limitations

Professional research does not hide its limitations. This document is deliberately thorough.

## 1. Category-Level Spending: Solved for 36 Countries, Not the Full Panel

**v1 of this project evaluated and descoped category-level spending** (food, housing, transport, etc.) for the 182-country panel, because OECD's SDMX API — the only free source with COICOP-style category detail — requires precise multi-dimension query keys that could not be resolved within v1's time budget.

**v2 solved the API problem.** Rather than guessing dimension-key values, the fix was to fetch the dataflow's own DSD structure (`.../dataflow/OECD.SDD.NAD/DSD_NAMAIN10@DF_TABLE5/1.0?references=all`) and query its `availableconstraint` endpoint, which reports which dimension-value combinations actually have data. That revealed the correct 12-part key (see `src/data_collection/oecd_categories.py` for the full key and the reasoning). The result: real COICOP category-level household spending for **36 countries** (OECD members plus several partner economies), saved to `data/processed/category_spending_shares_oecd.csv`, validated by confirming each country's 12 category shares sum to ~95–102% of its reported total (a check consistent with genuine, internally-coherent data — see the `total_check` derivation in that script's tests).

What this **does not** change:
- Coverage is still ~38 economies, not 182 — OECD does not publish this for most of the developing world, and no free source does either. This is presented as a clearly-scoped **supplementary layer**, deliberately not blended into the main 182-country master dataset.
- Commercial sources (Euromonitor, Statista, GlobalData) would still be needed for genuinely global category coverage; this project still has no licence for those and does not represent this 36-country layer as a substitute.

**Consequence:** Visualisation #6 now shows real category-level data — food's share of household spending vs. GDP per capita (Engel's Law), Pearson r = -0.74 (p < 0.001, n = 36) — replacing v1's GDP-share substitute. A supplementary Visualisation #13 shows a 4-category composition breakdown for 18 selected countries. Both are explicitly labelled with their 36-country/OECD-plus-partners scope in the chart footnote, so a reader cannot mistake them for the full global panel.

## 2. Currency, Inflation, and Exchange Rates

Nominal-USD comparisons are affected by exchange-rate movements that have nothing to do with actual consumer behaviour. Example found directly in this dataset: Japan's nominal-USD household consumption *fell* from 2013 to 2023 in current-USD terms, substantially reflecting yen depreciation against the dollar over that period, not a real decline in Japanese consumer demand. This project addresses this by using constant-2015-USD (real) series for every growth and CAGR calculation — but nominal-USD figures are still used for market-size totals and shares (necessarily, since that is what "how much is spent globally" means), and any reader comparing nominal-USD *levels* across two countries should keep exchange-rate effects in mind.

PPP adjustment (via `gdp_per_capita_ppp_current_intl`) is used for income comparisons specifically because it corrects for local price-level differences that nominal exchange rates do not — but PPP conversion factors themselves are periodic estimates (typically updated via the International Comparison Program every few years), not live market data, and carry their own estimation uncertainty.

## 3. Regional Classification Is a Judgment Call, Not a Fact

The Project 007 8-region framework is not an official statistical standard. It is built from UN M49 with three documented manual overrides (see `data/processed/REGION_MAPPING.csv`). A different, equally reasonable analyst could classify Central Asia, the Caucasus, or Iran differently. The classification is transparent and reproducible, not objectively "correct" — regional comparisons in this project should be read with that in mind, especially for countries near a regional boundary.

## 4. Data Completeness Is Uneven, and That Unevenness Is Not Random

35 of 217 economies (16%) have zero consumer-spending data for 2013–2023 — see `DATA_COVERAGE.md` for the full list. This is not a random sample of missingness: it disproportionately affects very small states (limited statistical capacity) and a specific set of larger economies with well-documented national-accounts difficulties (Nigeria, Venezuela, Myanmar, South Sudan, Eritrea, North Korea). **Nigeria's absence is a materially significant gap** — as Africa's largest economy by GDP, its exclusion likely understates Africa's true regional consumption total and may distort Africa's regional growth/attractiveness figures. This is stated explicitly rather than left as a silent gap in a regional total.

## 5. Correlation Is Not Causation — Explicitly, Everywhere in This Project

Every correlation reported in Notebook 05 and elsewhere describes an observed statistical association in a single cross-section (or panel) of country-year data. None of them establish that one variable *causes* another. Specific risks:
- **Reverse causality**: higher spending could plausibly drive measured "income" upward in some national accounts frameworks, not just the reverse.
- **Omitted variable bias**: institutional quality, trade openness, natural resource wealth, and colonial/historical legacy plausibly drive both income and spending patterns simultaneously, without either causing the other directly.
- **Ecological correlation**: relationships observed at the country level do not necessarily hold at the individual/household level (the "ecological fallacy") — a country-level correlation between internet penetration and spending does not mean any specific internet user in that country spends more.

Language throughout this project ("suggests," "is associated with," "appears consistent with") is chosen deliberately to avoid overclaiming causal mechanisms the data cannot support.

## 6. Small Clusters Are Real Findings, Not Errors

The market segmentation (Notebook 06) produced one 2-country cluster (Argentina, Lebanon). This is reported as-is rather than merged into a larger cluster to look tidier, because it reflects a genuine, distinct pattern (severe currency/inflation crisis) in the standardised data — but a 2-country "segment" should be read as "two notable outliers with a shared characteristic," not as a generalisable market archetype with predictive value for other countries that might later enter a similar crisis.

## 7. The Market Attractiveness Score Is a Documented Choice, Not an Optimum

Equal weighting across five pillars (market size, growth, spending power, digital readiness, and — added in v2 — market stability) was a deliberate simplification, explicitly not derived from any optimisation or stakeholder-weighted process. A sensitivity check (re-weighting growth 2x) produced a Spearman rank correlation of 0.992 against the base ranking, indicating the *ranking* is not fragile to this particular choice — but a different, defensible weighting scheme would produce a different ranking, and the composite score should not be read as a single objective "correct" answer. See `MARKET_ATTRACTIVENESS_METHODOLOGY.md`.

**v1 named Argentina and Lebanon as markets that would score well on the original four pillars despite active macro crises, because the index had no risk/regulatory dimension.** v2 adds a Market Stability pillar (World Bank Worldwide Governance Indicators: political stability, rule of law, regulatory quality — see `src/data_collection/governance_indicators.py`) specifically to close that gap. Outcome: Argentina now ranks 79th of 183 (composite 44.2, market-stability sub-score 49.3 — middling, not alarming, since it is still pulled up by market size) and Lebanon ranks 122nd (composite 36.1, market-stability sub-score 26.5 — genuinely weak). This is a real, measurable effect of adding the pillar, not a cosmetic fix — but it is still one composite index with one specific operationalisation of "stability" (a 3-dimension WGI average), not a substitute for actual country-risk due diligence.

## 8. Behavioural Claims Are Interpretive, Not Directly Measured

This dataset contains no direct behavioural or attitudinal data (no consumer surveys, no purchase-intent data, no brand/category-level panel data). Statements in the Regional Consumer Profiles about "price sensitivity," "premiumisation," or "convenience-seeking" are **interpretations consistent with** the macro/demographic patterns observed, not direct measurements of consumer psychology, and are flagged as such wherever they appear.

## 9. Data Frequency and Recency

World Bank data, even where available, lags real-time by 1–2 years for most countries and considerably more for a small number (see `DATA_COVERAGE.md` for the exact year-by-country breakdown). This project's "2023" figures are, for most countries, genuinely 2023; for 11 countries they are the most recent available year, which may be as early as 2015. This is stated explicitly per-country rather than presented as a uniform "current" snapshot.

## 10. What This Project Does Not Claim

This project does not claim to have identified the single best market for any specific business, does not claim its segments are the only valid way to group these countries, and does not claim any of its findings would replicate identically with a different (even equally reasonable) methodological choice at each decision point documented above. It claims to have applied a transparent, reproducible, evidence-based methodology to real public data, and to report honestly where that methodology's limits are.
