#Création des dataframe avec les variables qui nous intéresse la dernière
#variable représente le vol ("records_XX")

#NOTE  : le vol numéro 702 de aircraft1 a été ignorés car il manque les catégories :
# "block0_items", "block0_values"

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

def construire_dataset_aircraft(h5_path, set_variable_a_garder, csv_output=None):

    Aircraft = h5py.File(h5_path, "r")

    liste_vols = []
    records_ignores = []

    for record_name in Aircraft.keys():

        record = Aircraft[record_name]

        if not all(k in record.keys() for k in ["axis0", "axis1", "block0_values"]):
            records_ignores.append(record_name)
            continue

        axis0 = record["axis0"][:]
        axis1 = record["axis1"][:]
        values = record["block0_values"][:]

        colonnes = [x.decode("utf-8") if isinstance(x, bytes) else str(x) for x in axis0]

        df_vol = pd.DataFrame(values, columns=colonnes, index=axis1)

        colonnes_presentes = [col for col in set_variable_a_garder if col in df_vol.columns]

        df_vol_reduit = df_vol[colonnes_presentes].copy()
        df_vol_reduit["record"] = record_name

        liste_vols.append(df_vol_reduit)

    dataset = pd.concat(liste_vols, ignore_index=True)

    print("Dataset créé :", dataset.shape)
    print("Records ignorés :", records_ignores)

    if csv_output is not None:
        dataset.to_csv(csv_output, index=False)



construire_dataset_aircraft("archive/Aircraft_01.h5",set_variable_a_garder,
"dataset_aircraft1.csv")
construire_dataset_aircraft("archive/Aircraft_02.h5",set_variable_a_garder,
"dataset_aircraft2.csv")
construire_dataset_aircraft("archive/Aircraft_03.h5",set_variable_a_garder,
"dataset_aircraft3.csv")
