import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import requests
from io import StringIO
from alerts import AlertManager

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
    
    # Inicializar gerenciador de alertas
    alert_manager = AlertManager()
    
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
        
        # Adicionar coluna de ano de vencimento
        df['Ano Vencimento'] = df['Data Vencimento'].dt.year
        
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
        
        # Criar dicionário para mapear anos para datas de vencimento
        vencimentos_por_ano = {}
        for data in vencimentos_disponiveis:
            ano = data.year
            if ano not in vencimentos_por_ano:
                vencimentos_por_ano[ano] = []
            vencimentos_por_ano[ano].append(data)
        
        # Ordenar anos em ordem decrescente
        anos_disponiveis = sorted(vencimentos_por_ano.keys(), reverse=True)
        
        # Obter ano atual
        ano_atual = datetime.now().year
        
        # Selecionar anos (pré-selecionando anos >= ano atual)
        anos_selecionados = st.sidebar.multiselect(
            "Selecione os anos de vencimento",
            options=anos_disponiveis,
            default=[ano for ano in anos_disponiveis if ano >= ano_atual]
        )
        
        # Obter datas de vencimento correspondentes aos anos selecionados
        vencimentos_selecionados = []
        for ano in anos_selecionados:
            vencimentos_selecionados.extend(vencimentos_por_ano[ano])
        
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
            color='Ano Vencimento',
            title='Taxa de Compra ao Longo do Tempo',
            labels={
                'Data Base': 'Data',
                'Taxa Compra Manha': 'Taxa de Compra (%)',
                'Ano Vencimento': 'Ano de Vencimento'
            }
        )
        st.plotly_chart(fig_taxa, use_container_width=True)
        
        # Gráfico de linha para preços
        st.subheader(f"Evolução dos Preços - {tipo_selecionado}")
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
        
        # Tabela com dados recentes
        st.subheader("Dados Recentes")
        st.dataframe(
            df_filtrado.sort_values('Data Base', ascending=False).head(10),
            use_container_width=True
        )
        
        # Seção de Alertas
        st.header("📢 Configuração de Alertas")
        
        # Formulário para novo alerta
        with st.form("novo_alerta"):
            st.subheader("Novo Alerta")
            
            col1, col2 = st.columns(2)
            
            with col1:
                nome = st.text_input("Seu Nome")
                email = st.text_input("Seu Email")
                tipo_titulo_alerta = st.selectbox(
                    "Tipo de Título",
                    tipos_titulo
                )
                ano_vencimento_alerta = st.selectbox(
                    "Ano de Vencimento",
                    sorted(vencimentos_por_ano.keys(), reverse=True)
                )
            
            with col2:
                st.subheader("Critérios de Alerta")
                preco_min = st.number_input(
                    "Preço Mínimo (R$)",
                    min_value=0.0,
                    value=None,
                    step=0.01
                )
                preco_max = st.number_input(
                    "Preço Máximo (R$)",
                    min_value=0.0,
                    value=None,
                    step=0.01
                )
                taxa_min = st.number_input(
                    "Taxa Mínima (%)",
                    min_value=0.0,
                    value=None,
                    step=0.01
                )
                taxa_max = st.number_input(
                    "Taxa Máxima (%)",
                    min_value=0.0,
                    value=None,
                    step=0.01
                )
            
            if st.form_submit_button("Criar Alerta"):
                if nome and email:
                    alert_manager.add_alert(
                        nome=nome,
                        email=email,
                        tipo_titulo=tipo_titulo_alerta,
                        ano_vencimento=ano_vencimento_alerta,
                        preco_min=preco_min,
                        preco_max=preco_max,
                        taxa_min=taxa_min,
                        taxa_max=taxa_max
                    )
                    st.success("Alerta criado com sucesso!")
                else:
                    st.error("Por favor, preencha nome e email.")
        
        # Tabela de alertas ativos
        st.subheader("Alertas Ativos")
        if not alert_manager.alerts.empty:
            # Adicionar coluna de ações
            alertas_df = alert_manager.alerts.copy()
            alertas_df['Ações'] = range(len(alertas_df))
            
            # Mostrar tabela com botões de remoção
            for idx, alerta in alertas_df.iterrows():
                col1, col2 = st.columns([0.9, 0.1])
                with col1:
                    st.write(f"**{alerta['nome']}** - {alerta['tipo_titulo']} ({alerta['ano_vencimento']})")
                    st.write(f"Email: {alerta['email']}")
                    detalhes = []
                    if pd.notna(alerta['preco_min']):
                        detalhes.append(f"Preço Mín: R$ {alerta['preco_min']:.2f}")
                    if pd.notna(alerta['preco_max']):
                        detalhes.append(f"Preço Máx: R$ {alerta['preco_max']:.2f}")
                    if pd.notna(alerta['taxa_min']):
                        detalhes.append(f"Taxa Mín: {alerta['taxa_min']:.2f}%")
                    if pd.notna(alerta['taxa_max']):
                        detalhes.append(f"Taxa Máx: {alerta['taxa_max']:.2f}%")
                    st.write(" | ".join(detalhes))
                    st.write(f"Criado em: {alerta['data_criacao']}")
                with col2:
                    if st.button("🗑️", key=f"remove_{idx}"):
                        alert_manager.remove_alert(idx)
                        st.rerun()
                st.divider()
        else:
            st.info("Nenhum alerta configurado.")
        
        # Botão para verificar alertas
        if st.button("Verificar Alertas"):
            alerts_triggered = alert_manager.check_alerts(df)
            if alerts_triggered:
                st.success(f"{len(alerts_triggered)} alerta(s) acionado(s)!")
                for alert in alerts_triggered:
                    try:
                        alert_manager.send_alert_email(alert)
                        st.success(f"Email enviado para {alert['email']}")
                    except Exception as e:
                        st.error(f"Erro ao enviar email: {str(e)}")
            else:
                st.info("Nenhum alerta acionado.")

if __name__ == "__main__":
    main()