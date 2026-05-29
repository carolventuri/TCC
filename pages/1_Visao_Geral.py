"""
pages/1_Visao_Geral.py — Visão geral dos indicadores.
 
Gráficos desta página:
    1 — Linha:             evolução de TC, TE, TR, TPE e IEf por ano
    2 — Linha:             evolução de MREG e MRET por ano
    3 — Barras empilhadas: matrículas atendidas por ano e categoria
    4 — Linha:             Ingressantes e Concluintes por ano
    5 — Barras empilhadas: matrículas por curso e ano
    6 - Barras empilhadas : motivos de saída por ano
    7 - Barras horizontais: Proporção de motivos de evasão por curso (último ano)
    8 - Barras empilhadas: Conclusões no Prazo e Conclusões com Atraso por Curso
    9 - Barras horizontais: Tempo Mediano de Conclusão por Curso
    10 - Boxplot : Distribuição do Tempo até Conclusão por Curso
"""
 
import streamlit as st
import plotly.express as px
import pandas as pd
 
# Importa as funções e paletas do módulo compartilhado
from utils import (
    carregar_dados,
    calcular_indicadores,
    aplicar_layout_light,
    gerar_mapa_cores,
    CAMINHO_DADOS,
    CORES_INDICADORES,
    CORES_SITUACAO,
    CORES_CURSO,
    CORES_CATEGORIA,
    PALETA_QUALITATIVA_LIGHT,
    CORES_SITUACAO_LIGHT,
    CORES_CONCLUSAO_LIGHT,
    COR_TEMPO_MEDIANO,
    CORES_MATRICULAS_ATIVAS_LIGHT,
    CORES_FLUXO_LIGHT,
)

 
# Configuração da página 
st.set_page_config(page_title="Visão Geral", page_icon=":classical_building:", layout="wide")
st.title(":classical_building: Visão Geral")
st.markdown(
    "#### Panorama geral de Permanência e Êxito dos Estudantes do IFRS Campus Restinga."
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

# Mapa de cores dos cursos recalculado após os filtros.
CORES_CURSO_LIGHT = gerar_mapa_cores(df["Nome de Curso"])
 
# Calcula os indicadores agrupados por Ano (campus inteiro)
ind_ano = calcular_indicadores(df, ["Ano"])


st.markdown("---")
# SEÇÃO — INDICADORES E MATRÍCULAS
st.markdown("## Indicadores e Matrículas")
  
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
fig_g1.update_layout(hovermode="x unified")
aplicar_layout_light(fig_g1, legenda_y=-0.2)
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
    color_discrete_map=CORES_MATRICULAS_ATIVAS_LIGHT,
    labels={"Tipo": ""},
)
fig_g2.update_xaxes(tickmode="linear", dtick=1)
fig_g2.update_layout(hovermode="x unified")
aplicar_layout_light(fig_g2, legenda_y=-0.2)
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
    aplicar_layout_light(fig_g3, legenda_y=-0.2)
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
        color_discrete_map=CORES_FLUXO_LIGHT,
        labels={"Tipo": "", "Quantidade": "Matrículas"}, 
    )
    fig_g4.update_xaxes(tickmode="linear", dtick=1)
    fig_g4.update_layout(hovermode="x unified")
    aplicar_layout_light(fig_g4, legenda_y=-0.2)
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
    color_discrete_map=CORES_CURSO_LIGHT,
    barmode="stack",
    labels={"Qtd": "Matrículas", "Nome de Curso": "Curso"},
)
fig_g5.update_xaxes(tickmode="linear", dtick=1)
aplicar_layout_light(fig_g5, legenda_y=-0.25)
st.plotly_chart(fig_g5, width='stretch')

import plotly.graph_objects as go
import numpy as np

st.markdown("---")


# SEÇÃO — EVASÃO

st.markdown("## Evasão")

col_g6, col_g7 = st.columns(2)

