import streamlit as st
import plotly.express as px
import pandas as pd

from utils.chatbot import get_chatbot_response

from typing import Dict, Any


# Configuration de la page
st.set_page_config(
    page_title="Dashboard Churn - Télécoms",
    page_icon="📱",
    layout="wide"
)
from utils.data_loader import load_data
from utils.ui_style import set_background, custom_sidebar_style
from utils.auth import check_authentication



# Chargement des données
data = load_data()

# Appliquer les styles UI
set_background()
custom_sidebar_style()

check_authentication()
# =============================================
# SIDEBAR - FILTRES INTERACTIFS (VERSION FINALE)
# =============================================
with st.sidebar:
    st.header("🔎 Filtres Stratégiques")

    # 1. Filtre Type de Contrat - Version professionnelle
    contract_options = data['Contract'].unique().tolist()
    selected_contract = st.selectbox(
        "Type de contrat",
        options=["Tous"] + contract_options,
        index=0,  # "Tous" sélectionné par défaut
        key="contract_selector"
    )

    # 2. Filtre Genre
    gender_options = ["Tous"] + data['gender'].unique().tolist()
    gender_filter = st.radio(
        "Genre",
        options=gender_options,
        index=0,
        horizontal=True,
        key="gender_selector"
    )

    # 2. Nouveau filtre : Méthode de paiement (en dessous des sliders)
    payment_methods = ["Toutes"] + sorted(data['PaymentMethod'].unique().tolist())
    selected_payment = st.selectbox(
        "Méthode de paiement",
        options=payment_methods,
        index=0,
        help="Filtrer par type de paiement utilisé"
    )

    # 3. Filtres avancés
    with st.expander("Filtres Avancés"):
        internet_options = ["Tous"] + data['InternetService'].unique().tolist()
        internet_service = st.selectbox(
            "Service Internet",
            options=internet_options,
            index=0,
            key="internet_selector"
        )

        tenure_range = st.slider(
            "Ancienneté (mois)",
            min_value=int(data['tenure'].min()),
            max_value=int(data['tenure'].max()),
            value=(0, 72),
            key="tenure_selector"
        )

        monthly_charges = st.slider(
            "Charges mensuelles ($)",
            min_value=float(data['MonthlyCharges'].min()),
            max_value=float(data['MonthlyCharges'].max()),
            value=(float(data['MonthlyCharges'].min()), float(data['MonthlyCharges'].max())),
            key="charges_selector"
        )



# APPLICATION DES FILTRES (VERSION FINALE)

df_filtered = data.copy()

# Filtre Contrat
if selected_contract != "Tous":
    df_filtered = df_filtered[df_filtered['Contract'] == selected_contract]

# Filtres obligatoires
df_filtered = df_filtered[
    df_filtered['tenure'].between(*tenure_range) &
    df_filtered['MonthlyCharges'].between(*monthly_charges)
]

# Filtres optionnels
if gender_filter != "Tous":
    df_filtered = df_filtered[df_filtered['gender'] == gender_filter]

if internet_service != "Tous":
    df_filtered = df_filtered[df_filtered['InternetService'] == internet_service]


# Ajouter cette condition à votre bloc de filtrage existant
if selected_payment != "Toutes":
    df_filtered = df_filtered[df_filtered['PaymentMethod'] == selected_payment]


# SECTION KPI - HEADER (VERSION SÉCURISÉE)

st.title("📊 Tableau de Bord - Analyse du Churn")
st.markdown("**Outil décisionnel pour la rétention client**")
st.divider()


def safe_divide(a, b):
    return a / b if b != 0 else 0


# Ligne 1 - KPIs Principaux
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

total_clients = len(df_filtered)
kpi1.metric(
    "👥 Clients Actifs",
    f"{total_clients:,}",
    delta=f"{safe_divide((total_clients - len(data)), len(data)) * 100:.1f}%"
)

churn_count = len(df_filtered[df_filtered['Churn'] == 'Yes'])
kpi2.metric(
    "⚠️ Taux de Churn",
    f"{safe_divide(churn_count, total_clients) * 100:.1f}%",
    delta=f"{(safe_divide(churn_count, total_clients) - safe_divide(len(data[data['Churn'] == 'Yes']), len(data))) * 100:.1f}pts",
    delta_color="inverse"
)

