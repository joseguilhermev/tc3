import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import pickle

# 1. Load the Data
df = pd.read_parquet("transformed_data.parquet")

# Plot target distribution
sns.countplot(x="higher_or_lower", data=df)
plt.title("Distribution of Target (higher_or_lower)")
plt.show()

# Plot histograms of some key features
features_to_plot = [
    "change",
    "change_lag1",
    "change_lag2",
    "price_range",
    "relative_volatility",
]
df[features_to_plot].hist(bins=30, figsize=(12, 8))
plt.suptitle("Histograms of Key Features")
plt.show()

# Correlation heatmap
plt.figure(figsize=(10, 8))
numeric_df = df.drop(["Date", "Symbol", "higher_or_lower"], axis=1, errors="ignore")
corr = numeric_df.corr()

sns.heatmap(corr, cmap="coolwarm", annot=False)
plt.title("Feature Correlation Heatmap")
plt.show()

# 2. Feature Engineering

# Option 1: Use a higher correlation threshold or skip dropping features entirely.
# Let's say we increase the threshold to 0.95:
corr_matrix = numeric_df.corr().abs()
upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
to_drop = [column for column in upper.columns if any(upper[column] > 0.95)]
print("Dropping highly correlated features with threshold > 0.95:", to_drop)

# If you prefer not to drop at all, you can comment this line out.
numeric_df = numeric_df.drop(columns=to_drop, errors="ignore")

# Update X and y
X = numeric_df
y = df["higher_or_lower"]

# Drop rows with missing values
X = X.dropna()
y = y.loc[X.index]  # Align target variable

# Split into train and test set
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 3. Model Training with XGBoost
xgb_model = XGBClassifier(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=10,
    random_state=42,
    eval_metric="logloss",
)

xgb_model.fit(X_train, y_train)

# Predictions
y_pred = xgb_model.predict(X_test)

# Evaluation
print("Classification Report:")
print(classification_report(y_test, y_pred))

print("Confusion Matrix:")
conf_mat = confusion_matrix(y_test, y_pred)
sns.heatmap(
    conf_mat, annot=True, fmt="d", cmap="Blues", xticklabels=[0, 1], yticklabels=[0, 1]
)
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.show()

# Save the model in pickle format
with open("models/xgb_model.pkl", "wb") as file:
    pickle.dump(xgb_model, file)
