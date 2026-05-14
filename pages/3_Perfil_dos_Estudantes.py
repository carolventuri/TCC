"""
pages/3_Perfil_dos_Estudantes.py — Perfil sociodemográfico dos estudantes.
 
Todos os gráficos usam o último ano disponível nos dados.
 
  Seção 1 — Perfil geral (gráficos 10–13):
    10 — Pirâmide etária:    faixa etária × sexo
    11 — Barras horizontais: distribuição por cor/raça
    12 — Barras horizontais: distribuição por renda familiar
    13 — Pizza (donut):      distribuição por turno
 
  Seção 2 — Heatmaps de evasão (gráficos 14–16):
    14 — Heatmap: Taxa de Evasão — Faixa Etária × Renda Familiar
    15 — Heatmap: Taxa de Evasão — Sexo × Turno
    16 — Heatmap: Taxa de Evasão — Cor/Raça × Renda Familiar
 
  Seção 3 — Heatmaps de retenção (gráficos 17–19):
    17 — Heatmap: Taxa de Retenção — Faixa Etária × Renda Familiar
    18 — Heatmap: Taxa de Retenção — Sexo × Turno
    19 — Heatmap: Taxa de Retenção — Cor/Raça × Renda Familiar
 
  Seção 4 — Visão consolidada (gráfico 20):
    20 — Heatmap: Situação × Perfil Sociodemográfico (todas as variáveis × eixo X)
"""
 
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
 
from utils import (
    carregar_dados,
    CAMINHO_DADOS,
)
 
# Configuração da página
st.set_page_config(
    page_title="Perfil dos Estudantes",
    page_icon=":mortar_board:",
    layout="wide",
)
st.title(":mortar_board: Perfil dos Estudantes")
st.markdown(
    "Distribuição sociodemográfica dos estudantes matriculados no IFRS Campus Restinga. "
    "Todos os gráficos utilizam os dados do **último ano disponível**."
)
 
# Carga dos dados
df_completo = carregar_dados(CAMINHO_DADOS)
 
# Filtros desta página
st.markdown("### Filtros")
 
col_f1, col_f2 = st.columns(2)
 
with col_f1:
    tipos_disponiveis = sorted(df_completo["Tipo de Curso"].unique())
    tipos_selecionados = st.multiselect(
        "Tipo de Curso",
        options=tipos_disponiveis,
        default=tipos_disponiveis,
    )
 
with col_f2:
    cursos_disponiveis = sorted(df_completo["Nome de Curso"].unique())
    cursos_selecionados = st.multiselect(
        "Curso",
        options=cursos_disponiveis,
        default=cursos_disponiveis,
    )
 
# Último ano e DataFrame filtrado
ultimo_ano = int(df_completo["Ano"].max())
 
df = df_completo[
    (df_completo["Ano"] == ultimo_ano)
    & (df_completo["Tipo de Curso"].isin(tipos_selecionados))
    & (df_completo["Nome de Curso"].isin(cursos_selecionados))
].copy()
 
st.caption(
    f"Dados referentes ao ano de **{ultimo_ano}** · "
    f"{len(df):,} matrículas".replace(",", ".")
)
st.markdown("---")
 
# ── Listas de ordem para categorias ──────────────────────────────────────────
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
 
faixas_presentes = [f for f in ORDEM_ETARIA if f in df["Faixa Etária"].unique()]
rendas_presentes = [r for r in ORDEM_RENDA  if r in df["Renda Familiar"].unique()]
 
