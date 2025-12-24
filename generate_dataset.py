import pandas as pd
import numpy as np

n_etudiants = 1200
departements = ["Informatique", "Maths", "Physique", "Chimie", "Biologie", "Génie Civil"]
ues = ["UE1", "UE2", "UE3", "UE4"]
matieres = {
    "UE1": ["Python", "Algèbre", "Mécanique"],
    "UE2": ["Statistiques", "Analyse", "Thermodynamique"],
    "UE3": ["Bases de données", "Probabilités", "Électronique"],
    "UE4": ["Machine Learning", "Topologie", "Chimie Organique"]
}
enseignants = ["Prof A", "Prof B", "Prof C", "Prof D", "Prof E"]

data = []
np.random.seed(42)

for etu_id in range(1, n_etudiants + 1):
    departement = np.random.choice(departements)
    for ue in ues:
        for matiere in matieres[ue]:
            enseignant = np.random.choice(enseignants)
            note = np.clip(np.random.normal(loc=12, scale=3), 0, 20)
            data.append([etu_id, departement, ue, matiere, enseignant, round(note, 2)])

df = pd.DataFrame(data, columns=["id_etudiant", "departement", "UE", "matiere", "enseignant", "note"])
df.to_csv("notes.csv", index=False)
print("✅ Dataset simulé généré : notes.csv")