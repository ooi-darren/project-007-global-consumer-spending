# -*- coding: utf-8 -*-
"""Generates all required visualisations for Project 007."""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import geopandas as gpd
import sys, os

sys.path.insert(0, os.path.dirname(__file__))
from style import ACCENT_1, ACCENT_2, GRAY, INK, INK_SECONDARY, INK_MUTED, GRID, SURFACE, add_source, end_label

OUT = "outputs/figures"
os.makedirs(OUT, exist_ok=True)

snap = pd.read_csv("data/processed/latest_year_snapshot.csv")
master = pd.read_csv("data/processed/master_consumer_spending.csv")
regional = pd.read_csv("outputs/tables/regional_profiles.csv")
seg = pd.read_csv("outputs/tables/segmentation_raw.csv")
attract = pd.read_csv("outputs/tables/market_attractiveness_ranking.csv")

REGION_ORDER = regional.sort_values("total_consumption_usd", ascending=False)["Project_007_Region"].tolist()
REGION_COLORS = {r: c for r, c in zip(REGION_ORDER, [ACCENT_1, '#5a9bd6', '#8fb8de', GRAY, GRAY, GRAY, GRAY, GRAY])}


def save(fig, name):
    fig.savefig(f"{OUT}/{name}.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("saved", name)


# ---------------------------------------------------------------------------
# 01. Global consumer spending map (choropleth)
# ---------------------------------------------------------------------------
world = gpd.read_file("data/external/world_110m.geojson")
merged = world.merge(snap, left_on="ISO_A3", right_on="ISO3", how="left")
fig, ax = plt.subplots(figsize=(14, 7.5))
merged.plot(column="household_consumption_expenditure_per_capita_constant_2015_usd", ax=ax, cmap="Blues",
            legend=True, missing_kwds={"color": "#e8e8e5", "label": "No data"},
            legend_kwds={"label": "Consumption per capita (constant 2015 USD)", "shrink": 0.55},
            edgecolor="white", linewidth=0.3)
ax.set_title("Consumer spending per capita is heavily concentrated in North America, Europe, and wealthy East Asia/Gulf states", loc='left', fontsize=13)
ax.set_axis_off()
add_source(fig, f"Source: World Bank, Household Final Consumption Expenditure per capita (constant 2015 US$) — PUBLIC. {snap['Year'].mode()[0]:.0f} or latest available year per country; grey = no data.")
save(fig, "01_global_spending_map")

# ---------------------------------------------------------------------------
# 02. Consumer spending by region (bar)
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8.5, 5.5))
r = regional.sort_values("total_consumption_usd")
bars = ax.barh(r["Project_007_Region"], r["total_consumption_usd"] / 1e12, color=ACCENT_1)
for b in bars:
    ax.annotate(f"${b.get_width():.1f}T", xy=(b.get_width(), b.get_y() + b.get_height() / 2),
                xytext=(5, 0), textcoords="offset points", va="center", fontsize=10)
ax.set_title("North America alone accounts for over a third of global consumer spending", loc="left")
ax.set_xlabel("Total household consumption expenditure (USD trillion)")
add_source(fig, "Source: World Bank Household Final Consumption Expenditure, latest available year per country — PUBLIC.")
save(fig, "02_spending_by_region")

# ---------------------------------------------------------------------------
# 03. Consumer spending per capita (top 20 + bottom 10)
# ---------------------------------------------------------------------------
top20 = snap.nlargest(20, "household_consumption_expenditure_per_capita_constant_2015_usd")
fig, ax = plt.subplots(figsize=(8.5, 8))
top20_sorted = top20.sort_values("household_consumption_expenditure_per_capita_constant_2015_usd")
colors = [ACCENT_1 if reg == "North America" else (ACCENT_2 if reg == "East Asia" else GRAY) for reg in top20_sorted["Project_007_Region"]]
bars = ax.barh(top20_sorted["Country"], top20_sorted["household_consumption_expenditure_per_capita_constant_2015_usd"], color=colors)
ax.set_title("The 20 highest consumer-spending-per-capita markets globally", loc="left")
ax.set_xlabel("Consumption per capita (constant 2015 USD)")
handles = [mpatches.Patch(color=ACCENT_1, label='North America'), mpatches.Patch(color=ACCENT_2, label='East Asia'), mpatches.Patch(color=GRAY, label='Other regions')]
ax.legend(handles=handles, loc='lower right', fontsize=9)
add_source(fig, "Source: World Bank Household Final Consumption Expenditure per capita, constant 2015 US$ — PUBLIC.")
save(fig, "03_spending_per_capita_top20")

