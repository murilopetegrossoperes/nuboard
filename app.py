import streamlit as st
import pandas as pd
from etl import carregar_dados

st.set_page_config(page_title="nuboard", page_icon="🟣", layout="wide")

st.title("🟣nuboard")
st.markdown("---")

st.sidebar.header("⚙️ Configurações")
arquivo_upload = st.sidebar.file_uploader("Faça o upload do seu extrato (CSV)", type=["csv"])

@st.cache_data
def obter_dados(arquivo):
    # Passa o arquivo enviado pelo usuário em vez de um nome fixo
    return carregar_dados(arquivo)

# Verifica se o usuário já subiu algum arquivo
if arquivo_upload is not None:
    dados = obter_dados(arquivo_upload)
    
    if dados is not None:
        # 1. SEPARAÇÃO DE RECEITAS E DESPESAS
        # Despesas (valores menores que zero). Transformamos em positivo para os gráficos.
        df_despesas = dados[dados['valor'] < 0].copy()
        df_despesas['valor'] = df_despesas['valor'].abs()
        
        # Receitas/Entradas (valores maiores que zero)
        df_receitas = dados[dados['valor'] > 0].copy()

        # Cálculos Financeiros
        total_despesas = df_despesas['valor'].sum()
        total_receitas = df_receitas['valor'].sum()
        lucro_saldo = total_receitas - total_despesas

        # 2. LINHA DE INDICADORES (KPIs) ATUALIZADA
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(label="Total de Entradas 🟢", value=f"R$ {total_receitas:.2f}")
        with col2:
            st.metric(label="Total de Saídas 🔴", value=f"R$ {total_despesas:.2f}")
        with col3:
            # Se for lucro fica verde, se for prejuízo fica normal (com sinal negativo)
            st.metric(label="Lucro / Saldo do Mês 💰", value=f"R$ {lucro_saldo:.2f}")
        with col4:
            if not df_despesas.empty:
                categoria_campea = df_despesas.groupby('categoria')['valor'].sum().idxmax()
                st.metric(label="Categoria do maior gasto", value=categoria_campea)
            else:
                st.metric(label="Categoria do maior gasto", value="-")

        st.markdown("---")

        # 3. GRÁFICO NOVO: ENTRADAS VS SAÍDAS
        st.subheader("⚖️ Entradas vs Saídas Diárias")
        
        # Agrupa entradas e saídas por dia para criar um gráfico comparativo
        receitas_diarias = df_receitas.groupby('data')['valor'].sum().rename("Entradas")
        despesas_diarias = df_despesas.groupby('data')['valor'].sum().rename("Saídas")
        
        # Junta as duas tabelas lado a lado. Preenche dias sem movimento com 0.
        df_comparativo = pd.concat([receitas_diarias, despesas_diarias], axis=1).fillna(0)
        
        # O Streamlit cria automaticamente um gráfico de barras com duas cores
        st.bar_chart(df_comparativo, color=["#17B169", "#FF5733"]) # Verde para entradas, vermelho para saídas

        st.markdown("---")

        # 4. GRÁFICOS DE DESPESAS
        col_esq, col_dir = st.columns(2)

        with col_esq:
            st.subheader("📊 Distribuição de Gastos")
            gastos_por_categoria = df_despesas.groupby('categoria')['valor'].sum()
            st.bar_chart(gastos_por_categoria,color=["#840CCF"])

        with col_dir:
            st.subheader("📈 Evolução de Gastos")
            st.line_chart(despesas_diarias,color=["#840CCF"])

        # 5. TABELA DETALHADA
        st.markdown("---")
        st.subheader("📋 Detalhamento das Transações")
        st.dataframe(dados[['data', 'descricao', 'categoria', 'valor']], use_container_width=True)

    else:
        st.error("Houve um erro ao processar o arquivo. Verifique se é um extrato válido do Nubank.")
else:
    # Mensagem exibida quando o app abre e nenhum arquivo foi enviado ainda
    st.info("👈 Por favor, faça o upload do seu extrato CSV na barra lateral para visualizar o dashboard.")