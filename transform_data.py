import pandas as pd
import numpy as np

# Read the original CSV
df = pd.read_csv("/Users/guivasconcelos/Desktop/tc3/data/BIT_1min.csv")

# Ensure Date is a datetime (if needed)
df["Date"] = pd.to_datetime(df["Date"])

# Sort by date if not already sorted
df = df.sort_values(by="Date").reset_index(drop=True)

# Create lagged close columns
df["close_lag1"] = df["Close"].shift(1)
df["close_lag2"] = df["Close"].shift(2)
df["close_lag3"] = df["Close"].shift(3)


# Compute percentage change function
def pct_change(current, previous):
    # If previous is zero or NaN, return 0 to avoid division error.
    return np.where(
        (previous != 0) & ~np.isnan(previous),
        ((current - previous) / previous) * 100.0,
        0.0,
    )


# Compute changes based on close and lagged closes
df["change"] = pct_change(df["Close"], df["close_lag1"])
df["change_lag1"] = pct_change(df["close_lag1"], df["close_lag2"])
df["change_lag2"] = pct_change(df["close_lag2"], df["close_lag3"])

# higher_or_lower: 1 if the *next* close > current close else 0
# Use shift(-1) to get the next row's close.
df["higher_or_lower"] = np.where(df["Close"].shift(-1) > df["Close"], 1.0, 0.0)

# price_range: high - low
df["price_range"] = df["High"] - df["Low"]

# relative_volatility: price_range / open
df["relative_volatility"] = np.where(
    df["Open"] != 0, df["price_range"] / df["Open"], 0.0
)

# avg_lagged_close: mean of close_lag1, close_lag2, close_lag3
df["avg_lagged_close"] = (df["close_lag1"] + df["close_lag2"] + df["close_lag3"]) / 3.0

# avg_lagged_change: average of lagged changes (here we have change_lag1 and change_lag2)
df["avg_lagged_change"] = (df["change_lag1"] + df["change_lag2"]) / 2.0

# Ratios relative to lagged closes
df["ratio_to_lag1"] = np.where(
    df["close_lag1"] != 0, df["Close"] / df["close_lag1"], 1.0
)
df["ratio_to_lag2"] = np.where(
    df["close_lag2"] != 0, df["Close"] / df["close_lag2"], 1.0
)
df["ratio_to_lag3"] = np.where(
    df["close_lag3"] != 0, df["Close"] / df["close_lag3"], 1.0
)

# Drop rows without sufficient lag data
df = df.dropna(subset=["close_lag1", "close_lag2", "close_lag3"])

# Also, because we used shift(-1) for higher_or_lower, the last row won't have a next close.
# Decide how to handle it. Usually, you'd drop the last row if it doesn't have a "next" close.
df = df.iloc[:-1]  # Drops the last row

# Select the columns you want to export
output_columns = [
    "Date",
    "Open",
    "High",
    "Low",
    "Close",
    "change",
    "change_lag1",
    "change_lag2",
    "close_lag1",
    "close_lag2",
    "close_lag3",
    "higher_or_lower",
    "price_range",
    "relative_volatility",
    "avg_lagged_change",
    "avg_lagged_close",
    "ratio_to_lag1",
    "ratio_to_lag2",
    "ratio_to_lag3",
]

# Write to a new CSV
# to csv
df[output_columns].to_csv("transformed_data.csv", index=False)
df[output_columns].to_parquet("transformed_data.parquet", index=False, engine="pyarrow")

print("Transformation complete. 'transformed_data.csv' created.")