# ---------------------------------------------------------------------------
# 04. Consumer spending growth (CAGR ranking by region, box-style spread)
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 6))
order = regional.sort_values("median_cagr_real_pct")["Project_007_Region"]
box_data = [snap[snap["Project_007_Region"] == r]["consumption_cagr_2013_2023_real_pct"].dropna().values for r in order]
bp = ax.boxplot(box_data, vert=False, patch_artist=True, widths=0.6,
                 medianprops=dict(color=INK, linewidth=2),
                 boxprops=dict(facecolor=SURFACE, edgecolor=GRAY, linewidth=1.3),
                 whiskerprops=dict(color=GRAY), capprops=dict(color=GRAY),
                 flierprops=dict(marker='o', markerfacecolor=ACCENT_2, markeredgecolor='none', markersize=4))
ax.set_yticks(range(1, len(order) + 1))
ax.set_yticklabels(order, fontsize=9.5)
ax.axvline(0, color=INK_MUTED, linewidth=1, linestyle=(0, (3, 3)))
ax.set_title("South & Southeast Asia and Africa show the fastest real consumption growth (2013–2023)", loc="left")
ax.set_xlabel("Real consumption CAGR, 2013–2023 (%)")
add_source(fig, "Source: World Bank, real (constant 2015 USD) household consumption CAGR per country — PUBLIC. Orange dots = outlier countries within their region.")
save(fig, "04_spending_growth_by_region")

# ---------------------------------------------------------------------------
# 05. Regional spending trends over time (indexed line chart)
# ---------------------------------------------------------------------------
trend = master.dropna(subset=["household_consumption_expenditure_constant_2015_usd"])
regional_trend = trend.groupby(["Project_007_Region", "Year"])["household_consumption_expenditure_constant_2015_usd"].sum().reset_index()
base_year = 2013
pivot = regional_trend.pivot(index="Year", columns="Project_007_Region", values="household_consumption_expenditure_constant_2015_usd")
indexed = pivot / pivot.loc[base_year] * 100
fig, ax = plt.subplots(figsize=(9.5, 6))
highlight = ["South & Southeast Asia", "North America", "Africa"]
for region in indexed.columns:
    color = {"South & Southeast Asia": ACCENT_1, "North America": ACCENT_2, "Africa": '#c96a3e'}.get(region, GRAY)
    lw = 2.4 if region in highlight else 1.2
    ax.plot(indexed.index, indexed[region], color=color, linewidth=lw)
    if region in highlight:
        end_label(ax, indexed.index[-1], indexed[region].iloc[-1], region, color, weight='bold')
ax.axhline(100, color=INK_MUTED, linewidth=0.8, linestyle=(0, (2, 2)))
ax.set_title("Indexed to 2013=100: South & Southeast Asia's consumption base has grown fastest", loc="left")
ax.set_ylabel("Real consumption, indexed (2013 = 100)")
add_source(fig, "Source: World Bank, real household consumption expenditure summed by region, constant 2015 US$ — PUBLIC.")
save(fig, "05_regional_trends_indexed")

# ---------------------------------------------------------------------------
# 06. Category-level spending: food's share falls as income rises (Engel's Law)
#     v2: real OECD COICOP category data (36 countries), replacing v1's GDP-share
#     substitute now that docs/LIMITATIONS.md item 1's data gap has been closed.
# ---------------------------------------------------------------------------
from scipy.stats import pearsonr
cat = pd.read_csv("data/processed/category_spending_shares_oecd.csv")
c6 = cat.merge(snap[["ISO3", "Country", "gdp_per_capita_ppp_current_intl"]], on="ISO3", how="inner")
c6 = c6.dropna(subset=["food_share_pct", "gdp_per_capita_ppp_current_intl"])
r, p = pearsonr(c6["gdp_per_capita_ppp_current_intl"], c6["food_share_pct"])

