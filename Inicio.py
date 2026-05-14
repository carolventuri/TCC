"""
Inicio.py — Página inicial do Dashboard IFRS Campus Restinga.

Como executar:
    streamlit run Inicio.py

"""

import streamlit as st

st.set_page_config(
    page_title="IFRS Campus Restinga",
    page_icon=":bar_chart:",
    layout="wide",
)

# Cabeçalho
st.title("IFRS Campus Restinga: Indicadores de Permanência e Êxito dos Estudantes")

st.markdown(
    """
    #### Bem-vindo(a) ao painel interativo de indicadores acadêmicos do **IFRS Campus Restinga**!

    Os dados são provenientes dos microdados de matrículas da Plataforma Nilo Peçanha (PNP),
    abrangendo o período de **2017 a 2024**, e os indicadores são calculados conforme as
    definições do Plano Estratégico de Permanência e Êxito (PEPE) do IFRS.
    """
)

    
st.markdown("---")

# ── Descrição das páginas ─────────────────────────────────────────────────────
st.markdown("### Use o menu lateral para acessar cada seção do dashboard:")



st.markdown(
        """
        :classical_building: **Visão Geral do Campus**: 
        Panorama completo do campus: evolução dos indicadores,
        volume de matrículas por ano e distribuição geral das situações de matrícula.
        
        :bar_chart: **Visão por Indicador**: 
        Análise detalhada de cada indicador (TC, TE, TR, IEf, TPE, TEFAcad)
        filtrada por curso e tipo de curso, com rankings e heatmaps.
       
        :mortar_board: **Perfil dos Estudantes**: 
        Distribuição sociodemográfica: sexo, cor/raça, faixa etária,
        renda familiar e turno — com cruzamentos por evasão e tipo de curso.
       
        :mag: **Análise de Evasão e Retenção**: 
        Estudo aprofundado dos motivos de evasão, evolução temporal,
        correlações entre indicadores e comparação entre cursos.

        :clipboard: **Tabelas de Dados**: 
        Consulta e exportação das tabelas de indicadores calculados,
        com opção de download em formato CSV.
        """
)

st.markdown("---")

# ── Resumo dos indicadores ───────────────────────────────────────────────────
st.markdown("### Indicadores de Permanência e Êxito:")

st.markdown(

    """
    | Sigla | Nome completo | O que mede |
    |-------|--------------|------------|
    | **TC** | Taxa de Conclusão | % de concluintes em relação às matrículas atendidas |
    | **TE** | Taxa de Evasão | % de evadidos em relação às matrículas atendidas |
    | **TR** | Taxa de Retenção | % de alunos além do prazo previsto em relação às matrículas atendidas |
    | **IEf** | Índice de Eficiência | % de concluintes entre os que finalizaram o vínculo |
    | **TPE** | Taxa de Permanência e Êxito | TC + Taxa de Matrícula Continuada Regular |
    | **MREG** | Matrículas Ativas Regulares | matrículas ativas e dentro do prazo previsto de conclusão do curso |
    | **MRET** | Matrículas Ativas Retidas | matrículas ativas após a data prevista para conclusão do curso |
    """
)

st.markdown("---")
st.caption(
    "Fonte: Plataforma Nilo Peçanha (PNP) · Microdados de Matrículas 2017–2024 · "
)
