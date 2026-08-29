# Market Attractiveness Index — Methodology

Full transparency on how `outputs/tables/market_attractiveness_ranking.csv` was built, per Section 14 of the project brief: define variables, standardise, explain weights, explain scoring, sensitivity-check, document limitations.

## 1. Variables (Four Pillars)

| Pillar | Underlying variable | Why this variable |
|---|---|---|
| **Market Size** | `household_consumption_expenditure_current_usd` | The direct, most literal measure of "how much money is spent in this market" |
| **Market Growth** | `consumption_cagr_2013_2023_real_pct` | Real (inflation-adjusted) growth, so it reflects genuine volume expansion, not currency or price effects |
| **Spending Power** | `household_consumption_expenditure_per_capita_constant_2015_usd` | Real per-capita spending — distinguishes a market where individual consumers spend a lot from one that is merely populous |
| **Digital Readiness** | `internet_users_pct_of_population` | A proxy for how digitally-enabled a market's consumers and distribution channels are likely to be |

These four were chosen because they map directly onto the four questions a business typically asks when screening a market: *how big is it, how fast is it growing, how much does each consumer spend, and how digitally accessible is it.* They are not the only reasonable choice — e.g. a version emphasising political/regulatory risk, ease of doing business, or logistics infrastructure would be equally legitimate for a different strategic question.

## 2. Standardisation

Each pillar's raw variable is **min-max normalised to a 0–100 scale**, within the sample of countries that have a valid value for that variable:

```
score = (value - min(value)) / (max(value) - min(value)) * 100
```

Min-max (rather than z-score) was chosen specifically because the final output is meant to be read as an intuitive 0–100 "score," which a standardised z-score does not directly give.

## 3. Weighting

**Equal weights (25% each).** This is a deliberate, stated simplification — not derived from any survey, expert panel, or optimisation. The brief explicitly warns against arbitrary weight assignment (Section 14); equal weighting is the most defensible *default* precisely because it makes no implicit claim about which pillar matters more, leaving that judgment explicitly to the reader rather than burying an opinionated weighting inside an apparently objective "score."

A country missing a value for one pillar is scored on the **remaining available pillars only** (reweighted, not zero-filled) — `n_pillars_available` is recorded per country so this is auditable, not silently absorbed into the average.

## 4. Scoring

Composite score = unweighted mean of the available pillar scores (0–100 each). Countries are then ranked descending. Full output: `outputs/tables/market_attractiveness_ranking.csv`, with every pillar sub-score retained alongside the composite, so any reader can recompute an alternative weighting directly from that file without rerunning any code.

## 5. Sensitivity Analysis

A second version of the score was computed with Market Growth double-weighted (i.e. 2:1:1:1 across the four pillars, renormalised), simulating a growth-focused investor's priorities. The two rankings were compared with a **Spearman rank correlation of 0.985** — indicating the overall ranking is materially stable to this specific reweighting. This does not mean *every* weighting scheme would produce a similar ranking (see Limitation below), only that this one plausible alternative does not substantially disturb the result.

## 6. Limitations of This Index

- **Equal weighting is a choice, not a finding.** A reader with a different strategic priority (e.g., pure market size for an M&A screen, or pure growth for a venture-style thesis) should treat this composite score as a starting point and recompute with their own weights using the retained pillar sub-scores.
- **No risk, regulatory, or ease-of-business dimension is included.** A market can score well on all four pillars and still be difficult to enter for reasons this index does not capture (see `docs/LIMITATIONS.md`, item 7, on Argentina and Lebanon scoring moderately despite active macro crises — a direct illustration of this gap).
- **Market size mechanically favours populous/large-economy countries** over per-capita-attractive but small markets — this is intentional (size is one of the four things the index is explicitly measuring) but means the top of the ranking will structurally tilt toward large economies (the US, China) regardless of how attractive a smaller market might be on a per-consumer basis. Readers interested specifically in per-consumer attractiveness should look at the Spending Power pillar sub-score in isolation.