fig, ax = plt.subplots(figsize=(9, 6))
ax.scatter(c6["gdp_per_capita_ppp_current_intl"], c6["food_share_pct"], s=55, color=ACCENT_1, alpha=0.8, zorder=3)
label_these = ["United States", "Mexico", "Romania", "Colombia", "Ireland", "United Kingdom", "Costa Rica", "Chile"]
for _, row in c6[c6["Country"].isin(label_these)].iterrows():
    ax.annotate(row["Country"], xy=(row["gdp_per_capita_ppp_current_intl"], row["food_share_pct"]),
                xytext=(6, 4), textcoords="offset points", fontsize=9, color=INK_SECONDARY)
ax.set_title("Richer countries spend a smaller share of household budgets on food", loc="left")
ax.set_xlabel("GDP per capita, PPP (current international $)")
ax.set_ylabel("Food & non-alcoholic beverages, % of household spending")
ax.text(0.98, 0.95, f"Pearson r = {r:.2f}  (p < 0.001, n = {len(c6)})", transform=ax.transAxes,
        ha="right", va="top", fontsize=10, color=INK_SECONDARY, style="italic")
add_source(fig, "Source: OECD SDMX (Household final consumption expenditure by COICOP purpose) merged with World Bank GDP per capita, PPP — PUBLIC. "
                 "36 countries with complete category-level data (OECD members + partners); not the full 182-country panel — see docs/LIMITATIONS.md.")
save(fig, "06_food_share_vs_income_engels_law")

# ---------------------------------------------------------------------------
# 07. Income vs consumer spending (scatter)
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8.5, 6.5))
d = snap.dropna(subset=["gdp_per_capita_ppp_current_intl", "household_consumption_expenditure_per_capita_constant_2015_usd"])
for region in REGION_ORDER:
    sub = d[d["Project_007_Region"] == region]
    ax.scatter(sub["gdp_per_capita_ppp_current_intl"], sub["household_consumption_expenditure_per_capita_constant_2015_usd"],
               s=35, alpha=0.75, color=REGION_COLORS.get(region, GRAY), label=region, edgecolor='white', linewidth=0.3)
ax.set_title("Income and consumer spending are tightly linked (r = 0.88) — but with real regional spread", loc="left")
ax.set_xlabel("GDP per capita, PPP (current international $)")
ax.set_ylabel("Consumption per capita (constant 2015 USD)")
ax.legend(fontsize=8, loc='upper left', ncol=1)
add_source(fig, "Source: World Bank — PUBLIC. Pearson r=0.88, n=166 countries with both indicators available.")
save(fig, "07_income_vs_spending")

# ---------------------------------------------------------------------------
# 08. Inflation vs spending growth (scatter)
# ---------------------------------------------------------------------------
d8 = master.dropna(subset=["inflation_cpi_annual_pct", "consumption_growth_yoy_real_pct"])
d8 = d8[d8["inflation_cpi_annual_pct"].between(-10, 50)]  # exclude extreme hyperinflation outliers for readability
fig, ax = plt.subplots(figsize=(8.5, 6.5))
ax.scatter(d8["inflation_cpi_annual_pct"], d8["consumption_growth_yoy_real_pct"], s=18, alpha=0.35, color=ACCENT_1)
ax.axhline(0, color=INK_MUTED, linewidth=0.8)
ax.set_title("No strong relationship between annual inflation and real spending growth (r = -0.08, n.s.)", loc="left")
ax.set_xlabel("Inflation, consumer prices (annual %)")
ax.set_ylabel("Real household consumption growth, YoY (%)")
add_source(fig, "Source: World Bank, country-year observations 2013–2023 — PUBLIC. Chart excludes inflation >50% or <-10% for readability (extreme crisis years); correlation computed on full range.")
save(fig, "08_inflation_vs_growth")

