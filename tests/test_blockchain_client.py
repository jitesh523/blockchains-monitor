import asyncio
import sys
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

class MockBlockNotFound(Exception):
    pass

# Mock heavy external module to allow tests to run locally without full installs
if "web3" not in sys.modules:
    sys.modules["web3"] = MagicMock()
    exceptions_module = MagicMock()
    exceptions_module.BlockNotFound = MockBlockNotFound
    sys.modules["web3.exceptions"] = exceptions_module
if "aiohttp" not in sys.modules:
    sys.modules["aiohttp"] = MagicMock()
if "dotenv" not in sys.modules:
    sys.modules["dotenv"] = MagicMock()

from web3.exceptions import BlockNotFound

from src.api.blockchain_client import BlockchainClient


@pytest.fixture
def mock_config():
    config = MagicMock()
    config.NETWORKS = {
        "ethereum": {
            "rpc_url": "http://mock-eth-rpc",
            "api_key": "mock-etherscan-key",
            "explorer_api": "http://mock-explorer-api"
        }
    }
    return config


def test_initialize_networks(mock_config):
    """Test connecting to the configured networks via Web3."""
    with patch("src.api.blockchain_client.Config", return_value=mock_config):
        with patch("src.api.blockchain_client.Web3") as MockWeb3:
            mock_w3 = MagicMock()
            mock_w3.is_connected.return_value = True
            MockWeb3.return_value = mock_w3
            
            client = BlockchainClient()
            # __init__ calls initialize_networks()
            
            assert "ethereum" in client.networks
            assert client.networks["ethereum"]["web3"] == mock_w3
            assert client.networks["ethereum"]["config"] == mock_config.NETWORKS["ethereum"]


def test_get_block_timestamp(mock_config):
    """Test standard block timestamp retrieval mapping via Web3."""
    async def _run():
        with patch("src.api.blockchain_client.Config", return_value=mock_config):
            with patch("src.api.blockchain_client.Web3") as MockWeb3:
                mock_w3 = MagicMock()
                mock_w3.is_connected.return_value = True
                
                # Setup mock block with a known timestamp
                mock_block = MagicMock()
                mock_block.timestamp = 1600000000
                mock_w3.eth.get_block.return_value = mock_block
                
                MockWeb3.return_value = mock_w3
                
                client = BlockchainClient()
                
                dt = await client._get_block_timestamp("ethereum", 12345)
                assert dt.timestamp() == 1600000000

    asyncio.run(_run())


def test_get_block_timestamp_not_found(mock_config):
    """Test correct exception catching when a block is not found."""
    async def _run():
        with patch("src.api.blockchain_client.Config", return_value=mock_config):
            with patch("src.api.blockchain_client.Web3") as MockWeb3:
                mock_w3 = MagicMock()
                mock_w3.is_connected.return_value = True
                
                # Make it raise BlockNotFound
                mock_w3.eth.get_block.side_effect = BlockNotFound("Block not found")
                
                MockWeb3.return_value = mock_w3
                
                client = BlockchainClient()
                
                dt = await client._get_block_timestamp("ethereum", 9999999999)
                
                # It should catch the exception and return datetime.now(), so we assert object type
                assert isinstance(dt, datetime)

    asyncio.run(_run())


def test_async_context_manager(mock_config):
    """Test HTTP aiohttp session lifecycle via async with."""
    async def _run():
        with patch("src.api.blockchain_client.Config", return_value=mock_config):
            with patch("src.api.blockchain_client.Web3"):
                client = BlockchainClient()
                
                # Mock aiohttp
                with patch("aiohttp.ClientSession", new_callable=MagicMock) as mock_session_class:
                    mock_session = AsyncMock()
                    mock_session_class.return_value = mock_session
                    
                    async with client as c:
                        assert c.session is not None
                        assert c.session == mock_session
                        
                    # Verify session is cleaned up
                    mock_session.close.assert_called_once()
                    
    asyncio.run(_run())
