📉 Prédiction de l'attrition des clients - Telecom Churn App
Cette application web interactive, développée avec Streamlit, a pour objectif de prédire l'attrition (le "churn") des clients d'une entreprise de télécommunications. Elle permet d'analyser les facteurs qui influencent la fidélité des clients et d'identifier ceux qui sont à risque de résilier leur abonnement.

🧠 Modèle et fonctionnalités clés
L'application intègre un modèle de Machine Learning entraîné sur un jeu de données de télécommunications.

📊 Tableau de bord interactif : Visualisation des données d'attrition et exploration des caractéristiques des clients.

📈 Analyse de l'attrition : Graphiques et indicateurs pour comprendre les facteurs clés de l'attrition (service internet, type de contrat, etc.).

🔮 Prédiction personnalisée : Un formulaire permet de saisir les données d'un client pour obtenir une prédiction en temps réel sur son risque de churn.

📥 Téléchargement des résultats : Possibilité de télécharger les données d'analyse ou de prédiction.

🛠️ Technologies utilisées
Streamlit : Création de l'interface web.

Python : Langage de programmation principal.

Pandas / Numpy : Manipulation et analyse des données.

Scikit-learn : Entraînement et gestion du modèle de prédiction (par exemple, RandomForestClassifier).

Plotly / Matplotlib / Seaborn : Visualisations de données.

CSS : Personnalisation de l'interface utilisateur.

FastAPI : Création de l'API REST.

📁 Structure du projet
telecom_churn_app/
├── app/
│   ├── pages/
│   │   ├── 
│   │   ├── 1_Dashbord.py
│   │   └── 2_prevoir.py
│   └── auth.py
├── API/
│   ├── main.py
│   
├── model/
│   ├── modele_random_forest.pkl
│   └── training_columns.pkl
├── utils/
│   ├── __init__.py
│   └── ui_style.py
    └── auth.py
     └── data_loader.py
    └── chatbot.py


└── requirements.txt

🚀 Lancer l'application en local
Cette section est destinée aux développeurs et aux utilisateurs qui souhaitent exécuter l'application sur leur propre machine.

Clonez le dépôt :

git clone https://github.com/laminethiao/telecom-churn-app.git
cd telecom-churn-app

Installez les dépendances :

pip install -r requirements.txt

Lancez l'interface Streamlit :

streamlit run app.py

🌐 Lancer l'API en local
L'API, construite avec FastAPI, gère les requêtes de prédiction.

Lancez le serveur Uvicorn :

uvicorn API.main:app --reload

Accédez à la documentation de l'API :
Une fois le serveur lancé, vous pouvez consulter l'interface interactive de documentation (Swagger UI) à l'adresse suivante :
http://127.0.0.1:8000/docs

Exemple de requête :
Voici un exemple de corps de requête JSON pour envoyer des données à l'API de prédiction :

{
  "gender": "Male",
  "SeniorCitizen": 0,
  "Partner": "Yes",
  "Dependents": "No",
  "tenure": 12,
  "PhoneService": "Yes",
  "MultipleLines": "No",
  "InternetService": "Fiber optic",
  "OnlineSecurity": "No",
  "OnlineBackup": "Yes",
  "DeviceProtection": "No",
  "TechSupport": "No",
  "StreamingTV": "Yes",
  "StreamingMovies": "Yes",
  "Contract": "Month-to-month",
  "PaperlessBilling": "Yes",
  "PaymentMethod": "Electronic check",
  "MonthlyCharges": 85.5,
  "TotalCharges": 1020.5
}

Auteur ✨
LAMINE THIAO: - Lien vers votre profil GitHub