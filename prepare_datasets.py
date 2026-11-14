import pandas as pd

PUB = r"C:\data_public\LocalNetDynamics\dataset\localnet_dynamics.parquet"
SORTIE = r"C:\data_public"

# ---- Dataset public (une seule cible : 8.8.8.8) ----
pub = pd.read_parquet(PUB)
pub["timestamp"] = pd.to_datetime(pub["timestamp_local"].str[:19])
pub = pub.rename(columns={
    "target": "host",
    "rtt_avg_ms": "latence_moy_ms",
    "rtt_max_ms": "latence_max_ms",
    "packet_loss_pct": "perte_pct",
})
extras = ["dns_resolve_ms", "tcp_connect_median_ms", "http_ms"]
pub["source"] = "localnetdynamics"
pub = pub[["timestamp", "source", "run_id", "host", "latence_moy_ms",
           "latence_max_ms", "jitter_ms", "perte_pct"] + extras]

# ---- Vos données (les 3 cibles sont conservées) ----
moi = pd.read_csv("data_clean.csv", parse_dates=["timestamp"])
moi["source"] = "collecte_perso"
moi["run_id"] = "collecte_13nov"
moi = moi[["timestamp", "source", "run_id", "host", "latence_moy_ms",
           "latence_max_ms", "jitter_ms", "perte_pct"]]

# ---- Ré-échantillonnage à 1 minute ----
def a_la_minute(df, cols_extra=()):
    agg = {"latence_moy_ms": "mean", "latence_max_ms": "max",
           "jitter_ms": "mean", "perte_pct": "mean"}
    for c in cols_extra:
        agg[c] = "mean"
    return (df.set_index("timestamp")
              .groupby(["source", "run_id", "host"])
              .resample("1min").agg(agg)
              .dropna(subset=["latence_moy_ms"])
              .reset_index())

pub_min = a_la_minute(pub, extras)
moi_min = a_la_minute(moi)

pub_min.to_csv(SORTIE + r"\localnet_1min.csv", index=False)
moi_min.to_csv(SORTIE + r"\collecte_1min.csv", index=False)

print("Dataset public :", pub_min.shape,
      "|", pub_min["timestamp"].min(), "->", pub_min["timestamp"].max())
print("Vos données   :", moi_min.shape,
      "|", moi_min["timestamp"].min(), "->", moi_min["timestamp"].max())

# Comparaison sur la cible commune
m = moi_min[moi_min["host"] == "8.8.8.8"]
print("\nCible 8.8.8.8, latence moyenne (ms) :")
print("  public :", round(pub_min["latence_moy_ms"].median(), 1), "(médiane)")
print("  vous   :", round(m["latence_moy_ms"].median(), 1), "(médiane)")