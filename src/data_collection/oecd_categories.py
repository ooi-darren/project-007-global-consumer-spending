# -*- coding: utf-8 -*-
"""
Supplementary category-level (COICOP) household spending data, OECD SDMX API.

This was initially evaluated and descoped (see docs/LIMITATIONS.md v1) because
the SDMX dimension-key structure could not be resolved. On a second, more
careful pass -- using the API's own `availableconstraint` endpoint to discover
real, valid dimension values rather than guessing -- a working query was found.

Coverage: ~40 countries (OECD members plus several partner economies: Colombia,
Costa Rica, Cameroon, Senegal, Hong Kong), NOT the full 182-country panel. This
is presented as a clearly-scoped supplementary layer, not blended into the main
master dataset, consistent with the brief's instruction not to force identical
category coverage across countries where the underlying data doesn't support it.

Dataflow: OECD.SDD.NAD, DSD_NAMAIN10@DF_TABLE5 (Household final consumption
expenditure by COICOP purpose). Key structure (12 dimensions):
FREQ.REF_AREA.SECTOR.COUNTERPART_SECTOR.TRANSACTION.INSTR_ASSET.ACTIVITY.
EXPENDITURE.UNIT_MEASURE.PRICE_BASE.TRANSFORMATION.TABLE_IDENTIFIER
"""
import requests
import pandas as pd

URL = ("https://sdmx.oecd.org/public/rest/data/OECD.SDD.NAD,DSD_NAMAIN10@DF_TABLE5,1.0/"
       "A..S14..P31DC....XDC.V.N.T0117")

COICOP_LABELS = {
    "CP01": "Food & non-alcoholic beverages", "CP02": "Alcohol, tobacco & narcotics",
    "CP03": "Clothing & footwear", "CP04": "Housing, water, electricity, gas & fuels",
    "CP05": "Household goods & maintenance", "CP06": "Health",
    "CP07": "Transport", "CP08": "Communication", "CP09": "Recreation & culture",
    "CP10": "Education", "CP11": "Restaurants & hotels", "CP12": "Other goods & services",
}
AGGREGATES_TO_EXCLUDE = {"EA20", "EU27_2020"}  # euro-area / EU aggregates, not countries


def fetch():
    resp = requests.get(URL, params={"startPeriod": "2021", "endPeriod": "2023", "format": "csvfile"}, timeout=90)
    resp.raise_for_status()
    with open("data/raw/oecd_coicop_raw.csv", "wb") as f:
        f.write(resp.content)
    df = pd.read_csv("data/raw/oecd_coicop_raw.csv")
    top_level = list(COICOP_LABELS.keys()) + ["_T"]
    df = df[df["EXPENDITURE"].isin(top_level)]
    df = df[~df["REF_AREA"].isin(AGGREGATES_TO_EXCLUDE)]
    return df


def build_category_shares(df):
    # Pivot first, then pick each country's latest year that has a COMPLETE
    # category breakdown (not just a `_T` total with no CP01-CP12 detail --
    # some countries report totals for a year before detail catches up).
    pivot = df.pivot_table(index=["REF_AREA", "TIME_PERIOD"], columns="EXPENDITURE", values="OBS_VALUE").reset_index()
    cp_cols = [c for c in COICOP_LABELS if c in pivot.columns]
    pivot = pivot.dropna(subset=cp_cols, how="all")
    latest_year = pivot.groupby("REF_AREA")["TIME_PERIOD"].transform("max")
    pivot = pivot[pivot["TIME_PERIOD"] == latest_year]

    for code in COICOP_LABELS:
        pivot[f"{code}_share_pct"] = (pivot[code] / pivot["_T"] * 100).round(2)

    out_cols = ["REF_AREA", "TIME_PERIOD"] + [f"{c}_share_pct" for c in COICOP_LABELS]
    out = pivot[out_cols].rename(columns={"REF_AREA": "ISO3", "TIME_PERIOD": "Year"})
    out = out.rename(columns={f"{c}_share_pct": f"{COICOP_LABELS[c].split(' ')[0].lower().replace(',', '')}_share_pct" for c in COICOP_LABELS})
    return out


if __name__ == "__main__":
    df = fetch()
    print(f"Fetched {len(df)} rows, {df['REF_AREA'].nunique()} countries (after excluding EU/euro-area aggregates)")
    shares = build_category_shares(df)
    shares.to_csv("data/processed/category_spending_shares_oecd.csv", index=False)
    print(f"Saved category_spending_shares_oecd.csv: {shares.shape}")
    print(shares.head())
