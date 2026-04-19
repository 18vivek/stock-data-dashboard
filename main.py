from fastapi import FastAPI
import pandas as pd
import numpy as np

app = FastAPI()

# Load your CSV
data = pd.read_csv("tcs_stock_data.csv")
# ✅ Fix ALL problematic values
# Convert important columns to numeric
cols_to_convert = ["Open", "High", "Low", "Close"]

for col in cols_to_convert:
    data[col] = pd.to_numeric(data[col], errors="coerce")

# Replace inf with NaN
data.replace([np.inf, -np.inf], np.nan, inplace=True)

# Fill numeric columns
numeric_cols = data.select_dtypes(include=[np.number]).columns
data[numeric_cols] = data[numeric_cols].fillna(0)

# Convert non-numeric columns safely to string
for col in data.columns:
    if col not in numeric_cols:
        data[col] = data[col].astype(str)
print(data.columns)

@app.get("/")
def home():
    return {"message": "Stock API is running 🚀"}


# 1. /companies
@app.get("/companies")
def get_companies():
    return ["TCS"]


# 2. /data/{symbol}
@app.get("/data/{symbol}")
def get_stock_data(symbol: str):
    if symbol.upper() == "TCS":
        cleaned_data = data.tail(30).copy()

        # Convert all values safely
        cleaned_data = cleaned_data.replace([np.inf, -np.inf], 0)
        cleaned_data = cleaned_data.fillna(0)

        return cleaned_data.to_dict(orient="records")

    return {"error": "Company not found"}

# 3. /summary/{symbol}
@app.get("/summary/{symbol}")
def get_summary(symbol: str):
    if symbol.upper() == "TCS":

        high = data["High"].max()
        low = data["Low"].min()
        avg = data["Close"].mean()

        return {
            "52_week_high": float(high),
            "52_week_low": float(low),
            "average_close": float(avg)
        }

    return {"error": "Company not found"}