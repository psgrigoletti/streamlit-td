import streamlit as st
import pandas as pd
import plotly.express as px


def plot_taxa_evolucao(df_filtrado, tipo_selecionado):
    """
    Gera gráfico de linha para evolução das taxas.
    """
    fig_taxa = px.line(
        df_filtrado,
        x='Data Base',
        y='Taxa Compra Manha',
        color='Ano Vencimento',
        title='Taxa de Compra ao Longo do Tempo',
        labels={
            'Data Base': 'Data',
            'Taxa Compra Manha': 'Taxa de Compra (%)',
            'Ano Vencimento': 'Ano de Vencimento'
        }
    )
    st.plotly_chart(fig_taxa, use_container_width=True)


def plot_preco_evolucao(df_filtrado, tipo_selecionado):
    """
    Gera gráfico de linha para evolução dos preços.
    """
    fig_preco = px.line(
        df_filtrado,
        x='Data Base',
        y='PU Compra Manha',
        color='Ano Vencimento',
        title='Preço de Compra ao Longo do Tempo',
        labels={
            'Data Base': 'Data',
            'PU Compra Manha': 'Preço de Compra (R$)',
            'Ano Vencimento': 'Ano de Vencimento'
        }
    )
    st.plotly_chart(fig_preco, use_container_width=True)


def plot_dolar_evolucao(df_dolar):
    """
    Gera gráfico de linha para evolução do dólar.
    """
    if df_dolar is not None:
        fig_dolar = px.line(
            df_dolar,
            x='data',
            y='valor',
            title='Cotação do Dólar ao Longo do Tempo',
            labels={
                'data': 'Data',
                'valor': 'Cotação (R$)'
            }
        )
        st.plotly_chart(fig_dolar, use_container_width=True) 