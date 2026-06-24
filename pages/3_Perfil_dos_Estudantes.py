"""
pages/3_Perfil_dos_Estudantes.py — Perfil sociodemográfico dos estudantes.

Gráficos desta página:
    15 — Pirâmide etária por sexo
    16 — Distribuição por cor/raça
    17 — Distribuição por renda familiar
    18 — Distribuição por turno
    19 a 21 — Heatmaps de evasão por perfil
    22 a 24 — Heatmaps de retenção por perfil
    25 — Visão consolidada: situação × categoria sociodemográfica

"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from utils import (
    calcular_indicadores,
    escala_indicador,
    carregar_dados,
    gerar_mapa_cores,
    aplicar_layout_light,
    ROTULOS_INDICADORES,
    CAMINHO_DADOS,
    
)

ORDEM_ETARIA = [
    "Menor de 14 anos", "15 a 19 anos", "20 a 24 anos",
    "25 a 29 anos", "30 a 34 anos", "35 a 39 anos",
    "40 a 44 anos", "45 a 49 anos", "50 a 54 anos",
    "55 a 59 anos", "Maior de 60 anos",
]

ORDEM_RENDA = [
    "0<RFP<=0,5", "0,5<RFP<=1", "1<RFP<=1,5",
    "1,5<RFP<=2,5", "2,5<RFP<=3,5", "RFP>3,5", "Não declarada",
]

CORES_SEXO = {
    "F": "#AD1457",  # magenta
    "M": "#00838F",  # teal
}

PALETA_CATEGORIAS = [
    "#2E7D32", "#6A1B9A", "#EF6C00", "#00838F", "#AD1457",
    "#827717", "#5D4037", "#455A64", "#F9A825",
]


def pivot_indicador_perfil(
    df_base,
    col_y,
    col_x,
    indicador,
    ordem_y=None,
    ordem_x=None,
    n_minimo=1,
):
    ind = calcular_indicadores(df_base, [col_y, col_x])

    ind.loc[ind["matr_atendidas"] < n_minimo, indicador] = pd.NA

    pivot = ind.pivot_table(
        index=col_y,
        columns=col_x,
        values=indicador,
        aggfunc="mean",
    )

    if ordem_y:
        ordem_y_presentes = [c for c in ordem_y if c in pivot.index]
        pivot = pivot.reindex(ordem_y_presentes)

    if ordem_x:
        ordem_x_presentes = [c for c in ordem_x if c in pivot.columns]
        pivot = pivot[ordem_x_presentes]

    return pivot


def plot_heatmap_perfil(pivot, indicador, eixo_x, eixo_y):
    fig = px.imshow(
        pivot,
        text_auto=".1f",
        color_continuous_scale=escala_indicador(indicador),
        labels={"color": f"{ROTULOS_INDICADORES[indicador]} (%)"},
        aspect="auto",
    )
    aplicar_layout_light(fig)
    fig.update_layout(
        xaxis_title=eixo_x,
        yaxis_title=eixo_y,
        coloraxis_colorbar=dict(title=f"{ROTULOS_INDICADORES[indicador]} (%)"),
    )
    return fig



# Configuração da página 
st.set_page_config(page_title="Perfil dos Estudantes", page_icon=":mortar_board:", layout="wide")
st.title(":mortar_board: Perfil dos Estudantes")
st.markdown(
    " #### Perfil sociodemográfico das matrículas do IFRS Campus Restinga, com cruzamentos "
    "de evasão e retenção por faixa etária, renda familiar, sexo, turno e cor/raça."
)

with st.expander("ℹ️ Como funciona o N mínimo por célula"):
    st.write(
        """
        Os heatmaps desta página apresentam indicadores calculados para diferentes grupos de estudantes.
    Quando um grupo possui poucas matrículas, os percentuais podem ser pouco representativos e sofrer
    grandes variações. Por isso, é possível definir um **N mínimo por célula**. Sempre que um cruzamento possuir menos
    matrículas do que o valor informado, a célula será exibida em branco, evitando interpretações
    baseadas em grupos muito pequenos.
        """
    )


st.markdown("---")

# Carga dos dados
df_completo = carregar_dados(CAMINHO_DADOS)

# Filtros
st.markdown("### Filtros")
col_f1, col_f2, col_f3, col_f4 = st.columns([1, 1.4, 1.8, 1.2])

with col_f1:
    anos_disponiveis = sorted(df_completo["Ano"].dropna().unique())
    ultimo_ano = int(max(anos_disponiveis))
    ano_selecionado = st.selectbox(
        "Ano de análise",
        options=anos_disponiveis,
        index=len(anos_disponiveis) - 1,
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
    n_minimo = st.number_input(
        "N mínimo por célula",
        min_value=1,
        max_value=30,
        value=5,
        step=1,
        help="""
        Define o número mínimo de matrículas necessário para que uma célula
        seja exibida nos heatmaps. Grupos menores são ocultados.
        """,
    )

# Filtra dados
df = df_completo[
    (df_completo["Ano"] == ano_selecionado)
    & (df_completo["Tipo de Curso"].isin(tipos_selecionados))
    & (df_completo["Nome de Curso"].isin(cursos_selecionados))
].copy()

st.markdown("---")

faixas_presentes = [f for f in ORDEM_ETARIA if f in df["Faixa Etária"].dropna().unique()]
rendas_presentes = [r for r in ORDEM_RENDA if r in df["Renda Familiar"].dropna().unique()]


# SEÇÃO - PERFIL GERAL

st.markdown(
    f"""
    <h2 style="color:#2f9e41; text-decoration: underline;">
        Perfil Geral dos Estudantes ({ano_selecionado})
    </h2>
    """,
    unsafe_allow_html=True,
)


col_10, col_11 = st.columns(2)

with col_10:
    st.markdown("### 15 — Pirâmide Etária por Sexo")
    st.markdown("Mostra a distribuição das matrículas por faixa etária e sexo.")

    piramide_df = (
        df.groupby(["Faixa Etária", "Sexo"])["Código da Matricula"]
        .nunique()
        .reset_index(name="Qtd")
    )
    piramide_df["Faixa Etária"] = pd.Categorical(
        piramide_df["Faixa Etária"], categories=faixas_presentes, ordered=True
    )
    piramide_df = piramide_df.sort_values("Faixa Etária")

    fig_g15 = go.Figure()
    sexos = sorted(piramide_df["Sexo"].dropna().unique())
    for sexo in sexos:
        subset = piramide_df[piramide_df["Sexo"] == sexo]
        multiplicador = -1 if sexo == sexos[0] else 1
        fig_g15.add_trace(go.Bar(
            name=sexo,
            y=subset["Faixa Etária"].astype(str),
            x=subset["Qtd"] * multiplicador,
            orientation="h",
            marker_color=CORES_SEXO.get(sexo, "#757575"),
            text=subset["Qtd"].astype(str),
            textposition="inside",
            hovertemplate="Sexo: %{fullData.name}<br>Faixa: %{y}<br>Matrículas: %{text}<extra></extra>",
        ))

    valor_max = int(piramide_df["Qtd"].max()) if len(piramide_df) else 10
    passo = max(1, valor_max // 5)
    ticks = list(range(-valor_max, valor_max + passo, passo))
    fig_g15.update_layout(
        barmode="relative",
        xaxis=dict(tickvals=ticks, ticktext=[str(abs(v)) for v in ticks], title="Matrículas"),
        yaxis=dict(title=""),
    )
    aplicar_layout_light(fig_g15, altura=430)
    st.plotly_chart(fig_g15, width="stretch")

with col_11:
    st.markdown("### 16 — Distribuição por Cor/Raça")
    raca_df = (
        df.groupby("Cor / Raça")["Código da Matricula"]
        .nunique()
        .reset_index(name="Qtd")
        .sort_values("Qtd", ascending=True)
    )
    raca_df["Percentual"] = raca_df["Qtd"] / raca_df["Qtd"].sum() * 100
    raca_df["Texto"] = raca_df.apply(
        lambda linha: f"{int(linha['Qtd'])} ({linha['Percentual']:.1f}%)",
        axis=1,
    )

    fig_g16 = px.bar(
        raca_df,
        x="Qtd",
        y="Cor / Raça",
        orientation="h",
        color="Qtd",
        color_continuous_scale="YlGnBu",
        text="Texto",
        labels={"Qtd": "Matrículas",},
    )
    fig_g16.update_traces(textposition="outside", cliponaxis=False)
    fig_g16.update_xaxes(range=[0, raca_df["Qtd"].max() * 1.25])
    fig_g16.update_layout(coloraxis_showscale=False)
    aplicar_layout_light(fig_g16, altura=430)
    st.plotly_chart(fig_g16, width="stretch")

col_12, col_13 = st.columns(2)

with col_12:
    st.markdown("### 17 — Distribuição por Renda Familiar")
    st.markdown("Renda familiar per capita (RFP), em faixas de salário mínimo.")

    renda_df = (
        df.groupby("Renda Familiar")["Código da Matricula"]
        .nunique()
        .reindex(rendas_presentes)
        .reset_index(name="Qtd")
    )
    renda_df["Percentual"] = renda_df["Qtd"] / renda_df["Qtd"].sum() * 100
    renda_df["Texto"] = renda_df.apply(
        lambda linha: f"{int(linha['Qtd'])} ({linha['Percentual']:.1f}%)",
        axis=1,
    )

    fig_g17 = px.bar(
        renda_df.sort_values("Qtd", ascending=True),
        x="Qtd",
        y="Renda Familiar",
        orientation="h",
        color="Qtd",
        color_continuous_scale="YlGnBu",
        text="Texto",
        labels={"Qtd": "Matrículas", "Renda Familiar": "Renda"},
    )
    fig_g17.update_traces(textposition="outside", cliponaxis=False)
    fig_g17.update_xaxes(range=[0, renda_df["Qtd"].max() * 1.25])
    fig_g17.update_layout(coloraxis_showscale=False)
    aplicar_layout_light(fig_g17, altura=430)
    st.plotly_chart(fig_g17, width="stretch")

with col_13:
    st.markdown("### 18 — Distribuição por Turno")
    turno_df = (
        df.groupby("Turno")["Código da Matricula"]
        .nunique()
        .reset_index(name="Qtd")
        .sort_values("Qtd", ascending=False)
    )
    turno_df["Percentual"] = turno_df["Qtd"] / turno_df["Qtd"].sum() * 100
    turno_df["Texto"] = turno_df.apply(
        lambda linha: f"{int(linha['Qtd'])} ({linha['Percentual']:.1f}%)",
        axis=1,
    )

    cores_turno = gerar_mapa_cores(turno_df["Turno"])
    fig_g18 = px.bar(
        turno_df,
        x="Turno",
        y="Qtd",
        color="Turno",
        color_discrete_map=cores_turno,
        text="Texto",
        labels={"Qtd": "Matrículas",},
    )
    fig_g18.update_traces(textposition="outside", cliponaxis=False)
    fig_g18.update_layout(showlegend=False)
    aplicar_layout_light(fig_g18, altura=430)
    st.plotly_chart(fig_g18, width="stretch")

st.markdown("---")

# SEÇÃO - TAXA DE EVASÃO POR PERFIL

st.markdown(
    f"""
    <h2 style="color:#2f9e41; text-decoration: underline;">
        Taxa de Evasão por Perfil ({ano_selecionado})
    </h2>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    "Cada célula mostra a taxa de evasão dentro do cruzamento analisado. "
)

