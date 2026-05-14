"""
pages/2_Visao_por_Indicador.py — Visão por indicador.

Gráficos desta página:
    6  — Barras agrupadas:  indicador selecionado por tipo de curso e ano
    7  — Barras horizontais: ranking do indicador por curso (último ano)
    8  — Heatmap:           indicador por Curso × Ano
    9  — Heatmap:           todos os indicadores por curso (último ano)
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from utils import (
    carregar_dados,
    calcular_indicadores,
    CAMINHO_DADOS,
    CORES_INDICADORES,
)

# Configuração da página 
st.set_page_config(page_title="Visão Por Indicador", page_icon=":bar_chart:", layout="wide")
st.title(":bar_chart: Visão Por Indicador")
st.markdown(
    "Análise detalhada de cada indicador acadêmico, filtrada por curso, "
    "tipo de curso e período."
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
    # Rótulos para o seletor de indicador e para os gráficos
    ROTULOS_INDICADORES = {
        "TC":      "Taxa de Conclusão",
        "TE":      "Taxa de Evasão",
        "TR":      "Taxa de Retenção",
        "IEf":     "Índice de Eficiência",
        "TPE":     "Taxa de Permanência e Êxito",
    }
    indicador = st.selectbox(
        "Indicador a analisar (gráficos 6 e 8)",
        options=list(ROTULOS_INDICADORES.keys()),
        format_func=lambda x: ROTULOS_INDICADORES[x],
    )

# Aplica os filtros
df = df_completo[
    (df_completo["Ano"] >= periodo[0])
    & (df_completo["Ano"] <= periodo[1])
    & (df_completo["Tipo de Curso"].isin(tipos_selecionados))
].copy()

# Calcula os indicadores nas granularidades necessárias
ind_ano_curso = calcular_indicadores(df, ["Ano", "Nome de Curso"])
ind_ano_tipo  = calcular_indicadores(df, ["Ano", "Tipo de Curso"])

# Identifica o último ano disponível nos dados filtrados
ultimo_ano = int(ind_ano_curso["Ano"].max())

# Define a escala de cor conforme o indicador selecionado
escala_cor = "Reds" if indicador in ["TE", "TR"] else "Blues"

st.markdown("---")

# 6: Indicador por tipo de curso e ano (barras agrupadas)
st.markdown(f"### 6 - {ROTULOS_INDICADORES[indicador]} por Tipo de Curso e Ano")
st.markdown(
    "Barras agrupadas comparando o desempenho entre tipos de curso a cada ano."
)

fig_g6 = px.bar(
    ind_ano_tipo,
    x="Ano",
    y=indicador,
    color="Tipo de Curso",
    barmode="group",
    text_auto=".1f",
    labels={indicador: f"{ROTULOS_INDICADORES[indicador]} (%)", "Tipo de Curso": "Tipo de Curso"},
)
fig_g6.update_xaxes(tickmode="linear", dtick=1)
st.plotly_chart(fig_g6, width='stretch')

# 7: Ranking do indicador por curso (último ano)
st.markdown(f"### 7 - Ranking de {ROTULOS_INDICADORES[indicador]} por Curso ({ultimo_ano})")
st.markdown(
    f"Barras horizontais ordenadas pelo valor do indicador **no último ano disponível ({ultimo_ano})**. "
)

# Filtra somente os dados do último ano e ordena para a barra maior ficar no topo
ranking = (
    ind_ano_curso[ind_ano_curso["Ano"] == ultimo_ano]
    [["Nome de Curso", indicador]]
    .sort_values(indicador, ascending=True)
)

fig_g7 = px.bar(
    ranking,
    x=indicador,
    y="Nome de Curso",
    orientation="h",
    color=indicador,
    color_continuous_scale=escala_cor,
    text_auto=".1f",
    labels={indicador: f"{ROTULOS_INDICADORES[indicador]} (%)", "Nome de Curso": ""},
)
fig_g7.update_layout(coloraxis_showscale=False)
st.plotly_chart(fig_g7, width='stretch')

# 8: Heatmap do indicador por Curso × Ano
st.markdown(f"### 8 — Mapa de Calor: {ROTULOS_INDICADORES[indicador]} por Curso e Ano")
st.markdown(
    "Cada célula mostra o valor do indicador para um curso em um determinado ano. "
)

# pivot_table() reorganiza o DataFrame: cursos nas linhas, anos nas colunas
pivot = ind_ano_curso.pivot_table(
    index="Nome de Curso",
    columns="Ano",
    values=indicador,
    fill_value=0,
)

fig_g8 = px.imshow(
    pivot,
    text_auto=".1f",
    color_continuous_scale=escala_cor,
    labels={"color": f"{ROTULOS_INDICADORES[indicador]} (%)"},
    aspect="auto",
)
st.plotly_chart(fig_g8, width='stretch')

# 9: Heatmap de todos os indicadores por curso (último ano)
st.markdown(f"### 9 — Todos os Indicadores por Curso ({ultimo_ano})")
st.markdown(
    "Visão consolidada de TC, TE, TR, IEf e TPE para todos os cursos "
    f"no último ano disponível ({ultimo_ano}). "
)

todos_indicadores = ["TC", "TE", "TR", "IEf", "TPE"]

# Seleciona apenas o último ano e usa o nome do curso como índice da tabela
pivot_todos = (
    ind_ano_curso[ind_ano_curso["Ano"] == ultimo_ano]
    .set_index("Nome de Curso")[todos_indicadores]
)

fig_g9 = px.imshow(
    pivot_todos,
    text_auto=".1f",
    color_continuous_scale="Greens",
    labels={"color": "(%)"},
    aspect="auto",
)
st.plotly_chart(fig_g9, width='stretch')