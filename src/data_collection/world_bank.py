"""
World Bank data collection for Project 007 — Global Consumer Spending Intelligence.

Pulls indicators from the World Bank Open Data API (api.worldbank.org/v2), which
requires no authentication and is redistributable (World Bank Open Data is CC-BY 4.0).

API docs: https://datahelpdesk.worldbank.org/knowledgebase/articles/889392

Usage: python world_bank.py
Writes one raw JSON-derived CSV per indicator to data/raw/worldbank/, plus a
combined long-format panel to data/raw/worldbank_panel_long.csv.
"""
import requests
import pandas as pd
import time
import os

INDICATORS = {
    "NY.GDP.MKTP.CD": "gdp_current_usd",
    "NY.GDP.PCAP.CD": "gdp_per_capita_current_usd",
    "NY.GDP.PCAP.PP.CD": "gdp_per_capita_ppp_current_intl",
    "SP.POP.TOTL": "population_total",
    "NE.CON.PRVT.CD": "household_consumption_expenditure_current_usd",
    "NE.CON.PRVT.KD": "household_consumption_expenditure_constant_2015_usd",
    "NE.CON.PRVT.PC.KD": "household_consumption_expenditure_per_capita_constant_2015_usd",
    "NE.CON.PRVT.ZS": "household_consumption_pct_of_gdp",
    "FP.CPI.TOTL.ZG": "inflation_cpi_annual_pct",
    "SL.UEM.TOTL.ZS": "unemployment_pct_of_labor_force",
    "SP.URB.TOTL.IN.ZS": "urban_population_pct",
    "IT.NET.USER.ZS": "internet_users_pct_of_population",
    "SP.POP.65UP.TO.ZS": "population_65_plus_pct",
    "SP.POP.DPND": "age_dependency_ratio_pct",
}

YEAR_RANGE = "2013:2023"
BASE = "https://api.worldbank.org/v2/country/all/indicator/{code}"
OUT_DIR = os.path.join("data", "raw", "worldbank")
os.makedirs(OUT_DIR, exist_ok=True)


def fetch_indicator(code, name):
    all_rows = []
    page = 1
    while True:
        url = BASE.format(code=code)
        params = {"format": "json", "date": YEAR_RANGE, "per_page": 20000, "page": page}
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        payload = resp.json()
        if not isinstance(payload, list) or len(payload) < 2 or payload[1] is None:
            break
        meta, rows = payload[0], payload[1]
        all_rows.extend(rows)
        if page >= meta.get("pages", 1):
            break
        page += 1
    df = pd.DataFrame([
        {
            "country_name": r["country"]["value"],
            "iso3": r["countryiso3code"],
            "year": int(r["date"]),
            name: r["value"],
        }
        for r in all_rows
    ])
    out_path = os.path.join(OUT_DIR, f"{name}.csv")
    df.to_csv(out_path, index=False)
    print(f"{code} ({name}): {len(df)} rows -> {out_path}")
    return df


def main():
    frames = []
    for code, name in INDICATORS.items():
        df = fetch_indicator(code, name)
        frames.append(df.set_index(["iso3", "year", "country_name"])[[name]])
        time.sleep(0.3)
    combined = pd.concat(frames, axis=1).reset_index()
    combined.to_csv(os.path.join("data", "raw", "worldbank_panel_wide.csv"), index=False)
    print("Combined panel:", combined.shape)


if __name__ == "__main__":
    main()
