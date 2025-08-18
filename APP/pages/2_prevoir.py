import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import time
from pathlib import Path
import joblib
import os
import plotly.express as px

st.set_page_config(
    page_title="Prédiction de Churn - Télécoms",
    page_icon="🔮",
    layout="wide"
)

# Les fonctions suivantes ne sont pas incluses dans cet exemple,
# mais leur usage est conservé dans le code.
from utils.ui_style import set_background, custom_sidebar_style, apply_prediction_button_style
from utils.auth import check_authentication


# =============================================
# INITIALISATION ET CONFIGURATION
# =============================================

# Configuration des chemins
# Chemin racine du projet (remonte au dossier parent de 'app/pages')
# Utilisation de .resolve() pour gérer les liens symboliques et obtenir le chemin absolu
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Chemins des modèles - CORRECTION DU CHEMIN
# Suppression du slash initial '/' pour un chemin relatif correct depuis la racine du projet
MODEL_PATH = PROJECT_ROOT / "model" / "modele_random_forest.pkl"
COLUMNS_PATH = PROJECT_ROOT / "model" / "training_columns.pkl"

# URL de l'API : Lire depuis une variable d'environnement pour la flexibilité de déploiement
API_URL = os.getenv("API_CHURN_URL", "[http://127.0.0.1:8000/predict](http://127.0.0.1:8000/predict)")


# =============================================
# FONCTIONS UTILITAIRES
# =============================================

@st.cache_resource  # Cache le chargement du modèle pour éviter de le recharger à chaque réexécution
def load_churn_model(model_path, columns_path):
    """Charge le modèle de prédiction et les colonnes d'entraînement."""
    try:
        model = joblib.load(model_path)
        training_columns = joblib.load(columns_path)
        return model, training_columns
    except FileNotFoundError:
        st.error(
            f"Erreur: Fichier modèle ou colonnes introuvable. Vérifiez les chemins : {model_path} et {columns_path}")
        st.stop()
    except Exception as e:
        st.error(f"Erreur lors du chargement du modèle : {e}")
        st.stop()


# Chargement initial des modèles
# Le chargement est protégé par un try-except qui arrêtera l'application en cas d'échec
try:
    model, training_columns = load_churn_model(MODEL_PATH, COLUMNS_PATH)
except:
    st.stop()


def try_api_prediction(client_data: dict):
    """
    Tente une prédiction via l'API externe.
    Gère les erreurs de connexion et les erreurs HTTP.
    """
    # Conversion forcée des types pour correspondre au modèle FastAPI
    client_data = client_data.copy()
    client_data["MonthlyCharges"] = float(client_data["MonthlyCharges"])
    client_data["TotalCharges"] = float(client_data["TotalCharges"])
    client_data["SeniorCitizen"] = int(client_data["SeniorCitizen"])

    try:
        # Envoi des données avec timeout court
        response = requests.post(
            API_URL,
            json=client_data,
            headers={"Content-Type": "application/json"},
            timeout=10  # Augmenté légèrement le timeout pour plus de robustesse
        )

        response.raise_for_status()  # Lève une exception pour les codes d'état HTTP 4xx/5xx
        return response.json(), "API"

    except requests.exceptions.ConnectionError:
        st.error(f"""
        ❌ **Impossible de joindre l'API de prédiction.**

        Vérifiez les points suivants :
        - L'API est-elle lancée ? (Ex: `uvicorn API.main:app --reload`)
        - L'URL configurée est-elle correcte ? (`{API_URL}`)
        - Aucun pare-feu ne bloque-t-il le port `8000` (ou le port de l'API) ?
        """)
        return None, None
    except requests.exceptions.Timeout:
        st.error("⌛ L'API a mis trop de temps à répondre. Veuillez réessayer.")
        return None, None
    except requests.exceptions.RequestException as e:
        st.error(f"Une erreur est survenue lors de la requête API : {e}")
        st.exception(e)  # Affiche les détails de l'exception pour le débogage
        return None, None
    except Exception as e:
        st.error(f"Une erreur inattendue est survenue lors de l'appel API : {e}")
        st.exception(e)
        return None, None


