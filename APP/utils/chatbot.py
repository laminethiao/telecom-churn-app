import pandas as pd
from typing import Dict, Any



# LOGIQUE DU CHATBOT AMÉLIORÉE

def safe_divide(a, b):
    """Fonction utilitaire pour diviser sans erreur de division par zéro."""
    return a / b if b != 0 else 0


def get_chatbot_response(df: pd.DataFrame, user_input: str) -> str:
   
    
    # Mettre en minuscules pour faciliter la correspondance des mots-clés
    user_input = user_input.lower()

    # Dictionnaire des mots-clés pour chaque KPI
    kpi_keywords = {
        'clients_actifs': ['clients actifs', 'nombre de clients', 'combien de clients', 'total de clients'],
        'taux_churn': ['taux de churn', 'taux d\'attrition', 'pourcentage de désabonnement', 'clients partis'],
        'revenu_mensuel': ['revenu mensuel', 'revenus mensuels', 'facturation mensuelle', 'chiffre d\'affaires'],
        'anciennete': ['ancienneté moyenne', 'ancienneté clients'],
        'sans_internet': ['sans internet', 'pas d\'internet', 'internet service non'],
        'facture_demat': ['facture dématérialisée', 'facturation dématérialisée', 'paperless billing'],
        'clients_seniors': ['clients seniors', 'plus de 65 ans', 'personnes âgées']
    }

    # Calcul des KPIs actuels pour le DataFrame filtré
    total_clients = len(df)
    churn_count = len(df[df['Churn'] == 'Yes'])
    monthly_revenue = df['MonthlyCharges'].sum()
    avg_tenure = df['tenure'].mean()
    no_internet_percent = safe_divide(len(df[df['InternetService'] == 'No']), total_clients) * 100
    paperless_percent = safe_divide(len(df[df['PaperlessBilling'] == 'Yes']), total_clients) * 100
    seniors_percent = safe_divide(len(df[df['SeniorCitizen'] == 1]), total_clients) * 100

    # Stockage des valeurs des KPIs pour les réponses
    kpi_values = {
        'clients_actifs': f"👥 {total_clients:,} clients actifs",
        'taux_churn': f"⚠️ Le taux de churn est de {safe_divide(churn_count, total_clients) * 100:.1f}%",
        'revenu_mensuel': f"💸 Le revenu mensuel total est de ${monthly_revenue:,.0f}",
        'anciennete': f"⏳ L'ancienneté moyenne est de {avg_tenure:.1f} mois",
        'sans_internet': f"  {no_internet_percent:.1f}% des clients n'ont pas de service internet",
        'facture_demat': f"🌱 {paperless_percent:.1f}% des clients ont opté pour la facture dématérialisée",
        'clients_seniors': f"👵 {seniors_percent:.1f}% des clients sont des seniors"
    }

    # Cherche les KPIs demandés dans la question de l'utilisateur
    matched_kpis = []
    for kpi, keywords in kpi_keywords.items():
        if any(keyword in user_input for keyword in keywords):
            matched_kpis.append(kpi)

    # Construit la réponse en fonction des KPIs trouvés
    if matched_kpis:
        # Réponse pour un seul KPI
        if len(matched_kpis) == 1:
            kpi_name = matched_kpis[0]
            # Formuler une réponse plus conversationnelle
            if kpi_name == 'taux_churn':
                return f"Selon les données filtrées, {kpi_values[kpi_name]}. C'est une mesure clé pour la rétention client."
            elif kpi_name == 'clients_actifs':
                return f"Actuellement, il y a {kpi_values[kpi_name]}. Ce chiffre peut varier avec les filtres appliqués."
            else:
                return kpi_values[kpi_name] + "."

        # Réponse pour plusieurs KPIs
        else:
            responses = [kpi_values[kpi] for kpi in matched_kpis]
            response_text = " et ".join(responses)
            return f"Voici les informations demandées : {response_text}."

    # Si aucun KPI n'est trouvé
    return "Désolé, je n'ai pas compris votre question. Je peux vous donner des informations sur : `clients actifs`, `taux de churn`, `revenu mensuel`, `ancienneté moyenne`, `facture dématérialisée`, `clients seniors` ou les clients `sans internet`."

