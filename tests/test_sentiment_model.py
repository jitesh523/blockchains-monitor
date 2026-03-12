"""
Tests for src.models.sentiment_model
Migrated from legacy test_sentiment.py print script to Pytest.
"""

import sys
from unittest.mock import MagicMock

_MOCK_MODULES = ["transformers", "torch"]
for mod_name in _MOCK_MODULES:
    if mod_name not in sys.modules:
        sys.modules[mod_name] = MagicMock()

from unittest.mock import patch, MagicMock
from src.models.sentiment_model import (
    analyze_sentiment,
    analyze_sentiment_detailed,
    categorize_sentiment,
    get_sentiment_color,
    get_sentiment_for_protocol
)


def test_analyze_sentiment_empty():
    """Test handling of empty text lists."""
    assert analyze_sentiment([]) == 0.0


@patch("src.models.sentiment_model.sentiment_pipeline")
def test_analyze_sentiment_positive(mock_pipeline):
    """Test scoring of explicitly positive texts."""
    mock_pipeline.return_value = [
        {"label": "POSITIVE", "score": 0.95},
        {"label": "POSITIVE", "score": 0.85}
    ]
    texts = ["Great upgrade!", "Bullish."]
    score = analyze_sentiment(texts)
    assert score == 0.90


@patch("src.models.sentiment_model.sentiment_pipeline")
def test_analyze_sentiment_negative(mock_pipeline):
    """Test scoring of negative texts."""
    mock_pipeline.return_value = [
        {"label": "NEGATIVE", "score": 0.9},
        {"label": "NEGATIVE", "score": 0.8}
    ]
    texts = ["Terrible upgrade", "Selling my bags"]
    score = analyze_sentiment(texts)
    assert score == -0.85


@patch("src.models.sentiment_model.sentiment_pipeline")
def test_analyze_sentiment_detailed(mock_pipeline):
    """Test detailed breakdown of sentiments."""
    mock_pipeline.return_value = [
        {"label": "POSITIVE", "score": 0.90},
        {"label": "NEGATIVE", "score": 0.70}
    ]
    texts = ["Good stuff", "Bad stuff"]
    res = analyze_sentiment_detailed(texts)
    
    assert res["average_sentiment"] == 0.10  # (0.9 - 0.7) / 2
    assert res["positive_count"] == 1
    assert res["negative_count"] == 1
    assert res["total_texts"] == 2
    assert len(res["individual_scores"]) == 2


def test_categorize_sentiment():
    """Test standard categorization bands."""
    assert categorize_sentiment(0.5) == "Very Positive"
    assert categorize_sentiment(0.2) == "Positive"
    assert categorize_sentiment(0.0) == "Neutral"
    assert categorize_sentiment(-0.2) == "Negative"
    assert categorize_sentiment(-0.5) == "Very Negative"


def test_get_sentiment_color():
    """Test visual color mapping."""
    assert get_sentiment_color(0.5) == "🟢"
    assert get_sentiment_color(0.2) == "🟡"
    assert get_sentiment_color(-0.4) == "🔴"


def test_get_sentiment_for_protocol():
    """Test high-level protocol sentiment fetcher."""
    res = get_sentiment_for_protocol("uniswap")
    assert "average_sentiment" in res
    assert "positive_count" in res
    assert "protocol" in res
    assert res["protocol"] == "uniswap"
    assert "timestamp" in res
