import pandas as pd
from prophet import Prophet
import httpx
from datetime import datetime

async def get_tvl_history(protocol_slug: str, days: int = 90) -> pd.DataFrame:
    """Fetch historical TVL data for a protocol."""
    url = f"https://api.llama.fi/protocol/{protocol_slug}"
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        data = r.json()["tvl"]

    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"], unit="s")
    df = df.rename(columns={"date": "ds", "totalLiquidityUSD": "y"})
    return df[["ds", "y"]].dropna()

def forecast_tvl(df: pd.DataFrame, future_days: int = 7) -> float:
    """Forecast future TVL using Prophet."""
    model = Prophet()
    model.fit(df)
    future = model.make_future_dataframe(periods=future_days)
    forecast = model.predict(future)
    return round(float(forecast["yhat"].iloc[-1]), 2)

# Example usage
async def display_tvl_forecast(protocol_slug: str):
    """Display current and forecasted TVL for a protocol."""
    df = await get_tvl_history(protocol_slug)
    current_tvl = df["y"].iloc[-1]
    forecasted_tvl = forecast_tvl(df)
    delta = forecasted_tvl - current_tvl
    print(f"Current TVL: ${current_tvl:,.2f}")
    print(f"Forecasted TVL: ${forecasted_tvl:,.2f}")
    print(f"Change: {delta:+,.2f}")

# If used with a UI component like Streamlit's st.metric, you could do:
# st.metric("TVL Forecast (7d)", f"${forecasted_tvl:,.2f}", delta=f"{delta:+,.2f}")
