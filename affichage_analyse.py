import pandas as pd
from analyse_montee import analyse_montee
from calcul_variable_montee import calcul_variables_montee
# lecture du fichier brut
df_vols1 = pd.read_parquet("vols_avec_palier1.parquet")

# créer la colonne record_clean
col_record = [c for c in df_vols1.columns if 'record' in c.lower()]
if len(col_record) != 1:
    raise ValueError(f"Impossible de trouver la colonne record unique, trouvé : {col_record}")

df_vols1['record_clean'] = df_vols1[col_record[0]].astype(str).str.strip()

# maintenant on peut grouper par record_clean
df_agg1 = pd.DataFrame([calcul_variables_montee(df_vol)
                        for _, df_vol in df_vols1.groupby('record_clean', sort=False)])
# analyse
analyse_montee(df_agg1)