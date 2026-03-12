"""
Tests for src.models.risk_model — RiskAssessment scoring logic.

Tests the pure scoring/normalization functions in isolation without
requiring heavy ML or network dependencies.
"""

import sys
from unittest.mock import MagicMock

# Mock all heavy dependencies that are not installed in the test env.
# This allows us to import the risk_model module without needing
# transformers, torch, httpx, arch, prophet, etc.
_MOCK_MODULES = [
    "transformers", "torch", "prophet",
    "httpx", "arch", "arch.arch_model",
    "statsmodels", "statsmodels.tsa", "statsmodels.tsa.arima",
    "tweepy",
]
for mod_name in _MOCK_MODULES:
    if mod_name not in sys.modules:
        sys.modules[mod_name] = MagicMock()

import numpy as np
import pytest

from src.models.risk_model import RiskAssessment


@pytest.fixture
def risk_assessor():
    return RiskAssessment()


class TestNormalizeVolatilityScore:
    """Tests for _normalize_volatility_score()."""

    def test_low_volatility(self, risk_assessor):
        assert risk_assessor._normalize_volatility_score(10.0) == 0.2

    def test_medium_volatility(self, risk_assessor):
        assert risk_assessor._normalize_volatility_score(40.0) == 0.5

    def test_high_volatility(self, risk_assessor):
        score = risk_assessor._normalize_volatility_score(80.0)
        assert score == 0.8

    def test_very_high_volatility_capped(self, risk_assessor):
        score = risk_assessor._normalize_volatility_score(150.0)
        assert score <= 1.0

    def test_nan_returns_default(self, risk_assessor):
        assert risk_assessor._normalize_volatility_score(np.nan) == 0.5

    def test_zero_returns_default(self, risk_assessor):
        assert risk_assessor._normalize_volatility_score(0) == 0.5

    def test_negative_returns_default(self, risk_assessor):
        assert risk_assessor._normalize_volatility_score(-5) == 0.5


class TestNormalizeSentimentScore:
    """Tests for _normalize_sentiment_score()."""

    def test_positive_sentiment_low_risk(self, risk_assessor):
        # sentiment=+1 → risk should be low (close to 0)
        score = risk_assessor._normalize_sentiment_score(1.0)
        assert score == 0.0

    def test_negative_sentiment_high_risk(self, risk_assessor):
        # sentiment=-1 → risk should be high (close to 1)
        score = risk_assessor._normalize_sentiment_score(-1.0)
        assert score == 1.0

    def test_neutral_sentiment(self, risk_assessor):
        score = risk_assessor._normalize_sentiment_score(0.0)
        assert score == 0.5

    def test_clamped_above_one(self, risk_assessor):
        # out-of-range sentiment
        score = risk_assessor._normalize_sentiment_score(-2.0)
        assert score <= 1.0

    def test_clamped_below_zero(self, risk_assessor):
        score = risk_assessor._normalize_sentiment_score(2.0)
        assert score >= 0.0


class TestCategorizeRisk:
    """Tests for _categorize_risk()."""

    @pytest.mark.parametrize("score,expected", [
        (10, "Low"),
        (25, "Low"),
        (26, "Medium"),
        (50, "Medium"),
        (51, "High"),
        (75, "High"),
        (76, "Critical"),
        (100, "Critical"),
    ])
    def test_risk_categories(self, risk_assessor, score, expected):
        assert risk_assessor._categorize_risk(score) == expected


class TestGetRiskColor:
    """Tests for _get_risk_color()."""

    def test_low_is_green(self, risk_assessor):
        assert risk_assessor._get_risk_color(20) == "🟢"

    def test_medium_is_yellow(self, risk_assessor):
        assert risk_assessor._get_risk_color(40) == "🟡"

    def test_high_is_orange(self, risk_assessor):
        assert risk_assessor._get_risk_color(60) == "🟠"

    def test_critical_is_red(self, risk_assessor):
        assert risk_assessor._get_risk_color(90) == "🔴"


class TestGenerateRecommendations:
    """Tests for _generate_recommendations()."""

    def test_returns_list(self, risk_assessor):
        recs = risk_assessor._generate_recommendations(50, {"volatility": 30}, {"average_sentiment": 0})
        assert isinstance(recs, list)
        assert len(recs) >= 1

    def test_high_risk_warns(self, risk_assessor):
        recs = risk_assessor._generate_recommendations(80, {"volatility": 70}, {"average_sentiment": -0.5})
        full_text = " ".join(recs)
        assert "Critical" in full_text or "risk" in full_text.lower()

    def test_high_volatility_mentioned(self, risk_assessor):
        recs = risk_assessor._generate_recommendations(50, {"volatility": 65}, {"average_sentiment": 0})
        full_text = " ".join(recs)
        assert "volatility" in full_text.lower() or "stop loss" in full_text.lower()


class TestCompareProtocols:
    """Tests for compare_protocols()."""

    def test_empty_list(self, risk_assessor):
        assert risk_assessor.compare_protocols([]) == {}

    def test_identifies_lowest_and_highest(self, risk_assessor):
        protocols = [
            {"protocol": "A", "overall_risk_score": 20},
            {"protocol": "B", "overall_risk_score": 80},
            {"protocol": "C", "overall_risk_score": 50},
        ]
        result = risk_assessor.compare_protocols(protocols)
        assert result["lowest_risk"]["protocol"] == "A"
        assert result["highest_risk"]["protocol"] == "B"

    def test_risk_distribution(self, risk_assessor):
        protocols = [
            {"protocol": "A", "overall_risk_score": 10},
            {"protocol": "B", "overall_risk_score": 30},
            {"protocol": "C", "overall_risk_score": 60},
            {"protocol": "D", "overall_risk_score": 90},
        ]
        result = risk_assessor.compare_protocols(protocols)
        dist = result["risk_distribution"]
        assert dist["low"] == 1
        assert dist["medium"] == 1
        assert dist["high"] == 1
        assert dist["critical"] == 1
