Automated Data Extraction, Feature Engineering, and Prediction Pipeline
=======================================================================

Este repositório contém um pipeline completo para extração de dados, engenharia de atributos, treinamento de um modelo de Machine Learning (XGBoost) e realização de inferências em tempo real. O projeto integra diversas tecnologias, incluindo FastAPI, Playwright, MongoDB, Streamlit, e Docker (com Docker Compose) para orquestrar a solução.

Sumário
-------

-   Visão Geral
-   Arquitetura do Projeto
-   Funcionalidades
-   Tecnologias Utilizadas
-   Preparação do Ambiente
-   Como Executar
-   Fluxo de Trabalho do Projeto
    -   1.  Extração de Dados (Scraping)
    -   1.  Engenharia de Atributos e Armazenamento
    -   1.  Treinamento do Modelo
    -   1.  Inferência e Predição
-   Endpoints Disponíveis (FastAPI)
-   Visualização (Streamlit)
-   Monitoramento do Banco de Dados (Mongo Express)
-   Estrutura de Arquivos
-   Próximos Passos e Melhorias Futuras
-   Licença

Visão Geral
-----------

Este projeto tem como objetivo:

1.  Extrair dados históricos de preços (por exemplo, BTC/USD) a partir de uma fonte web.
2.  Processar e armazenar esses dados em um banco de dados MongoDB.
3.  Aplicar engenharia de atributos (feature engineering) para gerar variáveis preditivas.
4.  Treinar um modelo de Machine Learning (XGBoost) para prever tendências (0 = "Short", 1 = "Long").
5.  Executar predições em tempo real a partir dos dados mais recentes.
6.  Apresentar os resultados (incluindo automação periódica) via uma interface Streamlit.

Arquitetura do Projeto
----------------------

A arquitetura compreende múltiplos contêineres Docker orquestrados pelo Docker Compose:

-   fastapi-app: Fornece endpoints de scraping (extração) e predição.
-   mongo: Banco de dados NoSQL para armazenar dados brutos e dados pós-engenharia.
-   mongo-express: Interface web para monitorar o banco de dados MongoDB.
-   streamlit-app: Interface web interativa para iniciar o fluxo de extração e exibir predições.

Adicionalmente, o treinamento do modelo é realizado offline (utilizando notebooks ou scripts), resultando em um artefato (modelo treinado em `models/xgb_model.pkl`) pronto para inferência.

Funcionalidades
---------------

-   Extração Automatizada de Dados: Utiliza Playwright para renderizar páginas dinâmicas e extrair dados de tabelas.
-   Engenharia de Atributos: Geração de recursos como `change`, `change_lag1`, `price_range`, `relative_volatility`, entre outros.
-   Armazenamento em Banco NoSQL: Persiste dados e features no MongoDB.
-   Treinamento de Modelo XGBoost: Algoritmo de boosting para classificação binária.
-   API de Inferência (FastAPI): Endpoint para obter predições em tempo real.
-   Interface Web (Streamlit): Painel interativo para iniciar extrações, obter predições e visualizar sinais (Long/Short).
-   Monitoramento via Mongo Express: Visualização rápida dos dados armazenados.

Tecnologias Utilizadas
----------------------

-   Linguagem: Python 3
-   Framework de API: FastAPI
-   Extração Web: Playwright (para interagir com páginas dinâmicas)
-   Banco de Dados: MongoDB (com Mongo Express para visualização)
-   Modelagem: XGBoost, Scikit-Learn
-   Visualização e UI: Streamlit
-   Orquestração de Contêineres: Docker & Docker Compose
-   Ambiente: Ubuntu/Linux (imagens slim do Python)

Preparação do Ambiente
----------------------

**Requisitos:**

-   Docker instalado.
-   Docker Compose instalado.

**Variáveis de Ambiente Importantes:**

-   `MONGO_URI` (padrão: `mongodb://mongo:27017`)
-   `MONGO_DB` (padrão: `prices`)

Estas variáveis são configuradas automaticamente pelo Docker Compose.

Como Executar
-------------

1.  **Clonar o repositório**:

bash

Copy code

`git clone <url-do-repositorio>
cd <pasta-do-repositorio>`

1.  **Construir e iniciar os contêineres**:

bash

Copy code

`docker-compose up --build`

Esse comando iniciará:

-   FastAPI na porta 11000
-   MongoDB na porta 27017
-   Mongo Express na porta 8081
-   Streamlit na porta 8501

