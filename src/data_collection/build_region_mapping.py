# -*- coding: utf-8 -*-
"""
Builds REGION_MAPPING.csv for Project 007.

Base classification: UN M49 standard (via the widely-used ISO-3166-Countries-with-
Regional-Codes compilation, itself sourced from the UN Statistics Division:
https://unstats.un.org/unsd/methodology/m49/). This gives an authoritative,
publicly documented Region/Sub-region for every country.

The UN M49 sub-region is mapped to the Project 007 8-region framework using a
transparent, mostly mechanical rule (sub-region -> Project_007_Region), with a
small number of DOCUMENTED overrides where UN M49's geographic classification
diverges from common market-research/business convention (e.g., Iran is UN M49
"Southern Asia" but is treated as Middle East here, matching how virtually every
commercial market-research firm and the IMF's own regional department group it).

World Bank's own region label is retained as Official_Region, since World Bank
is this project's primary data source (Tier 1).
"""
import pandas as pd

un = pd.read_csv("data/external/un_m49_regions.csv")
wb_countries = pd.read_json("data/raw/wb_countries.json", typ="series")[1]
wb_df = pd.json_normalize(wb_countries)
wb_df = wb_df[wb_df["region.value"] != "Aggregates"].copy()
wb_df = wb_df.rename(columns={"id": "iso3", "name": "wb_name", "region.value": "official_region"})
wb_df = wb_df[["iso3", "wb_name", "official_region"]]

un = un.rename(columns={"alpha-3": "iso3", "name": "un_name", "sub-region": "sub_region"})
un = un[["iso3", "un_name", "region", "sub_region"]]

merged = wb_df.merge(un, on="iso3", how="left")

SUBREGION_TO_P007 = {
    "Northern America": "North America",
    "Northern Europe": "Europe",
    "Western Europe": "Europe",
    "Eastern Europe": "Europe",
    "Southern Europe": "Europe",
    "Central Asia": "Europe",  # follows World Bank's own "Europe & Central Asia" grouping
    "Latin America and the Caribbean": "Latin America",
    "Western Asia": "Middle East",
    "Northern Africa": "Africa",
    "Sub-Saharan Africa": "Africa",
    "Eastern Africa": "Africa",
    "Middle Africa": "Africa",
    "Southern Africa": "Africa",
    "Western Africa": "Africa",
    "Eastern Asia": "East Asia",
    "South-eastern Asia": "South & Southeast Asia",
    "Southern Asia": "South & Southeast Asia",
    "Australia and New Zealand": "Oceania",
    "Melanesia": "Oceania",
    "Micronesia": "Oceania",
    "Polynesia": "Oceania",
}

# Documented manual overrides: (iso3) -> (Project_007_Region, note)
OVERRIDES = {
    "IRN": ("Middle East", "UN M49 classifies Iran as Southern Asia; overridden to Middle East to match standard market-research/IMF regional convention."),
    "TWN": ("East Asia", "ISO/UN source has no region for Taiwan (political status); assigned East Asia by standard geographic and economic convention."),
    "AFG": ("South & Southeast Asia", "UN M49 Southern Asia; kept in South & Southeast Asia bucket (not Middle East) consistent with South Asian regional economic groupings (e.g. SAARC)."),
    "CHI": ("Europe", "Channel Islands (Jersey/Guernsey, UK Crown Dependencies) have no UN M49 sub-region; assigned Europe by geography."),
    "XKX": ("Europe", "Kosovo has a non-standard/provisional ISO code (XKX) not present in the UN M49 reference table used; assigned Europe (Balkans) by geography."),
}

def assign_region(row):
    if row["iso3"] in OVERRIDES:
        return OVERRIDES[row["iso3"]][0]
    sub = row["sub_region"]
    if pd.isna(sub):
        return "Unclassified"
    return SUBREGION_TO_P007.get(sub, "Unclassified")

def note_for(row):
    if row["iso3"] in OVERRIDES:
        return OVERRIDES[row["iso3"]][1]
    if pd.isna(row["sub_region"]):
        return "No UN M49 sub-region match found for this ISO3 code; needs manual review."
    return ""

merged["Project_007_Region"] = merged.apply(assign_region, axis=1)
merged["Notes"] = merged.apply(note_for, axis=1)
merged["Source"] = "World Bank (country list, Official_Region) + UN M49 via ISO-3166-Countries-with-Regional-Codes (Sub_Region, base geography)"

out = merged.rename(columns={
    "wb_name": "Country", "iso3": "ISO3", "official_region": "Official_Region", "sub_region": "Sub_Region",
})[["Country", "ISO3", "Project_007_Region", "Official_Region", "Sub_Region", "Source", "Notes"]]

out = out.sort_values(["Project_007_Region", "Country"]).reset_index(drop=True)
out.to_csv("data/processed/REGION_MAPPING.csv", index=False)

print("Total countries:", len(out))
print(out["Project_007_Region"].value_counts())
unclassified = out[out["Project_007_Region"] == "Unclassified"]
if len(unclassified):
    print("\nUNCLASSIFIED (needs review):")
    print(unclassified[["Country", "ISO3"]].to_string(index=False))
