import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import sys
if "requests" not in sys.modules:
    sys.modules["requests"] = MagicMock()
if "redis" not in sys.modules:
    sys.modules["redis"] = MagicMock()
if "asyncpg" not in sys.modules:
    sys.modules["asyncpg"] = MagicMock()
if "fastapi" not in sys.modules:
    sys.modules["fastapi"] = MagicMock()
if "fastapi.middleware" not in sys.modules:
    sys.modules["fastapi.middleware"] = MagicMock()
if "fastapi.middleware.cors" not in sys.modules:
    sys.modules["fastapi.middleware.cors"] = MagicMock()

from src.services.realtime_service import RealtimeService


def test_generate_sentiment_data():
    """Test the sentiment aggregator correctly structures and dispatches metrics to the database."""
    async def _run():
        service = RealtimeService()
        
        # Patch the database insert dependency allowing us to run this sync loop
        with patch("src.services.realtime_service.db_service.insert_sentiment_data", new_callable=AsyncMock) as mock_insert:
            data = await service.generate_sentiment_data()
            
            assert "overall_sentiment" in data
            assert "sentiment_sources" in data
            assert len(data["sentiment_sources"]) == 2
            
            # Ensure proper payload structure
            assert "source" in data["sentiment_sources"][0]
            assert "sentiment" in data["sentiment_sources"][0]
            
            # Verify we dispatched it to Postgres
            mock_insert.assert_called_once()
            
    asyncio.run(_run())


def test_assess_risk_levels():
    """Test risk assessment generation constructs proper payload distributions."""
    async def _run():
        service = RealtimeService()
        
        with patch("src.services.realtime_service.db_service.insert_risk_event", new_callable=AsyncMock):
            risk_data = await service.assess_risk_levels()
            
            assert "ethereum" in risk_data
            assert "uniswap" in risk_data
            
            # Validate properties
            assert "risk_score" in risk_data["ethereum"]
            assert "risk_level" in risk_data["ethereum"]
            assert "factors" in risk_data["ethereum"]
            
            assert len(risk_data["ethereum"]["factors"]) == 3
            
    asyncio.run(_run())