st.markdown("### 19 — Evasão: Faixa Etária × Renda Familiar")
pivot_g19 = pivot_indicador_perfil(df, "Faixa Etária", "Renda Familiar", "TE", ORDEM_ETARIA, ORDEM_RENDA, n_minimo)
fig_g19 = plot_heatmap_perfil(pivot_g19, "TE", "Renda Familiar", "Faixa Etária")
st.plotly_chart(fig_g19, width="stretch")

col_15, col_16 = st.columns(2)

with col_15:
    st.markdown("### 20 — Evasão: Sexo × Turno")
    pivot_g20 = pivot_indicador_perfil(df, "Sexo", "Turno", "TE", n_minimo=n_minimo)
    fig_g20 = plot_heatmap_perfil(pivot_g20, "TE", "Turno", "Sexo")
    st.plotly_chart(fig_g20, width="stretch")

with col_16:
    st.markdown("### 21 — Evasão: Cor/Raça × Renda Familiar")
    pivot_g21 = pivot_indicador_perfil(df, "Cor / Raça", "Renda Familiar", "TE", ordem_x=ORDEM_RENDA, n_minimo=n_minimo)
    fig_g21 = plot_heatmap_perfil(pivot_g21, "TE", "Renda Familiar", "Cor/Raça")
    st.plotly_chart(fig_g21, width="stretch")

