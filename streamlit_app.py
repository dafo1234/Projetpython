import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(page_title="Analyse EPL", layout="wide")
st.title("Tableau de bord EPL")

# --- Upload du fichier ---
uploaded_file = st.sidebar.file_uploader("📂 Charger un fichier CSV ou Excel", type=["csv", "xlsx"])

if uploaded_file is not None:
    # Lecture du fichier
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.success(f"✅ Fichier chargé : {uploaded_file.name}")

    # --- Filtres interactifs ---
    st.sidebar.header("Filtres")
    departement = st.sidebar.multiselect("Département", df["departement"].unique())
    ue = st.sidebar.multiselect("UE", df["UE"].unique())
    matiere = st.sidebar.multiselect("Matière", df["matiere"].unique())
    enseignant = st.sidebar.multiselect("Enseignant", df["enseignant"].unique())

    # Appliquer les filtres
    df_filtre = df.copy()
    if departement:
        df_filtre = df_filtre[df_filtre["departement"].isin(departement)]
    if ue:
        df_filtre = df_filtre[df_filtre["UE"].isin(ue)]
    if matiere:
        df_filtre = df_filtre[df_filtre["matiere"].isin(matiere)]
    if enseignant:
        df_filtre = df_filtre[df_filtre["enseignant"].isin(enseignant)]

    # --- Création des onglets ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👩‍🎓 Étudiants", "📘 Notes", "👨‍🏫 Enseignants", "🏛️ Départements", "📄 Bulletins"
    ])

    # --- Onglet Étudiants ---
    with tab1:
        st.header("Statistiques sur les étudiants")
        st.metric("Nombre d'étudiants", df_filtre["id_etudiant"].nunique())

        taux_reussite = (df_filtre["note"] >= 10).mean() * 100
        st.metric("Taux de réussite", f"{taux_reussite:.2f}%")

        moy_etudiant = df_filtre.groupby("id_etudiant")["note"].mean().reset_index()
        moy_etudiant.columns = ["id_etudiant", "moyenne"]
        st.subheader("Moyenne par étudiant")
        st.dataframe(moy_etudiant.head(20))

        st.metric("Écart-type global", round(df_filtre["note"].std(), 2))

        st.subheader("Distribution des notes")
        fig, ax = plt.subplots()
        sns.histplot(df_filtre["note"], bins=20, kde=True, ax=ax)
        st.pyplot(fig)

        if "sexe" in df_filtre.columns:
            st.subheader("Moyenne des notes par sexe")
            moy_sexe = df_filtre.groupby("sexe")["note"].mean().reset_index()
            st.dataframe(moy_sexe)

        if "age" in df_filtre.columns:
            st.subheader("Tableau des stats par âge")
            stats_age = df_filtre.groupby("age")["note"].agg(["mean", "median", "std", "count"]).reset_index()
            st.dataframe(stats_age)

        if "bulletin" in df_filtre.columns:
            st.subheader("Bulletins des étudiants")
            bulletins = df_filtre.groupby(["id_etudiant", "bulletin"])["note"].mean().reset_index()
            bulletins.columns = ["id_etudiant", "bulletin", "moyenne"]
            st.dataframe(bulletins)

            st.download_button(
                label="📥 Télécharger les bulletins (CSV)",
                data=bulletins.to_csv(index=False).encode("utf-8"),
                file_name="bulletins_etudiants.csv",
                mime="text/csv"
            )

    # --- Onglet Notes ---
    with tab2:
        st.header("Statistiques sur les notes")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Moyenne générale", round(df_filtre["note"].mean(), 2))
        col2.metric("Médiane", round(df_filtre["note"].median(), 2))
        col3.metric("Écart-type", round(df_filtre["note"].std(), 2))
        col4.metric("Taux de réussite", f"{(df_filtre['note'] >= 10).mean() * 100:.2f}%")

        st.subheader("Distribution des notes")
        fig, ax = plt.subplots()
        sns.histplot(df_filtre["note"], bins=20, kde=True, ax=ax)
        st.pyplot(fig)

        st.subheader("Classement des étudiants")
        classement = df_filtre.groupby("id_etudiant")["note"].mean().sort_values(ascending=False).reset_index()
        classement.columns = ["id_etudiant", "moyenne"]
        st.dataframe(classement.head(20))

    # --- Onglet Enseignants ---
    with tab3:
        st.header("Statistiques sur les enseignants")
        moy_ens = df_filtre.groupby("enseignant")["note"].mean().sort_values(ascending=False).reset_index()
        st.dataframe(moy_ens)

        st.subheader("Boxplot des notes par enseignant")
        fig, ax = plt.subplots()
        sns.boxplot(x="enseignant", y="note", data=df_filtre, ax=ax)
        st.pyplot(fig)

    # --- Onglet Départements ---
    with tab4:
        st.header("Statistiques par département")
        stats_dept = df_filtre.groupby("departement")["note"].agg(["mean", "median", "std", "count"]).reset_index()
        st.dataframe(stats_dept)

        st.subheader("Boxplot des notes par département")
        fig, ax = plt.subplots()
        sns.boxplot(x="departement", y="note", data=df_filtre, ax=ax)
        st.pyplot(fig)

        st.subheader("Histogramme des étudiants par département")
        fig, ax = plt.subplots()
        sns.countplot(x="departement", data=df_filtre, ax=ax)
        st.pyplot(fig)

    # --- Export Excel multi-feuilles ---
    st.sidebar.header("Export complet")
    if st.sidebar.button("Exporter rapport Excel multi-feuilles"):
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            if "age" in df_filtre.columns:
                stats_age.to_excel(writer, sheet_name="Etudiants", index=False)
            classement.to_excel(writer, sheet_name="Notes", index=False)
            moy_ens.to_excel(writer, sheet_name="Enseignants", index=False)
            stats_dept.to_excel(writer, sheet_name="Departements", index=False)
            if "bulletin" in df_filtre.columns:
                bulletins.to_excel(writer, sheet_name="Bulletins", index=False)

        st.download_button(
            label="Télécharger rapport Excel",
            data=output.getvalue(),
            file_name="rapport_EPL.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

else:
    st.warning("Veuillez charger un fichier CSV ou Excel pour commencer.")