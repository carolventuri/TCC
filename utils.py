"""
utils.py — Funções compartilhadas entre todas as páginas do dashboard.
Contém:
  - carregar_dados()    
  - calcular_indicadores()
"""
 
import pandas as pd
import numpy as np
import streamlit as st
 
 
CAMINHO_DADOS = "dados_tratados/restinga_dados_tratados.parquet"
 

# PALETAS DE CORES
# Centralizadas aqui para que todas as páginas usem as mesmas cores.

# Uma cor para cada indicador
CORES_INDICADORES = {
    "TC":       "#4E79A7",  # azul
    "TE":       "#E15759",  # vermelho
    "TR":       "#F28E2B",  # laranja
    "IEf":      "#59A14F",  # verde
    "TPE":      "#B07AA1",  # lilás
}


 
# Uma cor para cada situação de matrícula
CORES_SITUACAO = {
    "Ingressante":          "#A5D6A7",   # verde claro
    "Em fluxo":             "#4CAF50",   # verde
    "Retido":               "#FF9800",   # laranja
    "Concluída no prazo":   "#2196F3",   # azul
    "Concluída com atraso": "#64B5F6",   # azul claro
    "Abandono":             "#F44336",   # vermelho
    "Desligada":            "#E91E63",   # rosa
    "Transf. externa":      "#9E9E9E",   # cinza médio
    "Transf. interna":      "#BDBDBD",   # cinza claro
    "Integralizada":        "#00BCD4",   # ciano
 
}
 
# Uma cor para cada categoria de situação
CORES_CATEGORIA = {
    "Em curso":    "#4CAF50",   # verde
    "Concluintes": "#2196F3",   # azul
    "Evadidos":    "#F44336",   # vermelho
}

CORES_CURSO = {
    "Análise e Desenvolvimento de Sistemas": "#5E60CE",  # azul violeta
    "Eletrônica Industrial":                "#E63946",  # vermelho
    "Gestão Desportiva e de Lazer":         "#2A9D8F",  # verde água
    "Letras - Português e Espanhol":        "#9B5DE5",  # roxo
    "Técnico em Comércio":                  "#F4A261",  # laranja
    "Técnico em Eletrônica":                "#00B4D8",  # ciano
    "Técnico em Guia de Turismo":           "#EF476F",  # rosa
    "Técnico em Informática":               "#8AC926",  # verde limão
    "Técnico em Lazer":                     "#C77DFF",  # lilás
    "Processos Gerenciais":                 "#FFBE0B",  # amarelo
    "Técnico em Agroecologia":              "#4361EE",  # azul
}

 
# CARGA DOS DADOS
# O decorator @st.cache_data faz o Streamlit guardar o resultado em memória
@st.cache_data
def carregar_dados(caminho: str = CAMINHO_DADOS) -> pd.DataFrame:
   
    df = pd.read_parquet(caminho)
 
    return df
 
# CÁLCULO DOS INDICADORES
def calcular_indicadores(df, agrupamento):

    df_indicadores = (
        df.groupby(agrupamento)
        .agg(
            ingressantes    = ("Situação de Matrícula", lambda x: (x == "Ingressante").sum()),
            em_curso        = ("Categoria da Situação",  lambda x: (x == "Em curso").sum()),
            concluintes     = ("Categoria da Situação",  lambda x: (x == "Concluintes").sum()),
            evadidos        = ("Categoria da Situação",  lambda x: (x == "Evadidos").sum()),
            matr_atendidas  = ("Código da Matricula",    "count"),
            conc_no_prazo   = ("Situação de Matrícula",  lambda x: (x == "Concluída no prazo").sum()),
            conc_com_atraso = ("Situação de Matrícula",  lambda x: (x == "Concluída com atraso").sum()),
            abandono        = ("Situação de Matrícula",  lambda x: (x == "Abandono").sum()),
            desligados      = ("Situação de Matrícula",  lambda x: (x == "Desligada").sum()),
            transf_ext      = ("Situação de Matrícula",  lambda x: (x == "Transf. externa").sum()),
            transf_int      = ("Situação de Matrícula",  lambda x: (x == "Transf. interna").sum()),
            integralizadas  = ("Situação de Matrícula",  lambda x: (x == "Integralizada").sum()),
            conc_previstos  = ("Concluinte_Previsto",    "sum"),
            MREG            = ("Situação de Matrícula",
                               lambda x: ((x == "Em fluxo") | (x == "Ingressante")).sum()),
            MRET            = ("Situação de Matrícula",  lambda x: (x == "Retido").sum()),
        )
        .reset_index()
    )

    # Evita divisão por zero substituindo 0 por NaN antes de dividir
    ma = df_indicadores["matr_atendidas"].replace(0, np.nan)

    # TC — Taxa de Conclusão
    df_indicadores["TC"] = (
        (df_indicadores["conc_no_prazo"] + df_indicadores["conc_com_atraso"]) / ma * 100
    )

    # TE — Taxa de Evasão
    df_indicadores["TE"] = (
        (df_indicadores["abandono"] + df_indicadores["desligados"] + df_indicadores["transf_ext"])
        / ma * 100
    )

    # TR — Taxa de Retenção
    df_indicadores["TR"] = df_indicadores["MRET"] / ma * 100

    # IEf — Índice de Eficiência
    # Numerador: todos os concluintes (no prazo + com atraso)
    # Denominador: matrículas que tiveram algum desfecho (todas as saídas)
    matr_finalizadas = (
        df_indicadores["conc_no_prazo"] + df_indicadores["conc_com_atraso"]
        + df_indicadores["abandono"] + df_indicadores["desligados"]
        + df_indicadores["transf_int"] + df_indicadores["transf_ext"]
    ).replace(0, np.nan)
    df_indicadores["IEf"] = (
        (df_indicadores["conc_no_prazo"] + df_indicadores["conc_com_atraso"])
        / matr_finalizadas * 100
    )
        
    # TMREG — Taxa de Matrícula Continuada Regular
    df_indicadores["TMREG"] = df_indicadores["MREG"] / ma * 100

    # TPE — Taxa de Permanência e Êxito
    df_indicadores["TPE"] = df_indicadores["TC"] + df_indicadores["TMREG"]


    return df_indicadores.fillna(0).round(2)


