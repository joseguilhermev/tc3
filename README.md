Here is the corrected and well-structured version of your Markdown document:

---

# Automated Data Extraction, Feature Engineering, and Prediction Pipeline

This repository contains a complete pipeline for data extraction, feature engineering, training a Machine Learning model (XGBoost), and performing real-time inferences. The project integrates various technologies, including FastAPI, Playwright, MongoDB, Streamlit, and Docker (with Docker Compose) to orchestrate the solution.

---

## Table of Contents

1. [Overview](#overview)
2. [Project Architecture](#project-architecture)
3. [Features](#features)
4. [Technologies Used](#technologies-used)
5. [Environment Setup](#environment-setup)
6. [How to Run](#how-to-run)
7. [Project Workflow](#project-workflow)
    1. [Data Extraction (Scraping)](#1-data-extraction-scraping)
    2. [Feature Engineering and Storage](#2-feature-engineering-and-storage)
    3. [Model Training](#3-model-training)
    4. [Inference and Prediction](#4-inference-and-prediction)
8. [Available Endpoints (FastAPI)](#available-endpoints-fastapi)
9. [Visualization (Streamlit)](#visualization-streamlit)
10. [Database Monitoring (Mongo Express)](#database-monitoring-mongo-express)
11. [File Structure](#file-structure)
12. [Future Steps and Improvements](#future-steps-and-improvements)
13. [License](#license)

---

## Overview

This project aims to:

1. Extract historical price data (e.g., BTC/USD) from a web source.
2. Process and store these data in a MongoDB database.
3. Apply feature engineering to generate predictive variables.
4. Train a Machine Learning model (XGBoost) to predict trends (`0 = Short`, `1 = Long`).
5. Perform real-time predictions using the latest data.
6. Present results (including periodic automation) via a Streamlit interface.

---

## Project Architecture

The architecture includes multiple Docker containers orchestrated by Docker Compose:

- **fastapi-app**: Provides endpoints for scraping (data extraction) and prediction.
- **mongo**: A NoSQL database to store raw and processed data.
- **mongo-express**: A web interface to monitor the MongoDB database.
- **streamlit-app**: An interactive web interface for initiating the extraction workflow and displaying predictions.

Model training is performed offline (using notebooks or scripts), resulting in an artifact (`models/xgb_model.pkl`) ready for inference.

---

## Features

- **Automated Data Extraction**: Uses Playwright to render dynamic pages and extract table data.
- **Feature Engineering**: Generates features like `change`, `change_lag1`, `price_range`, `relative_volatility`, among others.
- **NoSQL Storage**: Stores raw and engineered data in MongoDB.
- **XGBoost Model Training**: Implements a boosting algorithm for binary classification.
- **Inference API (FastAPI)**: Provides endpoints for real-time predictions.
- **Web Interface (Streamlit)**: Interactive dashboard for data extraction and prediction.
- **Database Monitoring**: Mongo Express for quick visualization of stored data.

---

## Technologies Used

- **Language**: Python 3
- **API Framework**: FastAPI
- **Web Scraping**: Playwright (to interact with dynamic pages)
- **Database**: MongoDB (with Mongo Express for visualization)
- **Modeling**: XGBoost, Scikit-Learn
- **Visualization and UI**: Streamlit
- **Container Orchestration**: Docker & Docker Compose
- **Environment**: Ubuntu/Linux (Python slim images)

---

## Environment Setup

**Requirements:**

- Docker installed.
- Docker Compose installed.

**Important Environment Variables:**

- `MONGO_URI` (default: `mongodb://mongo:27017`)
- `MONGO_DB` (default: `prices`)

These variables are automatically configured by Docker Compose.

---

## How to Run

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```

2. **Build and start the containers**:

   ```bash
   docker-compose up --build
   ```

   This will start:

   - FastAPI at `http://localhost:11000`
   - MongoDB at `http://localhost:27017`
   - Mongo Express at `http://localhost:8081`
   - Streamlit at `http://localhost:8501`

---

## Project Workflow

### 1. Data Extraction (Scraping)

The script `src/endpoints/scraping.py` provides a `POST /extract` endpoint that:

- Accepts a URL (default: a page with BTC/USD price history).
- Uses Playwright to navigate to the page, wait for table loading, and extract data.
- Parses the data via BeautifulSoup to extract relevant columns: `open`, `high`, `low`, `close`.
- Inserts the preprocessed data into MongoDB.

### 2. Feature Engineering and Storage

The script `src/utils.py` contains functions to:

- Calculate percentage changes (`change`, `change_lag1`, `change_lag2`).
- Generate `price_range`, `relative_volatility`, `avg_lagged_change`, and more.

The resulting data are stored in MongoDB (collection: `prices`). The file `transform_data.py` demonstrates how data are transformed for training.

### 3. Model Training

The script `train_test.py`:

- Loads transformed data (`transformed_data.parquet`).
- Performs exploratory data analysis (EDA).
- Trains an XGBoost model to predict the next price direction.
- Saves the trained model to `models/xgb_model.pkl`.

This step is performed locally before deployment. The trained model is used by the inference endpoint.

### 4. Inference and Prediction

The script `src/endpoints/inference.py` provides a `GET /predict` endpoint that:

- Loads the latest record from MongoDB.
- Creates a dataframe with the necessary features.
- Loads the model from `xgb_model.pkl`.
- Returns the prediction (`0 = Short`, `1 = Long`) in JSON format.

---

## Available Endpoints (FastAPI)

- **`POST /extract`** (tags: scraping): Starts data extraction from a given URL.
- **`GET /predict`** (tags: inference): Returns the model's prediction based on the latest data.

**Example Usage**:

```bash
curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"url":"https://www.cashbackforex.com/chart?s=BTC.USD-1m","collection_name":"prices"}' \
     http://localhost:11000/extract

curl -X GET http://localhost:11000/predict
```

---

## Visualization (Streamlit)

The Streamlit interface (`app.py`) allows users to:

- Automate the extraction and prediction process periodically.
- Display the latest prediction (`Short`/`Long`).

Access the interface at: `http://localhost:8501`.

---

## Database Monitoring (Mongo Express)

Mongo Express is available at: `http://localhost:8081`

- **Username**: admin  
- **Password**: password  

You can inspect the `prices` collection and verify stored data.

---

## File Structure

```plaintext
.
├── src/
│   ├── endpoints/
│   │   ├── inference.py    # Prediction endpoint
│   │   └── scraping.py     # Data extraction and MongoDB insertion
│   └── utils.py            # Utilities (MongoDB, parsing, feature engineering)
├── app.py                  # Streamlit interface
├── main.py                 # FastAPI initialization (includes scraping & inference routers)
├── compose.yml             # Docker Compose definitions
├── Dockerfile              # Main Dockerfile
├── eda.py                  # Exploratory Data Analysis
├── requirements.txt        # Python dependencies
├── test.py                 # Simple scraping test with HTML rendering
├── train_test.py           # XGBoost model training and evaluation
└── transform_data.py       # Data transformation for training
```

---

## Future Steps and Improvements

- **Automation with Crontab/Airflow**: Automate periodic pipeline execution in production.
- **Data Validation**: Implement robust checks to ensure data quality.
- **Scalability**: Add caching, load balancing, and MongoDB replication for production environments.
- **Alerts and Notifications**: Send alerts (email/Slack) when specific market conditions are detected.
- **Model Improvements**: Explore other algorithms, hyperparameter optimization, and additional features (macro, technical, etc.).

---
