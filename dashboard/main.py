import streamlit as st
import pandas as pd
import plotly.express as px


st.set_page_config(page_title='Indicadores Acadêmicos - IFRS Restinga', page_icon=":bar_chart:", layout="wide")

st.text("Seja Bem-Vindo!")

st.markdown("""
#### Indicadores Acadêmicos do IFRS - Campus Restinga
            
""")



##DATAFRAME COM TODOS OS DADOS TRATADOS:
df = pd.read_parquet("../dados_tratados/teste_restinga_dados_preparados.parquet")

df_indicadores_curso_ano = pd.read_parquet("../dados_tratados/teste_indicadores_curso_ano.parquet")


colunas_datas = ["Data de Fim Previsto do Ciclo", "Data de Inicio do Ciclo", "Data de Ocorrencia da Matricula", "Mês De Ocorrência da Situação"]

columns_fmt = {
    col: st.column_config.DatetimeColumn(col, format="DD/MM/YYYY") 
    for col in colunas_datas
}

# Expander de estatísticas gerais
exp = st.expander("Indicadores acadêmoicos IFRS Campus Restinga")

# tabs para navegar em diferentes visões e gráficos
tab_geral, tab_perfil_aluno, tab_indicadores = exp.tabs(tabs=["Painel Geral do Campus", "Perfil Alunos", "Indicadores de Permanência e Êxito"])

# aba para painel geral do Campus
with tab_geral:
    st.dataframe(df, hide_index=True, column_config=columns_fmt)
with tab_perfil_aluno:
    pass
with tab_indicadores:
    st.dataframe(df_indicadores_curso_ano, hide_index=True)
    df_matriculas_curso = df_indicadores_curso_ano.pivot_table(index="Ano", columns="Nome de Curso", values="matriculas_atendidas")
    st.line_chart(df_matriculas_curso)