"""
Tests for scenario_simulator.simulate_upgrade_scenario().
"""

import pytest

from scenario_simulator import simulate_upgrade_scenario


class TestSimulateUpgradeScenario:
    """Core behaviour of the scenario simulator."""

    def test_returns_required_keys(self):
        result = simulate_upgrade_scenario({"upgrade": "X", "chain": "Ethereum"})
        assert "impact_score" in result
        assert "risk_category" in result
        assert "factors" in result
        assert "recommendations" in result

    def test_impact_score_in_range(self):
        result = simulate_upgrade_scenario({"upgrade": "X", "chain": "Ethereum"})
        assert 0 <= result["impact_score"] <= 100

    def test_risk_category_valid(self):
        result = simulate_upgrade_scenario({"upgrade": "X", "chain": "Ethereum"})
        assert result["risk_category"] in {"Low", "Medium", "High", "Critical"}


class TestUpgradeTypes:
    """Different upgrade types produce different risk levels."""

    def test_parameter_change_is_low(self):
        result = simulate_upgrade_scenario({
            "upgrade": "X", "chain": "Ethereum",
            "upgrade_type": "parameter_change", "market_condition": "neutral",
        })
        assert result["impact_score"] < 50

    def test_emergency_is_high(self):
        result = simulate_upgrade_scenario({
            "upgrade": "X", "chain": "Ethereum",
            "upgrade_type": "emergency", "market_condition": "crisis",
        })
        assert result["impact_score"] > 60


class TestMarketConditions:
    """Market conditions affect the risk score."""

    def test_bullish_lower_than_crisis(self):
        bullish = simulate_upgrade_scenario({
            "upgrade": "X", "chain": "Ethereum",
            "upgrade_type": "governance", "market_condition": "bullish",
        })
        crisis = simulate_upgrade_scenario({
            "upgrade": "X", "chain": "Ethereum",
            "upgrade_type": "governance", "market_condition": "crisis",
        })
        assert bullish["impact_score"] < crisis["impact_score"]


class TestCustomWeights:
    """Custom factor weights override defaults."""

    def test_custom_weights_applied(self):
        # Give all weight to volatility with a known override
        result = simulate_upgrade_scenario(
            {"upgrade": "X", "chain": "Ethereum", "volatility_override": 1.0},
            weights={"volatility": 1.0, "sentiment": 0.0, "governance": 0.0, "technical": 0.0},
        )
        assert result["impact_score"] == 100.0

    def test_zero_weights_give_zero(self):
        result = simulate_upgrade_scenario(
            {"upgrade": "X", "chain": "Ethereum"},
            weights={"volatility": 0.0, "sentiment": 0.0, "governance": 0.0, "technical": 0.0},
        )
        assert result["impact_score"] == 0.0


class TestEdgeCases:
    """Edge cases and missing parameters."""

    def test_missing_chain_defaults(self):
        result = simulate_upgrade_scenario({"upgrade": "X"})
        assert result["impact_score"] >= 0

    def test_unknown_upgrade_type(self):
        result = simulate_upgrade_scenario({
            "upgrade": "X", "chain": "Ethereum",
            "upgrade_type": "completely_unknown",
        })
        # Should fall back to default score, not crash
        assert 0 <= result["impact_score"] <= 100

    def test_unknown_market_condition(self):
        result = simulate_upgrade_scenario({
            "upgrade": "X", "chain": "Ethereum",
            "market_condition": "unknown_condition",
        })
        assert 0 <= result["impact_score"] <= 100

    def test_overrides_take_precedence(self):
        result = simulate_upgrade_scenario({
            "upgrade": "X", "chain": "Ethereum",
            "volatility_override": 0.0,
            "sentiment_override": 0.0,
        })
        # With vol and sentiment at 0, score should be lower
        assert result["impact_score"] < 50

    def test_recommendations_is_list(self):
        result = simulate_upgrade_scenario({"upgrade": "X", "chain": "Ethereum"})
        assert isinstance(result["recommendations"], list)
        assert len(result["recommendations"]) >= 1

    def test_factors_has_all_keys(self):
        result = simulate_upgrade_scenario({"upgrade": "X", "chain": "Ethereum"})
        for key in ("volatility", "sentiment", "governance", "technical"):
            assert key in result["factors"]
