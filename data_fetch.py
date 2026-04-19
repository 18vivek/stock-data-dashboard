import yfinance as yf
import pandas as pd

# Fetch stock data (TCS example)
data = yf.download("TCS.NS", period="1mo")
data.reset_index(inplace=True)

# 1. Daily Return
data["Daily Return"] = (data["Close"] - data["Open"]) / data["Open"]

# 2. 7-day Moving Average
data["7 Day MA"] = data["Close"].rolling(window=7).mean()

print(data.head())
data.to_csv("tcs_stock_data.csv", index=False)