with col_g6:
    # Gráfico 6: Motivos de saída por ano
    st.markdown("### 6 — Motivos de Saída por Ano")
    st.markdown(
        "Evolução do volume de cada tipo de saída ao longo da série histórica. "
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
        color_discrete_map=CORES_SITUACAO_LIGHT,
        labels={"Qtd": "Matrículas", "Situação de Matrícula": "Motivo"},
        text_auto=True,
    )
    fig_g6.update_xaxes(tickmode="linear", dtick=1)
    aplicar_layout_light(fig_g6, legenda_y=-0.3)
    st.plotly_chart(fig_g6, width="stretch")

with col_g7:
    # Gráfico 7: Proporção de motivos de evasão por curso (último ano)
    ultimo_ano = int(df_completo["Ano"].max())
    st.markdown(f"### 7 — Motivos de Evasão por Curso ({ultimo_ano})")
    st.markdown(
        f"Volume de cada motivo de evasão por curso em **{ultimo_ano}**. "
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
        color_discrete_map=CORES_SITUACAO_LIGHT,
        text_auto=True,
        labels={"Qtd": "Matrículas", "Nome de Curso": "", "Situação de Matrícula": "Motivo"},
        category_orders={"Nome de Curso": ordem_cursos},
    )
    aplicar_layout_light(fig_g7, legenda_y=-0.2)
    st.plotly_chart(fig_g7, width="stretch")

st.markdown("---")


# SEÇÃO — CONCLUSÃO

st.markdown("## Conclusão")

# Prepara df_concluidos (necessário para gráficos 9 e 10)
def preparar_concluidos(df_base):
    """
    Prepara uma base única de concluintes para os gráficos de tempo de conclusão.

    Regras adotadas:
    1. Usa a base já filtrada na página (período, tipo de curso e curso).
    2. Considera apenas situações finais de conclusão:
       - Concluída no prazo
       - Concluída com atraso
    3. Remove duplicidades por matrícula, preservando a última ocorrência registrada.
       Isso evita contar duas vezes o mesmo estudante se houver linhas repetidas.
    4. Calcula o tempo de conclusão em anos:
       (Mês de Ocorrência da Situação - Data de Início do Ciclo) / 365,25.
    """
    dc = df_base[
        df_base["Situação de Matrícula"].isin(["Concluída no prazo", "Concluída com atraso"])
    ].copy()

    dc["Data de Inicio do Ciclo"] = pd.to_datetime(
        dc["Data de Inicio do Ciclo"], errors="coerce"
    )
    dc["Mês De Ocorrência da Situação"] = pd.to_datetime(
        dc["Mês De Ocorrência da Situação"], errors="coerce"
    )

    dc = dc.dropna(subset=[
        "Código da Matricula",
        "Nome de Curso",
        "Tipo de Curso",
        "Data de Inicio do Ciclo",
        "Mês De Ocorrência da Situação",
    ])

    # Se houver mais de uma linha para a mesma matrícula, fica a ocorrência final.
    dc = dc.sort_values("Mês De Ocorrência da Situação")
    dc = dc.drop_duplicates(subset=["Código da Matricula"], keep="last")

    dc["Anos_Conclusao"] = (
        (dc["Mês De Ocorrência da Situação"] - dc["Data de Inicio do Ciclo"])
        .dt.days / 365.25
    )

    dc["Ano_Ingresso"] = dc["Data de Inicio do Ciclo"].dt.year
    dc["Ano_Conclusao"] = dc["Mês De Ocorrência da Situação"].dt.year

    dc = dc[
        (dc["Anos_Conclusao"] > 0)
        & (dc["Anos_Conclusao"] < 15)
    ].copy()

    dc["Anos_Conclusao"] = dc["Anos_Conclusao"].round(2)
    return dc


df_conc = preparar_concluidos(df)

# Gráfico 8: Conclusões no Prazo e Conclusões com Atraso por Curso
st.markdown("### 8 — Conclusões no Prazo e Conclusões com Atraso por Curso")
st.markdown(
    "Volume de concluintes por curso separado em 'Concluída no prazo' e "
    "'Concluída com atraso'."
)

