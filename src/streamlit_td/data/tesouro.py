import streamlit as st
import pandas as pd
import requests
from io import StringIO

import sys
sys.path.append("..")

from config import TESOURO_API_URL, CACHE_TTL


@st.cache_data(ttl=CACHE_TTL)  # Cache por 1 hora
def fetch_tesouro_data():
    """
    Busca dados do Tesouro Direto através da API do Tesouro Transparente.
    Os dados são cacheados por 1 hora para evitar múltiplas requisições.
    """
    try:
        response = requests.get(TESOURO_API_URL)
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.text), sep=';', decimal=',')
        return df
    except Exception as e:
        st.error(f"Erro ao buscar dados do Tesouro Direto: {str(e)}")
        return None


def process_tesouro_data(df):
    """
    Processa os dados do Tesouro Direto, convertendo datas e adicionando
    colunas necessárias.
    """
    if df is not None:
        # Converter coluna de data
        df['Data Vencimento'] = pd.to_datetime(
            df['Data Vencimento'], 
            format='%d/%m/%Y'
        )
        df['Data Base'] = pd.to_datetime(
            df['Data Base'], 
            format='%d/%m/%Y'
        )
        
        # Adicionar coluna de ano de vencimento
        df['Ano Vencimento'] = df['Data Vencimento'].dt.year
        
        return df
    return None 