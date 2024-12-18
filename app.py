import streamlit as st
import requests
import time

# Streamlit Page Title
st.title("Automated Data Extraction and Prediction App")

# Endpoint URLs
EXTRACT_ENDPOINT = "http://fastapi-app:11000/extract"
PREDICT_ENDPOINT = "http://fastapi-app:11000/predict"


# Function to call the extract endpoint
def start_extraction():
    try:
        payload = {
            "url": "https://www.cashbackforex.com/chart?s=BTC.USD-1m",
            "collection_name": "prices",
        }
        response = requests.post(EXTRACT_ENDPOINT, json=payload)
        if response.status_code == 200:
            st.success("Data extraction started successfully!")
        else:
            st.error(f"Extract endpoint failed with status code {response.status_code}")
    except Exception as e:
        st.error(f"Error during extraction: {e}")


# Function to call the prediction endpoint
def get_prediction():
    try:
        prediction_response = requests.get(PREDICT_ENDPOINT)
        if prediction_response.status_code == 200:
            result = prediction_response.json()
            prediction = result.get("prediction", None)
            return prediction
        else:
            st.error(
                f"Prediction endpoint failed with status code {prediction_response.status_code}"
            )
            return None
    except Exception as e:
        st.error(f"Error during prediction: {e}")
        return None


# Infinite Loop to automate the process
if st.button("Start Automation"):
    st.warning("Automation started. Do not close this window!")
    while True:
        # Step 1: Start Extraction
        st.info("Starting data extraction...")
        start_extraction()

        # Step 2: Wait for 5 seconds to ensure extraction completion
        st.info("Waiting for 5 seconds to ensure extraction is complete...")
        time.sleep(5)

        # Step 3: Call Prediction Endpoint
        st.info("Fetching prediction...")
        prediction = get_prediction()

        # Step 4: Display Prediction
        if prediction == 0:
            st.markdown("<h2 style='color:red;'>Short</h2>", unsafe_allow_html=True)
        elif prediction == 1:
            st.markdown("<h2 style='color:green;'>Long</h2>", unsafe_allow_html=True)
        else:
            st.warning("Unexpected prediction value received or failed.")

        st.info(
            "Waiting for 1 minute and 5 seconds before starting data extraction and prediction again..."
        )
        time.sleep(65)
        # Optional log or separator
        st.write("---")