# Usa contagem distinta de matrículas para evitar duplicidades.
conc_prazo = (
    df[
        df["Situação de Matrícula"].isin(["Concluída no prazo", "Concluída com atraso"])
    ]
    .groupby(["Nome de Curso", "Situação de Matrícula"], as_index=False)["Código da Matricula"]
    .nunique()
    .rename(columns={"Código da Matricula": "Qtd"})
)

ordem_conclusao = (
    conc_prazo.groupby("Nome de Curso")["Qtd"]
    .sum()
    .sort_values(ascending=False)
    .index.tolist()
)

fig_g8 = px.bar(
    conc_prazo,
    x="Nome de Curso", y="Qtd",
    color="Situação de Matrícula",
    barmode="stack",
    color_discrete_map=CORES_CONCLUSAO_LIGHT,
    labels={"Qtd": "Concluintes", "Nome de Curso": "", "Situação de Matrícula": "Situação"},
    text_auto=True,
    category_orders={"Nome de Curso": ordem_conclusao},
)
fig_g8.update_layout(xaxis_tickangle=-30)
aplicar_layout_light(fig_g8, legenda_y=-0.5)
st.plotly_chart(fig_g8, width="stretch")

# Gráficos 9 e 10 lado a lado
col_g9, col_g10 = st.columns(2)

with col_g9:
    # Gráfico 9: Tempo mediano de conclusão por curso 
    st.markdown("### 9 — Tempo Mediano de Conclusão por Curso")
    st.markdown(
        "Mediana de anos entre o ingresso e a conclusão do curso. "
    )

    with st.expander("Como o tempo mediano de conclusão foi calculado"):
        st.markdown(
            """
            **Base usada:** base filtrada da página: período, tipo de curso e curso.  
            **Quem entra no cálculo:** apenas matrículas com situação **Concluída no prazo** ou **Concluída com atraso**.  
            **Unidade de contagem:** matrícula distinta (`Código da Matricula`), para evitar duplicidade caso a mesma matrícula apareça mais de uma vez.  
            **Tempo individual de conclusão:** diferença entre `Mês De Ocorrência da Situação` e `Data de Inicio do Ciclo`, dividida por **365,25**.  
            **Mediana por curso:** depois de calcular o tempo individual de cada concluinte, a mediana é calculada por curso. Assim, se um curso tiver 5 concluintes, o valor exibido é o tempo central; se tiver 4, é a média dos dois tempos centrais.  
            **Filtros de consistência:** foram removidos registros sem datas válidas, tempos negativos/zero e tempos iguais ou superiores a 15 anos.
            """
        )

    if len(df_conc) > 0:
        tempo_mediano = (
            df_conc.groupby(["Nome de Curso", "Tipo de Curso"])["Anos_Conclusao"]
            .agg(Mediana="median", Media="mean", N="count")
            .reset_index()
            .round(2)
            .sort_values("Mediana", ascending=True)
        )


        fig_g9 = px.bar(
            tempo_mediano,
            x="Mediana", y="Nome de Curso",
            orientation="h",
            text="Mediana",
            labels={"Mediana": "Mediana (anos)", "Nome de Curso": ""},
            custom_data=["Media", "N", "Tipo de Curso"],
        )
        fig_g9.update_traces(marker_color=COR_TEMPO_MEDIANO)
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
        aplicar_layout_light(fig_g9)
        st.plotly_chart(fig_g9, width="stretch")
    else:
        st.info("Sem dados de concluídos para o filtro selecionado.")

with col_g10:
    # Gráfico 10: Boxplot do tempo até conclusão por curso
    st.markdown("### 10 — Distribuição do Tempo até Conclusão por Curso")
    st.markdown(
        "Boxplot complementa o gráfico 9: mostra a dispersão e os outliers. "
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
            color_discrete_map=CORES_CURSO_LIGHT,
            points="outliers",
            labels={"Anos_Conclusao": "Anos após o Ingresso", "Nome de Curso": ""},
            category_orders={"Nome de Curso": ordem_box},
        )
        fig_g10.update_layout(showlegend=False, xaxis_tickangle=-30)
        aplicar_layout_light(fig_g10)
        
        st.plotly_chart(fig_g10, width="stretch")
    else:
        st.info("Sem dados de concluídos para o filtro selecionado.")
