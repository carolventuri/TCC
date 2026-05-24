"""
pages/3_Perfil_dos_Estudantes.py — Perfil sociodemográfico dos estudantes.

Gráficos desta página:
    15 — Pirâmide etária por sexo
    16 — Distribuição por cor/raça
    17 — Distribuição por renda familiar
    18 — Distribuição por turno
    19 a 21 — Heatmaps de evasão por perfil
    22 a 24 — Heatmaps de retenção por perfil
    25 — Visão consolidada: situação × perfil sociodemográfico

"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from utils import (
    carregar_dados,
    gerar_mapa_cores,
    aplicar_layout_light,
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


def taxa_situacao(df_base, col_y, col_x, situacao, ordem_y=None, ordem_x=None, n_minimo=1):
    """
    Calcula taxa (%) de evasão ou retenção por cruzamento sociodemográfico.

    A taxa é calculada como:
        N da situação no cruzamento / total de matrículas distintas no cruzamento * 100

    Células com total menor que n_minimo são convertidas para NaN para evitar interpretações
    instáveis com denominadores muito pequenos.
    """
    if situacao == "Evasão":
        mask = df_base["Categoria da Situação"] == "Evadidos"
    elif situacao == "Retenção":
        mask = df_base["Situação de Matrícula"] == "Retido"
    elif situacao == "Conclusão":
        mask = df_base["Categoria da Situação"] == "Concluintes"
    else:
        raise ValueError("Situação deve ser Evasão, Retenção ou Conclusão.")

    total = (
        df_base.groupby([col_y, col_x])["Código da Matricula"]
        .nunique()
        .reset_index(name="Total")
    )

    contagem = (
        df_base[mask]
        .groupby([col_y, col_x])["Código da Matricula"]
        .nunique()
        .reset_index(name="N")
    )

    merged = total.merge(contagem, on=[col_y, col_x], how="left")
    merged["N"] = merged["N"].fillna(0)
    merged["Taxa (%)"] = (merged["N"] / merged["Total"] * 100).round(1)
    merged.loc[merged["Total"] < n_minimo, "Taxa (%)"] = np.nan

    pivot_taxa = merged.pivot_table(index=col_y, columns=col_x, values="Taxa (%)", aggfunc="mean")
    pivot_total = merged.pivot_table(index=col_y, columns=col_x, values="Total", aggfunc="sum")

    if ordem_y:
        ordem_y_presentes = [c for c in ordem_y if c in pivot_taxa.index]
        pivot_taxa = pivot_taxa.reindex(ordem_y_presentes)
        pivot_total = pivot_total.reindex(ordem_y_presentes)
    if ordem_x:
        ordem_x_presentes = [c for c in ordem_x if c in pivot_taxa.columns]
        pivot_taxa = pivot_taxa[ordem_x_presentes]
        pivot_total = pivot_total[ordem_x_presentes]

    return pivot_taxa, pivot_total


def plot_heatmap_taxa(pivot, titulo_cor, escala, eixo_x, eixo_y):
    fig = px.imshow(
        pivot,
        text_auto=".1f",
        color_continuous_scale=escala,
        labels={"color": titulo_cor},
        aspect="auto",
    )
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#263238"),
        margin=dict(l=20, r=20, t=40, b=40),
        xaxis_title=eixo_x,
        yaxis_title=eixo_y,
        coloraxis_colorbar=dict(title=titulo_cor),
    )
    return fig


# Configuração da página 
st.set_page_config(page_title="Perfil dos Estudantes", page_icon=":mortar_board:", layout="wide")
st.title(":mortar_board: Perfil dos Estudantes")
st.markdown(
    " Perfil sociodemográfico das matrículas do IFRS Campus Restinga, com cruzamentos "
    "de evasão e retenção por faixa etária, renda familiar, sexo, turno e cor/raça."
)

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
        help="Células de heatmap com menos matrículas que este valor ficam em branco.",
    )

# Filtra dados
df = df_completo[
    (df_completo["Ano"] == ano_selecionado)
    & (df_completo["Tipo de Curso"].isin(tipos_selecionados))
    & (df_completo["Nome de Curso"].isin(cursos_selecionados))
].copy()

if df.empty:
    st.warning("Não há dados para os filtros selecionados.")
    st.stop()

st.markdown("---")

faixas_presentes = [f for f in ORDEM_ETARIA if f in df["Faixa Etária"].dropna().unique()]
rendas_presentes = [r for r in ORDEM_RENDA if r in df["Renda Familiar"].dropna().unique()]


# Perfil geral

st.markdown(f"## Perfil Geral dos Estudantes ({ano_selecionado})")

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
    fig_g16 = px.bar(
        raca_df,
        x="Qtd",
        y="Cor / Raça",
        orientation="h",
        color="Qtd",
        color_continuous_scale="YlGnBu",
        text="Qtd",
        labels={"Qtd": "Matrículas", "Cor / Raça": ""},
    )
    fig_g16.update_layout(coloraxis_showscale=False)
    aplicar_layout_light(fig_g16, altura=430)
    st.plotly_chart(fig_g16, width="stretch")

col_12, col_13 = st.columns(2)

with col_12:
    st.markdown("### 17 — Distribuição por Renda Familiar")
    st.markdown("Renda familiar per capita, em faixas de salário mínimo.")

    renda_df = (
        df.groupby("Renda Familiar")["Código da Matricula"]
        .nunique()
        .reindex(rendas_presentes)
        .reset_index(name="Qtd")
    )
    fig_g17 = px.bar(
        renda_df.sort_values("Qtd", ascending=True),
        x="Qtd",
        y="Renda Familiar",
        orientation="h",
        color="Qtd",
        color_continuous_scale="YlGnBu",
        text="Qtd",
        labels={"Qtd": "Matrículas", "Renda Familiar": "Renda"},
    )
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
    cores_turno = gerar_mapa_cores(turno_df["Turno"])
    fig_g18 = px.bar(
        turno_df,
        x="Turno",
        y="Qtd",
        color="Turno",
        color_discrete_map=cores_turno,
        text="Qtd",
        labels={"Qtd": "Matrículas", "Turno": ""},
    )
    fig_g18.update_traces(textposition="outside", cliponaxis=False)
    aplicar_layout_light(fig_g18, altura=430)
    st.plotly_chart(fig_g18, width="stretch")

st.markdown("---")

# Evasão

st.markdown(f"## Taxa de Evasão por Perfil ({ano_selecionado})")
st.markdown(
    "Cada célula mostra a taxa de evasão dentro do cruzamento analisado. "
    f"Células com menos de **{n_minimo}** matrículas ficam em branco para reduzir ruído estatístico."
)

st.markdown("### 19 — Evasão: Faixa Etária × Renda Familiar")
pivot_g19, _ = taxa_situacao(df, "Faixa Etária", "Renda Familiar", "Evasão", ORDEM_ETARIA, ORDEM_RENDA, n_minimo)
fig_g19 = plot_heatmap_taxa(pivot_g19, "Evasão (%)", "OrRd", "Renda Familiar", "Faixa Etária")
st.plotly_chart(fig_g19, width="stretch")

col_15, col_16 = st.columns(2)

with col_15:
    st.markdown("### 20 — Evasão: Sexo × Turno")
    pivot_g20, _ = taxa_situacao(df, "Sexo", "Turno", "Evasão", n_minimo=n_minimo)
    fig_g20 = plot_heatmap_taxa(pivot_g20, "Evasão (%)", "OrRd", "Turno", "Sexo")
    st.plotly_chart(fig_g20, width="stretch")

with col_16:
    st.markdown("### 21 — Evasão: Cor/Raça × Renda Familiar")
    pivot_g21, _ = taxa_situacao(df, "Cor / Raça", "Renda Familiar", "Evasão", ordem_x=ORDEM_RENDA, n_minimo=n_minimo)
    fig_g21 = plot_heatmap_taxa(pivot_g21, "Evasão (%)", "OrRd", "Renda Familiar", "Cor/Raça")
    st.plotly_chart(fig_g21, width="stretch")

st.markdown("---")

# Retenção

st.markdown(f"## Taxa de Retenção por Perfil ({ano_selecionado})")
st.markdown(
    "A retenção considera matrículas classificadas como retidas, isto é, ativas após "
    "o prazo previsto de conclusão."
)

st.markdown("### 22 — Retenção: Faixa Etária × Renda Familiar")
pivot_g22, _ = taxa_situacao(df, "Faixa Etária", "Renda Familiar", "Retenção", ORDEM_ETARIA, ORDEM_RENDA, n_minimo)
fig_g22 = plot_heatmap_taxa(pivot_g22, "Retenção (%)", "YlOrBr", "Renda Familiar", "Faixa Etária")
st.plotly_chart(fig_g22, width="stretch")

col_18, col_19 = st.columns(2)

with col_18:
    st.markdown("### 23 — Retenção: Sexo × Turno")
    pivot_g23, _ = taxa_situacao(df, "Sexo", "Turno", "Retenção", n_minimo=n_minimo)
    fig_g23 = plot_heatmap_taxa(pivot_g23, "Retenção (%)", "YlOrBr", "Turno", "Sexo")
    st.plotly_chart(fig_g23, width="stretch")

with col_19:
    st.markdown("### 24 — Retenção: Cor/Raça × Renda Familiar")
    pivot_g24, _ = taxa_situacao(df, "Cor / Raça", "Renda Familiar", "Retenção", ordem_x=ORDEM_RENDA, n_minimo=n_minimo)
    fig_g24 = plot_heatmap_taxa(pivot_g24, "Retenção (%)", "YlOrBr", "Renda Familiar", "Cor/Raça")
    st.plotly_chart(fig_g24, width="stretch")

st.markdown("---")

# Situação × Perfil Sociodemográfico]

st.markdown(f"## Situação × Perfil Sociodemográfico ({ano_selecionado})")
st.markdown(
    "Resumo visual das taxas de evasão, retenção e conclusão dentro de cada categoria "
    "sociodemográfica."
)

situacoes = {
    "Evasão": df["Categoria da Situação"] == "Evadidos",
    "Retenção": df["Situação de Matrícula"] == "Retido",
    "Conclusão": df["Categoria da Situação"] == "Concluintes",
}

variaveis = ["Sexo", "Turno", "Renda Familiar", "Faixa Etária", "Cor / Raça"]
linhas = []
for variavel in variaveis:
    total_por_cat = df.groupby(variavel)["Código da Matricula"].nunique()
    for categoria, total in total_por_cat.items():
        if pd.isna(categoria) or total < n_minimo:
            continue
        linha = {"Perfil": f"{variavel}: {categoria}", "Total": total}
        for nome_situacao, mask in situacoes.items():
            n = df[mask & (df[variavel] == categoria)]["Código da Matricula"].nunique()
            linha[nome_situacao] = round(n / total * 100, 1) if total else np.nan
        linhas.append(linha)

consolidado = pd.DataFrame(linhas)
if not consolidado.empty:
    matriz = consolidado.set_index("Perfil")[["Evasão", "Retenção", "Conclusão"]].T
    fig_25 = px.imshow(
        matriz,
        text_auto=".1f",
        color_continuous_scale="Purples",
        labels={"color": "Taxa (%)"},
        aspect="auto",
    )
    fig_25.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#263238"),
        margin=dict(l=20, r=20, t=40, b=120),
        xaxis_title="Categoria sociodemográfica",
        yaxis_title="Situação",
    )
    fig_25.update_xaxes(tickangle=-35)
    st.plotly_chart(fig_25, width="stretch")
else:
    st.info("Não há categorias com tamanho mínimo suficiente para exibir a visão consolidada.")

with st.expander("Como interpretar os heatmaps de perfil"):
    st.markdown(
        """
        - A taxa de cada célula é calculada com base no total de matrículas distintas daquele cruzamento.
        - Grupos muito pequenos podem produzir percentuais altos por acaso; por isso foi incluído o filtro de **N mínimo por célula**.
        """
    )
