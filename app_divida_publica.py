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
# ... (existing code) ...
    ax.axis('equal')  # Equal aspect ratio
    return fig

def criar_grafico_gastos_comparativo(df):
# ... (existing code) ...
    ax.spines['right'].set_visible(False)
    plt.xticks(rotation=45, ha='right')
    
    return fig

# --- Função de Análise Interativa (ATUALIZADA) ---

def responder_pergunta(pergunta, df_evolucao, df_detentores, df_gastos):
# ... (existing code) ...
    return "Selecione uma pergunta."


# --- Interface Principal do Streamlit ---
# ... (existing code) ...
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