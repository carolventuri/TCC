# Visualização de Indicadores Acadêmicos de Permanência e Êxito dos Estudantes do IFRS Campus Restinga


## Objetivo

Desenvolver um painel de visualização de indicadores acadêmicos utilizando Python.

## Estrutura

- dados_brutos/ → dados baixados da Plataforma Nilo Peçanha
- dados_tratados/ → dados após limpeza e transformação
- notebooks/ → preparacao dos dados e geração de gráficos
- pages/ → painel de visualização

## Tecnologias
- Python
- Pandas
- Plotly
- Streamlit

## Para rodar a aplicação:

Após baixar o diretório do projeto:

1) Para baixar os dados: Acessar a Plataforma Nilo Peçanha através do site https://www.gov.br/mec/pt-br/pnp , clicar em Acesse a Plataforma.
Na página que abrir, clicar em Produtos de Dados e em seguida, em Microdados. Na página que abrir, salvar os microdados de Matrículas de cada ano na pasta dados_brutos do projeto e descompactar os arquivos.

2) Criar um ambiente virtual:
Abra o terminal no diretório do projeto e execute: python -m venv venv.
Em seguida, ative-o com venv\Scripts\activate (Windows) ou source venv/bin/activate (Linux/macOS)

3) Instalar as dependências necessárias:
No terminal no diretório do projeto execute: pip install -r requirements.txt

4) Rodar a aplicação no navegador:
No terminal no diretório do projeto execute: streamlit run Inicio.py