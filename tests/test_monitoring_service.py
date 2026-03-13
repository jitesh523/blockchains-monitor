import asyncio
import sys
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Mock external dependencies for cross-platform compatibility without native installation
if "psutil" not in sys.modules:
    sys.modules["psutil"] = MagicMock()
if "requests" not in sys.modules:
    sys.modules["requests"] = MagicMock()
if "redis" not in sys.modules:
    sys.modules["redis"] = MagicMock()
if "asyncpg" not in sys.modules:
    sys.modules["asyncpg"] = MagicMock()

from src.services.monitoring_service import HealthCheck, MonitoringService


def test_check_database_health_uninitialized():
    """Test that database health returns unhealthy if pool is not initialized."""
    async def _run():
        service = MonitoringService()
        with patch("src.services.monitoring_service.db_service") as mock_db:
            mock_db.pool = None
            health = await service.check_database_health()
            assert health.status == "unhealthy"
            assert "Database pool not initialized" in health.details["error"]
            assert health.service == "database"
    asyncio.run(_run())
    

def test_check_redis_health_degraded():
    """Test that redis health returns degraded if client is absent (fallback)."""
    async def _run():
        service = MonitoringService()
        with patch("src.services.monitoring_service.cache_service") as mock_cache:
            mock_cache.redis_client = None
            health = await service.check_redis_health()
            assert health.status == "degraded"
            assert "fallback" in health.details["error"]
            assert health.service == "redis"
    asyncio.run(_run())


def test_check_api_health_healthy():
    """Test standard API connectivity check via requests."""
    async def _run():
        service = MonitoringService()
        
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_get.return_value = mock_response
            
            health = await service.check_api_health()
            
            assert health.status == "healthy"
            assert mock_get.called
            assert health.service == "external_apis"
    asyncio.run(_run())


def test_check_api_health_unhealthy():
    """Test API failure captures correctly."""
    async def _run():
        service = MonitoringService()
        
        with patch("requests.get", side_effect=Exception("Connection Timeout")):
            health = await service.check_api_health()
            
            assert health.status == "unhealthy"
            assert "Timeout" in health.details["error"]
    asyncio.run(_run())
