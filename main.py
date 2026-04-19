from fastapi import FastAPI
import pandas as pd
import numpy as np
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



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

@app.get("/compare")
def compare_stocks(symbol1: str, symbol2: str):

    import yfinance as yf
    import pandas as pd

    data1 = yf.download(f"{symbol1}.NS", period="1mo")
    data2 = yf.download(f"{symbol2}.NS", period="1mo")

    # ✅ Flatten columns (VERY IMPORTANT)
    if isinstance(data1.columns, pd.MultiIndex):
        data1.columns = data1.columns.get_level_values(0)

    if isinstance(data2.columns, pd.MultiIndex):
        data2.columns = data2.columns.get_level_values(0)

    data1 = data1.reset_index()
    data2 = data2.reset_index()

    # ✅ Safe numeric conversion
    data1["Close"] = pd.to_numeric(data1["Close"], errors="coerce")
    data2["Close"] = pd.to_numeric(data2["Close"], errors="coerce")

    data1.fillna(0, inplace=True)
    data2.fillna(0, inplace=True)

    return {
        "symbol1": data1[["Date", "Close"]].to_dict(orient="records"),
        "symbol2": data2[["Date", "Close"]].to_dict(orient="records")
    }