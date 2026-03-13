import sys
import time
from unittest.mock import MagicMock, patch

import pytest

# Mock heavy external modules so tests can run locally without full installs
if "redis" not in sys.modules:
    sys.modules["redis"] = MagicMock()

import redis

from src.services.cache_service import (
    CacheService,
    CircuitBreaker,
    cached,
    exponential_backoff,
    with_circuit_breaker
)


@pytest.fixture
def mock_redis():
    return MagicMock()


def test_cache_service_methods(mock_redis):
    """Test get, set, delete on the CacheService with a mocked Redis client."""
    with patch("redis.from_url", return_value=mock_redis):
        service = CacheService("redis://mock:6379/0")
        assert service.redis_client is not None
        
        # Test set
        assert service.set("test_key", {"data": 1}, ttl=60) is True
        mock_redis.setex.assert_called_once_with("test_key", 60, '{"data": 1}')
        
        # Test get
        mock_redis.get.return_value = '{"data": 1}'
        assert service.get("test_key") == {"data": 1}
        
        # Test delete
        assert service.delete("test_key") is True
        mock_redis.delete.assert_called_once_with("test_key")


def test_cache_service_fallback():
    """Test standard initialization fallback when Redis is unreachable."""
    with patch("redis.from_url", side_effect=Exception("Failed connection")):
        service = CacheService("redis://localhost:9999/0")
        assert service.redis_client is None
        
        assert service.set("key", "val") is False
        assert service.get("key") is None
        assert service.delete("key") is False


def test_exponential_backoff():
    """Test exponential backoff retries when encountering exceptions."""
    mock_func = MagicMock()
    # First 2 fail, 3rd succeeds
    mock_func.side_effect = [ValueError("fail 1"), ValueError("fail 2"), "success"]
    
    @exponential_backoff(max_retries=3, base_delay=0.01)
    def test_func():
        return mock_func()
        
    result = test_func()
    assert result == "success"
    assert mock_func.call_count == 3


def test_exponential_backoff_exhausted():
    """Test that it ultimately raises exception when all retries are exhausted."""
    mock_func = MagicMock(side_effect=ValueError("fail"))
    
    @exponential_backoff(max_retries=2, base_delay=0.01)
    def test_func():
        return mock_func()
        
    with pytest.raises(ValueError, match="fail"):
        test_func()


def test_circuit_breaker():
    """Test state transitions of the CircuitBreaker (CLOSED -> OPEN -> HALF_OPEN -> CLOSED)."""
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1)
    mock_func = MagicMock(side_effect=ValueError("fail"))
    mock_func.__name__ = "mock_func"
    
    # Attempt 1 -> fails
    with pytest.raises(ValueError):
        cb.call(mock_func)
    assert cb.state == "CLOSED"
    assert cb.failure_count == 1
    
    # Attempt 2 -> fails and trips breaker
    with pytest.raises(ValueError):
        cb.call(mock_func)
    assert cb.state == "OPEN"
    
    # Attempt 3 -> fails fast (breaker OPEN)
    with pytest.raises(Exception, match="Circuit breaker OPEN"):
        cb.call(mock_func)
        
    # Wait for recovery
    time.sleep(0.15)
    
    # Attempt 4 -> HALF_OPEN, succeeds -> CLOSED
    mock_func.side_effect = None
    mock_func.return_value = "success"
    assert cb.call(mock_func) == "success"
    assert cb.state == "CLOSED"
    assert cb.failure_count == 0
