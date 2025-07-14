# 🔗 Blockchain Protocol Upgrade Monitor

A high-performance protocol upgrade monitoring system that tracks blockchain network events, predicts volatility and liquidity shifts, and provides execution guidance for trading strategies. This system connects to multiple data sources including blockchain APIs, social media feeds, and market data streams to provide real-time risk assessment.

![Dashboard Preview](https://img.shields.io/badge/Status-Production%20Ready-green)
![Python](https://img.shields.io/badge/Python-3.13+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.46+-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🚀 Features

### 🎨 Modern UI Components
- **Dark & Light Mode Support** with professional styling
- **Animated Dashboard** with smooth transitions and hover effects
- **Responsive Layout** optimized for all screen sizes
- **Interactive Timeline** with expandable proposal cards
- **Real-time Updates** with auto-refresh capabilities

### 📊 Core Analytics
- **Volatility Forecasting** using GARCH(1,1) models
- **Sentiment Analysis** powered by BERT transformers
- **Risk Assessment** with multi-factor scoring
- **Liquidity Prediction** using Prophet time series models
- **Portfolio Impact Analysis** with correlation metrics

### 🌐 Network Support
- **Ethereum** - Mainnet monitoring and analysis
- **Polygon** - L2 scaling solution tracking
- **Arbitrum** - Optimistic rollup insights
- **Multi-chain** - Cross-chain governance analysis

### 🔄 Data Integration
- **Blockchain APIs**: Etherscan, PolygonScan, Arbiscan
- **Governance Platforms**: Snapshot, Tally
- **Market Data**: CoinGecko, CoinMarketCap
- **Social Media**: Twitter sentiment analysis
- **DeFi Analytics**: DeFi Pulse, DeFi Llama

## 🛠️ Installation

### Prerequisites
- Python 3.13+
- Node.js (for additional dependencies)
- Git

### Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/jitesh523/blockchains-monitor.git
cd blockchains-monitor
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys
```

5. **Run the application**
```bash
streamlit run app.py
```

6. **Access the dashboard**
   - Local: http://localhost:8501
   - Network: Available on your local network

## 📊 Usage Examples

### Monitor Protocol Upgrades

```python
from src.api.governance import GovernanceClient
import asyncio

async def monitor_proposals():
    client = GovernanceClient()
    proposals = await client.fetch_snapshot_proposals("uniswap")
    for proposal in proposals:
        print(f"Proposal: {proposal['title']}")
        print(f"Status: {proposal['state']}")
```

### Analyze Volatility

```python
from src.models.volatility_model import get_protocol_volatility
import asyncio

async def analyze_volatility():
    vol_data = await get_protocol_volatility("ethereum")
    print(f"Volatility: {vol_data['volatility']}%")
```

## 🧪 Testing

```bash
# Test volatility model
python test_volatility.py

# Test sentiment analysis
python test_sentiment.py

# Test integrated models
python test_integrated_models.py
```

## 🔧 Models Documentation

### GARCH Volatility Model
- **Input**: Historical price data (180 days)
- **Output**: Annualized volatility forecast
- **Model**: GARCH(1,1) with normal distribution

### BERT Sentiment Analysis
- **Model**: DistilBERT fine-tuned on financial data
- **Input**: Text data (tweets, proposals, comments)
- **Output**: Sentiment score (-1 to +1)

### Risk Assessment Framework
- **Volatility Weight**: 40%
- **Sentiment Weight**: 30%
- **Governance Weight**: 20%
- **Technical Weight**: 10%

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **Streamlit** for the amazing web framework
- **HuggingFace** for transformer models
- **CoinGecko** for market data
- **Etherscan** for blockchain data

---

Built with ❤️ for the DeFi community
