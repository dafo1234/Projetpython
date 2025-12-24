import pandas as pd
import numpy as np

def calcul_statistiques(df):
    stats = df.groupby(["departement", "UE", "matiere"]).agg(
        moyenne=("note", "mean"),
        mediane=("note", "median"),
        ecart_type=("note", "std"),
        taux_reussite=("note", lambda x: (x >= 10).mean() * 100)
    ).reset_index()
    return stats