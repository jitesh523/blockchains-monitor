import asyncio
import sys
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Mock asyncpg to bypass needing a real PostgreSQL server locally
if "asyncpg" not in sys.modules:
    sys.modules["asyncpg"] = MagicMock()

from src.services.database_service import DatabaseService, PriceData


class MockAcquireContext:
    def __init__(self, conn):
        self.conn = conn
        
    async def __aenter__(self):
        return self.conn
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

@pytest.fixture
def mock_pool():
    pool = MagicMock()
    conn = AsyncMock()
    pool.close = AsyncMock()
    pool.acquire.return_value = MockAcquireContext(conn)
    return pool, conn


def test_database_connect(mock_pool):
    """Test connecting to the database and creating tables."""
    pool, conn = mock_pool
    
    async def _run():
        with patch("asyncpg.create_pool", new_callable=AsyncMock, return_value=pool):
            service = DatabaseService("postgresql://mock")
            await service.connect()
            
            assert service.pool is not None
            # create_tables should execute schema and index SQL
            assert pool.acquire.called
            assert conn.execute.call_count > 0
    
    asyncio.run(_run())


def test_insert_price_data(mock_pool):
    """Test inserting a PriceData object executes the correct INSERT query."""
    pool, conn = mock_pool
    
    async def _run():
        service = DatabaseService()
        service.pool = pool
        
        data = PriceData(
            token="ethereum", 
            price=2500.0, 
            volume_24h=1000000.0, 
            market_cap=300000000.0, 
            timestamp=datetime.now()
        )
        
        await service.insert_price_data(data)
        
        assert conn.execute.call_count == 1
        query_sql = conn.execute.call_args[0][0]
        assert "INSERT INTO price_data" in query_sql
        
    asyncio.run(_run())


def test_get_protocol_stats(mock_pool):
    """Test aggregating protocol stats fetches from both tables."""
    pool, conn = mock_pool
    
    async def _run():
        service = DatabaseService()
        service.pool = pool
        
        # Mock side_effect for the 2 queries in get_protocol_stats:
        # 1. protocol_events
        # 2. sentiment_trend
        conn.fetch.side_effect = [
            [{"protocol": "ethereum", "event_count": 5, "avg_risk": 65.0}],
            [{"day": datetime.now(), "avg_sentiment": -0.2}]
        ]
        
        stats = await service.get_protocol_stats()
        
        assert "protocol_events" in stats
        assert "sentiment_trend" in stats
        assert len(stats["protocol_events"]) == 1
        assert stats["protocol_events"][0]["protocol"] == "ethereum"
        
    asyncio.run(_run())


def test_cleanup_old_data(mock_pool):
    """Test retention policy triggers DELETE queries."""
    pool, conn = mock_pool
    
    async def _run():
        service = DatabaseService()
        service.pool = pool
        
        await service.cleanup_old_data(retention_days=30)
        
        # Should delete from price_data, sentiment_data, and risk_events (3 queries)
        assert conn.execute.call_count == 3
        
        for call_arg in conn.execute.call_args_list:
            assert "DELETE FROM" in call_arg[0][0]
            
    asyncio.run(_run())


def test_close(mock_pool):
    """Test closing the database connection pool."""
    pool, conn = mock_pool
    
    async def _run():
        service = DatabaseService()
        service.pool = pool
        await service.close()
        
        pool.close.assert_called_once()
        
    asyncio.run(_run())
