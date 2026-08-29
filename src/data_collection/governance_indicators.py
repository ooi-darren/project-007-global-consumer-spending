# -*- coding: utf-8 -*-
"""
World Bank Worldwide Governance Indicators (WGI) for Project 007.

Added in v2 to fill the gap documented in v1's docs/LIMITATIONS.md (item 7):
the original 4-pillar Market Attractiveness Index had no risk/regulatory
dimension, so a market could score well on size/growth/spending/digital
readiness while being one investors would actually treat cautiously for
stability reasons (the v1 write-up used Argentina and Lebanon as the
illustrating case).

Source: World Bank Worldwide Governance Indicators (WGI) project, same
api.worldbank.org/v2 endpoint as src/data_collection/world_bank.py (source=3
in the WB API's source catalogue), CC-BY 4.0, no authentication required.
https://info.worldbank.org/governance/wgi/

Each indicator is a **percentile rank (0-100) against all countries in the
WGI's own global sample** for that year -- already on a comparable 0-100
scale by construction, not a raw score this script invents.

Indicators pulled (3 of WGI's 6 dimensions -- the 3 most directly relevant to
"is this a stable place to do business", as opposed to voice/accountability
or government effectiveness which speak to different questions):
  GOV_WGI_PV.SC  political_stability_score   Political Stability & Absence of Violence
  GOV_WGI_RL.SC  rule_of_law_score           Rule of Law
  GOV_WGI_RQ.SC  regulatory_quality_score    Regulatory Quality

Usage: python src/data_collection/governance_indicators.py
Writes one CSV per indicator to data/raw/worldbank/, matching the naming and
row shape (iso3, year, value) of world_bank.py's output so downstream code
can treat them uniformly.
"""
import requests
import pandas as pd
import time
import os

INDICATORS = {
    "GOV_WGI_PV.SC": "political_stability_score",
    "GOV_WGI_RL.SC": "rule_of_law_score",
    "GOV_WGI_RQ.SC": "regulatory_quality_score",
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
    # Drop rows with no iso3 (WB aggregates like "World", "Arab World" --
    # same filtering logic as build_master_dataset.py's inner join, applied
    # here at source so this file is clean on its own).
    df = df[df["iso3"].notna() & (df["iso3"] != "")]
    df = df.drop(columns=["country_name"])
    out_path = os.path.join(OUT_DIR, f"{name}.csv")
    df.to_csv(out_path, index=False)
    print(f"{code} ({name}): {len(df)} rows, {df['iso3'].nunique()} countries -> {out_path}")
    return df


def main():
    for code, name in INDICATORS.items():
        fetch_indicator(code, name)
        time.sleep(0.3)


if __name__ == "__main__":
    main()
