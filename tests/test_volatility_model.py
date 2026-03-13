"""
Tests for src.models.volatility_model
Migrated from legacy test_volatility.py print script to Pytest.
"""

import sys
from unittest.mock import MagicMock

_MOCK_MODULES = ["httpx", "arch"]
for mod_name in _MOCK_MODULES:
    if mod_name not in sys.modules:
        sys.modules[mod_name] = MagicMock()

import math
from unittest.mock import patch

from src.models.volatility_model import (
    forecast_volatility,
    format_metric_value,
    format_volatility,
    get_token_mapping,
    get_volatility_color
)

import numpy as np
import pandas as pd
import pytest


def test_forecast_volatility_insufficient_data():
    """Test that GARCH forecast returns NaN if data is too short."""
    short_prices = pd.Series([1000, 1050, 1100])
    res = forecast_volatility(short_prices)
    assert math.isnan(res)


@patch("src.models.volatility_model.arch_model")
def test_forecast_volatility_success(mock_arch):
    """Test GARCH volatility forecast happy path."""
    # Mocking arch_model responses
    mock_res = mock_arch.return_value.fit.return_value
    mock_res.forecast.return_value.variance.iloc.__getitem__.return_value.mean.return_value = 1.5
    
    # 30+ prices
    prices = pd.Series([1000 + i for i in range(40)])
    
    vol = forecast_volatility(prices)
    
    # sqrt(1.5) * sqrt(252) approx 19.44
    assert round(vol, 1) == 19.4


def test_get_token_mapping():
    """Test name-to-coingecko ID mapping."""
    assert get_token_mapping("uniswap") == "uniswap"
    assert get_token_mapping("compound") == "compound-governance-token"
    assert get_token_mapping("unknown_proto") == "ethereum"


def test_format_volatility():
    """Test UI formatting of volatility strings."""
    assert format_volatility(float('nan')) == "--"
    assert format_volatility(None) == "--"
    assert format_volatility(15.42) == "15.4%"


def test_format_metric_value():
    """Test general metric formatter."""
    assert format_metric_value(float('nan')) == "--"
    assert format_metric_value(1234.56, suffix="M") == "1234.6M"
    assert format_metric_value("text") == "text"


def test_get_volatility_color():
    """Test volatility bucket color codes."""
    assert get_volatility_color(float('nan')) == "⚪"
    assert get_volatility_color(20.0) == "🟢"
    assert get_volatility_color(45.0) == "🟡"
    assert get_volatility_color(80.0) == "🔴"
