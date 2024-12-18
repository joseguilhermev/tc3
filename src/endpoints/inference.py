from fastapi import APIRouter
from src.utils import get_latest_data  # Fetch latest data from MongoDB
import pickle
import pandas as pd

# Initialize FastAPI router
router = APIRouter()

# Load the trained model
MODEL_PATH = "models/xgb_model.pkl"
with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

# Define the expected columns (same as training data)
FEATURE_COLUMNS = [
    "Open",
    "change",
    "change_lag1",
    "change_lag2",
    "price_range",
    "relative_volatility",
    "avg_lagged_change",
]


@router.get("/predict", tags=["inference"])
def predict():
    """
    Fetches the latest data, ensures it matches the training format, and predicts the outcome.
    """
    # Step 1: Fetch the latest data
    latest_data = get_latest_data("prices")
    if not latest_data:
        return {"error": "No data found in the database."}

    # Step 2: Convert the data into a DataFrame
    try:
        # Extract only the required columns and maintain the correct order
        data_dict = {col: latest_data.get(col, None) for col in FEATURE_COLUMNS}
        X_new = pd.DataFrame([data_dict])
        # show dataframe
        print(X_new)
        # Ensure no missing values in the DataFrame
        if X_new.isnull().any().any():
            return {"error": "Missing values detected in the input data."}

    except KeyError as e:
        return {"error": f"Missing key in the input data: {str(e)}"}

    # Step 3: Predict using the model
    prediction = model.predict(X_new)

    # Step 4: Return the prediction result
    return {"prediction": int(prediction[0])}
