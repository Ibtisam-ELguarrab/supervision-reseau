import pandas as pd, glob

fichiers = glob.glob(r"C:\data_public\LocalNetDynamics\**\*.parquet", recursive=True)
print("Fichiers :", fichiers)

df = pd.concat([pd.read_parquet(f) for f in fichiers], ignore_index=True)
print("\nForme :", df.shape)
print("\nColonnes et types :")
print(df.dtypes.to_string())
print("\nValeurs manquantes :")
print(df.isna().sum().to_string())
print("\nSessions :", df["run_id"].nunique())
print("Machines :", df["host_label"].unique())
print("\nPremière ligne :")
print(df.iloc[0].to_string())