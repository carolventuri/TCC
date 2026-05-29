"""
pages/5_Tabelas.py — Tabelas de indicadores para consulta e exportação.

Permite visualizar os indicadores calculados em diferentes granularidades
e baixar os resultados em formato CSV.
"""

import streamlit as st
import pandas as pd

from utils import (
    carregar_dados,
    calcular_indicadores,
    CAMINHO_DADOS,
)

# Configuração da página
st.set_page_config(page_title="Tabelas de Dados", page_icon="📋", layout="wide")
st.title("📋 Tabelas de Dados e Indicadores")
st.markdown(
    "Consulte e exporte os indicadores acadêmicos calculados para o IFRS Campus Restinga."
)

# Carga dos dados
df_completo = carregar_dados(CAMINHO_DADOS)

# Filtros desta página
st.markdown("### Filtros")

col_f1, col_f2 = st.columns(2)

with col_f1:
    anos_disponiveis = sorted(df_completo["Ano"].unique())
    periodo = st.slider(
        "Período de análise",
        min_value=int(min(anos_disponiveis)),
        max_value=int(max(anos_disponiveis)),
        value=(int(min(anos_disponiveis)), int(max(anos_disponiveis))),
    )

with col_f2:
    tipos_disponiveis = sorted(df_completo["Tipo de Curso"].unique())
    tipos_selecionados = st.multiselect(
        "Tipo de Curso",
        options=tipos_disponiveis,
        default=tipos_disponiveis,
    )

# Aplica os filtros
df = df_completo[
    (df_completo["Ano"] >= periodo[0])
    & (df_completo["Ano"] <= periodo[1])
    & (df_completo["Tipo de Curso"].isin(tipos_selecionados))
].copy()

st.markdown("---")

# Seletor de agrupamento
st.markdown("### Agrupamento")

agrupamento_opcoes = {
    "Por Ano (campus completo)":   ["Ano"],
    "Por Ano e Curso":             ["Ano", "Nome de Curso"],
    "Por Ano e Tipo de Curso":     ["Ano", "Tipo de Curso"],
    "Por Ano e Eixo Tecnológico":  ["Ano", "Eixo Tecnológico"],
    "Média por Curso (período)":   ["Nome de Curso"],
    "Média por Tipo (período)":    ["Tipo de Curso"],
}

agrupamento_escolhido = st.radio(
    "Selecione o agrupamento:",
    options=list(agrupamento_opcoes.keys()),
    horizontal=True,
)

# Calcula os indicadores para o agrupamento selecionado
agrupamento = agrupamento_opcoes[agrupamento_escolhido]
df_tabela = calcular_indicadores(df, agrupamento)

# Colunas a exibir
# Define a ordem de exibição das colunas
colunas_identificacao = ["Ano", "Nome de Curso", "Tipo de Curso", "Eixo Tecnológico"]
colunas_indicadores   = ["TC", "TE", "TR", "IEf", "TPE"]
colunas_contagens     = ["matr_atendidas", "ingressantes", "concluintes",
                         "evadidos", "MREG", "MRET",
                         "conc_no_prazo", "conc_com_atraso",
                         "abandono", "desligados", "transf_ext", "transf_int"]

# Mantém apenas as colunas que existem no DataFrame calculado
colunas_exibir = [
    c for c in (colunas_identificacao + colunas_indicadores + colunas_contagens)
    if c in df_tabela.columns
]

df_exibir = df_tabela[colunas_exibir].copy()

# Exibição da tabela 
st.markdown(f"### Resultado: {agrupamento_escolhido}")
st.markdown(f"**{len(df_exibir)} linhas** · **{len(df_exibir.columns)} colunas**")

# Aplica gradiente de cor nos indicadores para facilitar a leitura
colunas_grad = [c for c in colunas_indicadores if c in df_exibir.columns]

st.dataframe(
    df_exibir.style.format(
        {c: "{:.1f}" for c in colunas_grad}
    ).background_gradient(
        subset=colunas_grad,
        cmap="Blues",
    ),
    width='stretch',
    height=500,
)

# Exportação 
st.markdown("### Exportar")

# Gera o CSV em memória (separador ; e decimal , conforme padrão brasileiro)
csv_bytes = df_exibir.to_csv(
    index=False,
    sep=";",
    decimal=",",
).encode("utf-8")

nome_arquivo = f"indicadores_{agrupamento_escolhido.replace(' ', '_').lower()}.csv"

st.download_button(
    label="⬇️ Baixar tabela como CSV",
    data=csv_bytes,
    file_name=nome_arquivo,
    mime="text/csv",
)

# Legenda 
st.markdown("---")
st.markdown(
    """
    **Legenda dos indicadores:**

    | Sigla | Significado |
    |-------|-------------|
    | TC | Taxa de Conclusão (%) |
    | TE | Taxa de Evasão (%) |
    | TR | Taxa de Retenção (%) |
    | IEf | Índice de Eficiência (%) |
    | TPE | Taxa de Permanência e Êxito (%) |
    | MREG | Matrículas Ativas Regulares (contagem) |
    | MRET | Matrículas Ativas Retidas (contagem) |
    | matr_atendidas | Total de matrículas atendidas no período |
    """
)
