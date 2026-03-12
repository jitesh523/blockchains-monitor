"""
validation.py
Input and data validation using Pydantic models.

Provides structured validation for blockchain events, alert requests,
and other API inputs with clear error messages.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

# Known chains supported by the system
SUPPORTED_CHAINS = {"ethereum", "polygon", "arbitrum"}

# Known event types
VALID_EVENT_TYPES = {"upgrade", "governance", "parameter_change", "emergency", "fork", "migration"}


class BlockchainEvent(BaseModel):
    """Validated blockchain event payload."""

    type: str = Field(..., min_length=1, max_length=64, description="Event type")
    chain: str = Field(..., min_length=1, max_length=64, description="Blockchain network name")
    upgrade: Optional[str] = Field(None, max_length=128, description="Upgrade or proposal identifier")
    timestamp: Optional[datetime] = Field(None, description="Event timestamp (ISO-8601)")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Arbitrary extra data")

    @field_validator("type")
    @classmethod
    def type_must_be_known(cls, v: str) -> str:
        v_lower = v.strip().lower()
        if v_lower not in VALID_EVENT_TYPES:
            raise ValueError(f"Unknown event type '{v}'. Must be one of: {', '.join(sorted(VALID_EVENT_TYPES))}")
        return v_lower

    @field_validator("chain")
    @classmethod
    def chain_must_be_known(cls, v: str) -> str:
        v_lower = v.strip().lower()
        if v_lower not in SUPPORTED_CHAINS:
            raise ValueError(f"Unsupported chain '{v}'. Must be one of: {', '.join(sorted(SUPPORTED_CHAINS))}")
        return v_lower


class AlertRequest(BaseModel):
    """Validated alert request payload."""

    title: str = Field(..., min_length=1, max_length=256)
    message: str = Field(..., min_length=1, max_length=4096)
    channel: str = Field("email", pattern=r"^(email|slack|webhook|telegram)$")
    severity: str = Field("info", pattern=r"^(info|warning|critical)$")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


def validate_chain_name(chain: str) -> bool:
    """Check if a chain name is in the supported set."""
    return chain.strip().lower() in SUPPORTED_CHAINS


def validate_event_data(event: dict) -> bool:
    """Backward-compatible validation wrapper.

    Returns True if the event dict conforms to the BlockchainEvent schema,
    False otherwise.
    """
    if not isinstance(event, dict):
        return False
    try:
        BlockchainEvent(**event)
        return True
    except Exception:
        return False


def validate_event_data_strict(event: dict) -> BlockchainEvent:
    """Strict validation that returns a validated BlockchainEvent or raises."""
    return BlockchainEvent(**event)


if __name__ == "__main__":
    # Quick smoke test
    print(validate_event_data({"type": "upgrade", "chain": "Ethereum"}))  # True
    print(validate_event_data({"type": "unknown", "chain": "Ethereum"}))  # False
    print(validate_event_data({"type": "upgrade"}))  # False — missing chain

    evt = validate_event_data_strict({"type": "governance", "chain": "Polygon", "upgrade": "PIP-42"})
    print(f"Validated: {evt}")
