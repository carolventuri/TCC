"""
pages/1_Visao_Geral.py — Visão geral do campus.
 
Gráficos desta página:
    1 — Linha:             evolução de TC, TE, TR, TPE, IEf e TEFAcad por ano
    2 — Linha:             evolução de MREG e MRET por ano
    3 — Barras empilhadas: matrículas atendidas por ano e categoria
    4 — Linha:             Ingressantes e Concluintes por ano
    5 — Barras empilhadas: matrículas por curso e ano
"""
 
import streamlit as st
import plotly.express as px
import pandas as pd
 
# Importa as funções e paletas do módulo compartilhado
from utils import (
    carregar_dados,
    calcular_indicadores,
    CAMINHO_DADOS,
    CORES_INDICADORES,
    CORES_SITUACAO,
    CORES_CURSO,
    CORES_CATEGORIA,
)
 
# Configuração da página 
st.set_page_config(page_title="Visão Geral do Campus", page_icon=":classical_building:", layout="wide")
st.title(":classical_building: Visão Geral do Campus")
st.markdown(
    "#### Panorama geral dos indicadores acadêmicos de Permanência e Êxito do IFRS Campus Restinga ao longo dos anos."
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
 
# Calcula os indicadores agrupados por Ano (campus inteiro)
ind_ano = calcular_indicadores(df, ["Ano"])
 
  
# 1: Evolução dos indicadores percentuais por ano (linhas)
st.markdown("### 1 — Evolução dos Indicadores por Ano")
st.markdown(
    "Mostra como os indicadores de permanência e êxito evoluíram ao longo do tempo. "
)

mapeamento_indicadores = {
    "TC": "Taxa de Conclusão",
    "TE": "Taxa de Evasão",
    "TR": "Taxa de Retenção",
    "TPE": "Taxa de Permanência e Êxito",
    "IEf": "Índice de Eficiência",
}

# melt() transforma o DataFrame de formato largo (uma coluna por indicador) para formato longo 
ind_longo = ind_ano.melt(
    id_vars="Ano",
    value_vars=["TC", "TE", "TR", "TPE", "IEf"],
    var_name="Indicador",
    value_name="Valor (%)",
)

fig_g1 = px.line(
    ind_longo,
    x="Ano",
    y="Valor (%)",
    color="Indicador",
    markers=True,
    color_discrete_map=CORES_INDICADORES,
    labels={"Indicador": "", "Valor (%)": "(%)"},
)
# troca apenas o nome exibido na legenda
for trace in fig_g1.data:
    trace.name = mapeamento_indicadores.get(trace.name, trace.name)
    trace.hovertemplate = trace.hovertemplate.replace(
        trace.legendgroup,
        mapeamento_indicadores.get(trace.legendgroup, trace.legendgroup)
    )

fig_g1.update_xaxes(tickmode="linear", dtick=1)
fig_g1.update_layout(hovermode="x unified", legend=dict(orientation="h", y=-0.2))
st.plotly_chart(fig_g1, width='stretch')
 
# 2: Evolução de MREG e MRET por ano (linhas)
st.markdown("### 2 — Matrículas Ativas Regulares (MREG) e Retidas (MRET) por Ano")
st.markdown(
    "MREG = Em fluxo + Ingressantes (dentro do prazo). "
    "MRET = Retidos (além do prazo previsto). "
)
 
matr_ativas_longo = ind_ano.melt(
    id_vars="Ano",
    value_vars=["MREG", "MRET"],
    var_name="Tipo",
    value_name="Matrículas",
)
 
fig_g2 = px.line(
    matr_ativas_longo,
    x="Ano",
    y="Matrículas",
    color="Tipo",
    markers=True,
    color_discrete_map={"MREG": "#4CAF50", "MRET": "#FF9800"},
    labels={"Tipo": ""},
)
fig_g2.update_xaxes(tickmode="linear", dtick=1)
fig_g2.update_layout(hovermode="x unified", legend=dict(orientation="h", y=-0.2))
st.plotly_chart(fig_g2, width='stretch')
 
#  Gráficos 3 e 4 lado a lado 
col_g3, col_g4 = st.columns(2)
 
with col_g3:
    st.markdown("### 3 — Matrículas por Ano e Categoria")
    st.markdown(
        "Volume de matrículas por ano, separadas em Concluintes, Em curso e Evadidos."
    )
 
    mat_cat = (
        df.groupby(["Ano", "Categoria da Situação"])["Código da Matricula"]
        .count()
        .reset_index(name="Qtd")
    )
 
    fig_g3 = px.bar(
        mat_cat,
        x="Ano",
        y="Qtd",
        color="Categoria da Situação",
        barmode="stack",
        color_discrete_map=CORES_CATEGORIA,
        labels={"Qtd": "Matrículas", "Categoria da Situação": ""},
        text_auto=True,
    )
    
    fig_g3.update_xaxes(tickmode="linear", dtick=1)
    
    fig_g3.update_layout(
    legend=dict(
        orientation="h",   # horizontal
        yanchor="top",
        y=-0.2,            # posição abaixo do gráfico
        xanchor="center",
        x=0.5
    )
)    
    st.plotly_chart(fig_g3, width='stretch')
 
with col_g4:
    st.markdown("### 4 — Ingressantes e Concluintes por Ano")
    st.markdown(
        "Compara quantos alunos entram (Ingressantes) vs. quantos saem formados "
        "(Concluintes) a cada ano"
    )
 
    fluxo_longo = ind_ano.melt(
        id_vars="Ano",
        value_vars=["ingressantes", "concluintes"],
        var_name="Tipo",
        value_name="Quantidade",
    )
 
    # Renomeia os rótulos para ficarem mais legíveis na legenda
    fluxo_longo["Tipo"] = fluxo_longo["Tipo"].map({
        "ingressantes": "Ingressantes",
        "concluintes":  "Concluintes",
    })
 
    fig_g4 = px.line(
        fluxo_longo,
        x="Ano",
        y="Quantidade",
        color="Tipo",
        markers=True,
        color_discrete_map={
            "Ingressantes": "#7E57C2",
            "Concluintes":  "#2196F3",
        },
        labels={"Tipo": "", "Quantidade": "Matrículas"}, 
    )
    fig_g4.update_xaxes(tickmode="linear", dtick=1)
    fig_g4.update_layout(hovermode="x unified", legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig_g4, width='stretch')
 
 
# 5: Matrículas por curso e ano (barras empilhadas) 
st.markdown("### 5 — Matrículas Atendidas por Curso e Ano")
st.markdown(
    "Mostra a evolução do volume de matrículas em cada curso ao longo do tempo."
)
 
mat_curso_ano = (
    df.groupby(["Ano", "Nome de Curso"])["Código da Matricula"]
    .count()
    .reset_index(name="Qtd")
)
 
fig_g5 = px.bar(
    mat_curso_ano,
    x="Ano",
    y="Qtd",
    color="Nome de Curso",
    color_discrete_map=CORES_CURSO,
    barmode="stack",
    labels={"Qtd": "Matrículas", "Nome de Curso": "Curso"},
)
fig_g5.update_xaxes(tickmode="linear", dtick=1)
st.plotly_chart(fig_g5, width='stretch')