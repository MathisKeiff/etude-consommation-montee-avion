import pandas as pd

# Lire les fichiers Parquet générés
df_avec = pd.read_parquet("variables_montee_avec_palier.parquet")
df_sans = pd.read_parquet("variables_montee_sans_palier.parquet")

# Afficher quelques lignes pour vérification
print("===== Vols avec palier =====")
print(df_avec.head(), "\n")

print("===== Vols sans palier =====")
print(df_sans.head())