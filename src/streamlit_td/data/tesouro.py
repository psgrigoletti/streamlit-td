import streamlit as st
import pandas as pd
import requests
from io import StringIO


@st.cache_data(ttl=3600)  # Cache por 1 hora
def fetch_tesouro_data():
    """
    Busca dados do Tesouro Direto através da API do Tesouro Transparente.
    Os dados são cacheados por 1 hora para evitar múltiplas requisições.
    """
    base_url = (
        "https://www.tesourotransparente.gov.br/ckan/dataset/"
        "df56aa42-484a-4a59-8184-7676580c81e3/resource/"
        "796d2059-14e9-44e3-80c9-2d9e30b405c1/download/"
        "PrecoTaxaTesouroDireto.csv"
    )
    
    try:
        response = requests.get(base_url)
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.text), sep=';', decimal=',')
        return df
    except Exception as e:
        st.error(f"Erro ao buscar dados: {str(e)}")
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