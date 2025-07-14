"""
liquidity_model.py
Fetch historical TVL data for a DeFi protocol from DeFi Llama, forecast TVL using Prophet.
Requirements: requests, pandas, prophet (install prophet via pip, it's fbprophet or prophet depending on version)
"""
import requests
import pandas as pd
from prophet import Prophet
import datetime

def fetch_tvl(protocol: str = "curve"):
    url = f"https://api.llama.fi/protocol/{protocol}"
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    tvl = data.get("tvl", data.get("tvlHistory", []))
    if isinstance(tvl, dict):  # some protocols use chain:history dict
        # Choose 'ethereum' chain if exists or any
        tvl = next(iter(tvl.values()))
    df = pd.DataFrame(tvl)
    if "date" in df.columns:
        df["ds"] = pd.to_datetime(df["date"], unit="s")
    elif "timestamp" in df.columns:
        df["ds"] = pd.to_datetime(df["timestamp"], unit="s")
    else:
        raise Exception("TVL data missing date column")
    df["y"] = df["totalLiquidityUSD"] if "totalLiquidityUSD" in df.columns else df["tvl"]
    # Only keep ds and y columns
    df = df[["ds", "y"]]
    return df

def forecast_tvl(df, days=7):
    m = Prophet()
    m.fit(df)
    future = m.make_future_dataframe(periods=days)
    forecast = m.predict(future)
    return forecast.tail(days)[["ds", "yhat", "yhat_lower", "yhat_upper"]]

if __name__ == "__main__":
    # Use the correct slug for Curve
    df = fetch_tvl("curve-dex")
    result = forecast_tvl(df, days=7)
    print("7-day TVL forecast:")
    print(result)

