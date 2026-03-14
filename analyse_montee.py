import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

def analyse_montee(df):
    variables = [
        "carburant_cumule",
        "duree",
        "ALT_init",
        "ALT_fin",
        "taux_montee",
        "Mach_moyen",
        "N1_moyen",
        "N2_moyen",
        "TLA_moyen",
        "EGT_moyen"
    ]

    print("===== STATISTIQUES DESCRIPTIVES =====")
    print(df[variables].describe())

    # -------------------------------
    # Histogrammes
    # -------------------------------
    print("\n===== HISTOGRAMMES =====")
    n = len(variables)
    ncols = 2
    nrows = (n + 1) // ncols
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(14, nrows*4))
    axes = axes.flatten()

    for i, var in enumerate(variables):
        sns.histplot(df[var], kde=True, ax=axes[i], color="skyblue", edgecolor="black")
        axes[i].set_title(f"{var}", fontsize=12, fontweight='bold')
        axes[i].set_xlabel(var, fontsize=10)
        axes[i].set_ylabel("Fréquence", fontsize=10)
        axes[i].grid(True, linestyle='--', alpha=0.5)

    for j in range(i+1, len(axes)):
        fig.delaxes(axes[j])

    plt.tight_layout()
    plt.show()

    # -------------------------------
    # Boxplots
    # -------------------------------
    print("\n===== BOXPLOTS =====")
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(14, nrows*4))
    axes = axes.flatten()

    for i, var in enumerate(variables):
        sns.boxplot(x=df[var], ax=axes[i], color="lightgreen")
        axes[i].set_title(f"{var}", fontsize=12, fontweight='bold')
        axes[i].set_xlabel(var, fontsize=10)
        axes[i].grid(True, linestyle='--', alpha=0.5)

    for j in range(i+1, len(axes)):
        fig.delaxes(axes[j])

    plt.tight_layout()
    plt.show()

    # -------------------------------
    # Matrice de corrélation
    # -------------------------------
    print("\n===== MATRICE DE CORRELATION =====")
    corr = df[variables].corr()
    plt.figure(figsize=(10,8))
    sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f")
    plt.title("Matrice de corrélation")
    plt.show()

    # -------------------------------
    # PCA
    # -------------------------------
    print("\n===== PCA et Cercle de corrélation =====")
    features = [
        "duree",
        "Mach_moyen",
        "N1_moyen",
        "N2_moyen",
        "TLA_moyen",
        "taux_montee",
        "carburant_cumule"
    ]
    X = df[features].dropna()
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    pca = PCA(n_components=2)
    components = pca.fit_transform(X_scaled)

    # Cercle de corrélation
    correlations = pca.components_.T * np.sqrt(pca.explained_variance_)
    plt.figure(figsize=(7,7))
    plt.axhline(0, color='grey', lw=1)
    plt.axvline(0, color='grey', lw=1)

    for i, var in enumerate(features):
        plt.arrow(0, 0, correlations[i,0], correlations[i,1],
                  color='r', alpha=0.7, head_width=0.05)
        plt.text(correlations[i,0]*1.15, correlations[i,1]*1.15, var, color='b', fontsize=10)

    circle = plt.Circle((0,0), 1, color='grey', fill=False)
    plt.gca().add_artist(circle)
    plt.xlim(-1,1)
    plt.ylim(-1,1)
    plt.xlabel('PC1')
    plt.ylabel('PC2')
    plt.title("Cercle de corrélation des variables")
    plt.grid(True)
    plt.show()

    # -------------------------------
    # Clustering KMeans
    # -------------------------------
    print("\n===== CLUSTERING KMEANS =====")
    kmeans = KMeans(n_clusters=3, random_state=0)
    clusters = kmeans.fit_predict(X_scaled)
    df_cluster = df.loc[X.index].copy()
    df_cluster["cluster"] = clusters

    # PCA colorée par cluster
    plt.figure(figsize=(8,6))
    sns.scatterplot(x=components[:,0], y=components[:,1], hue=clusters, palette="Set1")
    plt.title("Clusters des profils de montée (PCA)")
    plt.xlabel("PC1")
    plt.ylabel("PC2")
    plt.show()

    # Boxplot consommation par cluster
    plt.figure(figsize=(8,6))
    sns.boxplot(x="cluster", y="carburant_cumule", data=df_cluster, palette="Set2")
    plt.title("Consommation de carburant par cluster")
    plt.show()

    # Profil moyen par cluster
    print("\n===== Profils moyens par cluster =====")
    print(df_cluster.groupby("cluster")[features + ["carburant_cumule"]].mean())