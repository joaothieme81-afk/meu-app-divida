# -*- coding: utf-8 -*-
"""
Este é um aplicativo Streamlit interativo para analisar dados da Dívida Pública
e dos Gastos Públicos Federais.

Os dados são lidos de arquivos JSON locais para garantir 100% de estabilidade
durante a apresentação, contornando a instabilidade das APIs oficiais.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json

# Configuração da página
st.set_page_config(
    page_title="Análise Orçamentária do Brasil",
    page_icon="🇧🇷",
    layout="wide"
)

# --- Funções de Carregamento de Dados (com cache) ---
# Usar o cache do Streamlit é crucial para performance.

@st.cache_data
def carregar_dados_json(caminho_arquivo):
    """Lê um arquivo JSON local e retorna os dados."""
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"Erro: O arquivo {caminho_arquivo} não foi encontrado. Certifique-se de que ele está na mesma pasta do app.")
        return None
    except Exception as e:
        st.error(f"Erro ao ler o arquivo {caminho_arquivo}: {e}")
        return None

@st.cache_data
def carregar_dataframes():
    """Carrega todos os arquivos JSON e os converte em DataFrames pandas."""
    dados_evolucao = carregar_dados_json('dados_evolucao_divida.json')
    dados_detentores = carregar_dados_json('dados_detentores_divida.json')
    dados_gastos = carregar_dados_json('dados_gastos_comparativo.json')

    if dados_evolucao and dados_detentores and dados_gastos:
        df_evolucao = pd.DataFrame(dados_evolucao).set_index('ano')
        df_detentores = pd.DataFrame(dados_detentores)
        df_gastos = pd.DataFrame(dados_gastos)
        return df_evolucao, df_detentores, df_gastos
    
    return None, None, None

# --- Funções dos Gráficos ---

def criar_grafico_evolucao(df):
    """Cria um gráfico de linha da evolução da dívida."""
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(df.index, df['valor_trilhoes'], marker='o', linestyle='-', color='#0072B2')
    
    ax.set_title('Evolução do Estoque da Dívida Pública Federal', fontsize=16)
    ax.set_xlabel('Ano', fontsize=12)
    ax.set_ylabel('Valor (em Trilhões de R$)', fontsize=12)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Adiciona os rótulos de valor em cada ponto
    for ano, valor in df['valor_trilhoes'].items():
        ax.text(ano, valor + 0.1, f'R$ {valor:.2f}T', ha='center', fontsize=10)
        
    return fig

def criar_grafico_detentores(df):
    """Cria um gráfico de pizza dos detentores da dívida."""
    df = df.set_index('credor')
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    wedges, texts, autotexts = ax.pie(
        df['porcentagem'], 
        autopct='%1.1f%%', 
        startangle=90,
        pctdistance=0.85,
        colors=plt.cm.Paired.colors
    )
    
    # Círculo no centro para fazer um "donut chart"
    centre_circle = plt.Circle((0,0),0.70,fc='white')
    fig.gca().add_artist(centre_circle)
    
    ax.set_title('Detentores da Dívida Pública (Foto Recente)', fontsize=16)
    
    # Criar a legenda com base nos dados do DataFrame
    legend_labels = [f'{i} - {p:.1f}%' for i, p in zip(df.index, df['porcentagem'])]
    ax.legend(
        legend_labels,
        title="Credores",
        loc="center left",
        bbox_to_anchor=(1, 0, 0.5, 1),
        fontsize=10
    )
    
    plt.setp(autotexts, size=10, weight="bold", color="black")
    ax.axis('equal')  # Equal aspect ratio
    return fig

def criar_grafico_gastos_comparativo(df):
    """Cria um gráfico de barras comparativo (2018 vs 2024)."""
    
    # Pivotar os dados para ter anos como colunas
    df_pivot = df.pivot(index='funcao', columns='ano', values='valor_bi')
    
    # Ordenar pela maior despesa em 2024 para um gráfico mais limpo
    df_pivot = df_pivot.sort_values(2024, ascending=False)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    df_pivot.plot(kind='bar', ax=ax, width=0.8)
    
    ax.set_title('Comparativo de Gastos por Função (2018 vs 2024)', fontsize=16)
    ax.set_xlabel('Função Orçamentária', fontsize=12)
    ax.set_ylabel('Valor (em Bilhões de R$)', fontsize=12)
    ax.legend(title='Ano', loc='upper right')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.xticks(rotation=45, ha='right')
    
    return fig

# --- Função de Análise Interativa (ATUALIZADA) ---

def responder_pergunta(pergunta, df_evolucao, df_detentores, df_gastos):
    """Processa a pergunta selecionada e retorna a resposta."""
    
    try:
        # --- PERGUNTAS DE LISTAGEM (NOVAS) ---
        if pergunta == "Listar todos os gastos de 2024 (do maior para o menor)":
            df_2024 = df_gastos[df_gastos['ano'] == 2024].copy()
            total_2024 = df_2024['valor_bi'].sum()
            df_2024['porcentagem'] = (df_2024['valor_bi'] / total_2024) * 100
            df_2024 = df_2024.sort_values(by='porcentagem', ascending=False)
            
            resposta_md = "### Gastos de 2024 (do maior para o menor):\n\n"
            for _, row in df_2024.iterrows():
                resposta_md += f"- **{row['funcao']}**: R$ {row['valor_bi']:.1f} bi ({row['porcentagem']:.1f}% do total listado)\n"
            return resposta_md

        elif pergunta == "Listar todos os gastos de 2018 (do maior para o menor)":
            df_2018 = df_gastos[df_gastos['ano'] == 2018].copy()
            total_2018 = df_2018['valor_bi'].sum()
            df_2018['porcentagem'] = (df_2018['valor_bi'] / total_2018) * 100
            df_2018 = df_2018.sort_values(by='porcentagem', ascending=False)
            
            resposta_md = "### Gastos de 2018 (do maior para o menor):\n\n"
            for _, row in df_2018.iterrows():
                resposta_md += f"- **{row['funcao']}**: R$ {row['valor_bi']:.1f} bi ({row['porcentagem']:.1f}% do total listado)\n"
            return resposta_md

        elif pergunta == "Listar todos os credores da Dívida (do maior para o menor)":
            df_sorted = df_detentores.sort_values(by='porcentagem', ascending=False)
            resposta_md = "### Credores da Dívida (do maior para o menor):\n\n"
            for _, row in df_sorted.iterrows():
                resposta_md += f"- **{row['credor']}**: {row['porcentagem']:.1f}%\n"
            return resposta_md

        # --- PERGUNTAS DIRETAS (ATUALIZADAS E LIMPAS) ---
        elif pergunta == "Qual foi o maior gasto em 2018?":
            df_2018 = df_gastos[df_gastos['ano'] == 2018]
            gasto_max_idx = df_2018['valor_bi'].idxmax()
            gasto = df_2018.loc[gasto_max_idx]
            return f"O maior gasto em 2018 foi com **{gasto['funcao']}**, no valor de **R$ {gasto['valor_bi']} Bilhões**."

        elif pergunta == "Qual foi o menor gasto em 2018?":
            df_2018 = df_gastos[df_gastos['ano'] == 2018]
            gasto_min_idx = df_2018['valor_bi'].idxmin()
            gasto = df_2018.loc[gasto_min_idx]
            return f"O menor gasto em 2018 (entre os principais listados) foi com **{gasto['funcao']}**, no valor de **R$ {gasto['valor_bi']} Bilhões**."

        elif pergunta == "Qual foi o maior gasto em 2024?":
            df_2024 = df_gastos[df_gastos['ano'] == 2024]
            gasto_max_idx = df_2024['valor_bi'].idxmax()
            gasto = df_2024.loc[gasto_max_idx]
            return f"O maior gasto em 2024 é com **{gasto['funcao']}**, no valor de **R$ {gasto['valor_bi']} Bilhões**."
        
        elif pergunta == "Qual o principal credor da Dívida Pública?":
            credor_max_idx = df_detentores['porcentagem'].idxmax()
            credor = df_detentores.loc[credor_max_idx]
            return f"O principal credor da Dívida Pública são os **{credor['credor']}**, detendo **{credor['porcentagem']}%** do total."

        elif pergunta == "Qual foi o ano com o maior estoque da Dívida?":
            ano_max_idx = df_evolucao['valor_trilhoes'].idxmax()
            valor_max = df_evolucao.loc[ano_max_idx]['valor_trilhoes']
            return f"O ano com o maior estoque da Dívida Pública no período foi **{ano_max_idx}**, atingindo **R$ {valor_max} Trilhões**."

        elif pergunta == "Qual foi o ano com o menor estoque da Dívida?":
            ano_min_idx = df_evolucao['valor_trilhoes'].idxmin()
            valor_min = df_evolucao.loc[ano_min_idx]['valor_trilhoes']
            return f"O ano com o menor estoque da Dívida Pública no período foi **{ano_min_idx}**, com **R$ {valor_min} Trilhões**."

    except Exception as e:
        return f"Ocorreu um erro ao processar sua pergunta: {e}"
    
    return "Selecione uma pergunta."


# --- Interface Principal do Streamlit ---

st.title("Análise da Dívida e Gastos Públicos no Brasil 🇧🇷")
st.markdown("""
Este aplicativo apresenta uma análise interativa dos dados orçamentários do Brasil, 
inspirado no artigo de João Nogueira Thieme sobre desigualdade e endividamento público.

