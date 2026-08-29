# -*- coding: utf-8 -*-
"""
Market Attractiveness Index for Project 007.

Methodology (full write-up in docs/MARKET_ATTRACTIVENESS_METHODOLOGY.md):
  1. Four equally-weighted pillars: Market Size, Market Growth, Spending Power,
     Digital Readiness. Equal weighting is a deliberate, documented choice (not
     a data-driven optimum) -- see methodology doc for the sensitivity check.
  2. Each pillar's underlying variable is min-max normalised to 0-100 within
     the sample of countries that have that variable (so a country missing one
     pillar is scored on the remaining pillars, reweighted, and flagged).
  3. Composite score = weighted average of available pillars.
"""
import pandas as pd
import numpy as np

snap = pd.read_csv("data/processed/latest_year_snapshot.csv")

PILLARS = {
    "market_size": "household_consumption_expenditure_current_usd",
    "market_growth": "consumption_cagr_2013_2023_real_pct",
    "spending_power": "household_consumption_expenditure_per_capita_constant_2015_usd",
    "digital_readiness": "internet_users_pct_of_population",
}

df = snap.copy()

def minmax(s):
    return (s - s.min()) / (s.max() - s.min()) * 100

for pillar, col in PILLARS.items():
    df[f"score_{pillar}"] = minmax(df[col])

score_cols = [f"score_{p}" for p in PILLARS]
df["n_pillars_available"] = df[score_cols].notna().sum(axis=1)
df["market_attractiveness_score"] = df[score_cols].mean(axis=1, skipna=True)
df.loc[df["n_pillars_available"] == 0, "market_attractiveness_score"] = np.nan

# Sensitivity check: recompute with market_growth weighted 2x, to test rank stability
df["score_alt_growth_weighted"] = df[score_cols].apply(
    lambda r: np.average(
        [r["score_market_size"], r["score_market_growth"], r["score_market_growth"],
         r["score_spending_power"], r["score_digital_readiness"]],
        weights=[1, 1, 1, 1, 1]
    ) if r.notna().all() else np.nan,
    axis=1
)

result = df.dropna(subset=["market_attractiveness_score"]).sort_values(
    "market_attractiveness_score", ascending=False
).reset_index(drop=True)
result["rank"] = result.index + 1

# rank correlation between base and sensitivity-weighted score
from scipy.stats import spearmanr
comparable = result.dropna(subset=["score_alt_growth_weighted"])
rho, p = spearmanr(comparable["market_attractiveness_score"], comparable["score_alt_growth_weighted"])
print(f"Sensitivity check (equal weights vs 2x growth weight): Spearman rho = {rho:.3f}")

out_cols = ["rank", "Country", "ISO3", "Project_007_Region", "market_attractiveness_score",
            "n_pillars_available"] + score_cols
result[out_cols].to_csv("outputs/tables/market_attractiveness_ranking.csv", index=False)

print("\nTop 15 markets by attractiveness score:")
print(result[["rank", "Country", "Project_007_Region", "market_attractiveness_score"]].head(15).to_string(index=False))
print("\nBottom 10:")
print(result[["rank", "Country", "Project_007_Region", "market_attractiveness_score"]].tail(10).to_string(index=False))