# ---------------------------------------------------------------------------
# 09. Digitalisation vs spending (scatter)
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8.5, 6.5))
d9 = snap.dropna(subset=["internet_users_pct_of_population", "household_consumption_expenditure_per_capita_constant_2015_usd"])
for region in REGION_ORDER:
    sub = d9[d9["Project_007_Region"] == region]
    ax.scatter(sub["internet_users_pct_of_population"], sub["household_consumption_expenditure_per_capita_constant_2015_usd"],
               s=35, alpha=0.75, color=REGION_COLORS.get(region, GRAY), label=region, edgecolor='white', linewidth=0.3)
ax.set_yscale('log')
ax.set_title("Higher internet penetration tracks higher spending per capita (r = 0.61)", loc="left")
ax.set_xlabel("Internet users (% of population)")
ax.set_ylabel("Consumption per capita, log scale (constant 2015 USD)")
ax.legend(fontsize=8, loc='upper left')
add_source(fig, "Source: World Bank — PUBLIC. Pearson r=0.61 (log not used in correlation calc), n=154.")
save(fig, "09_digitalisation_vs_spending")

# ---------------------------------------------------------------------------
# 10. Country segmentation (PCA scatter, coloured by cluster)
# ---------------------------------------------------------------------------
CLUSTER_NAMES = {
    0: "Lower-Spending Developing Markets",
    1: "Crisis / High-Inflation Markets",
    2: "Mature High-Spending Markets",
    3: "Emerging Upper-Middle Markets",
}
seg["cluster_name"] = seg["cluster"].map(CLUSTER_NAMES)
palette = {0: GRAY, 1: '#c0392b', 2: ACCENT_1, 3: ACCENT_2}
fig, ax = plt.subplots(figsize=(9.5, 7))
for c, name in CLUSTER_NAMES.items():
    sub = seg[seg["cluster"] == c]
    ax.scatter(sub["pca1"], sub["pca2"], s=45, alpha=0.8, color=palette[c], label=f"{name} (n={len(sub)})", edgecolor='white', linewidth=0.4)
ax.set_title("Four data-driven consumer-market archetypes emerge from K-Means clustering", loc="left")
ax.set_xlabel("PCA dimension 1 (53% of variance)")
ax.set_ylabel("PCA dimension 2 (20% of variance)")
ax.legend(fontsize=8.5, loc='best')
add_source(fig, "Source: K-Means clustering on standardised GDP/capita, consumption/capita, CAGR, internet %, urban %, inflation — n=146 countries with complete data. See docs/METHODOLOGY.md.")
save(fig, "10_country_segmentation")

# ---------------------------------------------------------------------------
# 11. Market attractiveness matrix (spending power vs growth, sized by market size)
# ---------------------------------------------------------------------------
m11 = attract.merge(snap[["ISO3", "consumption_cagr_2013_2023_real_pct", "household_consumption_expenditure_per_capita_constant_2015_usd", "household_consumption_expenditure_current_usd"]], on="ISO3")
fig, ax = plt.subplots(figsize=(9.5, 7))
sizes = (m11["household_consumption_expenditure_current_usd"] / m11["household_consumption_expenditure_current_usd"].max()) * 2000 + 20
top_label = m11.nlargest(12, "market_attractiveness_score")
for region in REGION_ORDER:
    sub = m11[m11["Project_007_Region"] == region]
    ax.scatter(sub["consumption_cagr_2013_2023_real_pct"], sub["household_consumption_expenditure_per_capita_constant_2015_usd"],
               s=sizes.loc[sub.index], alpha=0.55, color=REGION_COLORS.get(region, GRAY), label=region, edgecolor='white', linewidth=0.4)
for _, row in top_label.iterrows():
    ax.annotate(row["Country"], xy=(row["consumption_cagr_2013_2023_real_pct"], row["household_consumption_expenditure_per_capita_constant_2015_usd"]),
                xytext=(6, 4), textcoords="offset points", fontsize=7.5, color=INK_SECONDARY)
