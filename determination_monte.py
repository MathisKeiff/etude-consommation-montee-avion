import pandas as pd
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view




#Fonction permettant de récupérer l'indice du démarage d'une montée (altitude t0+5 - altitude t0>50)
def detecter_debut_montee_numpy(alt, seuil_montee=50, nb_points=5):
   
   #Check pour être sur que altitude comporte asser de valeurs 
    if len(alt) <= nb_points:
        return None

    #création d'un vecteur contenant toutes les différences alt[i + nb_points] - alt[i]
    diff = alt[nb_points:] - alt[:-nb_points]

    #renvoie les indices de diff ou la condition demandé est vraie
    idx = np.flatnonzero(diff > seuil_montee)

    if len(idx) == 0:
        return None

    return int(idx[0])

#Cette fonction analyse les profils d’altitude contenus dans un fichier parquet afin de 
#classifier les vols selon leur type de montée. L’objectif est de distinguer les montées 
#avec palier intermédiaire des montées continues sans palier.
def determination_profils_rapide(
    fichier_parquet,
    taille_echantillon,
    seuil_alt_min,
    seuil_stabilite,
    seuil_reprise,
    point_P,
    point_M,
    point_G,
    nom_parquet_avec_palier=None,
    nom_parquet_sans_palier=None
):
    df = pd.read_parquet(fichier_parquet)

    df_avec_palier = []
    df_sans_palier = []

    #variable de classification
    nb_total = 0
    nb_trop_court = 0
    nb_pas_decollage = 0
    nb_idx_max_trop_petit = 0
    nb_takeoff_none = 0
    nb_takeoff_trop_tard = 0
    nb_pas_classe = 0
    nb_classes = 0


    #Objectif : Catégoriser chaque vols 
    #boucler sur chaque => récupérer le nom du vols "record_XX" créer un df de toutes les valeurs du vols
    #la boucle for permet d'avoir un idx de 0...n le nombre de vol
    #df.groupby est une fonction qui permet de séparer le dataset vol par vol renvoie : (nom_du_groupe, dataframe_du_groupe)
    for idx, (record, df_vol) in enumerate(df.groupby("record", sort=False)):
        nb_total += 1

        #groupby ne reset pas les index quand il range par groupe
        df_vol = df_vol.reset_index(drop=True)


        alt = df_vol["ALT [ft]"].to_numpy()
        n = len(alt)

        #vérification du nombre de valeurs dans un vol
        if n <= taille_echantillon:
            nb_trop_court += 1
            continue
        
        #vérification que l'avion décolle
        alt_range = alt.max() - alt.min()
        if alt_range < seuil_alt_min:
            nb_pas_decollage += 1
            continue
        
        #vérification du nombre de valeurs après 
        idx_max = int(np.argmax(alt))
        if idx_max <= taille_echantillon:
            nb_idx_max_trop_petit += 1
            continue

        idx_takeoff = detecter_debut_montee_numpy(alt, seuil_montee=50, nb_points=5)

        #vérification que le vol comporte une montée
        if idx_takeoff is None:
            nb_takeoff_none += 1
            continue
        
        #vérification que l'algorithme ne détecte pas une montée après l'atteinte de l'altitude de croisière
        if idx_takeoff >= idx_max - taille_echantillon:
            nb_takeoff_trop_tard += 1
            continue

        #récupération de l'intervalle qui nous intéresse [début de la montée, fin de la montée]
        alt_montee = alt[idx_takeoff:idx_max]

        #vérification du nombre de valeur contenu dans alt_montee
        if len(alt_montee) < taille_echantillon:
            nb_takeoff_trop_tard += 1
            continue

        # Utilisation de la fonction sliding_window_view :
        # crée toutes les fenêtres glissantes possibles de taille "taille_echantillon" à partir du vecteur alt_montee
        windows = sliding_window_view(alt_montee, window_shape=taille_echantillon)

        # récupération du delta de chaque fenetre max - min
        #axis = 1 : permet de faire ligne par ligne
        delta_fenetres = windows.max(axis=1) - windows.min(axis=1)

        detection_palier = False
        classement_effectue = False

        #Objectif : classer les montées sans et avec plateau
        #1)récupération de l'indice du dernier point de la fenetre condidate
        #2)utilisation de 3 points : petit, moyen, grand
        #pour une vérification qu'une montée à lieu plus tard


        # recherche des montées suceptible d'avoir un plateau
        # si le delta d'une fenêtre est petit => succeptible d'être un palier 
        for j in np.flatnonzero(delta_fenetres < seuil_stabilite):

            idx_ref_local = j + taille_echantillon - 1
            alt_ref = alt_montee[idx_ref_local]

            idx_L = min(idx_ref_local + point_P, len(alt_montee) - 1)
            idx_M = min(idx_ref_local + point_M, len(alt_montee) - 1)
            idx_G = min(idx_ref_local + point_G, len(alt_montee) - 1)

            delta_L = alt_montee[idx_L] - alt_ref
            delta_M = alt_montee[idx_M] - alt_ref
            delta_G = alt_montee[idx_G] - alt_ref

            #on étudie les points sur alt_montee donc tous les points futurs doivent être supérieur à l'altitude référence
            if (
                delta_L > seuil_reprise
                or delta_M > seuil_reprise
                or delta_G > seuil_reprise
            ):
                detection_palier = True
                continue

            # la boucle for s'arrête au premier plateau où il n'y pas de reprise de montée (début de croisière)
            #comme le max_altitude se trouve sur "l'altitude de croisière"
            #on s'arrête au début de la phase de croisière
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
        
        #cas où on ne rencontre aucune fenêtre qui respecte le seuil de stabilité
        #cela veut dire que le max est très proche du début de la phase de croisière
        #on ajoute donc ce vol à ceux sans palier
        if not classement_effectue:
            nb_pas_classe += 1
            df_vol_coupe = df_vol.iloc[idx_takeoff:idx_max].copy()
            df_sans_palier.append(df_vol_coupe)
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


# appel de la fonction
determination_profils_rapide(
    fichier_parquet="dataset_aircraft1.parquet",
    taille_echantillon = 10,
    seuil_alt_min = 1000,
    seuil_stabilite=80,
    seuil_reprise=200,
    point_P=10,
    point_M=30,
    point_G=200,
    nom_parquet_avec_palier="vols_avec_palier1.parquet",
    nom_parquet_sans_palier="vols_sans_palier1.parquet"
)

determination_profils_rapide(
    fichier_parquet="dataset_aircraft2.parquet",
    taille_echantillon = 10,
    seuil_alt_min = 1000,
    seuil_stabilite=80,
    seuil_reprise=200,
    point_P=10,
    point_M=30,
    point_G=200,
    nom_parquet_avec_palier="vols_avec_palier2.parquet",
    nom_parquet_sans_palier="vols_sans_palier2.parquet"
)

determination_profils_rapide(
    fichier_parquet="dataset_aircraft3.parquet",
    taille_echantillon = 10,
    seuil_alt_min = 1000,
    seuil_stabilite=80,
    seuil_reprise=200,
    point_P=10,
    point_M=30,
    point_G=200,
    nom_parquet_avec_palier="vols_avec_palier3.parquet",
    nom_parquet_sans_palier="vols_sans_palier3.parquet"
)