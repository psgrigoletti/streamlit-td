import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

import sys
sys.path.append("..")

from config import BCB_API_URL, CACHE_TTL


@st.cache_data(ttl=CACHE_TTL)
def fetch_dolar_data(data_inicio, data_fim):
    """
    Busca dados do dólar através da API do Banco Central do Brasil.
    Os dados são cacheados por 1 hora para evitar múltiplas requisições.
    
    Como a API do BCB tem limite de 10 anos por consulta, esta função
    divide o período em consultas menores quando necessário.
    """
    # Converter para datetime se necessário
    if isinstance(data_inicio, str):
        data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
    if isinstance(data_fim, str):
        data_fim = datetime.strptime(data_fim, '%Y-%m-%d')
    
    # Calcular diferença em anos
    diff_anos = (data_fim - data_inicio).days / 365.25
    
    # Se o período for menor que 10 anos, faz uma única consulta
    if diff_anos <= 10:
        return _fetch_dolar_periodo(data_inicio, data_fim)
    
    # Para períodos maiores que 10 anos, divide em consultas menores
    dados_completos = []
    data_atual = data_inicio
    
    while data_atual < data_fim:
        # Calcular data final do período atual (máximo 10 anos)
        data_fim_periodo = min(
            data_atual + timedelta(days=3650),  # ~10 anos
            data_fim
        )
        
        # Buscar dados do período atual
        dados_periodo = _fetch_dolar_periodo(data_atual, data_fim_periodo)
        if dados_periodo is not None:
            dados_completos.append(dados_periodo)
        
        # Avançar para o próximo período
        data_atual = data_fim_periodo + timedelta(days=1)
    
    # Combinar todos os dados
    if dados_completos:
        return pd.concat(dados_completos, ignore_index=True)
    return None


def _fetch_dolar_periodo(data_inicio, data_fim):
    """
    Função auxiliar para buscar dados do dólar em um período específico.
    """
    # Formatar datas para o formato da API do BCB
    data_inicio_str = data_inicio.strftime('%d/%m/%Y')
    data_fim_str = data_fim.strftime('%d/%m/%Y')
    
    # URL da API do BCB para cotação do dólar (código 10813)
    url = f"{BCB_API_URL}?formato=json&dataInicial={data_inicio_str}&dataFinal={data_fim_str}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        dados = response.json()
        
        # Converter para DataFrame
        df = pd.DataFrame(dados)
        df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y')
        df['valor'] = pd.to_numeric(df['valor'])
        
        return df
    except Exception as e:
        st.error(f"Erro ao buscar dados do dólar: {str(e)}")
        return None 