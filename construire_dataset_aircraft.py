import h5py
import pandas as pd
import numpy as np


set_variable_a_garder = [
"Q_1 [lb/h]","Q_2 [lb/h]",
"EGT_1 [deg C]","EGT_2 [deg C]",
"N1_1 [% rpm]", "N1_2 [% rpm]","N2_1 [% rpm]","N2_2 [% rpm]",
"TLA_1 [deg]","TLA_2 [deg]",
"ALT [ft]",
"M [Mach]",
"TAT [deg C]", 
"PS3_1 [psia]","PS3_2 [psia]",
"PT2_1 [mbar]","PT2_2 [mbar]",
"T2_1 [deg C]","T2_2 [deg C]","T3_1 [deg C]","T3_2 [deg C]","T5_1 [deg C]","T5_2 [deg C]"
]

def construire_dataset_aircraft(h5_path, set_variable_a_garder, nom_parquet = None):
    
    Aircraft = h5py.File(h5_path, "r")
    
    liste_vols = []
    vol_ignore = []

    elem_record = ["axis0", "axis1", "block0_values"]

    #Création d'une variable pour ignorer les vols qui ne sont pas pris en compte
    ignore = False
    for record_name in Aircraft.keys():
        
        record = Aircraft[record_name]

        #Vérification que tous les éléments pour l'étude du vol record_XX sont présents
        #si il manque un seul des 3 éléments le vol n'est pas pris en compte
        for elem in elem_record:
            if not(elem in record.keys()):
                vol_ignore.append(record_name)
                ignore = True
                break
        
        if ignore:
            ignore = False
            continue
        
        axis0 = record["axis0"][:]
        axis1 = record["axis1"][:]
        values = record["block0_values"][:] #équivalent à [:,:]

        colonne = []
        for variable_name in axis0:
            colonne.append(variable_name.decode("utf-8"))
        
        df = pd.DataFrame(values, columns=colonne, index=axis1)
        
        #vérification que toute les variables ciblé sont présente dans le 
        #dataframe que l'on a créé
        for var in set_variable_a_garder:
            if not(var in df.columns):
                vol_ignore.append(record_name)
                ignore = True
                break
        if ignore:
            ignore = False
            continue

        df_cible = df[set_variable_a_garder].copy()

        #conversion explicite en numérique
        for col in df_cible.columns:
            df_cible[col] = pd.to_numeric(df_cible[col], errors="coerce")

        #optionnel : réduire la taille mémoire
        df_cible = df_cible.astype("float32")

        #ajout d'une colonne pour savoir sur qu'elle vol nous sommes
        df_cible["record"] = record_name

        liste_vols.append(df_cible)
    
    #fusionner tous les DataFrames pour en avoir qu'un seul
    dataset = pd.concat(liste_vols, ignore_index=True)

    print("Dataset créé :", dataset.shape)
    print("Records ignorés :", vol_ignore)
    print(dataset.dtypes)

    #création du fichier
    if nom_parquet is not None:
        dataset.to_parquet(nom_parquet, index=False)
        # si tu veux compression :
        # dataset.to_parquet(nom_parquet, index=False, compression="snappy")
    
    Aircraft.close()
    





#Création des trois csv
construire_dataset_aircraft("archive/Aircraft_01.h5", set_variable_a_garder, "dataset_aircraft1.parquet")
construire_dataset_aircraft("archive/Aircraft_02.h5", set_variable_a_garder, "dataset_aircraft2.parquet")
construire_dataset_aircraft("archive/Aircraft_03.h5", set_variable_a_garder, "dataset_aircraft3.parquet")