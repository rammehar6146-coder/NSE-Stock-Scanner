import yfinance as yf
import pandas as pd
import gspread
import time

from oauth2client.service_account import ServiceAccountCredentials

# Stock symbols
symbols_df = pd.read_csv("nse_symbols.csv")
symbols = [
   # "RELIANCE.NS",
   # "TCS.NS",
   # "INFY.NS",
   # "HDFCBANK.NS",
   # "ICICIBANK.NS",
   # "SBIN.NS",
   # "ITC.NS",
   # "LT.NS",
   # "AXISBANK.NS",
   # "KOTAKBANK.NS"
    
    str(sym).strip() + ".NS"
    for sym in symbols_df["SYMBOL"]
]

# 👇 ADD THESE LINES HERE
print("CSV ROWS:", len(symbols_df))
print("SYMBOLS LOADED:", len(symbols))
print("FIRST 15 SYMBOLS:", symbols[:15])

data = []

for stock in symbols:

    try:
        ticker = yf.Ticker(stock)

        hist = ticker.history(period="5d")

        if len(hist) == 0:
            continue

        latest = hist.iloc[-1]

        avg_volume = hist["Volume"].mean()

        rel_volume = latest["Volume"] / avg_volume

        data.append({
            "Symbol": stock,
            "Close": round(latest["Close"], 2),
            "Volume": int(latest["Volume"]),
            "AvgVolume": int(avg_volume),
            "RelVolume": round(rel_volume, 2)
        })

        print(f"Done: {stock}")

        time.sleep(0.2)

    except Exception as e:
        print(stock, e)

df = pd.DataFrame(data)

top250 = df.sort_values(
    by="Volume",
    ascending=False
)

# Google Sheet connection

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "credentials.json",
    scope
)

client = gspread.authorize(creds)

sheet = client.open(
       "NSE Stock Scanner"
).sheet1

sheet.clear()

sheet.update(
    [top250.columns.values.tolist()] +
    top250.values.tolist()
)

print("Google Sheet Updated")
