"""
user_risk_config.py
API for user-driven risk scoring and custom KPIs.
"""
from typing import Dict, Any

def user_risk_profile_config(factor_weights: Dict[str, float]) -> None:
    """
    Accept user-defined factor weights for risk model.
    """
    # Save to config, use in scoring models
    print("User risk profile weights set:", factor_weights)

if __name__ == "__main__":
    user_risk_profile_config({
        "volatility": 0.5,
        "sentiment": 0.2,
        "governance": 0.2,
        "custom": 0.1
    })

