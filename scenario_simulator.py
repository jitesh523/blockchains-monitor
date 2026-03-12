"""
scenario_simulator.py
Simulate the impact of blockchain protocol upgrades on risk metrics.

Given a set of scenario parameters (chain, upgrade type, market conditions),
compute a composite risk-impact score and return a structured result
with a risk breakdown and actionable recommendations.
"""
from __future__ import annotations

import logging
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Default factor weights (must sum to 1.0)
_DEFAULT_WEIGHTS = {
    "volatility": 0.35,
    "sentiment": 0.25,
    "governance": 0.20,
    "technical": 0.20,
}

# Lookup tables for sub-factor scoring (0–1 scale, higher = riskier)
_UPGRADE_TYPE_SCORES: Dict[str, float] = {
    "parameter_change": 0.25,
    "governance": 0.35,
    "implementation_upgrade": 0.65,
    "migration": 0.75,
    "fork": 0.85,
    "emergency": 0.95,
}

_MARKET_CONDITION_SCORES: Dict[str, float] = {
    "bullish": 0.20,
    "neutral": 0.40,
    "bearish": 0.65,
    "volatile": 0.80,
    "crisis": 0.95,
}

_CHAIN_COMPLEXITY: Dict[str, float] = {
    "ethereum": 0.50,
    "polygon": 0.35,
    "arbitrum": 0.40,
}


@dataclass
class ScenarioResult:
    """Structured output of a scenario simulation."""

    impact_score: float  # 0–100
    risk_category: str
    factors: Dict[str, float]
    recommendations: List[str]
    params: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _categorize(score: float) -> str:
    if score <= 25:
        return "Low"
    if score <= 50:
        return "Medium"
    if score <= 75:
        return "High"
    return "Critical"


def simulate_upgrade_scenario(
    params: Dict[str, Any],
    *,
    weights: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """Simulate a protocol upgrade scenario and return a risk assessment.

    Parameters
    ----------
    params : dict
        Must include:
        - ``chain`` (str): blockchain name
        - ``upgrade`` (str): upgrade identifier
        Optional:
        - ``upgrade_type`` (str): one of _UPGRADE_TYPE_SCORES keys
        - ``market_condition`` (str): one of _MARKET_CONDITION_SCORES keys
        - ``volatility_override`` (float): 0–1 custom volatility score
        - ``sentiment_override`` (float): 0–1 custom sentiment score
    weights : dict, optional
        Custom factor weights. Defaults to ``_DEFAULT_WEIGHTS``.

    Returns
    -------
    dict  (ScenarioResult as dict)
    """
    w = weights or _DEFAULT_WEIGHTS

    chain = str(params.get("chain", "ethereum")).lower()
    upgrade_type = str(params.get("upgrade_type", "governance")).lower()
    market = str(params.get("market_condition", "neutral")).lower()

    # --- Individual factor scores (0–1) ---
    volatility_score = params.get(
        "volatility_override",
        _MARKET_CONDITION_SCORES.get(market, 0.40) * 0.6
        + _CHAIN_COMPLEXITY.get(chain, 0.50) * 0.4,
    )

    sentiment_score = params.get(
        "sentiment_override",
        _MARKET_CONDITION_SCORES.get(market, 0.40),
    )

    governance_score = _UPGRADE_TYPE_SCORES.get(upgrade_type, 0.35)

    technical_score = (
        _UPGRADE_TYPE_SCORES.get(upgrade_type, 0.35) * 0.6
        + _CHAIN_COMPLEXITY.get(chain, 0.50) * 0.4
    )

    factors = {
        "volatility": round(volatility_score, 3),
        "sentiment": round(sentiment_score, 3),
        "governance": round(governance_score, 3),
        "technical": round(technical_score, 3),
    }

    # --- Weighted composite (0–100) ---
    composite = sum(factors[k] * w.get(k, 0) for k in factors)
    impact_score = round(min(max(composite * 100, 0), 100), 2)

    # --- Recommendations ---
    recs: List[str] = []
    if impact_score >= 75:
        recs.append("🔥 Critical risk — consider delaying or exiting positions")
    elif impact_score >= 50:
        recs.append("🚨 High risk — reduce exposure and set stop-losses")
    elif impact_score >= 25:
        recs.append("⚠️ Medium risk — monitor closely before acting")
    else:
        recs.append("✅ Low risk — proceed with standard position sizing")

    if volatility_score > 0.6:
        recs.append("📊 Expect elevated volatility — use tighter risk limits")
    if governance_score > 0.6:
        recs.append("🏛️ Complex governance upgrade — review proposal details")
    if technical_score > 0.6:
        recs.append("🔧 Technical complexity is high — watch for deployment issues")

    result = ScenarioResult(
        impact_score=impact_score,
        risk_category=_categorize(impact_score),
        factors=factors,
        recommendations=recs,
        params=params,
    )

    logger.info("Scenario simulation: %s → %.1f (%s)", params.get("upgrade"), impact_score, result.risk_category)
    return result.to_dict()


if __name__ == "__main__":
    # Quick demo
    scenarios = [
        {"upgrade": "EIP-9999", "chain": "Ethereum", "upgrade_type": "parameter_change", "market_condition": "neutral"},
        {"upgrade": "Emergency-Fix", "chain": "Arbitrum", "upgrade_type": "emergency", "market_condition": "crisis"},
        {"upgrade": "PIP-42", "chain": "Polygon", "upgrade_type": "governance", "market_condition": "bullish"},
    ]
    for s in scenarios:
        result = simulate_upgrade_scenario(s)
        print(f"\n{s['upgrade']} on {s['chain']}:")
        print(f"  Impact: {result['impact_score']} ({result['risk_category']})")
        for r in result["recommendations"]:
            print(f"  {r}")
