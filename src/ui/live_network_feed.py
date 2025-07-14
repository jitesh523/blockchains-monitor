import streamlit as st
import asyncio
import aiohttp
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

class NetworkMonitor:
    """Monitor live network metrics from various blockchain networks."""
    
    def __init__(self):
        self.etherscan_url = "https://api.etherscan.io/api"
        self.polygonscan_url = "https://api.polygonscan.com/api"
        self.arbiscan_url = "https://api.arbiscan.io/api"
    
    async def get_gas_price(self, network: str, api_key: str = None) -> Dict[str, Any]:
        """Get current gas price for a network."""
        try:
            urls = {
                'ethereum': self.etherscan_url,
                'polygon': self.polygonscan_url,
                'arbitrum': self.arbiscan_url
            }
            
            if network not in urls:
                return {'error': f'Network {network} not supported'}
            
            params = {
                'module': 'gastracker',
                'action': 'gasoracle',
                'apikey': api_key or 'YourApiKeyToken'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(urls[network], params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('status') == '1':
                            result = data['result']
                            return {
                                'safe_gas': result.get('SafeGasPrice', 'N/A'),
                                'standard_gas': result.get('ProposeGasPrice', 'N/A'),
                                'fast_gas': result.get('FastGasPrice', 'N/A'),
                                'timestamp': datetime.now().isoformat()
                            }
                    
                    return {'error': f'API error for {network}'}
        
        except Exception as e:
            logger.error(f"Error getting gas price for {network}: {e}")
            return {'error': str(e)}
    
    async def get_network_stats(self, network: str) -> Dict[str, Any]:
        """Get comprehensive network statistics."""
        try:
            # Mock data for demonstration - in production, fetch from actual APIs
            mock_data = {
                'ethereum': {
                    'gas_price': '32 Gwei',
                    'block_time': '12.5s',
                    'tps': '13 tx/s',
                    'total_txs': '1.2M',
                    'network_health': '🟢 Healthy'
                },
                'polygon': {
                    'gas_price': '82 Gwei',
                    'block_time': '2.3s',
                    'tps': '45 tx/s',
                    'total_txs': '890K',
                    'network_health': '🟢 Healthy'
                },
                'arbitrum': {
                    'gas_price': '0.15 Gwei',
                    'block_time': '1.2s',
                    'tps': '12 tx/s',
                    'total_txs': '340K',
                    'network_health': '🟢 Healthy'
                }
            }
            
            return mock_data.get(network, {'error': f'Network {network} not found'})
        
        except Exception as e:
            logger.error(f"Error getting network stats for {network}: {e}")
            return {'error': str(e)}

def render_live_network_feed():
    """Render the live network feed in the sidebar."""
    st.sidebar.header("⛓️ Live Network Feed")
    
    monitor = NetworkMonitor()
    networks = ['ethereum', 'polygon', 'arbitrum']
    
    for network in networks:
        with st.sidebar.expander(f"🔗 {network.capitalize()}", expanded=True):
            try:
                # Get network stats (using mock data for now)
                stats = asyncio.run(monitor.get_network_stats(network))
                
                if 'error' not in stats:
                    st.metric(
                        f"{network.capitalize()} Gas",
                        stats.get('gas_price', 'N/A')
                    )
                    st.metric(
                        "Block Time",
                        stats.get('block_time', 'N/A')
                    )
                    st.metric(
                        "TPS",
                        stats.get('tps', 'N/A')
                    )
                    st.write(f"Status: {stats.get('network_health', 'Unknown')}")
                else:
                    st.error(f"Error: {stats['error']}")
            
            except Exception as e:
                st.error(f"Error loading {network} data: {e}")
    
    st.sidebar.caption("Updates every 60s via Etherscan/Arbiscan")
    
    # Add refresh button
    if st.sidebar.button("🔄 Refresh Network Data"):
        st.rerun()

def render_network_overview():
    """Render a network overview in the main area."""
    st.subheader("🌐 Network Overview")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Ethereum Gas", "32 Gwei", delta="-2 Gwei")
        st.metric("ETH Block Time", "12.5s", delta="+0.2s")
    
    with col2:
        st.metric("Polygon Gas", "82 Gwei", delta="+5 Gwei")
        st.metric("MATIC Block Time", "2.3s", delta="-0.1s")
    
    with col3:
        st.metric("Arbitrum Gas", "0.15 Gwei", delta="+0.02 Gwei")
        st.metric("ARB Block Time", "1.2s", delta="0.0s")

async def get_live_network_data():
    """Fetch live network data from multiple sources."""
    monitor = NetworkMonitor()
    networks = ['ethereum', 'polygon', 'arbitrum']
    
    results = {}
    for network in networks:
        try:
            stats = await monitor.get_network_stats(network)
            results[network] = stats
        except Exception as e:
            results[network] = {'error': str(e)}
    
    return results

# Example usage
if __name__ == "__main__":
    st.title("Live Network Feed Example")
    
    # Render network overview
    render_network_overview()
    
    # Render live feed in sidebar
    render_live_network_feed()
    
    # Show detailed network data
    st.subheader("📊 Detailed Network Data")
    
    if st.button("Fetch Live Data"):
        with st.spinner("Fetching network data..."):
            data = asyncio.run(get_live_network_data())
            
            for network, stats in data.items():
                st.write(f"### {network.capitalize()}")
                if 'error' not in stats:
                    st.json(stats)
                else:
                    st.error(f"Error: {stats['error']}")
