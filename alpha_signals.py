"""
alpha_signals.py
Anomaly detection engine for trader-facing "alpha" signals.

Analyzes recent blockchain events and market data to detect
accumulation, liquidity rotation, or potential attack vectors.
"""
from __future__ import annotations

import logging
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class AlphaSignal:
    """A single detected alpha or anomaly signal."""
    signal_type: str
    confidence_score: float  # 0.0 to 1.0
    protocol: str
    narrative: str
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SignalAnalysisResult:
    """The result of an anomaly detection pass."""
    signals: List[AlphaSignal]
    highest_confidence: Optional[AlphaSignal]
    total_events_analyzed: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "signals": [s.to_dict() for s in self.signals],
            "highest_confidence": self.highest_confidence.to_dict() if self.highest_confidence else None,
            "total_events_analyzed": self.total_events_analyzed,
        }


def detect_whale_accumulation(event: Dict[str, Any]) -> Optional[AlphaSignal]:
    """Detect if an event represents significant whale accumulation."""
    volume = event.get("volume", 0)
    protocol_tvl = event.get("protocol_tvl", 0)
    protocol = event.get("protocol", "Unknown")

    if not volume or not protocol_tvl:
        return None

    # If volume is > 5% of TVL, flag as accumulation
    ratio = volume / protocol_tvl
    if ratio > 0.05:
        confidence = min(0.99, ratio * 10)  # scales up with ratio
        return AlphaSignal(
            signal_type="whale_accumulation",
            confidence_score=round(confidence, 3),
            protocol=protocol,
            narrative=f"Large volume detected: ${volume:,.0f} ({ratio*100:.1f}% of {protocol} TVL).",
            metadata={"volume": volume, "tvl": protocol_tvl, "ratio": ratio},
        )
    return None


def detect_liquidity_migration(event: Dict[str, Any]) -> Optional[AlphaSignal]:
    """Detect if liquidity is migrating rapidly."""
    tvl_change_24h = event.get("tvl_change_24h_pct", 0)
    protocol = event.get("protocol", "Unknown")

    # Drop of > 10% in 24h
    if tvl_change_24h < -10.0:
        confidence = min(0.99, abs(tvl_change_24h) / 50.0)
        return AlphaSignal(
            signal_type="liquidity_migration",
            confidence_score=round(confidence, 3),
            protocol=protocol,
            narrative=f"Rapid TVL drain: {protocol} lost {abs(tvl_change_24h):.1f}% liquidity in 24h.",
            metadata={"tvl_change_pct": tvl_change_24h},
        )
    return None


def detect_governance_attack(event: Dict[str, Any]) -> Optional[AlphaSignal]:
    """Detect high-risk rushed or emergency governance actions."""
    event_type = event.get("type", "")
    risk_level = event.get("risk", "")
    protocol = event.get("protocol", "Unknown")

    if event_type == "emergency" and risk_level in ("high", "critical"):
        return AlphaSignal(
            signal_type="governance_attack_risk",
            confidence_score=0.95,
            protocol=protocol,
            narrative=f"Critical emergency upgrade detected on {protocol}. Verify multi-sig/timelock.",
            metadata={"type": event_type, "risk": risk_level},
        )
    return None


def output_alpha_signals(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze a batch of events and output trader-facing alpha signals.

    Parameters
    ----------
    events : list of dict
        Raw event dictionaries containing metrics.

    Returns
    -------
    dict (SignalAnalysisResult)
    """
    logger.info("Analyzing %d events for alpha signals...", len(events))
    signals: List[AlphaSignal] = []

    for evt in events:
        if s := detect_whale_accumulation(evt):
            signals.append(s)
        if s := detect_liquidity_migration(evt):
            signals.append(s)
        if s := detect_governance_attack(evt):
            signals.append(s)

    # Sort by confidence
    signals.sort(key=lambda x: x.confidence_score, reverse=True)
    highest = signals[0] if signals else None

    result = SignalAnalysisResult(
        signals=signals,
        highest_confidence=highest,
        total_events_analyzed=len(events),
    )

    if highest:
        logger.warning(
            "Highest confidence signal: %s (%.2f) on %s",
            highest.signal_type, highest.confidence_score, highest.protocol
        )

    return result.to_dict()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    mock_events = [
        {"protocol": "Curve", "volume": 50_000_000, "protocol_tvl": 400_000_000},
        {"protocol": "Aave", "tvl_change_24h_pct": -15.5},
        {"protocol": "Compound", "type": "emergency", "risk": "critical"},
        {"protocol": "Uniswap", "volume": 1_000_000, "protocol_tvl": 3_000_000_000},  # Normal event
    ]

    result = output_alpha_signals(mock_events)
    import json
    print(json.dumps(result, indent=2))
