"""
pages/2_Visao_por_Indicador.py — Visão por indicador.

Gráficos desta página:
    11 — Barras agrupadas: indicador selecionado por tipo de curso e ano
    12 — Barras horizontais: Ranking do indicador por curso (último ano)
    13 — Heatmap: Indicador por Curso × Ano
    14 — Heatmap: Todos os indicadores por Curso (último ano)

"""

import streamlit as st
import plotly.express as px
import pandas as pd

from utils import (
    carregar_dados,
    calcular_indicadores,
    gerar_mapa_cores,
    aplicar_layout_light,
    escala_indicador,
    CAMINHO_DADOS,
    ROTULOS_INDICADORES,
    PALETA_TIPO_CURSO,
)

# Configuração da página 
st.set_page_config(page_title="Visão por Indicador", page_icon=":bar_chart:", layout="wide")
st.title(":bar_chart: Visão por Indicador")
st.markdown(
    "Exibição detalhada dos indicadores acadêmicos por período, tipo de curso e curso. "
    "Permitie observar quais cursos e tipos de curso mais contribuem para os resultados do campus."
)

# Carga dos dados
df_completo = carregar_dados(CAMINHO_DADOS)

# Filtros
st.markdown("### Filtros")
col_f1, col_f2, col_f3, col_f4 = st.columns([1.2, 1.4, 1.8, 1.4])

with col_f1:
    anos_disponiveis = sorted(df_completo["Ano"].dropna().unique())
    periodo = st.slider(
        "Período de análise",
        min_value=int(min(anos_disponiveis)),
        max_value=int(max(anos_disponiveis)),
        value=(int(min(anos_disponiveis)), int(max(anos_disponiveis))),
    )

with col_f2:
    tipos_disponiveis = sorted(df_completo["Tipo de Curso"].dropna().unique())
    tipos_selecionados = st.multiselect(
        "Tipo de Curso",
        options=tipos_disponiveis,
        default=tipos_disponiveis,
    )

with col_f3:
    cursos_disponiveis = sorted(df_completo["Nome de Curso"].dropna().unique())
    cursos_selecionados = st.multiselect(
        "Curso",
        options=cursos_disponiveis,
        default=cursos_disponiveis,
    )

with col_f4:
    indicador = st.selectbox(
        "Indicador",
        options=list(ROTULOS_INDICADORES.keys()),
        format_func=lambda x: ROTULOS_INDICADORES[x],
    )

# Aplica os filtros
df = df_completo[
    (df_completo["Ano"] >= periodo[0])
    & (df_completo["Ano"] <= periodo[1])
    & (df_completo["Tipo de Curso"].isin(tipos_selecionados))
    & (df_completo["Nome de Curso"].isin(cursos_selecionados))
].copy()

# Indicadores nas granularidades necessárias
ind_ano_curso = calcular_indicadores(df, ["Ano", "Nome de Curso"])
ind_ano_tipo = calcular_indicadores(df, ["Ano", "Tipo de Curso"])


ultimo_ano = int(ind_ano_curso["Ano"].max())
cores_tipo = gerar_mapa_cores(ind_ano_tipo["Tipo de Curso"])


st.markdown("---")

# 11 — Indicador por tipo de curso e ano
st.markdown(f"### 11 — {ROTULOS_INDICADORES[indicador]} por Tipo de Curso e Ano")
st.markdown(
    "Compara a evolução do indicador entre os tipos de curso."
)

fig_g11 = px.bar(
    ind_ano_tipo,
    x="Ano",
    y=indicador,
    color="Tipo de Curso",
    barmode="group",
    color_discrete_map=cores_tipo,
    text_auto=".1f",
    labels={indicador: f"{ROTULOS_INDICADORES[indicador]} (%)", "Tipo de Curso": "Tipo de Curso"},
)
fig_g11.update_xaxes(tickmode="linear", dtick=1)
fig_g11.update_traces(textposition="outside", cliponaxis=False)
aplicar_layout_light(fig_g11)
st.plotly_chart(fig_g11, width="stretch")


# 12 — Ranking por curso no último ano filtrado
st.markdown(f"### 12 — Ranking de {ROTULOS_INDICADORES[indicador]} por Curso ({ultimo_ano})")
st.markdown(
    "Ordena os cursos pelo valor do indicador no último ano disponível dentro dos filtros. "
)

ranking = (
    ind_ano_curso[ind_ano_curso["Ano"] == ultimo_ano][["Nome de Curso", indicador, "matr_atendidas"]]
    .sort_values(indicador, ascending=True)
)

fig_g12 = px.bar(
    ranking,
    x=indicador,
    y="Nome de Curso",
    orientation="h",
    color=indicador,
    color_continuous_scale=escala_indicador(indicador),
    text=indicador,
    labels={
        indicador: f"{ROTULOS_INDICADORES[indicador]} (%)",
        "Nome de Curso": "",
    },
    custom_data=["matr_atendidas"],
)
fig_g12.update_traces(
    texttemplate="%{x:.1f}%",
    textposition="outside",
    cliponaxis=False,
    hovertemplate=(
        "<b>%{y}</b><br>"
        f"{ROTULOS_INDICADORES[indicador]}: %{{x:.1f}}%<br>"
        "Matrículas atendidas: %{customdata[0]}<extra></extra>"
    ),
)
fig_g12.update_layout(coloraxis_showscale=False)
aplicar_layout_light(fig_g12, altura=max(430, 32 * len(ranking) + 140))
st.plotly_chart(fig_g12, width="stretch")


# 13 — Heatmap Curso × Ano
st.markdown(f"### 13 —{ROTULOS_INDICADORES[indicador]} por Curso e Ano")
st.markdown(
    "Cada célula mostra o valor do indicador para um curso em um ano. Células vazias "
    "indicam ausência de dado para aquela combinação."
)

pivot = ind_ano_curso.pivot_table(
    index="Nome de Curso",
    columns="Ano",
    values=indicador,
    aggfunc="mean",
)

fig_g13 = px.imshow(
    pivot,
    text_auto=".1f",
    color_continuous_scale=escala_indicador(indicador),
    labels=dict(x='Ano', y='', color=f'{ROTULOS_INDICADORES[indicador]} (%)'),
    aspect="auto",
)

aplicar_layout_light(fig_g13)
fig_g13.update_xaxes(tickmode='linear')
st.plotly_chart(fig_g13, width="stretch")


# 14 — Todos os indicadores por curso no último ano filtrado
st.markdown(f"### 14 — Todos os Indicadores por Curso ({ultimo_ano})")
st.markdown(
    "Apresenta uma visão consolidada dos principais indicadores no último ano filtrado. "
)

indicadores = ['TC', 'TE', 'TR', 'IEf', 'TPE']
base_ultimo = ind_ano_curso[ind_ano_curso['Ano'] == ultimo_ano].copy()
heat_ind = base_ultimo.set_index('Nome de Curso')[indicadores].sort_index()
heat_ind = heat_ind.rename(columns=ROTULOS_INDICADORES)

fig_g14 = px.imshow(
    heat_ind, text_auto='.1f', aspect='auto', color_continuous_scale='Purples',
    labels=dict(x='Indicador', y='', color='Valor (%)'),
)

aplicar_layout_light(fig_g14)
fig_g14.update_xaxes(tickmode='linear')
st.plotly_chart(fig_g14, width="stretch")
