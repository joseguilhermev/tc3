import pandas as pd

# 1. Load the Data
df = pd.read_csv("data/BIT_1min.csv")

# 2. EDA
# Check for missing values
print("Missing values per column:\n", df.isnull().sum())

# Check data types and basic info
print(df.info())

# Summary statistics
print(df.describe())