st.markdown("---")

# SEÇÃO - TAXA DE RETENÇÃO POR PERFIL

st.markdown(
    f"""
    <h2 style="color:#2f9e41; text-decoration: underline;">
        Taxa de Retenção por Perfil ({ano_selecionado})
    </h2>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    "Cada célula mostra a taxa de retenção dentro do cruzamento analisado."
)

st.markdown("### 22 — Retenção: Faixa Etária × Renda Familiar")
pivot_g22 = pivot_indicador_perfil(df, "Faixa Etária", "Renda Familiar", "TR", ORDEM_ETARIA, ORDEM_RENDA, n_minimo)
fig_g22 = plot_heatmap_perfil(pivot_g22, "TR", "Renda Familiar", "Faixa Etária")
st.plotly_chart(fig_g22, width="stretch")

col_18, col_19 = st.columns(2)

with col_18:
    st.markdown("### 23 — Retenção: Sexo × Turno")
    pivot_g23 = pivot_indicador_perfil(df, "Sexo", "Turno", "TR", n_minimo=n_minimo)
    fig_g23 = plot_heatmap_perfil(pivot_g23, "TR", "Turno", "Sexo")
    st.plotly_chart(fig_g23, width="stretch")

with col_19:
    st.markdown("### 24 — Retenção: Cor/Raça × Renda Familiar")
    pivot_g24 = pivot_indicador_perfil(df, "Cor / Raça", "Renda Familiar", "TR", ordem_x=ORDEM_RENDA, n_minimo=n_minimo)
    fig_g24 = plot_heatmap_perfil(pivot_g24, "TR", "Renda Familiar", "Cor/Raça")
    st.plotly_chart(fig_g24, width="stretch")

st.markdown("---")

# SEÇÃO - SITUAÇÃO X CATEGORIA SOCIODEMOGRÁFICA

st.markdown(
    f"""
    <h2 style="color:#2f9e41; text-decoration: underline;">
        Consolidado das Taxas de Evasão, Retenção e Conclusão por todas as Categorias Sociodemográficas ({ano_selecionado})
    </h2>
    """,
    unsafe_allow_html=True,
)
st.markdown(f"### 25 — Situação × Categoria Sociodemográfica")
st.markdown(
    "Resumo visual das taxas de evasão, retenção e conclusão dentro de cada categoria "
    "sociodemográfica."
)

variaveis = ["Sexo", "Turno", "Renda Familiar", "Faixa Etária", "Cor / Raça"]
indicadores_situacao = {"Evasão": "TE", "Retenção": "TR", "Conclusão": "TC"}

linhas = []
for variavel in variaveis:
    ind_variavel = calcular_indicadores(df, [variavel])
    ind_variavel = ind_variavel[ind_variavel["matr_atendidas"] >= n_minimo]

    for _, linha_ind in ind_variavel.iterrows():
        categoria = linha_ind[variavel]

        if pd.isna(categoria):
            continue

        linha = {"Perfil": f"{variavel}: {categoria}"}
        for rotulo, indicador_coluna in indicadores_situacao.items():
            linha[rotulo] = round(linha_ind[indicador_coluna], 1)

        linhas.append(linha)

consolidado = pd.DataFrame(linhas)

if not consolidado.empty:
    matriz = consolidado.set_index("Perfil")[list(indicadores_situacao.keys())].T

    fig_25 = px.imshow(
        matriz,
        text_auto=".1f",
        color_continuous_scale="Purples",
        labels={"color": "Taxa (%)"},
        aspect="auto",
    )

    colunas = list(matriz.columns)
    separadores = []
    variavel_atual = colunas[0].split(":")[0]

    for i, col in enumerate(colunas[1:], start=1):
        variavel_nova = col.split(":")[0]
        if variavel_nova != variavel_atual:
            separadores.append(i)
            variavel_atual = variavel_nova

    shapes = [
        dict(
            type="line",
            xref="x",
            yref="paper",
            x0=sep - 0.5,
            x1=sep - 0.5,
            y0=0,
            y1=1,
            line=dict(color="#263238", width=3),
        )
        for sep in separadores
    ]

    aplicar_layout_light(fig_25)

    fig_25.update_layout(
        margin=dict(l=20, r=20, t=40, b=120),
        xaxis_title="Categoria sociodemográfica",
        yaxis_title="Situação",
        shapes=shapes,
    )
    fig_25.update_xaxes(tickangle=-35)
    st.plotly_chart(fig_25, width="stretch")
else:
    st.info("Não há categorias com tamanho mínimo suficiente para exibir a visão consolidada.")
