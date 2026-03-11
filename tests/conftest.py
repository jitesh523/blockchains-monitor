"""
Shared test fixtures for blockchains-monitor tests.
"""

import os
import sys
from datetime import datetime, timedelta

import pytest

# Ensure project root is on sys.path so that ``import src.*`` and
# ``import config.*`` work regardless of how pytest is invoked.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


@pytest.fixture
def sample_crosschain_events():
    """Return a list of cross-chain events for testing correlation logic."""
    now = datetime(2025, 6, 1, 12, 0, 0)
    return [
        {"upgrade": "USDC1", "chain": "Ethereum", "timestamp": now},
        {"upgrade": "USDC1", "chain": "Polygon", "timestamp": now + timedelta(minutes=5)},
        {"upgrade": "USDC1", "chain": "Arbitrum", "timestamp": now + timedelta(minutes=10)},
        {"upgrade": "GMX2", "chain": "Arbitrum", "timestamp": now + timedelta(minutes=3)},
        {"upgrade": "GMX2", "chain": "Ethereum", "timestamp": now + timedelta(minutes=8)},
    ]


@pytest.fixture
def sample_single_chain_events():
    """Return events from a single chain only."""
    now = datetime(2025, 6, 1, 12, 0, 0)
    return [
        {"upgrade": "AAVE3", "chain": "Ethereum", "timestamp": now},
        {"upgrade": "AAVE3", "chain": "Ethereum", "timestamp": now + timedelta(minutes=15)},
    ]
