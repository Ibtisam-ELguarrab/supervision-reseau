import pandas as pd

DOSSIER = r"C:\data_public"
COLS = ["latence_moy_ms", "latence_max_ms", "jitter_ms", "perte_pct",
        "dns_resolve_ms", "tcp_connect_median_ms", "http_ms"]

def plus_longue_serie(s):
    groupes = (s != s.shift()).cumsum()
    return int(s.groupby(groupes).sum().max())

def regulariser(df):
    morceaux = []
    for (src, run, host), g in df.groupby(["source", "run_id", "host"]):
        g = g.set_index("timestamp").sort_index()
        g = g[~g.index.duplicated(keep="first")]

        # grille complète d'une minute
        grille = pd.date_range(g.index.min(), g.index.max(), freq="1min")
        g = g.reindex(grille)
        g["source"], g["run_id"], g["host"] = src, run, host

        # valeurs impossibles
        g.loc[(g["perte_pct"] < 0) | (g["perte_pct"] > 100), "perte_pct"] = pd.NA
        g.loc[g["latence_moy_ms"] < 0, "latence_moy_ms"] = pd.NA

        # marque les minutes sans mesure AVANT toute interpolation
        g["mesure_manquante"] = g["latence_moy_ms"].isna().astype(int)

        # interpolation limitée à 3 minutes consécutives, à l'intérieur de la série
        cols = [c for c in COLS if c in g.columns]
        g[cols] = g[cols].astype(float).interpolate(limit=3, limit_area="inside")

        g.index.name = "timestamp"
        g = g.reset_index()
        g["heure"] = g["timestamp"].dt.hour
        g["jour_semaine"] = g["timestamp"].dt.day_of_week
        morceaux.append(g)
    return pd.concat(morceaux, ignore_index=True)

for nom in ["localnet_1min", "collecte_1min"]:
    df = pd.read_csv(f"{DOSSIER}\\{nom}.csv", parse_dates=["timestamp"])
    propre = regulariser(df)
    propre.to_csv(f"{DOSSIER}\\{nom.replace('_1min', '_propre')}.csv", index=False)

    print(f"\n=== {nom} ===")
    print("Minutes avant :", len(df), "| après régularisation :", len(propre))
    print("Minutes sans mesure d'origine :", int(propre["mesure_manquante"].sum()))
    print("Plus longue série de minutes manquantes :",
          plus_longue_serie(propre["mesure_manquante"]))
    print("NaN restants (latence) :", int(propre["latence_moy_ms"].isna().sum()))
    print("Latence max observée (ms) :", round(propre["latence_moy_ms"].max(), 1))
    