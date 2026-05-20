"""
pages/1_Visao_Geral.py — Visão geral dos indicadores.
 
Gráficos desta página:
    1 — Linha:             evolução de TC, TE, TR, TPE e IEf por ano
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
st.set_page_config(page_title="Visão Geral", page_icon=":classical_building:", layout="wide")
st.title(":classical_building: Visão Geral")
st.markdown(
    "#### Panorama geral de Permanência e Êxito do IFRS Campus Restinga."
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

import plotly.graph_objects as go
import numpy as np

st.markdown("---")


# SEÇÃO 2 — EVASÃO

st.markdown("## Evasão")

col_g6, col_g7 = st.columns(2)

with col_g6:
    # Gráfico 6: Motivos de saída por ano
    st.markdown("### 6 — Motivos de Saída por Ano")
    st.markdown(
        "Evolução do volume de cada tipo de saída ao longo da série histórica. "
        "Identifica se houve aumento de abandono em determinados anos."
    )

    situacoes_saida = ["Abandono", "Desligada", "Transf. externa", "Transf. interna"]

    df_saidas = (
        df[df["Situação de Matrícula"].isin(situacoes_saida)]
        .groupby(["Ano", "Situação de Matrícula"])["Código da Matricula"]
        .count()
        .reset_index(name="Qtd")
    )

    fig_g6 = px.bar(
        df_saidas,
        x="Ano", y="Qtd",
        color="Situação de Matrícula",
        barmode="stack",
        color_discrete_map=CORES_SITUACAO,
        labels={"Qtd": "Matrículas", "Situação de Matrícula": "Motivo"},
        text_auto=True,
    )
    fig_g6.update_xaxes(tickmode="linear", dtick=1)
    fig_g6.update_layout(legend=dict(orientation="h", y=-0.3))
    st.plotly_chart(fig_g6, width="stretch")

with col_g7:
    # ── Gráfico 7: Proporção de motivos de evasão por curso (último ano) ─────
    ultimo_ano = int(df_completo["Ano"].max())
    st.markdown(f"### 7 — Motivos de Evasão por Curso ({ultimo_ano})")
    st.markdown(
        f"Proporção de cada motivo de evasão por curso em **{ultimo_ano}**. "
        "Cursos com predominância de 'Abandono' indicam problema de acolhimento; "
        "'Desligada' aponta para dificuldades de desempenho."
    )

    motivos_ev = ["Abandono", "Desligada", "Transf. externa"]

    df_ev_ano = df_completo[
        (df_completo["Ano"] == ultimo_ano)
        & (df_completo["Tipo de Curso"].isin(tipos_selecionados))
        & (df_completo["Nome de Curso"].isin(cursos_selecionados))
        & (df_completo["Situação de Matrícula"].isin(motivos_ev))
    ]

    ev_curso = (
        df_ev_ano
        .groupby(["Nome de Curso", "Situação de Matrícula"])["Código da Matricula"]
        .count()
        .reset_index(name="Qtd")
    )
    tot_ev = ev_curso.groupby("Nome de Curso")["Qtd"].sum().reset_index(name="Total")
    ev_curso = ev_curso.merge(tot_ev, on="Nome de Curso")

    ordem_cursos = tot_ev.sort_values("Total", ascending=False)["Nome de Curso"].tolist()

    fig_g7 = px.bar(
        ev_curso,
        y="Nome de Curso", x="Qtd",
        color="Situação de Matrícula",
        orientation="h",
        barmode="stack",
        color_discrete_map=CORES_SITUACAO,
        text_auto="True",
        labels={"Qtd": "Matrículas", "Nome de Curso": "", "Situação de Matrícula": "Motivo"},
        category_orders={"Nome de Curso": ordem_cursos},
    )
    fig_g7.update_layout(
        legend=dict(orientation="h", y=-0.2),
    )
    st.plotly_chart(fig_g7, width="stretch")

st.markdown("---")


# SEÇÃO 3 — CONCLUSÃO

st.markdown("## Conclusão")

# Prepara df_concluidos (necessário para gráficos 9, 10 e 11)
@st.cache_data
def preparar_concluidos(df_base, tipos, cursos):
    dc = df_base[
        (df_base["Tipo de Curso"].isin(tipos))
        & (df_base["Nome de Curso"].isin(cursos))
        & (df_base["Situação de Matrícula"].isin(["Concluída no prazo", "Concluída com atraso"]))
    ].copy()

    dc["Data de Inicio do Ciclo"] = pd.to_datetime(dc["Data de Inicio do Ciclo"], errors="coerce")
    dc["Mês De Ocorrência da Situação"] = pd.to_datetime(
        dc["Mês De Ocorrência da Situação"], errors="coerce"
    )
    dc["Anos_Conclusao"] = (
        (dc["Mês De Ocorrência da Situação"] - dc["Data de Inicio do Ciclo"])
        .dt.days / 365.25
    ).round(2)

    dc["Ano_Ingresso"] = dc["Data de Inicio do Ciclo"].dt.year
    dc = dc[
        (dc["Anos_Conclusao"] > 0)
        & (dc["Anos_Conclusao"] < 15)
        & (dc["Ano_Ingresso"] >= 2017)
    ]
    return dc


df_conc = preparar_concluidos(df_completo, tipos_selecionados, cursos_selecionados)

# ── Gráfico 8: Conclusões no prazo vs. com atraso por curso ──────────────────
st.markdown("### 8 — Conclusões: No Prazo vs. Com Atraso por Curso")
st.markdown(
    "Volume de concluintes por curso separado em 'Concluída no prazo' e "
    "'Concluída com atraso'. Cursos com alta proporção de conclusão com atraso "
    "confirmam o problema de retenção."
)

conc_prazo = (
    df[df["Categoria da Situação"] == "Concluintes"]
    .groupby(["Nome de Curso", "Situação de Matrícula"])["Código da Matricula"]
    .count()
    .reset_index(name="Qtd")
)

fig_g8 = px.bar(
    conc_prazo,
    x="Nome de Curso", y="Qtd",
    color="Situação de Matrícula",
    barmode="stack",
    color_discrete_map=CORES_SITUACAO,
    labels={"Qtd": "Concluintes", "Nome de Curso": "", "Situação de Matrícula": "Situação"},
    text_auto=True,
)
fig_g8.update_layout(
    xaxis_tickangle=-30,
    legend=dict(orientation="h", y=-0.2),
)
st.plotly_chart(fig_g8, width="stretch")

# Gráficos 9 e 10 lado a lado
col_g9, col_g10 = st.columns(2)

with col_g9:
    # Gráfico 9: Tempo mediano de conclusão por curso 
    st.markdown("### 9 — Tempo Mediano de Conclusão por Curso")
    st.markdown(
        "Mediana de anos entre o ingresso e a conclusão do curso. "
    )

    if len(df_conc) > 0:
        tempo_mediano = (
            df_conc.groupby(["Nome de Curso", "Tipo de Curso"])["Anos_Conclusao"]
            .agg(Mediana="median", Media="mean", N="count")
            .reset_index()
            .round(2)
            .sort_values("Mediana", ascending=True)
        )


        tempo_mediano["Cor"] = "#FF9800"

        fig_g9 = px.bar(
            tempo_mediano,
            x="Mediana", y="Nome de Curso",
            orientation="h",
            color="Cor",
            color_discrete_map={"#4CAF50": "#4CAF50", "#FF9800": "#FF9800"},
            text="Mediana",
            labels={"Mediana": "Mediana (anos)", "Nome de Curso": "", "Cor": ""},
            custom_data=["Media", "N", "Tipo de Curso"],
        )
        fig_g9.update_traces(
            texttemplate="%{x:.2f}",
            textposition="outside",
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Mediana: %{x:.2f} anos<br>"
                "Média: %{customdata[0]:.2f} anos<br>"
                "Concluintes: %{customdata[1]}<br>"
                "Tipo: %{customdata[2]}<extra></extra>"
            ),
        )

        fig_g9.update_layout(
            showlegend=False,
            xaxis=dict(range=[0, tempo_mediano["Mediana"].max() * 1.2]),
        )
        st.plotly_chart(fig_g9, width="stretch")
    else:
        st.info("Sem dados de concluídos para o filtro selecionado.")

with col_g10:
    # Gráfico 10: Boxplot do tempo até conclusão por curso
    st.markdown("### 10 — Distribuição do Tempo até Conclusão por Curso")
    st.markdown(
        "Boxplot complementa o gráfico 9: mostra a dispersão e os outliers. "
        "Um boxplot largo indica alta variabilidade entre os estudantes do mesmo curso."
    )

    if len(df_conc) > 0:
        ordem_box = (
            df_conc.groupby("Nome de Curso")["Anos_Conclusao"]
            .median()
            .sort_values(ascending=False)
            .index.tolist()
        )

        fig_g10 = px.box(
            df_conc,
            x="Nome de Curso", y="Anos_Conclusao",
            color="Nome de Curso",
            color_discrete_map=CORES_CURSO,
            points="outliers",
            labels={"Anos_Conclusao": "Anos após o Ingresso", "Nome de Curso": ""},
            category_orders={"Nome de Curso": ordem_box},
        )
        fig_g10.update_layout(showlegend=False, xaxis_tickangle=-30)
        
        st.plotly_chart(fig_g10, width="stretch")
    else:
        st.info("Sem dados de concluídos para o filtro selecionado.")
