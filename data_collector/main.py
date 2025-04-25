import asyncio
from data_collector.yahoo_fetcher import fetch_latest_price
from storage.save_parquet import append_to_parquet

TICKERS = ["AAPL", "MSFT", "BTC-USD","SPY","ETH-USD"]

async def fetch_and_store(ticker):
    while True:
        data = fetch_latest_price(ticker)
        if data:
            print(f"[{data['timestamp']}] {ticker} : {data['price']}")
            append_to_parquet(data)
        await asyncio.sleep(60)  # 1 min interval

async def main():
    tasks = [fetch_and_store(ticker) for ticker in TICKERS]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
