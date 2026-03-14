import pandas as pd
import matplotlib.pyplot as plt


df1 = pd.read_parquet("vols_avec_palier1.parquet")
df2 = pd.read_parquet("vols_sans_palier1.parquet")
print(df1.size)
print(df2.size)

import pandas as pd
import matplotlib.pyplot as plt


import pandas as pd
import matplotlib.pyplot as plt


def afficher_tous_les_vols(fichier_parquet):

    df = pd.read_parquet(fichier_parquet)

    vols = df["record"].unique()

    plt.figure(figsize=(10,6))

    for record in vols:

        df_vol = df[df["record"] == record].copy()
        df_vol = df_vol.reset_index(drop=True)

        t = range(len(df_vol))

        plt.plot(t, df_vol["ALT [ft]"], alpha=0.2)

    plt.xlabel("Temps (index)")
    plt.ylabel("Altitude (ft)")
    titre = fichier_parquet.replace(".parquet", "").replace("_", " ")
    plt.title(f"Profils d'altitude de tous les {titre}")
    plt.grid()

    plt.show()



afficher_tous_les_vols("vols_avec_palier1.parquet")
afficher_tous_les_vols("vols_sans_palier1.parquet")
