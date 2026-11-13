import pandas as pd
import numpy as np

# 1. Lecture (les lignes cassées sont ignorées)
df = pd.read_csv("data.csv", on_bad_lines="skip")
print("Lignes brutes :", len(df))

# 2. Types et lignes inutilisables
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df = df.dropna(subset=["timestamp", "host"])

# 3. Doublons exacts
avant = len(df)
df = df.drop_duplicates()
print("Doublons supprimés :", avant - len(df))

# 4. Cible sans réponse : latence 0.0 = valeur manquante, pas une vraie mesure
mask = df["disponible"] == 0
df.loc[mask, ["latence_moy_ms", "latence_max_ms", "jitter_ms"]] = np.nan
print("Mesures sans réponse (mises à NaN) :", int(mask.sum()))

# 5. Valeurs impossibles
df.loc[(df["perte_pct"] < 0) | (df["perte_pct"] > 100), "perte_pct"] = np.nan

# 6. Tri chronologique
df = df.sort_values("timestamp").reset_index(drop=True)

# 7. Colonnes utiles pour la personne 2 (sans rien retirer)
df["heure"] = df["timestamp"].dt.hour
df["jour_semaine"] = df["timestamp"].dt.day_of_week  # 0 = lundi, 6 = dimanche

# 8. Rapport
print("\nPériode :", df["timestamp"].min(), "->", df["timestamp"].max())
print("\nLignes par cible :\n", df["host"].value_counts())
print("\nValeurs manquantes :\n", df.isna().sum())
print("\nRésumé :\n", df[["latence_moy_ms", "jitter_ms", "perte_pct"]].describe().round(2))

df.to_csv("data_clean.csv", index=False)
print("\nFichier créé : data_clean.csv")