def try_local_prediction(client_data: dict, model, training_columns):
    """
    Tente une prédiction avec le modèle local chargé en mémoire.
    """
    try:
        input_df = pd.DataFrame([client_data])

        # Le code d'encodage one-hot a été omis dans la version fournie,
        # mais la conversion des valeurs 'Oui'/'Non' en 'Yes'/'No' est nécessaire.
        mapping = {'Oui': 'Yes', 'Non': 'No'}
        for col in ['MultipleLines', 'OnlineSecurity', 'OnlineBackup', 'DeviceProtection', 'TechSupport', 'StreamingTV',
                    'StreamingMovies']:
            if col in input_df.columns:
                input_df[col] = input_df[col].map(lambda x: mapping.get(x, x))

        # Encodage One-Hot pour le DataFrame
        input_encoded = pd.get_dummies(input_df)

        # Assurer que toutes les colonnes d'entraînement sont présentes, remplir avec 0 si manquant
        input_encoded = input_encoded.reindex(columns=training_columns, fill_value=0)

        prediction_raw = model.predict(input_encoded)[0]
        proba_raw = model.predict_proba(input_encoded)[0]

        # Trouver l'indice de la classe prédite pour obtenir sa probabilité
        class_index = model.classes_.tolist().index(prediction_raw)
        confidence = round(proba_raw[class_index] * 100, 2)

        prediction_message = "Le client va se désabonner" if prediction_raw == "Yes" else "Le client va rester"

        return {
            "prediction": prediction_message,
            "probabilité": f"{confidence:.2f}%",
            "feature_importances": get_feature_importances(model, training_columns, input_encoded)
        }, "modèle local"
    except Exception as e:
        st.error(f"Erreur lors de la prédiction locale : {e}")
        st.exception(e)
        return None, str(e)


def get_feature_importances(model, training_columns, input_data_encoded):
    """
    Extrait les importances des caractéristiques du modèle
    et les formate pour l'affichage.
    """
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
        feature_names = training_columns  # Les noms des colonnes après encodage one-hot

        # Créer un DataFrame pour faciliter le tri et la visualisation
        feature_importance_df = pd.DataFrame({
            'Feature': feature_names,
            'Importance': importances
        }).sort_values(by='Importance', ascending=False)

        # On peut ne garder que les N premières caractéristiques les plus importantes
        return feature_importance_df.head(10)  # Retourne les 10 plus importantes
    return None


# =============================================
# INTERFACE UTILISATEUR
# =============================================

# Appel des fonctions de style
set_background()
custom_sidebar_style()
apply_prediction_button_style()

check_authentication()

st.title("🔮 Prédiction de Churn Individualisée")
st.markdown("""
    **Outil d'IA pour anticiper le risque d'attrition client** *Basé sur le modèle Random Forest (précision: 85%)*
""")
st.divider()

with st.form("prediction_form"):
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Informations Client")
        gender = st.radio("Genre", ["Male", "Female"], horizontal=True)
        senior = st.checkbox("Senior (65+ ans)", help="Indique si le client est âgé de 65 ans ou plus.")
        partner = st.checkbox("Partenaire", help="Indique si le client a un partenaire.")
        dependents = st.checkbox("Personnes à charge", help="Indique si le client a des personnes à charge.")
        tenure = st.slider("Ancienneté (mois)", 1, 72, 12,
                           help="Nombre de mois pendant lesquels le client est resté avec la compagnie.")

    with col2:
        st.subheader("Services & Contrat")
        contract = st.selectbox("Type de contrat", ["Month-to-month", "One year", "Two year"],
                                help="Durée du contrat du client.")
        internet = st.selectbox("Service Internet", ["DSL", "Fiber optic", "No"],
                                help="Type de service Internet souscrit.")
        payment = st.selectbox("Méthode de paiement",
                               ["Electronic check", "Mailed check", "Bank transfer (automatic)",
                                "Credit card (automatic)"],
                               help="Méthode de paiement préférée du client.")
        monthly_charges = st.number_input("Charges mensuelles ($)", min_value=18.0, max_value=150.0, value=65.5,
                                          step=0.5, format="%.2f", help="Montant total facturé au client chaque mois.")
        total_charges = st.number_input("Charges totales ($)", min_value=0.0, max_value=10000.0,
                                        value=float(tenure * monthly_charges), step=10.0, format="%.2f",
                                        help="Montant total facturé au client sur toute la durée du contrat.")

    # Services optionnels
    with st.expander("Services optionnels"):
        services_col1, services_col2 = st.columns(2)
        with services_col1:
            phone = st.checkbox("Service téléphonique", value=True,
                                help="Indique si le client a un service téléphonique.")
            multiple_lines = st.checkbox("Lignes multiples",
                                         help="Indique si le client a plusieurs lignes téléphoniques.")
            online_security = st.checkbox("Sécurité en ligne",
                                          help="Indique si le client a souscrit à un service de sécurité en ligne.")
            online_backup = st.checkbox("Sauvegarde en ligne",
                                        help="Indique si le client a souscrit à un service de sauvegarde en ligne.")
        with services_col2:
            device_protection = st.checkbox("Protection appareil",
                                            help="Indique si le client a souscrit à un service de protection d'appareil.")
            tech_support = st.checkbox("Support technique",
                                       help="Indique si le client a souscrit à un service de support technique.")
            streaming_tv = st.checkbox("TV en streaming",
                                       help="Indique si le client a souscrit à un service de streaming TV.")
            streaming_movies = st.checkbox("Films en streaming",
                                           help="Indique si le client a souscrit à un service de streaming de films.")

    paperless = st.checkbox("Facturation électronique",
                            help="Indique si le client reçoit ses factures par voie électronique.")
    submitted = st.form_submit_button("Lancer la prédiction", type="primary")