CORES_SEXO = {"M": "#2196F3", "F": "#E91E63"}
 
 
# ── Função auxiliar: heatmap cruzado de dois atributos sociodemográficos ──────
def heatmap_cruzado(df, col_y, col_x, situacao, ordem_y=None, ordem_x=None):
    """
    Calcula a taxa de uma situação (Evasão ou Retenção) para cada combinação
    de dois atributos sociodemográficos, retornando um DataFrame pivotado
    pronto para px.imshow.
 
    Parâmetros
    ----------
    df        : DataFrame do último ano já filtrado
    col_y     : variável para o eixo Y (ex: "Faixa Etária")
    col_x     : variável para o eixo X (ex: "Renda Familiar")
    situacao  : "Evadidos" ou "Retido"
    ordem_y   : lista para ordenar as linhas do heatmap (eixo Y)
    ordem_x   : lista para ordenar as colunas do heatmap (eixo X)
 
    Retorna
    -------
    DataFrame pivotado: índice = col_y, colunas = col_x, valores = taxa (%)
    """
    # Seleciona apenas os registros da situação desejada
    if situacao == "Evadidos":
        mask = df["Categoria da Situação"] == "Evadidos"
    else:
        mask = df["Situação de Matrícula"] == "Retido"
 
    # Contagem da situação por combinação col_y × col_x
    contagem = (
        df[mask]
        .groupby([col_y, col_x])["Código da Matricula"]
        .count()
        .reset_index(name="N")
    )
 
    # Total de matrículas por combinação col_y × col_x (denominador)
    total = (
        df.groupby([col_y, col_x])["Código da Matricula"]
        .count()
        .reset_index(name="Total")
    )
 
    merged = total.merge(contagem, on=[col_y, col_x], how="left").fillna(0)
    merged["Taxa (%)"] = (merged["N"] / merged["Total"] * 100).round(1)
 
    # Pivota para formato de heatmap
    pivot = merged.pivot_table(
        index=col_y,
        columns=col_x,
        values="Taxa (%)",
        fill_value=np.nan,
    )
 
    # Reordena linhas e colunas conforme as ordens fornecidas
    if ordem_y:
        cats_y = [c for c in ordem_y if c in pivot.index]
        pivot = pivot.reindex(cats_y)
    if ordem_x:
        cats_x = [c for c in ordem_x if c in pivot.columns]
        pivot = pivot[cats_x]
 
    return pivot
 
 

# SEÇÃO 1 — PERFIL GERAL NO ÚLTIMO ANO

st.markdown(f"## Seção 1 — Perfil Geral dos Estudantes ({ultimo_ano})")
 
col_10, col_11 = st.columns(2)
 
with col_10:
    st.markdown("### 10 — Pirâmide Etária por Sexo")
    st.markdown(
        "Faixa etária no eixo vertical. Cada lado representa um sexo. "
        "Os números dentro das barras indicam o total de matrículas."
    )
 
    piramide_df = (
        df.groupby(["Faixa Etária", "Sexo"])["Código da Matricula"]
        .count()
        .reset_index(name="Qtd")
    )
    piramide_df["Faixa Etária"] = pd.Categorical(
        piramide_df["Faixa Etária"], categories=faixas_presentes, ordered=True
    )
    piramide_df = piramide_df.sort_values("Faixa Etária")
 
    sexos = piramide_df["Sexo"].dropna().unique().tolist()
    fig_10 = go.Figure()
 
    for i, sexo in enumerate(sexos):
        subset = piramide_df[piramide_df["Sexo"] == sexo]
        multiplicador = -1 if i == 0 else 1
        valores = subset["Qtd"] * multiplicador
        fig_10.add_trace(go.Bar(
            name=sexo,
            y=subset["Faixa Etária"].astype(str),
            x=valores,
            orientation="h",
            marker_color=CORES_SEXO.get(sexo, "#9E9E9E"),
            text=subset["Qtd"].astype(str),
            textposition="inside",
        ))
 
    valor_max = int(piramide_df["Qtd"].max()) if len(piramide_df) > 0 else 10
    passo = max(1, valor_max // 5)
    ticks = list(range(-valor_max, valor_max + passo, passo))
    fig_10.update_layout(
        barmode="relative",
        xaxis=dict(
            tickvals=ticks,
            ticktext=[str(abs(v)) for v in ticks],
            title="Matrículas",
        ),
        yaxis=dict(title=""),
        legend=dict(orientation="h", y=-0.18),
    )
    st.plotly_chart(fig_10, width="stretch")
 
with col_11:
    st.markdown("### 11 — Distribuição por Cor/Raça")
 
    raca_df = df["Cor / Raça"].value_counts().reset_index()
    raca_df.columns = ["Cor/Raça", "Qtd"]
    fig_11 = px.bar(
        raca_df.sort_values("Qtd", ascending=True),
        x="Qtd", y="Cor/Raça", orientation="h",
        color="Qtd", color_continuous_scale="Purples",
        text_auto=True, labels={"Qtd": "Matrículas"},
    )
    fig_11.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig_11, width="stretch")
 
