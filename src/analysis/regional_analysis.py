# -*- coding: utf-8 -*-
"""Regional aggregation and correlation analysis for Project 007."""
import pandas as pd
import numpy as np
from scipy import stats

snap = pd.read_csv("data/processed/latest_year_snapshot.csv")

# ---- Regional profile table ----
agg = snap.groupby("Project_007_Region").agg(
    n_countries=("ISO3", "count"),
    total_population=("population_total", "sum"),
    total_gdp_usd=("gdp_current_usd", "sum"),
    total_consumption_usd=("household_consumption_expenditure_current_usd", "sum"),
    median_gdp_per_capita_ppp=("gdp_per_capita_ppp_current_intl", "median"),
    median_consumption_per_capita=("household_consumption_expenditure_per_capita_constant_2015_usd", "median"),
    median_consumption_pct_gdp=("household_consumption_pct_of_gdp", "median"),
    median_cagr_real_pct=("consumption_cagr_2013_2023_real_pct", "median"),
    median_inflation_pct=("inflation_cpi_annual_pct", "median"),
    median_urban_pct=("urban_population_pct", "median"),
    median_internet_pct=("internet_users_pct_of_population", "median"),
    median_65plus_pct=("population_65_plus_pct", "median"),
).reset_index()

global_consumption = snap["household_consumption_expenditure_current_usd"].sum()
agg["global_consumption_share_pct"] = agg["total_consumption_usd"] / global_consumption * 100
agg = agg.sort_values("total_consumption_usd", ascending=False)
agg.to_csv("outputs/tables/regional_profiles.csv", index=False)
print("Regional profiles:\n", agg[["Project_007_Region", "n_countries", "global_consumption_share_pct", "median_cagr_real_pct"]].to_string(index=False))

# ---- Correlation analysis (income vs spending, digitalisation vs spending, inflation vs growth) ----
def corr_report(x_col, y_col, label):
    d = snap[[x_col, y_col]].dropna()
    if len(d) < 10:
        return {"pair": label, "n": len(d), "pearson_r": np.nan, "p_value": np.nan}
    r, p = stats.pearsonr(d[x_col], d[y_col])
    return {"pair": label, "n": len(d), "pearson_r": round(r, 3), "p_value": round(p, 5)}

pairs = [
    ("gdp_per_capita_ppp_current_intl", "household_consumption_expenditure_per_capita_constant_2015_usd", "GDP per capita (PPP) vs Consumption per capita"),
    ("internet_users_pct_of_population", "household_consumption_expenditure_per_capita_constant_2015_usd", "Internet penetration vs Consumption per capita"),
    ("internet_users_pct_of_population", "consumption_cagr_2013_2023_real_pct", "Internet penetration vs Consumption CAGR"),
    ("inflation_cpi_annual_pct", "consumption_growth_yoy_real_pct", "Inflation vs YoY real consumption growth"),
    ("urban_population_pct", "household_consumption_expenditure_per_capita_constant_2015_usd", "Urbanisation vs Consumption per capita"),
    ("population_65_plus_pct", "household_consumption_pct_of_gdp", "Aging population (65+) vs Consumption share of GDP"),
    ("gdp_per_capita_ppp_current_intl", "consumption_cagr_2013_2023_real_pct", "GDP per capita (PPP) vs Consumption CAGR (convergence check)"),
]
corr_results = pd.DataFrame([corr_report(*p) for p in pairs])
corr_results.to_csv("outputs/tables/correlation_analysis.csv", index=False)
print("\nCorrelation analysis:\n", corr_results.to_string(index=False))
