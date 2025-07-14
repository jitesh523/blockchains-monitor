import os
from dotenv import load_dotenv
from typing import Dict, List

load_dotenv()

class Config:
    """Configuration class for the blockchain upgrade monitoring system."""
    
    # API Keys
    ETHERSCAN_API_KEY = os.getenv('ETHERSCAN_API_KEY')
    POLYGONSCAN_API_KEY = os.getenv('POLYGONSCAN_API_KEY')
    ARBISCAN_API_KEY = os.getenv('ARBISCAN_API_KEY')
    INFURA_PROJECT_ID = os.getenv('INFURA_PROJECT_ID')
    ALCHEMY_API_KEY = os.getenv('ALCHEMY_API_KEY')
    
    # Social Media APIs
    TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')
    TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
    TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
    TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
    TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
    
    # Market Data APIs
    COINGECKO_API_KEY = os.getenv('COINGECKO_API_KEY')
    COINMARKETCAP_API_KEY = os.getenv('COINMARKETCAP_API_KEY')
    DEFILLAMA_API_KEY = os.getenv('DEFILLAMA_API_KEY')
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///blockchain_monitor.db')
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Application Settings
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    UPDATE_INTERVAL = int(os.getenv('UPDATE_INTERVAL', '30'))
    CACHE_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', '300'))
    MAX_WORKERS = int(os.getenv('MAX_WORKERS', '4'))
    
    # Telegram Bot
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
    
    # Network Configurations
    NETWORKS = {
        'ethereum': {
            'name': 'Ethereum',
            'chain_id': 1,
            'rpc_url': f'https://mainnet.infura.io/v3/{INFURA_PROJECT_ID}',
            'explorer_api': 'https://api.etherscan.io/api',
            'api_key': ETHERSCAN_API_KEY
        },
        'polygon': {
            'name': 'Polygon',
            'chain_id': 137,
            'rpc_url': f'https://polygon-mainnet.infura.io/v3/{INFURA_PROJECT_ID}',
            'explorer_api': 'https://api.polygonscan.com/api',
            'api_key': POLYGONSCAN_API_KEY
        },
        'arbitrum': {
            'name': 'Arbitrum',
            'chain_id': 42161,
            'rpc_url': f'https://arbitrum-mainnet.infura.io/v3/{INFURA_PROJECT_ID}',
            'explorer_api': 'https://api.arbiscan.io/api',
            'api_key': ARBISCAN_API_KEY
        }
    }
    
    # Protocol Categories
    PROTOCOL_CATEGORIES = {
        'DEX': ['Uniswap', 'SushiSwap', 'PancakeSwap', 'Balancer'],
        'LENDING': ['Aave', 'Compound', 'MakerDAO', 'Euler'],
        'YIELD': ['Yearn', 'Convex', 'Curve', 'Harvest'],
        'DERIVATIVES': ['dYdX', 'Perpetual', 'Synthetix', 'GMX'],
        'BRIDGE': ['Hop', 'Across', 'Synapse', 'Multichain']
    }
    
    # Risk Thresholds
    RISK_THRESHOLDS = {
        'volatility': {
            'low': 0.2,
            'medium': 0.5,
            'high': 0.8
        },
        'liquidity': {
            'low': 0.1,
            'medium': 0.3,
            'high': 0.6
        },
        'governance': {
            'low': 0.3,
            'medium': 0.6,
            'high': 0.9
        }
    }
    
    # Model Parameters
    GARCH_PARAMS = {
        'p': 1,
        'q': 1,
        'mean': 'Zero',
        'vol': 'GARCH',
        'dist': 'Normal'
    }
    
    ARIMA_PARAMS = {
        'order': (1, 1, 1),
        'seasonal_order': (1, 1, 1, 12)
    }
    
    # Sentiment Analysis
    SENTIMENT_KEYWORDS = {
        'positive': ['upgrade', 'improvement', 'bullish', 'growth', 'adoption'],
        'negative': ['hack', 'exploit', 'bug', 'bearish', 'dump'],
        'neutral': ['announcement', 'update', 'news', 'release']
    }
    
    # Alert Configuration
    ALERT_CHANNELS = ['telegram', 'email', 'webhook']
    ALERT_SEVERITY_LEVELS = ['info', 'warning', 'critical']
    
    @classmethod
    def get_network_config(cls, network: str) -> Dict:
        """Get configuration for a specific network."""
        return cls.NETWORKS.get(network.lower(), {})
    
    @classmethod
    def get_supported_networks(cls) -> List[str]:
        """Get list of supported networks."""
        return list(cls.NETWORKS.keys())
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that required configuration is present."""
        required_keys = [
            'ETHERSCAN_API_KEY',
            'INFURA_PROJECT_ID'
        ]
        
        missing_keys = [key for key in required_keys if not getattr(cls, key)]
        
        if missing_keys:
            print(f"Missing required configuration: {', '.join(missing_keys)}")
            return False
        
        return True
