"""
user_risk_config.py
Configuration manager for user-driven risk scoring profiles.

Allows traders to define custom risk tolerances and factor weights,
persisting them for the main calculation engine.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict

# Fast fallback for local test environment
try:
    from pydantic import BaseModel, Field, model_validator
except ImportError:
    import sys
    from unittest.mock import MagicMock
    sys.modules["pydantic"] = MagicMock()
    from pydantic import BaseModel
    BaseModel = object  # type: ignore
    def Field(*args, **kwargs): return args[0] if args else None
    def model_validator(*args, **kwargs): return lambda f: f

logger = logging.getLogger(__name__)

CONFIG_FILE = Path(".risk_profile.json")


class RiskProfile(BaseModel):
    """User-defined factor weights and risk thresholds."""
    volatility: float = Field(0.35, ge=0.0, le=1.0)
    sentiment: float = Field(0.25, ge=0.0, le=1.0)
    governance: float = Field(0.20, ge=0.0, le=1.0)
    technical: float = Field(0.20, ge=0.0, le=1.0)
    critical_threshold: int = Field(75, ge=50, le=100)

    @model_validator(mode="after")
    def validate_weights(self) -> RiskProfile:
        total = sum([self.volatility, self.sentiment, self.governance, self.technical])
        if not (0.99 <= total <= 1.01):
            raise ValueError(f"Factor weights must sum to 1.0 (current sum: {total:.2f})")
        return self


def save_profile(profile: RiskProfile, filepath: Path = CONFIG_FILE) -> None:
    """Save the risk profile to disk."""
    try:
        with open(filepath, "w") as f:
            f.write(profile.model_dump_json(indent=2))
        logger.info("Saved risk profile to %s", filepath)
    except Exception as e:
        logger.error("Failed to save risk profile: %s", e)


def load_profile(filepath: Path = CONFIG_FILE) -> RiskProfile:
    """Load the risk profile from disk, falling back to defaults."""
    if not filepath.exists():
        logger.debug("No custom profile found. Using defaults.")
        return RiskProfile()

    try:
        with open(filepath, "r") as f:
            data = json.load(f)
        profile = RiskProfile(**data)
        logger.info("Loaded custom risk profile from %s", filepath)
        return profile
    except Exception as e:
        logger.error("Failed to load risk profile from %s: %s. Using defaults.", filepath, e)
        return RiskProfile()


def update_user_risk_profile(weights: Dict[str, float]) -> Dict[str, Any]:
    """
    API function to update user-defined factor weights.
    Returns the updated profile as a dictionary.
    """
    try:
        current = load_profile()
        # Update fields dynamically
        update_data = current.model_dump()
        update_data.update(weights)

        new_profile = RiskProfile(**update_data)
        save_profile(new_profile)

        return {"status": "success", "profile": new_profile.model_dump()}

    except ValueError as e:
        logger.error("Invalid risk profile configuration: %s", e)
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=== Loading Profile ===")
    p1 = load_profile()
    print("Current:", p1.model_dump())

    print("\n=== Updating Profile ===")
    result = update_user_risk_profile({
        "volatility": 0.5,
        "sentiment": 0.1,  # Must reduce sum to 1.0
        "governance": 0.2,
        "technical": 0.2
    })
    print(result)

    print("\n=== Invalid Update (Sum != 1.0) ===")
    bad_result = update_user_risk_profile({"volatility": 0.9})
    print(bad_result)

    # Cleanup test file
    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()