**Nota:** Os dados são carregados de arquivos `.json` locais, que contêm "snapshots" (fotos) 
de dados reais e condensados dos portais oficiais (Tesouro Nacional, Siga Brasil). 
Esta abordagem garante 100% de estabilidade para a apresentação.
""")

# Carregar os dados
df_evolucao, df_detentores, df_gastos = carregar_dataframes()

if df_evolucao is not None and df_detentores is not None and df_gastos is not None:
    
    # Criar abas para cada gráfico/funcionalidade
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Gráfico 1: Evolução da Dívida",
        "📊 Gráfico 2: Comparativo de Gastos",
        " पाई Gráfico 3: Credores da Dívida",
        "💡 Insights Interativos"
    ])

    with tab1:
        st.header("Gráfico 1: A Trajetória da Dívida Pública (2018-2024)")
        st.markdown("""
        Este gráfico mostra o crescimento do estoque total da Dívida Pública Federal (DPF)
        ao longo dos últimos anos. Este é o dado macro que fundamenta a discussão sobre 
        o endividamento crescente.
        """)
        fig_evolucao = criar_grafico_evolucao(df_evolucao)
        st.pyplot(fig_evolucao)
        st.dataframe(df_evolucao, use_container_width=True)

    with tab2:
        st.header("Gráfico 2: Comparativo dos Principais Gastos (2018 vs 2024)")
        st.markdown("""
        Aqui, comparamos as principais funções de despesa do Orçamento Federal entre 
        2018 e 2024 (dados condensados). Note o crescimento expressivo nos gastos
        com a Dívida e Encargos Especiais.
        """)
        fig_gastos = criar_grafico_gastos_comparativo(df_gastos)
        st.pyplot(fig_gastos)
        st.dataframe(df_gastos.pivot(index='funcao', columns='ano', values='valor_bi'), use_container_width=True)

    with tab3:
        st.header("Gráfico 3: Quem são os Credores da Dívida?")
        st.markdown("""
        Este gráfico (baseado no "snapshot" mais recente do Tesouro Nacional) mostra 
        quem detém os títulos da dívida pública. Como o artigo aponta, a maior parte 
        está concentrada em Fundos de Previdência, Fundos de Investimento e Bancos.
        """)
        fig_detentores = criar_grafico_detentores(df_detentores)
        st.pyplot(fig_detentores)
        
        with st.expander("Ver descrições dos credores e dados em tabela"):
            st.dataframe(df_detentores, use_container_width=True)

    # Nova Aba Interativa!
    with tab4:
        st.header("💡 Insights Interativos")
        st.markdown("""
        Selecione uma pergunta pré-definida e o aplicativo irá consultar 
        o "dataset" (nossos arquivos `.json` locais) para encontrar a resposta.
        """)
        
        # Lista de perguntas ATUALIZADA
        lista_perguntas = [
            "Selecione uma pergunta...",
            "--- Perguntas de Listagem ---",
            "Listar todos os gastos de 2024 (do maior para o menor)",
            "Listar todos os gastos de 2018 (do maior para o menor)",
            "Listar todos os credores da Dívida (do maior para o menor)",
            "--- Perguntas Diretas ---",
            "Qual foi o maior gasto em 2018?",
            "Qual foi o menor gasto em 2018?",
            "Qual foi o maior gasto em 2024?",
            "Qual o principal credor da Dívida Pública?",
            "Qual foi o ano com o maior estoque da Dívida?",
            "Qual foi o ano com o menor estoque da Dívida?"
        ]
        
        pergunta_selecionada = st.selectbox("Escolha sua pergunta:", lista_perguntas)
        
        if st.button("Buscar Resposta", type="primary"):
            if "..." in pergunta_selecionada:
                st.warning("Por favor, selecione uma pergunta válida.")
            else:
                resposta = responder_pergunta(pergunta_selecionada, df_evolucao, df_detentores, df_gastos)
                # Respostas de listagem já vêm formatadas em Markdown
                if "###" in resposta:
                    st.markdown(resposta)
                else:
                    st.success(resposta)

else:
    st.error("Falha ao carregar os arquivos de dados JSON. Verifique se os arquivos `dados_evolucao_divida.json`, `dados_detentores_divida.json`, e `dados_gastos_comparativo.json` estão na mesma pasta que o aplicativo.")

st.sidebar.title("Sobre o Projeto")
st.sidebar.info("""
Este app foi desenvolvido com base no artigo "Uma análise da desigualdade social brasileira à luz do endividamento público" de João Nogueira Thieme.

Os dados (snapshots de 2018-2024) foram coletados manualmente dos seguintes portais oficiais para garantir 100% de estabilidade:

- **Tesouro Transparente** (Dívida Pública):
  `https://www.tesourotransparente.gov.br`
- **Siga Brasil** (Orçamento Federal):
  `https://www12.senado.leg.br/orcamento/sigabrasil`
- **Portal da Transparência** (Gastos):
  `https://portaldatransparencia.gov.br`
""")