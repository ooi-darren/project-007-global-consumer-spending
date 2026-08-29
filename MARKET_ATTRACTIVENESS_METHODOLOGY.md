# Market Attractiveness Index — Methodology

Full transparency on how `outputs/tables/market_attractiveness_ranking.csv` was built, per Section 14 of the project brief: define variables, standardise, explain weights, explain scoring, sensitivity-check, document limitations.

**v2 change:** added a fifth pillar, Market Stability, built from World Bank Worldwide Governance Indicators. v1's four pillars had no risk/regulatory dimension at all — `docs/LIMITATIONS.md` (v1) named Argentina and Lebanon as the specific illustration of that gap: markets that could score well on size/growth/spending/digital-readiness while carrying real political or regulatory risk the index had no way to reflect. This section now documents five pillars; the sensitivity-check numbers below are recomputed on the 5-pillar version.

## 1. Variables (Five Pillars)

| Pillar | Underlying variable | Why this variable |
|---|---|---|
| **Market Size** | `household_consumption_expenditure_current_usd` | The direct, most literal measure of "how much money is spent in this market" |
| **Market Growth** | `consumption_cagr_2013_2023_real_pct` | Real (inflation-adjusted) growth, so it reflects genuine volume expansion, not currency or price effects |
| **Spending Power** | `household_consumption_expenditure_per_capita_constant_2015_usd` | Real per-capita spending — distinguishes a market where individual consumers spend a lot from one that is merely populous |
| **Digital Readiness** | `internet_users_pct_of_population` | A proxy for how digitally-enabled a market's consumers and distribution channels are likely to be |
| **Market Stability** *(added v2)* | Average of 3 WGI percentile-rank indicators: political stability, rule of law, regulatory quality | Directly closes the risk/regulatory gap named in v1's Limitations — a market can no longer score well overall purely by being large, growing, rich, and online while carrying real governance risk |

These map onto the questions a business typically asks when screening a market: *how big is it, how fast is it growing, how much does each consumer spend, how digitally accessible is it, and how stable/predictable is it to operate in.* They are not the only reasonable choice — e.g. a version additionally weighting ease-of-business or logistics infrastructure would be equally legitimate for a different strategic question. Each of the 3 Market Stability sub-indicators is itself already a percentile rank (0–100) computed by the WGI project against its own global sample — this project only averages the 3 dimensions per country (requiring all 3 present, not a partial average) before re-normalising alongside the other pillars in step 2.

## 2. Standardisation

Each pillar's raw variable is **min-max normalised to a 0–100 scale**, within the sample of countries that have a valid value for that variable:

```
score = (value - min(value)) / (max(value) - min(value)) * 100
```

Min-max (rather than z-score) was chosen specifically because the final output is meant to be read as an intuitive 0–100 "score," which a standardised z-score does not directly give.

## 3. Weighting

**Equal weights (20% each of five pillars).** This is a deliberate, stated simplification — not derived from any survey, expert panel, or optimisation. The brief explicitly warns against arbitrary weight assignment (Section 14); equal weighting is the most defensible *default* precisely because it makes no implicit claim about which pillar matters more, leaving that judgment explicitly to the reader rather than burying an opinionated weighting inside an apparently objective "score."

A country missing a value for one pillar is scored on the **remaining available pillars only** (reweighted, not zero-filled) — `n_pillars_available` is recorded per country so this is auditable, not silently absorbed into the average.

## 4. Scoring

Composite score = unweighted mean of the available pillar scores (0–100 each). Countries are then ranked descending. Full output: `outputs/tables/market_attractiveness_ranking.csv`, with every pillar sub-score retained alongside the composite, so any reader can recompute an alternative weighting directly from that file without rerunning any code.

## 5. Sensitivity Analysis

A second version of the score was computed with Market Growth double-weighted (i.e. 2:1:1:1:1 across the five pillars, renormalised), simulating a growth-focused investor's priorities. The two rankings were compared with a **Spearman rank correlation of 0.992** (n = 153 countries with all 5 pillars available) — indicating the overall ranking is materially stable to this specific reweighting. This does not mean *every* weighting scheme would produce a similar ranking (see Limitation below), only that this one plausible alternative does not substantially disturb the result.

## 6. Limitations of This Index

- **Equal weighting is a choice, not a finding.** A reader with a different strategic priority (e.g., pure market size for an M&A screen, or pure growth for a venture-style thesis) should treat this composite score as a starting point and recompute with their own weights using the retained pillar sub-scores.
- **The Market Stability pillar (added v2) narrows the country sample.** Requiring all 3 WGI dimensions present drops the comparable sample to 153 countries (of 182 with the other 4 pillars) — a country missing WGI data entirely is scored on the remaining 4 pillars only, `n_pillars_available` records this per country, but this means the composite is not perfectly apples-to-apples across every row. This is a real, deliberate trade-off (adding real risk signal vs. losing some coverage), not an oversight.
- **"Stability" is operationalised narrowly** as an average of 3 WGI percentile dimensions — a legitimate, widely-used measure, but still one specific choice. It does not capture, e.g., currency convertibility risk, sanctions exposure, or sector-specific regulatory barriers a real market-entry decision would also need. **v1's Argentina/Lebanon example is a useful check on this**: with the pillar added, Argentina now ranks 79th (stability sub-score 49.3 — pulled down from where market size alone would put it, but not to the bottom) and Lebanon ranks 122nd (stability sub-score 26.5, genuinely weak) — a real, direction-correct effect, not a token fix — see `docs/LIMITATIONS.md` item 7 for the full numbers.
- **Market size mechanically favours populous/large-economy countries** over per-capita-attractive but small markets — this is intentional (size is one of the five things the index is explicitly measuring) but means the top of the ranking will structurally tilt toward large economies (the US) regardless of how attractive a smaller market might be on a per-consumer basis. Readers interested specifically in per-consumer attractiveness should look at the Spending Power pillar sub-score in isolation.
