import requests
import pandas as pd

BASE = "https://iss.moex.com/iss"

def fetch_candles(engine: str, market: str, security: str, interval: int, limit: int = 120) -> pd.DataFrame:
    """
    interval: 15, 60 etc (minutes)
    """
    url = f"{BASE}/engines/{engine}/markets/{market}/securities/{security}/candles.json"
    params = {"interval": interval, "limit": limit}
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    data = r.json()

    cols = data["candles"]["columns"]
    rows = data["candles"]["data"]
    df = pd.DataFrame(rows, columns=cols)

    # приведение типов
    for c in ["open", "close", "high", "low", "value", "volume"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    return df.dropna(subset=["open", "close", "high", "low"])