Acesse a interface do Streamlit em: <http://localhost:8501>

Fluxo de Trabalho do Projeto
----------------------------

### 1\. Extração de Dados (Scraping)

O script `src/endpoints/scraping.py` fornece um endpoint `POST /extract` que:

-   Recebe uma URL (por padrão, uma página com histórico de preços BTC/USD).
-   Utiliza Playwright para navegar até a página, esperar o carregamento da tabela e extrair dados.
-   Aplica parsing via BeautifulSoup e extrai colunas relevantes: `open`, `high`, `low`, `close`.
-   Insere os dados pré-processados no MongoDB.

### 2\. Engenharia de Atributos e Armazenamento

O script `src/utils.py` contém funções para:

-   Calcular mudanças percentuais (`change`, `change_lag1`, `change_lag2`).
-   Calcular `price_range`, `relative_volatility`, `avg_lagged_change`, entre outros.

Os dados resultantes são armazenados no MongoDB (coleção `prices`). O arquivo `transform_data.py` demonstra a transformação e criação do conjunto de treinamento usado offline.

### 3\. Treinamento do Modelo

O script `train_test.py`:

-   Carrega dados transformados (`transformed_data.parquet`).
-   Executa análise exploratória (EDA).
-   Treina um modelo XGBoost para prever a direção do próximo preço.
-   Salva o modelo em `models/xgb_model.pkl`.

Este passo é realizado localmente, antes da implantação. O modelo treinado é então usado pelo endpoint de inferência.

### 4\. Inferência e Predição

O script `src/endpoints/inference.py` fornece um endpoint `GET /predict` que:

-   Carrega o último registro inserido no MongoDB.
-   Gera um dataframe com as features necessárias.
-   Carrega o modelo `xgb_model.pkl`.
-   Retorna a predição (`0 = Short`, `1 = Long`) no formato JSON.

Endpoints Disponíveis (FastAPI)
-------------------------------

-   `POST /extract` (tags: scraping): Inicia extração de dados a partir de uma URL fornecida.
-   `GET /predict` (tags: inference): Retorna a predição do modelo baseado no dado mais recente.

Exemplo de uso (usando `curl`):

bash

Copy code

`curl -X POST\
     -H "Content-Type: application/json"\
     -d '{"url":"https://www.cashbackforex.com/chart?s=BTC.USD-1m","collection_name":"prices"}'\
     http://localhost:11000/extract

curl -X GET http://localhost:11000/predict`

Visualização (Streamlit)
------------------------

A interface Streamlit (`app.py`) permite:

-   Iniciar a automação do processo de extração e predição de forma periódica (loop infinito).
-   Exibir a última predição (Short/Long).

Acesse via <http://localhost:8501>.

Monitoramento do Banco de Dados (Mongo Express)
-----------------------------------------------

O Mongo Express está disponível em <http://localhost:8081>, onde:

-   Usuário: admin
-   Senha: password

Você pode inspecionar a coleção `prices` e verificar os dados armazenados.

Estrutura de Arquivos
---------------------

bash

Copy code

`.
├── src/
│   ├── endpoints/
│   │   ├── inference.py   # Endpoint de predição via modelo
│   │   └── scraping.py    # Endpoint de extração e inserção de dados no MongoDB
│   └── utils.py           # Funções utilitárias (MongoDB, parsing, feature eng.)
├── app.py                 # Interface Streamlit
├── main.py                # Inicialização do FastAPI, inclui routers de scraping e inference
├── compose.yml            # Definições do Docker Compose
├── Dockerfile             # Dockerfile principal
├── eda.py                 # Análise exploratória de dados
├── requirements.txt       # Dependências Python
├── test.py                # Teste simples de scraping com renderização HTML
├── train_test.py          # Treinamento e avaliação do modelo XGBoost
└── transform_data.py      # Transformação dos dados originais em conjunto final de treinamento`

Próximos Passos e Melhorias Futuras
-----------------------------------

-   Automação via Crontab/Airflow: Automatizar a execução periódica do pipeline em produção.
-   Validação de Dados: Implementar checagens mais robustas para garantir a qualidade dos dados extraídos.
-   Escalabilidade: Implementar caching, load balancing e estratégias de replicação do MongoDB em ambientes de produção.
-   Alertas e Notificações: Envio de alertas (e-mail/Slack) quando certas condições de mercado forem detectadas.
-   Melhorias no Modelo: Explorar outros algoritmos, otimização de hiperparâmetros e adição de novas features (macro, técnico, etc.).