col_12, col_13 = st.columns(2)
 
with col_12:
    st.markdown("### 12 — Distribuição por Renda Familiar")
    st.markdown("Renda per capita em salários mínimos.")
 
    rendas_ultimo = [r for r in rendas_presentes if r in df["Renda Familiar"].unique()]
    renda_df = (
        df["Renda Familiar"].value_counts()
        .reindex(rendas_ultimo).reset_index()
    )
    renda_df.columns = ["Renda", "Qtd"]
    fig_12 = px.bar(
        renda_df.sort_values("Qtd", ascending=True),
        x="Qtd", y="Renda", orientation="h",
        color="Qtd", color_continuous_scale="Greens",
        text_auto=True,
        labels={"Qtd": "Matrículas", "Renda": "Renda (SM per capita)"},
    )
    fig_12.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig_12, width="stretch")
 
with col_13:
    st.markdown("### 13 — Distribuição por Turno")
 
    turno_df = df["Turno"].value_counts().reset_index()
    turno_df.columns = ["Turno", "Qtd"]
    fig_13 = px.pie(
        turno_df, names="Turno", values="Qtd", hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig_13.update_traces(textposition="outside", textinfo="percent+label")
    st.plotly_chart(fig_13, width="stretch")
 
st.markdown("---")
 
# SEÇÃO 2 — HEATMAPS DE EVASÃO

st.markdown(f"## Seção 2 — Taxa de Evasão por Perfil ({ultimo_ano})")
st.markdown(
    "Cada célula mostra a **taxa de evasão (%)** — abandono, desligamento ou "
    "transferência externa — dentro daquele cruzamento de perfil. "
    "Células em branco indicam combinações sem matrículas suficientes. "
    "Cores mais escuras = maior evasão."
)
 
# ── Gráfico 14 — Evasão: Faixa Etária × Renda Familiar ───────────────────────
st.markdown("### 14 — Evasão: Faixa Etária × Renda Familiar")
st.markdown(
    "Permite identificar quais combinações de faixa etária e renda "
    "concentram as maiores taxas de evasão."
)
 
pivot_14 = heatmap_cruzado(
    df, "Faixa Etária", "Renda Familiar", "Evadidos",
    ordem_y=ORDEM_ETARIA, ordem_x=ORDEM_RENDA,
)
fig_14 = px.imshow(
    pivot_14,
    text_auto=".1f",
    color_continuous_scale="Reds",
    labels={"color": "Evasão (%)"},
    aspect="auto",
)
fig_14.update_layout(
    xaxis_title="Renda Familiar (SM per capita)",
    yaxis_title="Faixa Etária",
    coloraxis_colorbar=dict(title="Evasão (%)"),
)
st.plotly_chart(fig_14, width="stretch")
 
# Gráficos 15 e 16 lado a lado
col_15, col_16 = st.columns(2)
 
with col_15:
    st.markdown("### 15 — Evasão: Sexo × Turno")
 
    pivot_15 = heatmap_cruzado(df, "Sexo", "Turno", "Evadidos")
    fig_15 = px.imshow(
        pivot_15,
        text_auto=".1f",
        color_continuous_scale="Reds",
        labels={"color": "Evasão (%)"},
        aspect="auto",
    )
    fig_15.update_layout(
        xaxis_title="Turno",
        yaxis_title="Sexo",
        coloraxis_colorbar=dict(title="Evasão (%)"),
    )
    st.plotly_chart(fig_15, width="stretch")
 
with col_16:
    st.markdown("### 16 — Evasão: Cor/Raça × Renda Familiar")
 
    pivot_16 = heatmap_cruzado(
        df, "Cor / Raça", "Renda Familiar", "Evadidos",
        ordem_x=ORDEM_RENDA,
    )
    fig_16 = px.imshow(
        pivot_16,
        text_auto=".1f",
        color_continuous_scale="Reds",
        labels={"color": "Evasão (%)"},
        aspect="auto",
    )
    fig_16.update_layout(
        xaxis_title="Renda Familiar (SM per capita)",
        yaxis_title="Cor/Raça",
        coloraxis_colorbar=dict(title="Evasão (%)"),
    )
    st.plotly_chart(fig_16, width="stretch")
 
st.markdown("---")
 

# SEÇÃO 3 — HEATMAPS DE RETENÇÃO

st.markdown(f"## Seção 3 — Taxa de Retenção por Perfil ({ultimo_ano})")
st.markdown(
    "Cada célula mostra a **taxa de retenção (%)** — estudantes com matrícula ativa "
    "além do prazo previsto de conclusão — dentro daquele cruzamento de perfil. "
    "Cores mais escuras = maior retenção."
)
 
# Gráfico 17 — Retenção: Faixa Etária × Renda Familiar
st.markdown("### 17 — Retenção: Faixa Etária × Renda Familiar")
 
pivot_17 = heatmap_cruzado(
    df, "Faixa Etária", "Renda Familiar", "Retido",
    ordem_y=ORDEM_ETARIA, ordem_x=ORDEM_RENDA,
)
fig_17 = px.imshow(
    pivot_17,
    text_auto=".1f",
    color_continuous_scale="Oranges",
    labels={"color": "Retenção (%)"},
    aspect="auto",
)
fig_17.update_layout(
    xaxis_title="Renda Familiar (SM per capita)",
    yaxis_title="Faixa Etária",
    coloraxis_colorbar=dict(title="Retenção (%)"),
)
st.plotly_chart(fig_17, width="stretch")
 
# Gráficos 18 e 19 lado a lado
col_18, col_19 = st.columns(2)
 
with col_18:
    st.markdown("### 18 — Retenção: Sexo × Turno")
 
    pivot_18 = heatmap_cruzado(df, "Sexo", "Turno", "Retido")
    fig_18 = px.imshow(
        pivot_18,
        text_auto=".1f",
        color_continuous_scale="Oranges",
        labels={"color": "Retenção (%)"},
        aspect="auto",
    )
    fig_18.update_layout(
        xaxis_title="Turno",
        yaxis_title="Sexo",
        coloraxis_colorbar=dict(title="Retenção (%)"),
    )
    st.plotly_chart(fig_18, width="stretch")
 
with col_19:
    st.markdown("### 19 — Retenção: Cor/Raça × Renda Familiar")
 
    pivot_19 = heatmap_cruzado(
        df, "Cor / Raça", "Renda Familiar", "Retido",
        ordem_x=ORDEM_RENDA,
    )
    fig_19 = px.imshow(
        pivot_19,
        text_auto=".1f",
        color_continuous_scale="Oranges",
        labels={"color": "Retenção (%)"},
        aspect="auto",
    )
    fig_19.update_layout(
        xaxis_title="Renda Familiar (SM per capita)",
        yaxis_title="Cor/Raça",
        coloraxis_colorbar=dict(title="Retenção (%)"),
    )
    st.plotly_chart(fig_19, width="stretch")
 
st.markdown("---")
 
# SEÇÃO 4 — VISÃO CONSOLIDADA: SITUAÇÃO × PERFIL SOCIODEMOGRÁFICO

st.markdown(f"## Seção 4 — Situação × Perfil Sociodemográfico ({ultimo_ano})")
st.markdown(
    "Heatmap consolidado. O **eixo X** reúne todas as categorias sociodemográficas "
    "(Sexo, Turno, Renda e Faixa Etária) separadas por linhas tracejadas. "
    "O **eixo Y** mostra as três situações: Evasão, Retenção e Conclusão. "
    "Cada célula mostra o **percentual daquela situação dentro daquela categoria**."
)
 
# Calcula a taxa de cada situação dentro de cada categoria 
def taxa_situacao_por_categoria(df, coluna, situacoes):
    """
    Para cada categoria da coluna, calcula o percentual de cada situação
    em relação ao total de matrículas daquela categoria.
 
    Retorna um dicionário {situacao: {categoria: taxa%}}.
    """
    total_por_cat = (
        df.groupby(coluna)["Código da Matricula"].count()
    )
 
    resultado = {}
    for label, mask in situacoes.items():
        contagem = (
            df[mask].groupby(coluna)["Código da Matricula"].count()
        )
        taxa = (contagem / total_por_cat * 100).fillna(0).round(1)
        resultado[label] = taxa
 
    return resultado
 
 
# Define as três situações e suas máscaras de filtro
situacoes = {
    "Evasão":    df["Categoria da Situação"] == "Evadidos",
    "Retenção":  df["Situação de Matrícula"] == "Retido",
    "Conclusão": df["Categoria da Situação"] == "Concluintes",
}
 
# Variáveis e suas ordens para o eixo X
variaveis_x = [
    ("Sexo",           None),
    ("Turno",          None),
    ("Renda Familiar", ORDEM_RENDA),
    ("Faixa Etária",   ORDEM_ETARIA),
]
 
# Monta a matriz do heatmap consolidado
# Cada variável contribui com suas categorias como colunas do eixo X
colunas_x   = []   # rótulos das colunas (categorias)
separadores = []   # posições onde há troca de variável (para linhas divisórias)
matriz      = {s: [] for s in situacoes}
 
for nome_var, ordem in variaveis_x:
    taxas = taxa_situacao_por_categoria(df, nome_var, situacoes)
 
    # Define a ordem das categorias desta variável
    if ordem:
        cats = [c for c in ordem if c in df[nome_var].unique()]
    else:
        cats = sorted(df[nome_var].dropna().unique().tolist())
 
    separadores.append(len(colunas_x))   # posição do início desta variável
 
    for cat in cats:
        # Rótulo da coluna: "NomeVar: Categoria"
        colunas_x.append(f"{nome_var}: {cat}")
        for sit in situacoes:
            valor = taxas[sit].get(cat, 0)
            matriz[sit].append(valor)
 
# Transforma em DataFrame (linhas = situações, colunas = categorias)
df_heatmap = pd.DataFrame(matriz, index=colunas_x).T
 
fig_20 = px.imshow(
    df_heatmap,
    text_auto=".1f",
    color_continuous_scale="Blues",
    labels={"color": "(%)"},
    aspect="auto",
    height=300,
)
fig_20.update_layout(
    xaxis=dict(tickangle=-45, title=""),
    yaxis=dict(title=""),
    coloraxis_colorbar=dict(title="(%)"),
)
 
# Adiciona linhas tracejadas verticais entre as variáveis
for pos in separadores[1:]:   # pula a posição 0 (borda esquerda)
    fig_20.add_vline(
        x=pos - 0.5,
        line_dash="dash",
        line_color="gray",
        line_width=1.5,
    )
 
# Adiciona anotações indicando o grupo de cada variável
for i, (nome_var, _) in enumerate(variaveis_x):
    inicio = separadores[i]
    fim    = separadores[i + 1] if i + 1 < len(separadores) else len(colunas_x)
    centro = (inicio + fim - 1) / 2
    fig_20.add_annotation(
        x=centro,
        y=1.12,
        xref="x",
        yref="paper",
        text=f"<b>{nome_var}</b>",
        showarrow=False,
        font=dict(size=11),
    )
 
st.plotly_chart(fig_20, width="stretch")
 