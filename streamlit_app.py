import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
from io import BytesIO


st.set_page_config(page_title="Analyse EPL", layout="wide")
st.title("TABLEAU DE BORD STATISTIQUE EPL")

# --- Upload du fichier ---
uploaded_file = st.sidebar.file_uploader(" Charger un fichier CSV ou Excel", type=["csv", "xlsx"])

if uploaded_file is not None:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.success(f"✅ Fichier chargé : {uploaded_file.name}")

    # --- Filtres ---
    st.sidebar.header("Filtres")
    departement = st.sidebar.multiselect("Département", df["departement"].unique())
    ue = st.sidebar.multiselect("UE", df["UE"].unique())
    matiere = st.sidebar.multiselect("Matière", df["matiere"].unique())
    enseignant = st.sidebar.multiselect("Enseignant", df["enseignant"].unique())

    df_filtre = df.copy()
    if departement: df_filtre = df_filtre[df_filtre["departement"].isin(departement)]
    if ue: df_filtre = df_filtre[df_filtre["UE"].isin(ue)]
    if matiere: df_filtre = df_filtre[df_filtre["matiere"].isin(matiere)]
    if enseignant: df_filtre = df_filtre[df_filtre["enseignant"].isin(enseignant)]

    # --- Onglets ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        " Étudiants", "Notes", " Enseignants", "Départements", "Bulletins"
    ])

    # --- Étudiants ---
    with tab1:
        st.header("Statistiques sur les étudiants")
        st.metric("Nombre d'étudiants", df_filtre["id_etudiant"].nunique())
        taux_reussite = (df_filtre["note"] >= 10).mean() * 100
        st.metric("Taux de réussite", f"{taux_reussite:.2f}%")

        # Histogramme
        st.subheader("Distribution des notes : comparaison")
        col1, col2 = st.columns(2)
        with col1:
            fig, ax = plt.subplots()
            sns.histplot(df_filtre["note"], bins=20, kde=True, ax=ax)
            st.pyplot(fig)
        with col2:
            fig = px.histogram(df_filtre, x="note", nbins=20, marginal="box", title="Distribution des notes")
            st.plotly_chart(fig, use_container_width=True)

        # Scatter âge vs note
        if "age" in df_filtre.columns:
            st.subheader("Relation âge vs note : comparaison")
            col1, col2 = st.columns(2)
            with col1:
                fig, ax = plt.subplots()
                sns.scatterplot(x="age", y="note", data=df_filtre, ax=ax)
                st.pyplot(fig)
            with col2:
                fig = px.scatter(df_filtre, x="age", y="note", color="sexe" if "sexe" in df_filtre.columns else None,
                                 title="Notes en fonction de l'âge")
                st.plotly_chart(fig, use_container_width=True)

        # Moyenne par sexe + camembert
        if "sexe" in df_filtre.columns:
            st.subheader("Moyenne des notes par sexe : comparaison")
            col1, col2 = st.columns(2)
            with col1:
                fig, ax = plt.subplots()
                sns.barplot(x="sexe", y="note", data=df_filtre, ax=ax)
                st.pyplot(fig)
            with col2:
                moy_sexe = df_filtre.groupby("sexe")["note"].mean().reset_index()
                fig = px.bar(moy_sexe, x="sexe", y="note", color="sexe", title="Moyenne par sexe")
                st.plotly_chart(fig, use_container_width=True)

            st.subheader("Répartition des étudiants par sexe : comparaison")
            col1, col2 = st.columns(2)
            with col1:
                counts = df_filtre["sexe"].value_counts()
                fig, ax = plt.subplots()
                ax.pie(counts, labels=counts.index, autopct="%1.1f%%", startangle=90)
                ax.axis("equal")
                st.pyplot(fig)
            with col2:
                fig = px.pie(df_filtre, names="sexe", title="Répartition par sexe", hole=0.3)
                st.plotly_chart(fig, use_container_width=True)

        # Heatmap corrélations
        st.subheader("Corrélations entre variables : comparaison")
        corr = df_filtre.corr(numeric_only=True)
        col1, col2 = st.columns(2)
        with col1:
            fig, ax = plt.subplots()
            sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
            st.pyplot(fig)
        with col2:
            fig = px.imshow(corr, text_auto=True, color_continuous_scale="RdBu_r", title="Matrice de corrélation")
            st.plotly_chart(fig, use_container_width=True)

    # --- Notes ---
    with tab2:
        st.header("Statistiques sur les notes")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Moyenne générale", round(df_filtre["note"].mean(), 2))
        col2.metric("Médiane", round(df_filtre["note"].median(), 2))
        col3.metric("Écart-type", round(df_filtre["note"].std(), 2))
        col4.metric("Taux de réussite", f"{(df_filtre['note'] >= 10).mean() * 100:.2f}%")

        st.subheader("Distribution des notes : comparaison")
        col1, col2 = st.columns(2)
        with col1:
            fig, ax = plt.subplots()
            sns.histplot(df_filtre["note"], bins=20, kde=True, ax=ax)
            st.pyplot(fig)
        with col2:
            fig = px.histogram(df_filtre, x="note", nbins=20, title="Distribution des notes")
            st.plotly_chart(fig, use_container_width=True)

    # --- Enseignants ---
    with tab3:
        st.header("Statistiques sur les enseignants")
        moy_ens = df_filtre.groupby("enseignant")["note"].mean().reset_index()
        st.dataframe(moy_ens)

        st.subheader("Moyenne des notes par enseignant : comparaison")
        col1, col2 = st.columns(2)
        with col1:
            fig, ax = plt.subplots()
            sns.barplot(x="enseignant", y="note", data=df_filtre, ax=ax)
            st.pyplot(fig)
        with col2:
            fig = px.bar(moy_ens, x="enseignant", y="note", color="enseignant", title="Moyenne par enseignant")
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Boxplot des notes par enseignant : comparaison")
        col1, col2 = st.columns(2)
        with col1:
            fig, ax = plt.subplots()
            sns.boxplot(x="enseignant", y="note", data=df_filtre, ax=ax)
            st.pyplot(fig)
        with col2:
            fig = px.box(df_filtre, x="enseignant", y="note", points="all", title="Boxplot des notes par enseignant")
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Répartition des moyennes par enseignant : comparaison")
        col1, col2 = st.columns(2)
        with col1:
            fig, ax = plt.subplots()
            ax.pie(moy_ens["note"], labels=moy_ens["enseignant"], autopct="%1.1f%%", startangle=90)
            ax.axis("equal")
            st.pyplot(fig)
        with col2:
            fig = px.pie(moy_ens, names="enseignant", values="note", title="Répartition des moyennes par enseignant", hole=0.3)
            st.plotly_chart(fig, use_container_width=True)

        # --- Onglet Départements ---
    with tab4:
        st.header("Statistiques par département")
        stats_dept = df_filtre.groupby("departement")["note"].agg(["mean", "median", "std", "count"]).reset_index()
        st.dataframe(stats_dept)

        st.subheader("Moyenne des notes par département : comparaison")
        col1, col2 = st.columns(2)
        with col1:
            fig, ax = plt.subplots()
            sns.barplot(x="departement", y="note", data=df_filtre, ax=ax)
            st.pyplot(fig)
        with col2:
            fig = px.bar(stats_dept, x="departement", y="mean", color="departement", title="Moyenne par département")
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Boxplot des notes par département : comparaison")
        col1, col2 = st.columns(2)
        with col1:
            fig, ax = plt.subplots()
            sns.boxplot(x="departement", y="note", data=df_filtre, ax=ax)
            st.pyplot(fig)
        with col2:
            fig = px.box(df_filtre, x="departement", y="note", points="all", title="Boxplot des notes par département")
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Répartition des étudiants par département (Diagramme circulaire)")
        col1, col2 = st.columns(2)
        with col1:
            counts = df_filtre["departement"].value_counts()
            fig, ax = plt.subplots()
            ax.pie(counts, labels=counts.index, autopct="%1.1f%%", startangle=90)
            ax.axis("equal")
            st.pyplot(fig)
        with col2:
            fig = px.pie(df_filtre, names="departement", title="Répartition par département", hole=0.3)
            st.plotly_chart(fig, use_container_width=True)

    # --- Onglet Bulletins ---
    with tab5:
        st.header("Bulletins des étudiants")
        if "bulletin" in df_filtre.columns:
            bulletins = df_filtre.groupby(["id_etudiant", "bulletin"])["note"].mean().reset_index()
            bulletins.columns = ["id_etudiant", "bulletin", "moyenne"]
            st.dataframe(bulletins)

            st.download_button(
                label="Télécharger les bulletins (CSV)",
                data=bulletins.to_csv(index=False).encode("utf-8"),
                file_name="bulletins.csv",
                mime="text/csv"
            )
        else:
            st.warning("⚠️ La colonne 'bulletin' n'existe pas dans le dataset.")

    # --- Export Excel multi-feuilles ---
    st.sidebar.header("Export complet")
    if st.sidebar.button("Exporter rapport Excel multi-feuilles"):
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            # Statistiques étudiants (si colonne 'age' existe)
            if "age" in df_filtre.columns:
                stats_age = df_filtre.groupby("age")["note"].agg(["mean", "median", "std", "count"]).reset_index()
                stats_age.to_excel(writer, sheet_name="Etudiants", index=False)

            # Classement des notes
            classement = df_filtre.sort_values(by="note", ascending=False)
            classement.to_excel(writer, sheet_name="Notes", index=False)

            # Moyennes enseignants
            moy_ens = df_filtre.groupby("enseignant")["note"].mean().reset_index()
            moy_ens.to_excel(writer, sheet_name="Enseignants", index=False)

            # Statistiques départements
            stats_dept.to_excel(writer, sheet_name="Departements", index=False)

            # Bulletins si dispo
            if "bulletin" in df_filtre.columns:
                bulletins.to_excel(writer, sheet_name="Bulletins", index=False)

        st.download_button(
            label="Télécharger rapport Excel",
            data=output.getvalue(),
            file_name="rapport_EPL.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

else:
    st.warning(" Veuillez charger un fichier CSV ou Excel pour commencer, s'il vous plait.")