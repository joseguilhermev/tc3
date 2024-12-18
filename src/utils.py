import time
import logging
import os
from typing import Optional, Dict
import numpy as np
from pymongo import MongoClient
from pymongo.database import Database
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Environment variables
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB", "prices")

# MongoDB Singleton Instance
_mongo_db: Optional[Database] = None


def _get_db() -> Database:
    """
    Get the MongoDB database instance. Reuses the connection after initialization.
    """
    global _mongo_db
    if _mongo_db is None:
        mongo_client = MongoClient(MONGO_URI)
        _mongo_db = mongo_client[MONGO_DB_NAME]
        logging.info(f"Connected to MongoDB database: {MONGO_DB_NAME}")
    return _mongo_db


def get_mongo_collection(collection_name: str):
    """
    Utility function to get a MongoDB collection.
    """
    db = _get_db()
    return db[collection_name]


def parse_float(value: str) -> float:
    """
    Safely parse a float from a string, removing commas.
    """
    try:
        return float(value.replace(",", ""))
    except ValueError:
        logging.warning(f"Could not parse float from value: {value}")
        return float("nan")


def extract_data_from_row(row) -> Dict[str, float]:
    """
    Extract numerical data from a given table row.
    Expected row format (based on the page structure):
    [Date, Open, High, Low, Close, ...]
    """
    columns = row.find_all("td")
    if len(columns) < 5:  # Ensure there are enough columns
        return {}

    return {
        "open": parse_float(columns[1].text.strip()),
        "high": parse_float(columns[2].text.strip()),
        "low": parse_float(columns[3].text.strip()),
        "close": parse_float(columns[4].text.strip()),
    }


def compute_percentage_change(current_close: float, previous_close: float) -> float:
    """
    Compute the percentage change from previous_close to current_close.
    """
    if previous_close and previous_close != 0 and not np.isnan(previous_close):
        return ((current_close - previous_close) / previous_close) * 100.0
    return 0.0


def extract_and_insert_features(url: str, collection_name: str):
    """
    Extract and insert only required features into MongoDB.
    """
    logging.info("Starting data extraction process.")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            # Navigate to the URL
            logging.info(f"Navigating to {url}")
            page.goto(url, wait_until="domcontentloaded", timeout=60000)

            # Wait for the table to load
            logging.info("Waiting for table to load...")
            page.wait_for_function(
                """() => {
                    const table = document.querySelector("table.chart-price-history-table");
                    return table && table.rows.length > 3;
                }""",
                timeout=15000,
            )
            time.sleep(2)
            content = page.content()
            browser.close()

        except Exception as e:
            logging.error(f"Error during page navigation or extraction: {e}")
            browser.close()
            return {"status": "error", "message": str(e)}

    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(content, "html.parser")
    table = soup.select_one("table.chart-price-history-table")

    if not table:
        logging.warning("No table found on the page.")
        return {"status": "no_data"}

    rows = table.find_all("tr")

    if len(rows) <= 5:
        logging.warning("Not enough rows found to extract lagged data.")
        return {"status": "no_data"}

    # Extract necessary rows
    current_data = extract_data_from_row(rows[2])
    lag_data_1 = extract_data_from_row(rows[3])
    lag_data_2 = extract_data_from_row(rows[4])
    lag_data_3 = extract_data_from_row(rows[5])

    if not current_data or not lag_data_1 or not lag_data_2:
        logging.warning("Incomplete data rows found. Cannot proceed.")
        return {"status": "no_data"}

    # Compute required features
    change = compute_percentage_change(current_data["close"], lag_data_1["close"])
    change_lag1 = compute_percentage_change(lag_data_1["close"], lag_data_2["close"])
    change_lag2 = compute_percentage_change(lag_data_2["close"], lag_data_3["close"])

    price_range = current_data["high"] - current_data["low"]
    relative_volatility = (
        price_range / current_data["open"] if current_data["open"] != 0 else 0.0
    )
    avg_lagged_change = (change_lag1 + change_lag2) / 2.0

    # Prepare the data to insert
    data = {
        "Open": current_data["open"],
        "change": change,
        "change_lag1": change_lag1,
        "change_lag2": change_lag2,
        "price_range": price_range,
        "relative_volatility": relative_volatility,
        "avg_lagged_change": avg_lagged_change,
    }

    logging.info(f"Extracted Features: {data}")

    # Insert into MongoDB
    try:
        collection = get_mongo_collection(collection_name)
        result = collection.insert_one(data)
        logging.info("Data inserted into MongoDB successfully.")
        return {"status": "success", "inserted_id": str(result.inserted_id)}
    except Exception as db_e:
        logging.error(f"Error inserting data into MongoDB: {db_e}")
        return {"status": "error", "message": str(db_e)}


def get_latest_data(collection_name: str):
    collection = get_mongo_collection(collection_name)
    latest_data = collection.find_one(sort=[("_id", -1)])
    return latest_data
