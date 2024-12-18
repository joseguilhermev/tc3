Aqui está a versão traduzida e estruturada em português:

---

# Pipeline Automatizado de Extração de Dados, Engenharia de Atributos e Predição

Este repositório contém um pipeline completo para extração de dados, engenharia de atributos, treinamento de um modelo de Machine Learning (XGBoost) e execução de inferências em tempo real. O projeto integra diversas tecnologias, incluindo FastAPI, Playwright, MongoDB, Streamlit e Docker (com Docker Compose) para orquestrar a solução.

---

## Tabela de Conteúdos

1. [Visão Geral](#visão-geral)
2. [Arquitetura do Projeto](#arquitetura-do-projeto)
3. [Funcionalidades](#funcionalidades)
4. [Tecnologias Utilizadas](#tecnologias-utilizadas)
5. [Preparação do Ambiente](#preparação-do-ambiente)
6. [Como Executar](#como-executar)
7. [Fluxo de Trabalho do Projeto](#fluxo-de-trabalho-do-projeto)
    1. [Extração de Dados (Scraping)](#1-extração-de-dados-scraping)
    2. [Engenharia de Atributos e Armazenamento](#2-engenharia-de-atributos-e-armazenamento)
    3. [Treinamento do Modelo](#3-treinamento-do-modelo)
    4. [Inferência e Predição](#4-inferência-e-predição)
8. [Endpoints Disponíveis (FastAPI)](#endpoints-disponíveis-fastapi)
9. [Visualização (Streamlit)](#visualização-streamlit)
10. [Monitoramento do Banco de Dados (Mongo Express)](#monitoramento-do-banco-de-dados-mongo-express)
11. [Estrutura de Arquivos](#estrutura-de-arquivos)
12. [Próximos Passos e Melhorias Futuras](#próximos-passos-e-melhorias-futuras)
13. [Licença](#licença)

---

## Visão Geral

Este projeto tem como objetivo:

1. Extrair dados históricos de preços (e.g., BTC/USD) de uma fonte web.
2. Processar e armazenar esses dados em um banco de dados MongoDB.
3. Aplicar engenharia de atributos para gerar variáveis preditivas.
4. Treinar um modelo de Machine Learning (XGBoost) para prever tendências (`0 = Short`, `1 = Long`).
5. Realizar predições em tempo real com base nos dados mais recentes.
6. Apresentar resultados (incluindo automação periódica) por meio de uma interface Streamlit.

---

## Arquitetura do Projeto

A arquitetura compreende múltiplos contêineres Docker orquestrados pelo Docker Compose:

- **fastapi-app**: Fornece endpoints para scraping (extração de dados) e predição.
- **mongo**: Banco de dados NoSQL para armazenar dados brutos e processados.
- **mongo-express**: Interface web para monitorar o banco de dados MongoDB.
- **streamlit-app**: Interface web interativa para iniciar o fluxo de extração e exibir predições.

O treinamento do modelo é realizado offline (utilizando notebooks ou scripts), gerando um artefato (`models/xgb_model.pkl`) pronto para inferência.

---

## Funcionalidades

- **Extração Automatizada de Dados**: Usa Playwright para renderizar páginas dinâmicas e extrair dados de tabelas.
- **Engenharia de Atributos**: Gera atributos como `change`, `change_lag1`, `price_range`, `relative_volatility`, entre outros.
- **Armazenamento em NoSQL**: Armazena dados brutos e processados no MongoDB.
- **Treinamento de Modelo XGBoost**: Implementa um algoritmo de boosting para classificação binária.
- **API de Inferência (FastAPI)**: Oferece endpoints para predições em tempo real.
- **Interface Web (Streamlit)**: Painel interativo para extração de dados e predição.
- **Monitoramento de Banco de Dados**: Mongo Express para visualização rápida dos dados armazenados.

---

## Tecnologias Utilizadas

- **Linguagem**: Python 3
- **Framework de API**: FastAPI
- **Extração Web**: Playwright (para interação com páginas dinâmicas)
- **Banco de Dados**: MongoDB (com Mongo Express para visualização)
- **Modelagem**: XGBoost, Scikit-Learn
- **Visualização e UI**: Streamlit
- **Orquestração de Contêineres**: Docker & Docker Compose
- **Ambiente**: Ubuntu/Linux (imagens slim do Python)

---

## Preparação do Ambiente

**Requisitos:**

- Docker instalado.
- Docker Compose instalado.

**Variáveis de Ambiente Importantes:**

- `MONGO_URI` (padrão: `mongodb://mongo:27017`)
- `MONGO_DB` (padrão: `prices`)

Essas variáveis são configuradas automaticamente pelo Docker Compose.

---

## Como Executar

1. **Clonar o repositório**:

   ```bash
   git clone <url-do-repositorio>
   cd <pasta-do-repositorio>
   ```

2. **Construir e iniciar os contêineres**:

   ```bash
   docker-compose up --build
   ```

   Isso iniciará:

   - FastAPI em `http://localhost:11000`
   - MongoDB em `http://localhost:27017`
   - Mongo Express em `http://localhost:8081`
   - Streamlit em `http://localhost:8501`

---

## Fluxo de Trabalho do Projeto

### 1. Extração de Dados (Scraping)

O script `src/endpoints/scraping.py` fornece o endpoint `POST /extract`, que:

- Aceita uma URL (padrão: uma página com histórico de preços BTC/USD).
- Usa Playwright para navegar até a página, esperar o carregamento da tabela e extrair dados.
- Faz parsing dos dados com BeautifulSoup, extraindo colunas relevantes: `open`, `high`, `low`, `close`.
- Insere os dados pré-processados no MongoDB.

### 2. Engenharia de Atributos e Armazenamento

O script `src/utils.py` contém funções para:

- Calcular mudanças percentuais (`change`, `change_lag1`, `change_lag2`).
- Gerar `price_range`, `relative_volatility`, `avg_lagged_change`, entre outros.

Os dados resultantes são armazenados no MongoDB (coleção: `prices`). O arquivo `transform_data.py` demonstra a transformação dos dados para treinamento.

### 3. Treinamento do Modelo

O script `train_test.py`:

- Carrega os dados transformados (`transformed_data.parquet`).
- Realiza análise exploratória de dados (EDA).
- Treina um modelo XGBoost para prever a direção do próximo preço.
- Salva o modelo treinado em `models/xgb_model.pkl`.

Esse passo é realizado localmente antes da implantação. O modelo treinado é usado pelo endpoint de inferência.

### 4. Inferência e Predição

O script `src/endpoints/inference.py` fornece o endpoint `GET /predict`, que:

- Carrega o último registro inserido no MongoDB.
- Gera um dataframe com as features necessárias.
- Carrega o modelo `xgb_model.pkl`.
- Retorna a predição (`0 = Short`, `1 = Long`) no formato JSON.

---

## Endpoints Disponíveis (FastAPI)

- **`POST /extract`**: Inicia a extração de dados a partir de uma URL fornecida.
- **`GET /predict`**: Retorna a predição do modelo baseada nos dados mais recentes.

**Exemplo de Uso**:

```bash
curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"url":"https://www.cashbackforex.com/chart?s=BTC.USD-1m","collection_name":"prices"}' \
     http://localhost:11000/extract

curl -X GET http://localhost:11000/predict
```

---

## Visualização (Streamlit)

A interface Streamlit (`app.py`) permite:

- Automatizar o processo de extração e predição de forma periódica.
- Exibir a última predição (`Short`/`Long`).

Acesse em: `http://localhost:8501`.

---

## Monitoramento do Banco de Dados (Mongo Express)

Mongo Express está disponível em: `http://localhost:8081`

- **Usuário**: admin  
- **Senha**: password  

É possível inspecionar a coleção `prices` e verificar os dados armazenados.

---

## Estrutura de Arquivos

```plaintext
.
├── src/
│   ├── endpoints/
│   │   ├── inference.py    # Endpoint de predição
│   │   └── scraping.py     # Extração de dados e inserção no MongoDB
│   └── utils.py            # Funções utilitárias (MongoDB, parsing, engenharia de atributos)
├── app.py                  # Interface Streamlit
├── main.py                 # Inicialização do FastAPI (routers scraping e inference)
├── compose.yml             # Definições do Docker Compose
├── Dockerfile              # Dockerfile principal
├── eda.py                  # Análise exploratória de dados
├── requirements.txt        # Dependências do Python
├── test.py                 # Teste simples de scraping com HTML
├── train_test.py           # Treinamento e avaliação do modelo XGBoost
└── transform_data.py       # Transformação dos dados para treinamento
```

---

## Próximos Passos e Melhorias Futuras

- **Automação com Crontab/Airflow**: Automatizar a execução periódica do pipeline em produção.
- **Validação de Dados**: Implementar checagens robustas para garantir a qualidade dos dados.
- **Escalabilidade**: Adicionar caching, balanceamento de carga e replicação do MongoDB.
- **Alertas e Notificações**: Enviar alertas (e-mail/Slack) ao detectar condições específicas de mercado.
- **Melhorias no Modelo**: Explorar outros algoritmos, otimização de hiperparâmetros e novas features.

---

## Licença

Inclua informações sobre a licença aqui.

---
