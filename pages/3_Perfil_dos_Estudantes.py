"""
pages/3_Perfil_dos_Estudantes.py — Perfil sociodemográfico dos estudantes.

Gráficos desta página:
    10 — Pizza (donut):      distribuição por sexo
    11 — Barras horizontais: distribuição por cor/raça
    12 — Barras:             distribuição por faixa etária
    13 — Barras:             distribuição por renda familiar
    14 — Pizza (donut):      distribuição por turno
    15 — Barras empilhadas%: composição por cor/raça ao longo dos anos

"""

import streamlit as st
import plotly.express as px
import pandas as pd

from utils import (
    carregar_dados,
    CAMINHO_DADOS,
)

# Configuração da página
st.set_page_config(page_title="Perfil dos Estudantes", page_icon=":mortar_board:", layout="wide")
st.title(":mortar_board: Perfil dos Estudantes")
st.markdown(
    "Distribuição sociodemográfica dos estudantes matriculados no IFRS Campus Restinga "
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

st.markdown("---")


col_g19, col_g20 = st.columns(2)

with col_g19:
    st.markdown("### 10 — Distribuição por Sexo")

    sexo_df = df["Sexo"].value_counts().reset_index()
    sexo_df.columns = ["Sexo", "Qtd"]

    fig_g19 = px.pie(
        sexo_df,
        names="Sexo",
        values="Qtd",
        hole=0.4,
        color_discrete_sequence=["#2196F3", "#E91E63", "#9E9E9E"],
    )
    fig_g19.update_traces(textposition="outside", textinfo="percent+label")
    st.plotly_chart(fig_g19, width='stretch')

with col_g20:
    st.markdown("### 11 — Distribuição por Cor/Raça")

    raca_df = df["Cor / Raça"].value_counts().reset_index()
    raca_df.columns = ["Cor/Raça", "Qtd"]

    fig_g20 = px.bar(
        raca_df.sort_values("Qtd", ascending=True),
        x="Qtd",
        y="Cor/Raça",
        orientation="h",
        color="Qtd",
        color_continuous_scale="Purples",
        text_auto=True,
        labels={"Qtd": "Matrículas"},
    )
    fig_g20.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig_g20, width='stretch')


col_g21, col_g22 = st.columns(2)

with col_g21:
    st.markdown("### 12 — Distribuição por Faixa Etária")

    # Ordem cronológica das faixas etárias
    ordem_etaria = [
        "Menor de 14 anos", "15 a 19 anos", "20 a 24 anos",
        "25 a 29 anos", "30 a 34 anos", "35 a 39 anos",
        "40 a 44 anos", "45 a 49 anos", "50 a 54 anos",
        "55 a 59 anos", "Maior de 60 anos",
    ]
    # Mantém apenas as faixas que existem nos dados filtrados
    faixas_presentes = [f for f in ordem_etaria if f in df["Faixa Etária"].unique()]

    etaria_df = (
        df["Faixa Etária"]
        .value_counts()
        .reindex(faixas_presentes)
        .reset_index()
    )
    etaria_df.columns = ["Faixa Etária", "Qtd"]

    fig_g21 = px.bar(
        etaria_df,
        x="Faixa Etária",
        y="Qtd",
        color="Qtd",
        color_continuous_scale="Blues",
        text_auto=True,
        labels={"Qtd": "Matrículas"},
    )
    fig_g21.update_layout(coloraxis_showscale=False, xaxis_tickangle=-30)
    st.plotly_chart(fig_g21, width='stretch')

with col_g22:
    st.markdown("### 13 — Distribuição por Renda Familiar per capita")
    
    # Ordem lógica das faixas de renda
    ordem_renda = [
        "0<RFP<=0,5", "0,5<RFP<=1", "1<RFP<=1,5",
        "1,5<RFP<=2,5", "2,5<RFP<=3,5", "RFP>3,5", "Não declarada",
    ]
    rendas_presentes = [r for r in ordem_renda if r in df["Renda Familiar"].unique()]

    renda_df = (
        df["Renda Familiar"]
        .value_counts()
        .reindex(rendas_presentes)
        .reset_index()
    )
    renda_df.columns = ["Renda", "Qtd"]

    fig_g22 = px.bar(
        renda_df,
        x="Renda",
        y="Qtd",
        color="Qtd",
        color_continuous_scale="Greens",
        text_auto=True,
        labels={"Qtd": "Matrículas"},
    )
    fig_g22.update_layout(coloraxis_showscale=False, xaxis_tickangle=-20)
    st.plotly_chart(fig_g22, width='stretch')


col_g23, col_g24 = st.columns(2)

with col_g23:
    st.markdown("### 14 — Distribuição por Turno")

    turno_df = df["Turno"].value_counts().reset_index()
    turno_df.columns = ["Turno", "Qtd"]

    fig_g23 = px.pie(
        turno_df,
        names="Turno",
        values="Qtd",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig_g23.update_traces(textposition="outside", textinfo="percent+label")
    st.plotly_chart(fig_g23, width='stretch')

with col_g24:
    st.markdown("### 15 — Composição por Cor/Raça ao Longo dos Anos")

    raca_ano = (
        df.groupby(["Ano", "Cor / Raça"])["Código da Matricula"]
        .count()
        .reset_index(name="Qtd")
    )

    fig_g24 = px.bar(
        raca_ano,
        x="Ano",
        y="Qtd",
        color="Cor / Raça",
        barmode="stack",
        labels={"Qtd": "(%)", "Cor / Raça": "Cor/Raça"},
    )
    fig_g24.update_xaxes(tickmode="linear", dtick=1)
    st.plotly_chart(fig_g24, width='stretch')