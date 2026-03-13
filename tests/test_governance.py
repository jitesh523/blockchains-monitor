import asyncio
import sys
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Mock heavy external module to allow tests to run locally
if "httpx" not in sys.modules:
    sys.modules["httpx"] = MagicMock()

from src.api.governance import GovernanceClient


def test_normalize_snapshot_proposal():
    """Test data normalization for Snapshot GraphQL payloads."""
    client = GovernanceClient()
    raw = {
        "title": "Upgrade contract",
        "state": "active",
        "start": 1600000000,
        "scores_total": 5000
    }
    norm = client.normalize_snapshot_proposal(raw)
    
    assert norm["title"] == "Upgrade contract"
    assert norm["status"] == "active"
    assert norm["created"].timestamp() == 1600000000
    assert norm["votes"] == 5000


def test_normalize_tally_proposal():
    """Test data normalization for Tally REST API payloads."""
    client = GovernanceClient()
    raw = {
        "title": "Change parameters",
        "status": "pending",
        "created": "2023-01-01T12:00:00",
        "totalVotes": 1000
    }
    norm = client.normalize_tally_proposal(raw)
    
    assert norm["title"] == "Change parameters"
    assert norm["status"] == "pending"
    assert norm["created"].isoformat() == "2023-01-01T12:00:00"
    assert norm["votes"] == 1000


def test_fetch_snapshot_proposals():
    """Test standard fetch execution for Snapshot proposals."""
    async def _run():
        client = GovernanceClient()
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "proposals": [{"id": "1", "title": "Test"}]
            }
        }
        
        with patch("src.api.governance.httpx.AsyncClient") as MockClient:
            mock_client_instance = AsyncMock()
            mock_client_instance.post.return_value = mock_response
            
            # Setup context manager return
            MockClient.return_value.__aenter__.return_value = mock_client_instance
            
            res = await client.fetch_snapshot_proposals("uniswap")
            assert len(res) == 1
            assert res[0]["title"] == "Test"
            mock_client_instance.post.assert_called_once()
            
    asyncio.run(_run())


def test_fetch_tally_proposals():
    """Test standard fetch execution for Tally proposals."""
    async def _run():
        client = GovernanceClient()
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [{"id": "2", "title": "Tally Test"}]
        }
        
        with patch("src.api.governance.httpx.AsyncClient") as MockClient:
            mock_client_instance = AsyncMock()
            mock_client_instance.get.return_value = mock_response
            MockClient.return_value.__aenter__.return_value = mock_client_instance
            
            res = await client.fetch_tally_proposals("aave")
            assert len(res) == 1
            assert res[0]["title"] == "Tally Test"
            mock_client_instance.get.assert_called_once()
            
    asyncio.run(_run())
