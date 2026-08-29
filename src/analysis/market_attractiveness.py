# -*- coding: utf-8 -*-
"""
Market Attractiveness Index for Project 007.

Methodology (full write-up in MARKET_ATTRACTIVENESS_METHODOLOGY.md):
  1. Five equally-weighted pillars: Market Size, Market Growth, Spending Power,
     Digital Readiness, Market Stability. Equal weighting is a deliberate,
     documented choice (not a data-driven optimum) -- see methodology doc for
     the sensitivity check.
  2. Each pillar's underlying variable is min-max normalised to 0-100 within
     the sample of countries that have that variable (so a country missing one
     pillar is scored on the remaining pillars, reweighted, and flagged).
  3. Composite score = unweighted mean of available pillars.

v2 change: added the Market Stability pillar (World Bank Worldwide Governance
Indicators: political stability, rule of law, regulatory quality -- see
src/data_collection/governance_indicators.py) to close the gap v1 documented
in docs/LIMITATIONS.md item 7 -- a market could score well on size, growth,
spending power and digital readiness while carrying real political/regulatory
risk the original 4-pillar index had no way to reflect (v1 named Argentina and
Lebanon as the illustrating case; see whether this changes with v2, below).
"""
import pandas as pd
import numpy as np
from scipy.stats import spearmanr

snap = pd.read_csv("data/processed/latest_year_snapshot.csv")

PILLARS = {
    "market_size": "household_consumption_expenditure_current_usd",
    "market_growth": "consumption_cagr_2013_2023_real_pct",
    "spending_power": "household_consumption_expenditure_per_capita_constant_2015_usd",
    "digital_readiness": "internet_users_pct_of_population",
    "market_stability": "governance_stability_index_raw",  # built below, then dropped
}

df = snap.copy()

# ---- Build the Market Stability raw variable from the 3 WGI files ----
# Each WGI indicator is already a 0-100 percentile rank against the WGI's own
# global sample. For each country we take its own latest available year
# (<=2023), same "use each country's most recent real observation" rule
# applied everywhere else in this project (see build_master_dataset.py CAGR
# logic and docs/LIMITATIONS.md item 9), then average the 3 dimensions.
wgi_files = {
    "political_stability_score": "data/raw/worldbank/political_stability_score.csv",
    "rule_of_law_score": "data/raw/worldbank/rule_of_law_score.csv",
    "regulatory_quality_score": "data/raw/worldbank/regulatory_quality_score.csv",
}
wgi_latest = None
for col, path in wgi_files.items():
    g = pd.read_csv(path).dropna(subset=[col])
    g = g.loc[g.groupby("iso3")["year"].idxmax()][["iso3", col]]
    wgi_latest = g if wgi_latest is None else wgi_latest.merge(g, on="iso3", how="outer")

wgi_latest["governance_stability_index_raw"] = wgi_latest[list(wgi_files.keys())].mean(axis=1, skipna=False)
wgi_latest["n_wgi_dimensions_available"] = wgi_latest[list(wgi_files.keys())].notna().sum(axis=1)
# Require all 3 dimensions present, not a partial average silently passed off
# as equivalent to a full one -- a country with just 1 of 3 WGI dimensions
# reported is left NaN here, same "no zero-filling" rule as the other pillars.
wgi_latest.loc[wgi_latest["n_wgi_dimensions_available"] < 3, "governance_stability_index_raw"] = np.nan

df = df.merge(wgi_latest[["iso3", "governance_stability_index_raw"]], left_on="ISO3", right_on="iso3", how="left")


def minmax(s):
    return (s - s.min()) / (s.max() - s.min()) * 100


for pillar, col in PILLARS.items():
    df[f"score_{pillar}"] = minmax(df[col])

score_cols = [f"score_{p}" for p in PILLARS]
df["n_pillars_available"] = df[score_cols].notna().sum(axis=1)
df["market_attractiveness_score"] = df[score_cols].mean(axis=1, skipna=True)
df.loc[df["n_pillars_available"] == 0, "market_attractiveness_score"] = np.nan

# ---- Sensitivity check: recompute with market_growth weighted 2x (of 6 total
# weight units across the 5 pillars), to test rank stability. Fixed from v1,
# where this weighted average's `weights=` list did not actually differ from
# an unweighted mean -- a no-op bug caught while extending this to 5 pillars.
def alt_weighted(row):
    if row[score_cols].isna().any():
        return np.nan
    values = [row["score_market_size"], row["score_market_growth"], row["score_spending_power"],
              row["score_digital_readiness"], row["score_market_stability"]]
    weights = [1, 2, 1, 1, 1]
    return np.average(values, weights=weights)


df["score_alt_growth_weighted"] = df.apply(alt_weighted, axis=1)

result = df.dropna(subset=["market_attractiveness_score"]).sort_values(
    "market_attractiveness_score", ascending=False
).reset_index(drop=True)
result["rank"] = result.index + 1

comparable = result.dropna(subset=["score_alt_growth_weighted"])
rho, p = spearmanr(comparable["market_attractiveness_score"], comparable["score_alt_growth_weighted"])
print(f"Sensitivity check (equal weights vs 2x growth weight, n={len(comparable)}): Spearman rho = {rho:.3f}")

out_cols = ["rank", "Country", "ISO3", "Project_007_Region", "market_attractiveness_score",
            "n_pillars_available"] + score_cols
result[out_cols].to_csv("outputs/tables/market_attractiveness_ranking.csv", index=False)

print("\nTop 15 markets by attractiveness score:")
print(result[["rank", "Country", "Project_007_Region", "market_attractiveness_score"]].head(15).to_string(index=False))
print("\nBottom 10:")
print(result[["rank", "Country", "Project_007_Region", "market_attractiveness_score"]].tail(10).to_string(index=False))

# ---- v2 check: did adding Market Stability change Argentina / Lebanon's
# standing, per the v1 Limitation that named them? ----
watch = result[result["Country"].isin(["Argentina", "Lebanon"])]
if len(watch):
    print("\nArgentina / Lebanon after adding Market Stability pillar:")
    print(watch[["rank", "Country", "market_attractiveness_score", "score_market_stability"]].to_string(index=False))