# =============================================
# LOGIQUE DE PRÉDICTION
# =============================================
if submitted:
    # Validation de la cohérence des charges totales
    expected_total_charges = round(tenure * monthly_charges, 2)
    if tenure > 0 and abs(
            total_charges - expected_total_charges) > 1.0:  # Tolérance de 1.0 pour les petites différences
        st.warning(f"""
        ⚠️ **Incohérence détectée dans les charges totales !**
        Basé sur l'ancienneté ({tenure} mois) et les charges mensuelles (${monthly_charges:.2f}),
        les charges totales attendues seraient d'environ **${expected_total_charges:.2f}**.
        La valeur saisie (${total_charges:.2f}) pourrait affecter la précision de la prédiction.
        """)

    client_data = {
        "gender": gender,
        "SeniorCitizen": 1 if senior else 0,
        "Partner": "Yes" if partner else "No",
        "Dependents": "Yes" if dependents else "No",
        "tenure": tenure,
        "PhoneService": "Yes" if phone else "No",
        "MultipleLines": "Yes" if multiple_lines else "No",
        "InternetService": internet,
        "OnlineSecurity": "Yes" if online_security else "No",
        "OnlineBackup": "Yes" if online_backup else "No",
        "DeviceProtection": "Yes" if device_protection else "No",
        "TechSupport": "Yes" if tech_support else "No",
        "StreamingTV": "Yes" if streaming_tv else "No",
        "StreamingMovies": "Yes" if streaming_movies else "No",
        "Contract": contract,
        "PaperlessBilling": "Yes" if paperless else "No",
        "PaymentMethod": payment,
        "MonthlyCharges": monthly_charges,
        "TotalCharges": total_charges
    }

    # Barre de progression (simple visuel, peut être remplacé par un spinner)
    progress_text = "Calcul de la prédiction en cours..."
    progress_bar = st.progress(0, text=progress_text)
    for percent_complete in range(100):
        time.sleep(0.01)  # Réduit le délai pour une progression plus rapide
        progress_bar.progress(percent_complete + 1, text=progress_text)
    progress_bar.empty()  # Supprime la barre une fois terminée

    # Tentative de prédiction via API
    result, source = try_api_prediction(client_data)

    # Fallback local si échec API
    if result is None:
        st.warning("L'API n'est pas disponible. Tentative avec le modèle local...")
        result, error_msg = try_local_prediction(client_data, model, training_columns)
        if result is None:
            st.error(f"Échec de la prédiction locale : {error_msg}")
            st.stop()
        source = "local"

    # Affichage des résultats
    st.success(f"Prédiction réussie via {source.upper()}")
    prediction = result["prediction"]
    confidence = float(result["probabilité"].replace("%", ""))
    feature_importances_df = result.get("feature_importances")  # Récupérer les importances si disponibles

    # Onglets de résultats
    tab1, tab2 = st.tabs(["Résultat", "Recommandations & Facteurs Clés"])

    with tab1:
        # Affichage de la prédiction
        if "désabonner" in prediction:
            st.markdown(
                f'<div style="background-color:#ffe0e0; padding:15px; border-radius:10px; text-align:center; font-size:1.5em; color:#cc0000; font-weight:bold;">⚠️ {prediction}</div>',
                unsafe_allow_html=True)
        else:
            st.markdown(
                f'<div style="background-color:#e0ffe0; padding:15px; border-radius:10px; text-align:center; font-size:1.5em; color:#008000; font-weight:bold;">✅ {prediction}</div>',
                unsafe_allow_html=True)

        st.markdown(f"**Niveau de confiance :** {confidence:.2f}%")

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=confidence,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Niveau de Confiance de la Prédiction", 'font': {'size': 20}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "#4a00e0"},  # Couleur de la barre de jauge
                'steps': [
                    {'range': [0, 50], 'color': "lightcoral"},  # Risque élevé
                    {'range': [50, 75], 'color': "khaki"},  # Risque moyen
                    {'range': [75, 100], 'color': "lightgreen"}  # Faible risque
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': confidence}
            }
        ))
        fig.update_layout(height=250, margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("Recommandations et Facteurs Clés")

        if "désabonner" in prediction:
            st.warning(
                "Ce client présente un risque élevé de désabonnement. Voici des actions et les facteurs qui influencent cette prédiction :")
            st.markdown("""
            * **Offres personnalisées :** Proposez des forfaits adaptés à leur consommation réelle.
            * **Support proactif :** Contactez le client pour anticiper ses besoins ou résoudre des problèmes avant qu'il ne se plaigne.
            * **Programmes de fidélité :** Offrez des avantages exclusifs pour les inciter à rester.
            * **Analyse de la concurrence :** Comprenez pourquoi les clients partent chez les concurrents.
            """)
        else:
            st.info(
                "Ce client est susceptible de rester. Voici des stratégies pour renforcer sa fidélité et les facteurs clés :")
            st.markdown("""
            * **Valorisation :** Mettez en avant les bénéfices de leur abonnement actuel.
            * **Upselling/Cross-selling :** Proposez des services complémentaires pour augmenter leur valeur client.
            * **Enquêtes de satisfaction :** Recueillez leurs avis pour améliorer continuellement les services.
            * **Communication régulière :** Maintenez le contact avec des newsletters ou des offres exclusives.
            """)

        st.markdown("---")
        st.markdown("#### Impact des variables clés sur la prédiction")
        if feature_importances_df is not None:
            fig_importance = px.bar(
                feature_importances_df,
                x='Importance',
                y='Feature',
                orientation='h',
                title="Importance des Caractéristiques du Modèle",
                color_discrete_sequence=["#4a00e0"]
            )
            fig_importance.update_layout(yaxis={'categoryorder': 'total ascending'})  # Pour trier les barres
            st.plotly_chart(fig_importance, use_container_width=True)
        else:
            st.info("Les importances des caractéristiques ne sont pas disponibles pour le modèle API ou local.")

# =============================================
# Sidebar
# =============================================
with st.sidebar:
    st.header("ℹ️ À propos")
    st.markdown("""
    Cette application utilise un modèle de Machine Learning pour prédire le risque de désabonnement des clients télécoms.
    """)
    st.markdown("""
    **Performance du modèle (Random Forest)**:
    - **Précision**: 78 %
    - **Recall**: 79 %
    - **F1-score**: 78 %
    """)

    # Remplacez "URL_DE_VOTRE_RAPPORT" par l'URL de publication de votre rapport Power BI
    power_bi_report_url = "[https://app.powerbi.com/groups/me/reports/7c8fa6a9-1784-4296-b0b8-8ee6ed98f3f9/ae5f9ce7220067b35013?experience=power-bi](https://app.powerbi.com/groups/me/reports/7c8fa6a9-1784-4296-b0b8-8ee6ed98f3f9/ae5f9ce7220067b35013?experience=power-bi)"

    st.markdown(f"""
        **Visualisez le tableau de bord d'analyse du churn :** <br>
        <a href="{power_bi_report_url}" target="_blank">
            <button style="background-color: #F2C811; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px;">
                Rapport Power BI
            </button>
        </a>
    """, unsafe_allow_html=True)
    st.divider()

st.divider()
st.caption("© 2025 Télécom Analytics - Tous droits réservés.")
