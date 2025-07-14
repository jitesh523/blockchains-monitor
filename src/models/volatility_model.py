"""
Volatility forecasting with GARCH(1,1)

Functions
---------
get_prices(token_id:str, days:int=180) -> pd.Series
    Fetches daily price data from CoinGecko (last `days`).
forecast_volatility(prices:pd.Series, horizon:int=3) -> float
    Fits a GARCH(1,1) model and returns the annualised
    volatility (%) forecast for `horizon` days ahead.
"""

import httpx
import pandas as pd
import numpy as np
from datetime import datetime
from arch import arch_model
import logging

logger = logging.getLogger(__name__)

COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/{id}/market_chart"

async def get_prices(token_id: str, days: int = 180) -> pd.Series:
    """Fetch daily price data from CoinGecko API."""
    params = {"vs_currency": "usd", "days": days, "interval": "daily"}
    
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(COINGECKO_URL.format(id=token_id), params=params)
            r.raise_for_status()
            prices = r.json()["prices"]
        
        # CoinGecko returns [[ts, price], ...]
        s = pd.Series({datetime.utcfromtimestamp(ts/1000): p for ts, p in prices})
        s.sort_index(inplace=True)
        return s
    
    except Exception as e:
        logger.error(f"Error fetching prices for {token_id}: {e}")
        return pd.Series(dtype=float)

def forecast_volatility(prices: pd.Series, horizon: int = 3) -> float:
    """Fit GARCH(1,1) model and forecast volatility."""
    if len(prices) < 30:
        logger.warning("Price series too short for GARCH; returning NaN")
        return np.nan
    
    try:
        # Calculate log returns
        log_ret = 100 * np.log(prices / prices.shift(1)).dropna()
        
        # Fit GARCH(1,1) model
        model = arch_model(log_ret, vol="Garch", p=1, q=1, rescale=True)
        res = model.fit(disp="off")
        
        # Variance forecast → convert to daily σ, then annualise (√252)
        var_fcast = res.forecast(horizon=horizon).variance.iloc[-1].mean()
        daily_vol = np.sqrt(var_fcast)
        annual_vol = daily_vol * np.sqrt(252)
        
        return round(float(annual_vol), 2)
    
    except Exception as e:
        logger.error(f"Error forecasting volatility: {e}")
        return np.nan

def get_token_mapping(protocol_name: str) -> str:
    """Map protocol names to CoinGecko token IDs."""
    mapping = {
        'uniswap': 'uniswap',
        'aave': 'aave',
        'compound': 'compound-governance-token',
        'ens': 'ethereum-name-service',
        'ethereum': 'ethereum',
        'polygon': 'matic-network',
        'arbitrum': 'arbitrum'
    }
    
    return mapping.get(protocol_name.lower(), 'ethereum')

async def get_protocol_volatility(protocol_name: str, days: int = 180, horizon: int = 3) -> dict:
    """Get volatility forecast for a specific protocol."""
    token_id = get_token_mapping(protocol_name)
    
    try:
        prices = await get_prices(token_id, days)
        if prices.empty:
            return {'volatility': np.nan, 'error': 'No price data available'}
        
        volatility = forecast_volatility(prices, horizon)
        
        return {
            'volatility': volatility,
            'token_id': token_id,
            'data_points': len(prices),
            'latest_price': prices.iloc[-1] if not prices.empty else np.nan,
            'price_change_24h': ((prices.iloc[-1] / prices.iloc[-2]) - 1) * 100 if len(prices) > 1 else np.nan
        }
    
    except Exception as e:
        logger.error(f"Error getting protocol volatility for {protocol_name}: {e}")
        return {'volatility': np.nan, 'error': str(e)}

def format_volatility(volatility: float) -> str:
    """Format volatility value for display, handling NaN values."""
    if volatility is None or (isinstance(volatility, float) and np.isnan(volatility)):
        return "--"
    return f"{volatility:.1f}%"

def format_metric_value(value: float, suffix: str = "", fallback: str = "--") -> str:
    """Format any metric value for display, handling NaN and None values."""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return fallback
    if isinstance(value, (int, float)):
        return f"{value:.1f}{suffix}"
    return str(value)

def get_volatility_color(volatility: float) -> str:
    """Get color indicator for volatility level."""
    if volatility is None or (isinstance(volatility, float) and np.isnan(volatility)):
        return "⚪"
    if volatility < 30:
        return "🟢"
    elif volatility < 60:
        return "🟡"
    else:
        return "🔴"
