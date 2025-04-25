import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import os

def append_to_parquet(data: dict, folder: str = "data/"):
    os.makedirs(folder, exist_ok=True)
    
    ticker = data["ticker"]
    filename = os.path.join(folder, f"{ticker}.parquet")

    df = pd.DataFrame([data])
    table = pa.Table.from_pandas(df)

    if not os.path.exists(filename):
        pq.write_table(table, filename)
    else:
        existing = pq.read_table(filename).to_pandas()
        combined = pd.concat([existing, df], ignore_index=True)
        pq.write_table(pa.Table.from_pandas(combined), filename)
