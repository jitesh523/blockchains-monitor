"""
Tests for integrated model sanity checks.
Migrated from legacy test_integrated_models.py to Pytest.
"""

import sys
from unittest.mock import MagicMock

_MOCK_MODULES = ["httpx", "transformers", "torch", "arch", "prophet"]
for mod_name in _MOCK_MODULES:
    if mod_name not in sys.modules:
        sys.modules[mod_name] = MagicMock()

from unittest.mock import patch, MagicMock

import pytest

from src.models.liquidity_model import forecast_tvl
from src.models.risk_model import get_risk_assessment
from src.models.sentiment_model import get_sentiment_for_protocol
from src.models.volatility_model import get_protocol_volatility
import asyncio
import pandas as pd


@patch("src.models.volatility_model.get_prices")
def test_integrated_volatility(mock_get_prices):
    """Test volatility fetcher integration."""
    # Build sufficient mock data
    mock_get_prices.return_value = pd.Series([1000 + i for i in range(40)])
    res = asyncio.run(get_protocol_volatility("uniswap"))
    assert "volatility" in res
    assert res["token_id"] == "uniswap"
    assert res["data_points"] == 40


def test_integrated_sentiment():
    """Test sentiment high-level integrated call."""
    res = get_sentiment_for_protocol("aave")
    assert res["protocol"] == "aave"
    assert "average_sentiment" in res
    assert "positive_count" in res


@patch("src.models.liquidity_model.Prophet")
def test_integrated_liquidity(mock_prophet_class):
    """Test liquidity TVL forecasting component."""
    df = pd.DataFrame({
        "ds": pd.date_range(start="1/1/2023", periods=30),
        "y": [1000 + i*10 for i in range(30)]
    })
    
    # Mock prophet output correctly
    mock_model = mock_prophet_class.return_value
    mock_future = MagicMock()
    mock_model.make_future_dataframe.return_value = mock_future
    # Mock the dataframe returned by model.predict
    mock_pred_df = pd.DataFrame({"yhat": [1500.0]})
    mock_model.predict.return_value = mock_pred_df
    
    forecasted = forecast_tvl(df)
    assert isinstance(forecasted, float)
    assert forecasted == 1500.0


@patch("src.models.risk_model.get_protocol_volatility")
@patch("src.models.risk_model.get_sentiment_for_protocol")
def test_integrated_risk_assessment(mock_sent, mock_vol):
    """Test that risk_model weaves together inputs successfully."""
    mock_vol.return_value = {"volatility": 40.0}
    mock_sent.return_value = {"average_sentiment": -0.2}
    
    res = asyncio.run(get_risk_assessment("ethereum"))
    
    assert res["protocol"] == "ethereum"
    assert "overall_risk_score" in res
    assert "risk_category" in res
    assert "components" in res
    assert "volatility" in res["components"]
    assert "sentiment" in res["components"]
