"""
pages/4_Analise_Evasao_e_Retencao.py — Análise de evasão e retenção.

Gráficos desta página:
     — Barras empilhadas:  motivos de saída por ano
     — Barras empilhadas:  conclusões no prazo vs. com atraso por curso   
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from utils import (
    carregar_dados,
    calcular_indicadores,
    CAMINHO_DADOS,
    CORES_SITUACAO,
    CORES_CATEGORIA
)

# Configuração da página
st.set_page_config(page_title="Evasão e Retenção", page_icon="🔍", layout="wide")
st.title("🔍 Evasão e Retenção")
st.markdown(
    "Análise detalhada dos motivos de evasão, padrões de retenção e correlações "
    "entre indicadores para o IFRS Campus Restinga."
)

# Carga dos dados
df_completo = carregar_dados(CAMINHO_DADOS)

# Filtros desta página
st.markdown("### Filtros")

col_f1, col_f2, col_f3 = st.columns(3)

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

with col_f3:
    cursos_disponiveis = sorted(df_completo["Nome de Curso"].unique())
    cursos_selecionados = st.multiselect(
        "Curso",
        options=cursos_disponiveis,
        default=cursos_disponiveis,
    )

# Aplica os filtros
df = df_completo[
    (df_completo["Ano"] >= periodo[0])
    & (df_completo["Ano"] <= periodo[1])
    & (df_completo["Tipo de Curso"].isin(tipos_selecionados))
    & (df_completo["Nome de Curso"].isin(cursos_selecionados))
].copy()

# Calcula os indicadores necessários
ind_ano_curso = calcular_indicadores(df, ["Ano", "Nome de Curso"])


st.markdown("---")

#  XXXX : Motivos de saída por ano (barras empilhadas)
st.markdown("### — Motivos de Saída por Ano")
st.markdown(
    "Barras empilhadas mostrando o volume de cada tipo de saída (Abandono, "
    "Desligamento, Transferências) por ano."
)

# Filtra apenas as situações que representam saídas
situacoes_saida = ["Abandono", "Desligada", "Transf. externa", "Transf. interna", "Reprovada"]
df_saidas = (
    df[df["Situação de Matrícula"].isin(situacoes_saida)]
    .groupby(["Ano", "Situação de Matrícula"])["Código da Matricula"]
    .count()
    .reset_index(name="Qtd")
)

fig_g12 = px.bar(
    df_saidas,
    x="Ano",
    y="Qtd",
    color="Situação de Matrícula",
    barmode="stack",
    color_discrete_map=CORES_SITUACAO,
    labels={"Qtd": "Matrículas", "Situação de Matrícula": "Motivo"},
    text_auto=True,
)
fig_g12.update_xaxes(tickmode="linear", dtick=1)
st.plotly_chart(fig_g12, width='stretch')



st.markdown("### — Conclusões: No Prazo vs. Com Atraso")
st.markdown(
    "Mostra, por curso, quantas conclusões ocorreram dentro e fora do prazo previsto."
)

# Filtra apenas concluintes e conta por situação detalhada
conc_prazo = (
    df[df["Categoria da Situação"] == "Concluintes"]
    .groupby(["Nome de Curso", "Situação de Matrícula"])["Código da Matricula"]
    .count()
    .reset_index(name="Qtd")
)

fig_g17 = px.bar(
        conc_prazo,
        x="Nome de Curso",
        y="Qtd",
        color="Situação de Matrícula",
        barmode="stack",
        color_discrete_map=CORES_SITUACAO,
        labels={"Qtd": "Concluintes", "Nome de Curso": ""},
        text_auto=True,
    )
fig_g17.update_layout(xaxis_tickangle=-30)

st.plotly_chart(fig_g17, width='stretch')