monthly_revenue = df_filtered['MonthlyCharges'].sum()
kpi3.metric(
    "💸 Revenu Mensuel",
    f"${monthly_revenue:,.0f}"
)

avg_tenure = df_filtered['tenure'].mean()
kpi4.metric(
    "⏳ Ancienneté Moyenne",
    f"{avg_tenure:.1f} mois" if not pd.isna(avg_tenure) else "0 mois"
)

# Ligne 2 - KPIs Secondaires
kpi5, kpi6, kpi7 = st.columns(3)

no_internet = safe_divide(len(df_filtered[df_filtered['InternetService'] == 'No']), total_clients) * 100
kpi5.metric("📶 Sans Internet", f"{no_internet:.1f}%")

paperless = safe_divide(len(df_filtered[df_filtered['PaperlessBilling'] == 'Yes']), total_clients) * 100
kpi6.metric("🌱 Facture Démat", f"{paperless:.1f}%")

seniors = safe_divide(len(df_filtered[df_filtered['SeniorCitizen'] == 1]), total_clients) * 100
kpi7.metric("👵 Clients Seniors", f"{seniors:.1f}%")

st.divider()


# BOUTON DE TÉLÉCHARGEMENT DES KPIs


# Créer un DataFrame contenant uniquement les KPIs
kpi_data = {
    'KPI': [
        'Clients Actifs',
        'Taux de Churn (%)',
        'Revenu Mensuel ($)',
        'Ancienneté Moyenne (mois)',
        'Sans Internet (%)',
        'Facture Démat (%)',
        'Clients Seniors (%)'
    ],
    'Valeur': [
        total_clients,
        round(safe_divide(churn_count, total_clients) * 100, 2),
        round(monthly_revenue, 2),
        round(avg_tenure, 2) if not pd.isna(avg_tenure) else 0,
        round(no_internet, 2),
        round(paperless, 2),
        round(seniors, 2)
    ]
}
df_kpis = pd.DataFrame(kpi_data)

# Bouton qui prépare et affiche le bouton de téléchargement
if st.button("✅ Préparer le fichier CSV des KPIs"):
    # Afficher l'aperçu du DataFrame des KPIs
    st.markdown("### Aperçu des KPIs")
    st.dataframe(df_kpis, use_container_width=True)

    st.success("✅ Le fichier des KPIs est prêt à être téléchargé ci-dessous ⬇️")
    csv = df_kpis.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Télécharger les KPIs filtrés (CSV)",
        data=csv,
        file_name="kpis_churn_filtres.csv",
        mime="text/csv",
        key="download_button_kpi"
    )

st.divider()



# NOUVEAU : CHATBOT POUR ANALYSE DES KPIS



with st.expander("🤖 Assistant d'Analyse des KPIs", expanded=True):
    st.markdown("""
    **Posez-moi une question sur les KPIs du tableau de bord :**
    """)
    user_question = st.text_input("Votre question ici :", key="chatbot_input")

    if user_question:
        response = get_chatbot_response(df_filtered, user_question)
        st.info(response)


# VISUALISATIONS

if len(df_filtered) > 0:
    tab1, tab2 = st.tabs(["Analyse Clients", "Services"])

    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            fig = px.histogram(
                df_filtered,
                x='tenure',
                color='Churn',
                title="Distribution par Ancienneté",
                nbins=20,
                color_discrete_map={'Yes': '#FFA07A', 'No': '#20B2AA'}
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.box(
                df_filtered,
                x='Churn',
                y='MonthlyCharges',
                color='Contract',
                title="Charges Mensuelles vs Churn",
                color_discrete_map={
                    'Month-to-month': '#FF7F50',
                    'One year': '#4682B4',
                    'Two year': '#9ACD32'
                }
            )
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        fig = px.sunburst(
            df_filtered,
            path=['Contract', 'InternetService'],
            values='MonthlyCharges',
            color='Churn',
            title="Répartition des Services",
            color_discrete_map={'Yes': '#FF6347', 'No': '#5F9EA0'}
        )
        st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Aucune donnée ne correspond aux filtres sélectionnés. Veuillez élargir vos critères.")


# FOOTER

st.divider()
st.caption("""
    *Dashboard actualisé en temps réel - © 2025 Télécom Analytics*
""")
