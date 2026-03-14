import pandas as pd

# -----------------------------
# 1️⃣ Liste des fichiers
# -----------------------------
fichiers_avec_palier = [
    "vols_avec_palier1.parquet",
    "vols_avec_palier2.parquet",
    "vols_avec_palier3.parquet"
]

fichiers_sans_palier = [
    "vols_sans_palier1.parquet",
    "vols_sans_palier2.parquet",
    "vols_sans_palier3.parquet"
]

# -----------------------------
# 2️⃣ Fonction pour lire et préparer les fichiers
# -----------------------------
def lire_et_preparer(fichiers):
    dfs = []
    for f in fichiers:
        df = pd.read_parquet(f)
        print(df["record"].nunique())
        df.columns = [c.strip() for c in df.columns]
        col_record = [c for c in df.columns if 'record' in c.lower()]
        if len(col_record) != 1:
            raise ValueError(f"Impossible de trouver une colonne record unique dans {f}, trouvé: {col_record}")
        df['record_clean'] = df[col_record[0]].astype(str).str.strip()
        dfs.append(df)
    df_concat = pd.concat(dfs, ignore_index=True)
    if 'record_clean' not in df_concat.columns:
        raise ValueError("Erreur : 'record_clean' n'existe pas après concaténation.")
    return df_concat

# -----------------------------
# 3️⃣ Lecture fichiers
# -----------------------------
df_avec = lire_et_preparer(fichiers_avec_palier)
df_sans = lire_et_preparer(fichiers_sans_palier)

# -----------------------------
# 4️⃣ Fonction calcul variables montée
# -----------------------------
def calcul_variables_montee(df_vol):
    carburant_cumule = (df_vol['Q_1 [lb/h]'] + df_vol['Q_2 [lb/h]']).sum()
    duree = len(df_vol)
    ALT_init = df_vol['ALT [ft]'].iloc[0]
    ALT_fin = df_vol['ALT [ft]'].iloc[-1]
    taux_montee = (ALT_fin - ALT_init) / duree
    Mach_moyen = df_vol['M [Mach]'].mean() if 'M [Mach]' in df_vol.columns else None
    N1_moyen = (df_vol['N1_1 [% rpm]'] + df_vol['N1_2 [% rpm]']).mean() / 2
    N2_moyen = (df_vol['N2_1 [% rpm]'] + df_vol['N2_2 [% rpm]']).mean() / 2
    TLA_moyen = (df_vol['TLA_1 [deg]'] + df_vol['TLA_2 [deg]']).mean() / 2
    EGT_moyen = (df_vol['EGT_1 [deg C]'] + df_vol['EGT_2 [deg C]']).mean() / 2

    return pd.Series({
        'record': df_vol['record_clean'].iloc[0],
        'carburant_cumule': carburant_cumule,
        'duree': duree,
        'ALT_init': ALT_init,
        'ALT_fin': ALT_fin,
        'taux_montee': taux_montee,
        'Mach_moyen': Mach_moyen,
        'N1_moyen': N1_moyen,
        'N2_moyen': N2_moyen,
        'TLA_moyen': TLA_moyen,
        'EGT_moyen': EGT_moyen
    })

# -----------------------------
# 5️⃣ Calcul des variables par vol
# -----------------------------
df_avec_agg = pd.DataFrame([calcul_variables_montee(df_vol) 
                            for _, df_vol in df_avec.groupby('record_clean', sort=False)])
df_sans_agg = pd.DataFrame([calcul_variables_montee(df_vol) 
                            for _, df_vol in df_sans.groupby('record_clean', sort=False)])

# -----------------------------
# 6️⃣ Sauvegarde en Parquet
# -----------------------------
df_avec_agg.to_parquet("variables_montee_avec_palier.parquet", index=False)
df_sans_agg.to_parquet("variables_montee_sans_palier.parquet", index=False)

print("✅ Extraction terminée !")
print(f"Vols avec palier : {df_avec_agg.shape[0]}")
print(f"Vols sans palier : {df_sans_agg.shape[0]}")