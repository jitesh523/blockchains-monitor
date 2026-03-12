"""
mock_mode.py
Realistic mock data generators for offline demonstration and testing.

Provides deterministic, seed-controlled demo data for events, risk
assessments, and volatility without requiring API keys.
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

_CHAINS = ["Ethereum", "Polygon", "Arbitrum"]
_UPGRADE_TYPES = ["governance", "parameter_change", "implementation_upgrade", "fork", "emergency"]
_RISK_LEVELS = ["low", "medium", "high", "critical"]
_PROTOCOLS = ["Uniswap", "Aave", "Compound", "ENS", "Curve", "MakerDAO", "Lido"]

_UPGRADE_NAMES = [
    "EIP-4844", "EIP-7702", "PIP-42", "AIP-301",
    "CRV-Gauge-Rebalance", "MKR-Rate-Adjustment",
    "LDO-Oracle-Update", "UNI-Fee-Tier-Proposal",
    "ENS-Name-Wrapper-V2", "COMP-Reserve-Factor",
]


def mock_event_feed(count: int = 10, seed: int = 42) -> List[Dict[str, Any]]:
    """Generate a list of realistic timestamped blockchain events.

    Parameters
    ----------
    count : int
        Number of events to generate.
    seed : int
        Random seed for reproducible output.
    """
    rng = random.Random(seed)
    now = datetime.now(timezone.utc)
    events = []

    for i in range(count):
        chain = rng.choice(_CHAINS)
        events.append({
            "upgrade": rng.choice(_UPGRADE_NAMES),
            "chain": chain,
            "protocol": rng.choice(_PROTOCOLS),
            "type": rng.choice(_UPGRADE_TYPES),
            "risk": rng.choice(_RISK_LEVELS),
            "timestamp": (now - timedelta(hours=rng.randint(1, 720))).isoformat(),
            "block_number": rng.randint(18_000_000, 22_000_000),
        })

    return events


def mock_risk_assessment(protocol: str = "Ethereum", seed: int = 42) -> Dict[str, Any]:
    """Generate a realistic risk assessment for a protocol."""
    rng = random.Random(seed)
    risk_score = round(rng.uniform(10, 90), 2)

    if risk_score <= 25:
        category = "Low"
    elif risk_score <= 50:
        category = "Medium"
    elif risk_score <= 75:
        category = "High"
    else:
        category = "Critical"

    return {
        "protocol": protocol,
        "overall_risk_score": risk_score,
        "risk_category": category,
        "components": {
            "volatility": {"score": round(rng.uniform(0, 1), 3), "weight": 0.4},
            "sentiment": {"score": round(rng.uniform(0, 1), 3), "weight": 0.3},
            "governance": {"score": round(rng.uniform(0, 1), 3), "weight": 0.2},
            "technical": {"score": round(rng.uniform(0, 1), 3), "weight": 0.1},
        },
        "recommendations": [
            f"⚠️ {category} risk — monitor {protocol} closely",
            "📊 Review recent governance proposals before acting",
        ],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def mock_volatility_data(token: str = "ethereum", seed: int = 42) -> Dict[str, Any]:
    """Generate mock volatility data for a token."""
    rng = random.Random(seed)
    vol = round(rng.uniform(15, 85), 2)

    return {
        "token_id": token,
        "volatility": vol,
        "data_points": rng.randint(90, 180),
        "latest_price": round(rng.uniform(1000, 4000), 2),
        "price_change_24h": round(rng.uniform(-8, 8), 2),
    }


def mock_api_response(endpoint: str) -> Dict[str, Any]:
    """Return a generic mock API response."""
    return {
        "endpoint": endpoint,
        "status": "ok",
        "data": "mock_data",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    print("=== Mock Events ===")
    for evt in mock_event_feed(count=5):
        print(f"  {evt['chain']:>10} | {evt['protocol']:>10} | {evt['upgrade']} ({evt['risk']})")

    print("\n=== Mock Risk Assessment ===")
    risk = mock_risk_assessment("Uniswap")
    print(f"  {risk['protocol']}: {risk['overall_risk_score']} ({risk['risk_category']})")

    print("\n=== Mock Volatility ===")
    vol = mock_volatility_data("ethereum")
    print(f"  {vol['token_id']}: {vol['volatility']}% vol, ${vol['latest_price']}")
