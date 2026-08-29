# -*- coding: utf-8 -*-
"""
Market segmentation for Project 007.

Approach: standardise a set of theoretically-motivated variables (spending
power, spending growth, digitalisation, urbanisation, price stability), then
compare K-Means solutions for k=3..7 using silhouette score to pick k, rather
than assuming a cluster count in advance. Only countries with complete data on
all clustering variables are included (documented -- not silently imputed).
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA

snap = pd.read_csv("data/processed/latest_year_snapshot.csv")

CLUSTER_VARS = [
    "gdp_per_capita_ppp_current_intl",
    "household_consumption_expenditure_per_capita_constant_2015_usd",
    "consumption_cagr_2013_2023_real_pct",
    "internet_users_pct_of_population",
    "urban_population_pct",
    "inflation_cpi_annual_pct",
]

data = snap.dropna(subset=CLUSTER_VARS).copy()
print(f"Countries with complete data on all {len(CLUSTER_VARS)} clustering variables: {len(data)} / {len(snap)}")

X = data[CLUSTER_VARS].values
X_scaled = StandardScaler().fit_transform(X)

# ---- choose k by silhouette score ----
sil_scores = {}
for k in range(3, 8):
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(X_scaled)
    sil_scores[k] = silhouette_score(X_scaled, labels)
    print(f"k={k}: silhouette={sil_scores[k]:.3f}")

best_k = max(sil_scores, key=sil_scores.get)
print(f"\nSelected k={best_k} (highest silhouette score)")

km = KMeans(n_clusters=best_k, random_state=42, n_init=10)
data["cluster"] = km.fit_predict(X_scaled)

# ---- profile each cluster to assign a human-readable archetype name ----
profile = data.groupby("cluster")[CLUSTER_VARS + ["population_total"]].median()
profile["n_countries"] = data.groupby("cluster").size()
print("\nCluster profiles (medians):\n", profile.to_string())

# PCA for 2D visualisation
pca = PCA(n_components=2, random_state=42)
coords = pca.fit_transform(X_scaled)
data["pca1"], data["pca2"] = coords[:, 0], coords[:, 1]
print(f"\nPCA explained variance: {pca.explained_variance_ratio_.round(3)} (total {pca.explained_variance_ratio_.sum():.1%})")

data.to_csv("outputs/tables/segmentation_raw.csv", index=False)
profile.to_csv("outputs/tables/segmentation_cluster_profiles.csv")

with open("outputs/tables/segmentation_silhouette_scores.csv", "w") as f:
    f.write("k,silhouette_score\n")
    for k, s in sil_scores.items():
        f.write(f"{k},{s:.4f}\n")
