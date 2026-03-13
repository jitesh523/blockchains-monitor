"""
crosschain_analytics.py
Cross-chain event correlation utilities.

Given a list of events from multiple chains for the same or different upgrades,
this module clusters potentially related events within a time window and
returns a compact correlation summary with a confidence score.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, Iterable, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class CorrelatedCluster:
    """Represents a cluster of related events across chains."""

    upgrade: str
    chains: List[str]
    count: int
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    time_spread_sec: Optional[float]
    cross_chain: bool
    confidence: float  # 0..1
    sample_events: List[Dict[str, Any]]


def _parse_timestamp(ts: Any) -> Optional[datetime]:
    """Parse various timestamp formats to datetime (UTC-naive).
    Accepts datetime, ISO strings, or epoch seconds. Returns None if unknown.
    """
    if ts is None:
        return None
    if isinstance(ts, datetime):
        return ts
    if isinstance(ts, (int, float)):
        try:
            return datetime.utcfromtimestamp(float(ts))
        except Exception:
            return None
    if isinstance(ts, str):
        try:
            # datetime.fromisoformat handles most ISO-8601 strings (without Z)
            if ts.endswith("Z"):
                ts = ts[:-1]
            return datetime.fromisoformat(ts)
        except Exception:
            return None
    return None


def _cluster_key(evt: Dict[str, Any]) -> Tuple[str, Optional[datetime]]:
    """Return (upgrade, rounded_time) tuple to bucket events into windows."""
    upgrade = str(evt.get("upgrade") or evt.get("id") or "unknown").strip()
    ts = _parse_timestamp(evt.get("timestamp"))
    return upgrade, ts


def correlate_events(
    events: Iterable[Dict[str, Any]],
    window_minutes: int = 60,
    min_chains: int = 2,
) -> Dict[str, Any]:
    """
    Correlate cross-chain events by upgrade ID within a time window.

    Parameters
    - events: iterable of dicts with keys: `upgrade` (str), `chain` (str),
      optional `timestamp` (datetime | ISO str | epoch seconds), and any metadata.
    - window_minutes: how far apart events can be to be considered related.
    - min_chains: minimum distinct chains to mark as cross-chain.

    Returns
    - dict with `clusters` (list[CorrelatedCluster as dict]) and `summary`.
    """
    events_list = list(events) if not isinstance(events, list) else events
    if not events_list:
        return {"clusters": [], "summary": {"total": 0, "cross_chain": 0}}

    # Group by upgrade
    by_upgrade: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for e in events_list:
        upgrade = str(e.get("upgrade") or e.get("id") or "unknown").strip()
        by_upgrade[upgrade].append(e)

    clusters: List[CorrelatedCluster] = []
    window = timedelta(minutes=window_minutes)

    for upgrade, evts in by_upgrade.items():
        # Sort by timestamp (unknown timestamps go last)
        evts_sorted = sorted(
            evts,
            key=lambda x: _parse_timestamp(x.get("timestamp")) or datetime.max,
        )

        # Sliding window clustering
        bucket: List[Dict[str, Any]] = []
        bucket_start_ts: Optional[datetime] = None

        def flush_bucket():
            if not bucket:
                return
            ts_list = [_parse_timestamp(b.get("timestamp")) for b in bucket if _parse_timestamp(b.get("timestamp"))]
            start_ts = min(ts_list) if ts_list else None
            end_ts = max(ts_list) if ts_list else None
            spread = (end_ts - start_ts).total_seconds() if start_ts and end_ts else None
            chains = sorted({b.get("chain", "unknown") for b in bucket})
            cross_chain = len(chains) >= min_chains

            # Confidence: base on num events, cross-chain, and time compactness
            conf = 0.0
            if bucket:
                conf += min(len(bucket) / 5.0, 1.0) * 0.4  # up to 0.4
            if cross_chain:
                conf += 0.4  # strong cross-chain signal
            if spread is not None:
                # tighter time spread boosts confidence
                compact = max(0.0, 1.0 - (spread / max(1.0, window.total_seconds())))
                conf += compact * 0.2
            conf = round(min(conf, 1.0), 2)

            clusters.append(
                CorrelatedCluster(
                    upgrade=upgrade,
                    chains=chains,
                    count=len(bucket),
                    start_time=start_ts,
                    end_time=end_ts,
                    time_spread_sec=spread,
                    cross_chain=cross_chain,
                    confidence=conf,
                    sample_events=bucket[:5],
                )
            )

        for evt in evts_sorted:
            ts = _parse_timestamp(evt.get("timestamp"))
            if bucket_start_ts is None:
                bucket = [evt]
                bucket_start_ts = ts
                continue

            if ts is None or bucket_start_ts is None:
                # Unknown timestamp -> start a new bucket
                flush_bucket()
                bucket = [evt]
                bucket_start_ts = ts
                continue

            if ts - bucket_start_ts <= window:
                bucket.append(evt)
            else:
                flush_bucket()
                bucket = [evt]
                bucket_start_ts = ts

        flush_bucket()

    cross_chain_count = sum(1 for c in clusters if c.cross_chain)
    result = {
        "clusters": [c.__dict__ for c in clusters],
        "summary": {"total": len(clusters), "cross_chain": cross_chain_count},
    }

    logger.info(
        "Cross-chain correlation complete: %s clusters (%s cross-chain)",
        len(clusters),
        cross_chain_count,
    )
    return result


if __name__ == "__main__":
    # Example usage
    now = datetime.utcnow()
    sample = [
        {"upgrade": "USDC1", "chain": "Ethereum", "timestamp": now},
        {"upgrade": "USDC1", "chain": "Polygon", "timestamp": now + timedelta(minutes=5)},
        {"upgrade": "USDC1", "chain": "Arbitrum", "timestamp": now + timedelta(minutes=70)},  # new bucket
        {"upgrade": "GMX2", "chain": "Arbitrum", "timestamp": now + timedelta(minutes=3)},
    ]
    print(correlate_events(sample, window_minutes=60))
