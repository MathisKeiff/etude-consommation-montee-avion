import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def tracer_decollage_alt(
    fichier_parquet,
    alt_max=None,
    t_max=None,
    seuil_detection=5,
    max_vols=None
):
    """
    Trace les profils de décollage (ALT) pour tous les vols,
    en normalisant chaque courbe pour qu'elle commence en (0, 0).

    Paramètres
    ----------
    fichier_parquet : str
        Chemin du dataset parquet.

    alt_max : float ou None
        Altitude max après normalisation pour couper la courbe
        (ex: 3000 ft).

    t_max : int ou None
        Nombre max de points après décollage.

    seuil_detection : float
        Seuil de variation d'altitude pour détecter le décollage.

    max_vols : int ou None
        Nombre maximum de vols à tracer (None = tous).
    """

    df = pd.read_parquet(fichier_parquet)

    plt.figure(figsize=(10, 6))

    vols = list(df["record"].unique())
    if max_vols is not None:
        vols = vols[:max_vols]

    nb_traces = 0

    for record in vols:
        df_vol = df[df["record"] == record].copy()

        # sécurité : trier si jamais l'ordre n'est pas garanti
        df_vol = df_vol.reset_index(drop=True)

        if len(df_vol) < 2:
            continue

        # variation d'altitude
        dalt = df_vol["ALT [ft]"].diff()

        # premier point où la montée devient significative
        idx_takeoff_list = dalt[dalt > seuil_detection].index

        if len(idx_takeoff_list) == 0:
            continue

        idx_takeoff = idx_takeoff_list[0]

        # temps relatif : 0 au décollage
        df_vol["t_rel"] = np.arange(len(df_vol)) - idx_takeoff

        # altitude relative : 0 au décollage
        alt_takeoff = df_vol.loc[idx_takeoff, "ALT [ft]"]
        df_vol["alt_rel"] = df_vol["ALT [ft]"] - alt_takeoff

        # garder uniquement après décollage
        df_vol = df_vol[df_vol["t_rel"] >= 0].copy()

        # limiter l'altitude relative
        if alt_max is not None:
            df_vol = df_vol[df_vol["alt_rel"] <= alt_max]

        # limiter la durée
        if t_max is not None:
            df_vol = df_vol[df_vol["t_rel"] <= t_max]

        if df_vol.empty:
            continue

        plt.plot(df_vol["t_rel"], df_vol["alt_rel"], alpha=0.3)
        nb_traces += 1

    plt.xlabel("Temps relatif au décollage")
    plt.ylabel("Altitude relative (ft)")
    plt.title(f"Profils de décollage normalisés ({nb_traces} vols)")
    plt.grid(True)
    plt.show(block=True)
<<<<<<< HEAD
    plt.close("all")
=======
    plt.close('all')
>>>>>>> d4cf62fcfbb0a8e7e52135b4f28604b5dfe9f177
