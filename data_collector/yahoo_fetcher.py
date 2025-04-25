import yfinance as yf
from datetime import datetime

def fetch_latest_price(ticker: str) -> dict:
    data = yf.Ticker(ticker).history(period="5d", interval="1m")
    if not data.empty:
        last_row = data.iloc[-1]
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "ticker": ticker,
            "price": float(last_row["Close"])
        }
    else:
        return None

