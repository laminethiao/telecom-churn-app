
import pandas as pd
import streamlit as st

@st.cache_data
def load_data():
    df = pd.read_csv("APP/data/telco_clean.csv", encoding='utf-8')
    return df

