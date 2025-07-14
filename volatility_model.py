"""
volatility_model.py
Fetches ETH price data from CoinGecko and runs a GARCH(1,1) volatility forecast.
Requires: pandas, requests, arch. Install with pip if not already present.
"""
import requests
import pandas as pd
from arch import arch_model
import datetime

COINGECKO_API = "https://api.coingecko.com/api/v3"

def fetch_eth_prices(days=180):
    # Fetch last 'days' of daily ETH prices
    url = f"{COINGECKO_API}/coins/ethereum/market_chart"
    params = {"vs_currency": "usd", "days": days, "interval": "daily"}
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    prices = resp.json()["prices"]  # [ [timestamp, price], ... ]
    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["date"] = pd.to_datetime(df["timestamp"], unit="ms")
    df = df.set_index("date")
    return df["price"]

def compute_garch_volatility(prices):
    log_ret = pd.Series(prices).pct_change().dropna()
    model = arch_model(log_ret * 100, vol="Garch", p=1, q=1, dist="normal")
    res = model.fit(disp="off")
    # Forecast the next day's volatility (annualized)
    forecast = res.forecast(horizon=1)
    next_vol = forecast.variance.values[-1, 0] ** 0.5
    annualized_vol = next_vol * (252**0.5)  # 252 trading days
    return annualized_vol

if __name__ == "__main__":
    prices = fetch_eth_prices(days=180)
    vol = compute_garch_volatility(prices)
    print(f"GARCH(1,1) ETH annualized volatility forecast: {vol:.2f}%")

