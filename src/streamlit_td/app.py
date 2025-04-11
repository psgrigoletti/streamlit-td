import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import requests
from io import StringIO

st.set_page_config(
    page_title="Tesouro Direto - Visualização de Dados",
    page_icon="📈",
    layout="wide"
)

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

def main():
    st.title("📈 Visualização de Dados do Tesouro Direto")
    
    # Buscar dados (agora com cache)
    df = fetch_tesouro_data()
    
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
        
        # Sidebar para filtros
        st.sidebar.header("Filtros")
        
        # Filtro por tipo de título
        tipos_titulo = df['Tipo Titulo'].unique()
        tipo_selecionado = st.sidebar.selectbox(
            "Selecione o tipo de título",
            tipos_titulo
        )
        
        # Filtro por data de vencimento (seleção múltipla)
        vencimentos_disponiveis = (
            df[df['Tipo Titulo'] == tipo_selecionado]
            ['Data Vencimento']
            .unique()
        )
        vencimentos_selecionados = st.sidebar.multiselect(
            "Selecione as datas de vencimento",
            options=vencimentos_disponiveis,
            default=vencimentos_disponiveis[:3] 
            if len(vencimentos_disponiveis) > 0 
            else None,
            format_func=lambda x: x.strftime('%d/%m/%Y')
        )
        
        # Filtro por data base
        data_min = df['Data Base'].min()
        data_max = df['Data Base'].max()
        data_inicio = st.sidebar.date_input(
            "Data inicial",
            value=data_min,
            min_value=data_min,
            max_value=data_max
        )
        data_fim = st.sidebar.date_input(
            "Data final",
            value=data_max,
            min_value=data_min,
            max_value=data_max
        )
        
        # Aplicar filtros
        df_filtrado = df[
            (df['Tipo Titulo'] == tipo_selecionado) &
            (df['Data Base'] >= pd.to_datetime(data_inicio)) &
            (df['Data Base'] <= pd.to_datetime(data_fim))
        ]
        
        # Aplicar filtro de vencimentos se houver seleção
        if vencimentos_selecionados:
            df_filtrado = df_filtrado[
                df_filtrado['Data Vencimento']
                .isin(vencimentos_selecionados)
            ]
        
        # Ordenar dados por data base
        df_filtrado = df_filtrado.sort_values('Data Base')
        
        # Gráfico de linha para taxas
        st.subheader(f"Evolução das Taxas - {tipo_selecionado}")
        fig_taxa = px.line(
            df_filtrado,
            x='Data Base',
            y='Taxa Compra Manha',
            color='Data Vencimento',
            title='Taxa de Compra ao Longo do Tempo',
            labels={
                'Data Base': 'Data',
                'Taxa Compra Manha': 'Taxa de Compra (%)',
                'Data Vencimento': 'Data de Vencimento'
            }
        )
        st.plotly_chart(fig_taxa, use_container_width=True)
        
        # Tabela com dados recentes
        st.subheader("Dados Recentes")
        st.dataframe(
            df_filtrado.sort_values('Data Base', ascending=False).head(10),
            use_container_width=True
        )

if __name__ == "__main__":
    main() 