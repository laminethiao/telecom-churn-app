import streamlit as st


def set_background():
    st.markdown(
        """
        <style>
        /* Fond global bleu clair doux */
        .stApp {
            background-color: #e6f0f9;  /* Bleu clair très doux */
            background-attachment: fixed;
        }

        /* Texte des liens principaux du menu */
        section[data-testid="stSidebar"] div.css-1v0mbdj,
        section[data-testid="stSidebar"] div.css-1wvskn5 {
            color: white !important;
            font-weight: 600;
            font-size: 18px;
        }

        /* Icônes */
        section[data-testid="stSidebar"] svg {
            color: inherit !important;
        }

        /* Style pour améliorer la lisibilité des contenus */
        .st-emotion-cache-1y4p8pa {
            padding: 2rem 3rem;
        }

        /* Style des cartes/containers */
        .st-emotion-cache-ocqkz7, .st-emotion-cache-1pxazr7 {
            background-color: white;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            margin-bottom: 20px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def custom_sidebar_style():
    st.markdown("""
        <style>
        /* Fond de la sidebar */
        section[data-testid="stSidebar"] {
            background-color: #2E7D32;  /* Vert foncé */
            padding: 20px;
        }

        /* Styles des liens dans le menu */
        section[data-testid="stSidebar"] ul {
            padding-left: 0;
        }

        section[data-testid="stSidebar"] ul li {
            list-style-type: none;
            margin-bottom: 10px;
        }

        section[data-testid="stSidebar"] ul li a {
            display: block;
            background-color: #b7950b !important;  /* Jaune foncé */
            color: black !important;
            padding: 10px 15px;
            border-radius: 8px;
            text-align: center;
            text-decoration: none;
            font-weight: bold;
            transition: background-color 0.3s ease;
        }

        /* Hover effect */
        section[data-testid="stSidebar"] ul li a:hover {
            background-color: #2980b9 !important;  /* Bleu */
            color: white !important;
        }

        /* Style pour la page active */
        section[data-testid="stSidebar"] ul li a[aria-current="page"] {
            background-color: #b7950b !important;  /* Jaune foncé */
            color: black !important;
            font-weight: bold;
            border-left: 4px solid #2980b9;  /* Bordure bleue à gauche */
        }

        /* Titre sidebar + titres des champs */
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] label {
            color: white !important;
        }
        </style>
    """, unsafe_allow_html=True)


import streamlit as st


def apply_login_form_style():
    """
    Applique le style CSS spécifique au formulaire de connexion,
    en assurant que la couleur des boutons est bien appliquée.
    """
    st.markdown("""
    <style>
    /* Rendre le fond du formulaire transparent */
    div.stForm {
        background-color: transparent !important;
        border: none !important;
    }

    .stForm > div:first-child {
        background-color: transparent !important;
        border: none !important;
    }

    /* Styles pour les boutons "Se connecter" (primary) et "S'inscrire" (secondary) */
    div[data-testid="stFormSubmitButton"] button,
    .stButton button.secondary {
        background-color: #28a745; /* Vert foncé pour les deux */
        border-color: #28a745;
        color: white;
    }

    </style>
    """, unsafe_allow_html=True)


def apply_prediction_button_style():
    """
    Applique le style CSS spécifique au bouton de prédiction.
    """
    st.markdown("""
    <style>
    /* Cibler le bouton de prédiction par son data-testid et le type "primary" */
    div[data-testid="stFormSubmitButton"] > button[kind="primary"] {
        background-color: #28a745; /* Vert foncé */
        border-color: #28a745;
        color: white;
    }

    /* S'assurer que le style est appliqué aussi pour les boutons non primaires */
    div[data-testid="stFormSubmitButton"] > button {
        background-color: #28a745;
        border-color: #28a745;
        color: white;
    }

    /* Pour s'assurer que l'état hover fonctionne aussi */
    div[data-testid="stFormSubmitButton"] > button:hover {
        background-color: #218838; /* Vert un peu plus foncé au survol */
        border-color: #1e7e34;
    }
    </style>
    """, unsafe_allow_html=True)