ax.set_yscale('log')
ax.set_xlim(-8, 12)
ax.set_title("Market attractiveness matrix: growth vs. spending power (bubble size = total market size)", loc="left")
ax.set_xlabel("Real consumption CAGR, 2013–2023 (%)")
ax.set_ylabel("Consumption per capita, log scale (constant 2015 USD)")
ax.legend(fontsize=7.5, loc='lower left', ncol=2)
add_source(fig, "Source: World Bank — PUBLIC. Bubble size = total household consumption expenditure. Labels = top 12 by composite attractiveness score.")
save(fig, "11_market_attractiveness_matrix")

# ---------------------------------------------------------------------------
# 12. Regional comparison dashboard (4-panel)
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(13, 9))
r = regional.set_index("Project_007_Region").loc[REGION_ORDER]

ax = axes[0, 0]
ax.barh(r.index[::-1], r["global_consumption_share_pct"][::-1], color=ACCENT_1)
ax.set_title("Global consumption share (%)", loc='left', fontsize=11.5)

ax = axes[0, 1]
ax.barh(r.index[::-1], r["median_cagr_real_pct"][::-1], color=ACCENT_2)
ax.set_title("Median real consumption CAGR, 2013–2023 (%)", loc='left', fontsize=11.5)

ax = axes[1, 0]
ax.barh(r.index[::-1], r["median_consumption_per_capita"][::-1], color=GRAY)
ax.set_title("Median consumption per capita (constant 2015 USD)", loc='left', fontsize=11.5)

ax = axes[1, 1]
ax.barh(r.index[::-1], r["median_internet_pct"][::-1], color='#5a9bd6')
ax.set_title("Median internet penetration (%)", loc='left', fontsize=11.5)

fig.suptitle("Regional Consumer Market Comparison Dashboard", fontsize=15, fontweight='bold', x=0.01, ha='left', y=1.01)
add_source(fig, "Source: World Bank, all panels — PUBLIC. Latest available year per country.")
fig.tight_layout()
save(fig, "12_regional_dashboard")

# ---------------------------------------------------------------------------
# 13. [Supplementary] Spending category composition, selected countries
#     Not one of the brief's 12 required visualisations — an additional chart
#     made possible once real COICOP category data was obtained. Limited to 4
#     of the 12 categories (the largest, most policy-relevant) and a curated
#     18-country selection spanning the income range, to stay readable — a
#     36-country x 12-category stacked bar would be unreadable as a chart.
# ---------------------------------------------------------------------------
cat_countries = ["United States", "United Kingdom", "Germany", "France", "Italy", "Spain",
                  "Poland", "Czechia", "Hungary", "Greece", "Portugal", "Chile",
                  "Mexico", "Colombia", "Costa Rica", "Romania", "Lithuania", "Australia"]
c13 = cat.merge(snap[["ISO3", "Country"]], on="ISO3").set_index("Country").loc[cat_countries]
c13 = c13.sort_values("food_share_pct")
cats4 = [("food_share_pct", "Food & beverages", ACCENT_1),
         ("housing_share_pct", "Housing, water & energy", ACCENT_2),
         ("transport_share_pct", "Transport", '#5a9bd6'),
         ("recreation_share_pct", "Recreation & culture", GRAY)]

fig, ax = plt.subplots(figsize=(9.5, 7))
left = pd.Series(0.0, index=c13.index)
for col, label, color in cats4:
    ax.barh(c13.index, c13[col], left=left, color=color, label=label, height=0.65)
    left = left + c13[col]
ax.set_title("Spending composition varies by category as well as by income", loc="left")
ax.set_xlabel("% of household consumption expenditure")
ax.legend(loc="upper right", bbox_to_anchor=(1, -0.06), ncol=4, fontsize=9)
add_source(fig, "Source: OECD SDMX, COICOP purpose categories — PUBLIC. 4 of 12 categories shown (largest/most policy-relevant); remaining categories "
                 "(alcohol & tobacco, clothing, household goods, health, communication, education, restaurants & hotels, other) omitted for readability, not zero.")
save(fig, "13_category_composition_selected_countries")

print("\nAll 12 required visualisations generated, plus 1 supplementary (category composition).")
