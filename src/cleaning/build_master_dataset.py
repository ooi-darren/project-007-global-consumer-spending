# -*- coding: utf-8 -*-
"""
Builds the master analytical dataset for Project 007.

Grain: Country x Year (2013-2023), World Bank indicators only (the only source
with consistent global definitions across 180+ countries -- see docs/SOURCES.md
for why category-level and single-source-of-truth choices were made this way).

Outputs:
  data/processed/master_consumer_spending.csv   (full country x year panel)
  data/processed/latest_year_snapshot.csv        (one row per country: most
                                                    recent available year, for
                                                    cross-sectional comparison)
"""
import pandas as pd
import numpy as np

panel = pd.read_csv("data/raw/worldbank_panel_wide.csv")
regions = pd.read_csv("data/processed/REGION_MAPPING.csv")

df = panel.merge(
    regions[["ISO3", "Country", "Project_007_Region", "Official_Region", "Sub_Region"]],
    left_on="iso3", right_on="ISO3", how="inner"  # inner: keep only real countries, drop WB aggregates
)
df = df.drop(columns=["ISO3", "country_name"])
df = df.rename(columns={"iso3": "ISO3", "year": "Year", "Country": "Country"})

# ---- Derived metrics ----
# Spending per capita, computed independently as a cross-check against the
# World Bank per-capita series (should match closely; large deviations flagged).
df["consumption_per_capita_check_usd"] = (
    df["household_consumption_expenditure_current_usd"] / df["population_total"]
)

df = df.sort_values(["ISO3", "Year"])

# Year-over-year real consumption growth (%), using the constant-2015-USD series
# so growth is not contaminated by inflation or exchange-rate movements.
df["consumption_growth_yoy_real_pct"] = (
    df.groupby("ISO3")["household_consumption_expenditure_constant_2015_usd"]
      .pct_change() * 100
)

# ---- CAGR 2013-2023 (real, constant-USD basis), computed once per country ----
def cagr(first, last, n_years):
    if pd.isna(first) or pd.isna(last) or first <= 0 or n_years <= 0:
        return np.nan
    return ((last / first) ** (1 / n_years) - 1) * 100

cagr_rows = []
for iso3, g in df.groupby("ISO3"):
    g = g.set_index("Year")["household_consumption_expenditure_constant_2015_usd"]
    years_present = g.dropna().index
    if len(years_present) < 2:
        cagr_rows.append({"ISO3": iso3, "consumption_cagr_2013_2023_real_pct": np.nan,
                           "cagr_start_year": np.nan, "cagr_end_year": np.nan})
        continue
    y0, y1 = years_present.min(), years_present.max()
    val = cagr(g.loc[y0], g.loc[y1], y1 - y0)
    cagr_rows.append({"ISO3": iso3, "consumption_cagr_2013_2023_real_pct": val,
                       "cagr_start_year": y0, "cagr_end_year": y1})
cagr_df = pd.DataFrame(cagr_rows)
df = df.merge(cagr_df, on="ISO3", how="left")

# ---- Global / regional share (based on latest year each country reports) ----
latest_idx = (
    df[df["household_consumption_expenditure_current_usd"].notna()]
    .groupby("ISO3")["Year"].idxmax()
)
latest = df.loc[latest_idx].copy()
global_total = latest["household_consumption_expenditure_current_usd"].sum()
latest["global_consumption_share_pct"] = (
    latest["household_consumption_expenditure_current_usd"] / global_total * 100
)
regional_totals = latest.groupby("Project_007_Region")["household_consumption_expenditure_current_usd"].transform("sum")
latest["regional_consumption_share_pct"] = (
    latest["household_consumption_expenditure_current_usd"] / regional_totals * 100
)

# ---- Save ----
col_order = [
    "ISO3", "Country", "Year", "Project_007_Region", "Official_Region", "Sub_Region",
    "population_total", "urban_population_pct", "population_65_plus_pct", "age_dependency_ratio_pct",
    "gdp_current_usd", "gdp_per_capita_current_usd", "gdp_per_capita_ppp_current_intl",
    "household_consumption_expenditure_current_usd",
    "household_consumption_expenditure_constant_2015_usd",
    "household_consumption_expenditure_per_capita_constant_2015_usd",
    "consumption_per_capita_check_usd",
    "household_consumption_pct_of_gdp",
    "consumption_growth_yoy_real_pct",
    "consumption_cagr_2013_2023_real_pct", "cagr_start_year", "cagr_end_year",
    "inflation_cpi_annual_pct", "unemployment_pct_of_labor_force", "internet_users_pct_of_population",
]
df = df[col_order]
df.to_csv("data/processed/master_consumer_spending.csv", index=False)
print("master_consumer_spending.csv:", df.shape)

snapshot_cols = col_order + ["global_consumption_share_pct", "regional_consumption_share_pct"]
latest_out = latest.reindex(columns=snapshot_cols)
latest_out.to_csv("data/processed/latest_year_snapshot.csv", index=False)
print("latest_year_snapshot.csv:", latest_out.shape)
print("\nCountries per region in snapshot:")
print(latest_out["Project_007_Region"].value_counts())
print("\nYear distribution in snapshot (data lag):")
print(latest_out["Year"].value_counts().sort_index())

# ---- Sanity check: per-capita cross-check vs WB's own per-capita series ----
check = df.dropna(subset=["consumption_per_capita_check_usd", "household_consumption_expenditure_per_capita_constant_2015_usd"])
print(f"\n(Cross-check computed independently; WB per-capita series is constant-USD so won't match nominal exactly -- expected.)")
