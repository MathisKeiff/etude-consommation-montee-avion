import pandas as pd
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view


def detecter_debut_montee_numpy(alt, seuil_montee=50, nb_points=5):
    """
    Détection vectorisée du début de montée :
    premier i tel que alt[i+nb_points] - alt[i] > seuil_montee
    """
    if len(alt) <= nb_points:
        return None

    diff = alt[nb_points:] - alt[:-nb_points]
    idx = np.flatnonzero(diff > seuil_montee)

    if len(idx) == 0:
        return None

    return int(idx[0])


def determination_profils_rapide(
    fichier_parquet,
    seuil_stabilite,
    seuil_reprise,
    point_L,
    point_M,
    point_G,
    nom_parquet_avec_palier=None,
    nom_parquet_sans_palier=None
):
    df = pd.read_parquet(fichier_parquet)

    taille_echantillon = 10
    seuil_alt_min = 1000

    df_avec_palier = []
    df_sans_palier = []

    # Compteurs debug
    nb_total = 0
    nb_trop_court = 0
    nb_pas_decollage = 0
    nb_idx_max_trop_petit = 0
    nb_takeoff_none = 0
    nb_takeoff_trop_tard = 0
    nb_pas_classe = 0
    nb_classes = 0

    for idx, (record, df_vol) in enumerate(df.groupby("record", sort=False)):
        nb_total += 1

        df_vol = df_vol.reset_index(drop=True)

        alt = df_vol["ALT [ft]"].to_numpy()
        n = len(alt)

        if n <= taille_echantillon:
            nb_trop_court += 1
            continue

        alt_range = alt.max() - alt.min()
        if alt_range < seuil_alt_min:
            nb_pas_decollage += 1
            continue

        idx_max = int(np.argmax(alt))
        if idx_max <= taille_echantillon:
            nb_idx_max_trop_petit += 1
            continue

        idx_takeoff = detecter_debut_montee_numpy(alt, seuil_montee=50, nb_points=5)
        if idx_takeoff is None:
            nb_takeoff_none += 1
            continue

        if idx_takeoff >= idx_max - taille_echantillon:
            nb_takeoff_trop_tard += 1
            continue

        # Partie utile de la montée
        alt_montee = alt[idx_takeoff:idx_max]
        if len(alt_montee) < taille_echantillon:
            nb_takeoff_trop_tard += 1
            continue

        # Fenêtres glissantes numpy
        windows = sliding_window_view(alt_montee, window_shape=taille_echantillon)

        # delta_fenetre = max - min pour chaque fenêtre
        delta_fenetres = windows.max(axis=1) - windows.min(axis=1)

        detection_palier = False
        classement_effectue = False

        # indices locaux dans alt_montee
        for j in np.flatnonzero(delta_fenetres < seuil_stabilite):
            idx_ref_local = j + taille_echantillon - 1
            alt_ref = alt_montee[idx_ref_local]

            idx_L = min(idx_ref_local + point_L, len(alt_montee) - 1)
            idx_M = min(idx_ref_local + point_M, len(alt_montee) - 1)
            idx_G = min(idx_ref_local + point_G, len(alt_montee) - 1)

            delta_L = alt_montee[idx_L] - alt_ref
            delta_M = alt_montee[idx_M] - alt_ref
            delta_G = alt_montee[idx_G] - alt_ref

            if (
                delta_L > seuil_reprise
                or delta_M > seuil_reprise
                or delta_G > seuil_reprise
            ):
                detection_palier = True
                continue

            # fin de montée détectée
            end_local = j + taille_echantillon
            end_global = idx_takeoff + end_local
            df_vol_coupe = df_vol.iloc[idx_takeoff:end_global].copy()

            if detection_palier:
                df_avec_palier.append(df_vol_coupe)
            else:
                df_sans_palier.append(df_vol_coupe)

            classement_effectue = True
            nb_classes += 1
            break

        if not classement_effectue:
            nb_pas_classe += 1
            continue

    df_avec_palier_final = pd.concat(df_avec_palier, ignore_index=True) if df_avec_palier else pd.DataFrame()
    df_sans_palier_final = pd.concat(df_sans_palier, ignore_index=True) if df_sans_palier else pd.DataFrame()

    if nom_parquet_avec_palier is not None:
        df_avec_palier_final.to_parquet(nom_parquet_avec_palier, index=False)

    if nom_parquet_sans_palier is not None:
        df_sans_palier_final.to_parquet(nom_parquet_sans_palier, index=False)

    print("----- RÉSUMÉ TRAITEMENT -----")
    print("Total vols :", nb_total)
    print("Trop courts :", nb_trop_court)
    print("Pas de vrai décollage :", nb_pas_decollage)
    print("idx_max trop petit :", nb_idx_max_trop_petit)
    print("Pas de début de montée détecté :", nb_takeoff_none)
    print("Début de montée trop tardif :", nb_takeoff_trop_tard)
    print("Pas classés :", nb_pas_classe)
    print("Classés :", nb_classes)
    print("Avec palier :", df_avec_palier_final['record'].nunique() if not df_avec_palier_final.empty else 0)
    print("Sans palier :", df_sans_palier_final['record'].nunique() if not df_sans_palier_final.empty else 0)

    return df_avec_palier_final, df_sans_palier_final


# appel de la fonction
df_avec, df_sans = determination_profils_rapide(
    fichier_parquet="dataset_aircraft1.parquet",
    seuil_stabilite=80,
    seuil_reprise=1000,
    point_L=10,
    point_M=30,
    point_G=200,
    nom_parquet_avec_palier="vols_avec_palier1.parquet",
    nom_parquet_sans_palier="vols_sans_palier1.parquet"
)

df_avec, df_sans = determination_profils_rapide(
    fichier_parquet="dataset_aircraft2.parquet",
    seuil_stabilite=80,
    seuil_reprise=1000,
    point_L=10,
    point_M=30,
    point_G=200,
    nom_parquet_avec_palier="vols_avec_palier2.parquet",
    nom_parquet_sans_palier="vols_sans_palier2.parquet"
)

df_avec, df_sans = determination_profils_rapide(
    fichier_parquet="dataset_aircraft3.parquet",
    seuil_stabilite=80,
    seuil_reprise=1000,
    point_L=10,
    point_M=30,
    point_G=200,
    nom_parquet_avec_palier="vols_avec_palier3.parquet",
    nom_parquet_sans_palier="vols_sans_palier3.parquet"
)