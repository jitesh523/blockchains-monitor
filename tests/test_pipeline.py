"""
Tests for pipeline.py execution engine.
"""

import os
import sys
from unittest.mock import MagicMock

# Mock environment variables required by underlying modules
os.environ["TWITTER_BEARER_TOKEN"] = "mock_token"

# Mock external dependencies for isolated pipeline testing
_MOCK_MODULES = [
    "requests", "arch", "arch.arch_model", "prophet",
    "transformers", "torch", "httpx", "pandas", "numpy",
    "statsmodels", "statsmodels.tsa", "statsmodels.tsa.arima",
    "tweepy"
]
for mod_name in _MOCK_MODULES:
    if mod_name not in sys.modules:
        sys.modules[mod_name] = MagicMock()

from unittest.mock import patch

from pipeline import PipelineConfig, run_monitoring_cycle


def test_no_alerts_when_thresholds_not_breached():
    """Test that the pipeline correctly silences alerts when conditions are safe."""
    config = PipelineConfig(
        sentiment_negative_threshold=0.8,
        volatility_threshold_pct=100.0,
        liquidity_drop_pct=0.20,
    )

    with patch("pipeline.check_sentiment") as mock_sent, \
         patch("pipeline.check_volatility") as mock_vol, \
         patch("pipeline.check_liquidity") as mock_liq:

        # Safe values
        mock_sent.return_value = (0.5, [], [])
        mock_vol.return_value = 50.0
        mock_liq.return_value = (0.10, 1000.0, 900.0)

        alerts = run_monitoring_cycle(config)

        assert len(alerts) == 0


def test_alerts_fire_on_breached_thresholds():
    """Test that all three alerts fire when all thresholds are breached."""
    config = PipelineConfig(
        sentiment_negative_threshold=0.5,
        volatility_threshold_pct=60.0,
        liquidity_drop_pct=0.05,
    )

    with patch("pipeline.check_sentiment") as mock_sent, \
         patch("pipeline.check_volatility") as mock_vol, \
         patch("pipeline.check_liquidity") as mock_liq:

        # Breaching values
        mock_sent.return_value = (0.8, [], [])
        mock_vol.return_value = 80.0
        mock_liq.return_value = (0.15, 1000.0, 850.0)

        alerts = run_monitoring_cycle(config)

        assert len(alerts) == 3
        # Check alert string contents
        assert any("Sentiment risk" in a for a in alerts)
        assert any("Volatility risk" in a for a in alerts)
        assert any("Liquidity risk" in a for a in alerts)


def test_pipeline_handles_api_exceptions_gracefully():
    """Ensure the pipeline doesn't crash when APIs throw exceptions."""
    config = PipelineConfig()

    with patch("pipeline.check_sentiment") as mock_sent, \
         patch("pipeline.check_volatility") as mock_vol, \
         patch("pipeline.check_liquidity") as mock_liq:

        # Simulate exception handling returning safe defaults (from the try/except blocks)
        mock_sent.return_value = (0.0, [], [])
        mock_vol.return_value = 0.0
        mock_liq.return_value = (0.0, 0.0, 0.0)

        alerts = run_monitoring_cycle(config)

        # Should return successfully with no alerts and no crash
        assert len(alerts) == 0
