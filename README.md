# Blockchain Upgrade Monitor

## Secret Management
- **Never commit your real secrets!**
- Copy `.env.example` to `.env` and fill with your credentials.
- Use environment variables or secure secret managers (Vault, AWS Secrets Manager) in production.

## Alerts
- Alert delivery supports: Email, Webhook, Slack, Discord (see `alerts.py` — add service credentials in `.env`).
- Add your keys and webhook URLs to `.env` (template in `.env.example`).

## Auto-Mitigation
- Predefine mitigation actions in `mitigation.py` (stubs provided).
- Integrate with on-chain contracts and bots as needed.

## Input Sanitization
- Validate all incoming data and user input. DO NOT parse blockchain logs or external feeds directly without validation.

## DDOS/Rate Limits
- Implement `429` retry and client-side/backpressure logic. Use reverse proxies like Cloudflare for public endpoints.

## API Mock & Test
- Run `python mock_mode.py` for simulated data feeds if APIs are unavailable.
- See `tests/` for minimum required coverage and CI info.

## Documentation
- See `openapi.yaml` for API documentation (serves at `/docs` in development).
- Changelog and known issues in `CHANGELOG.md`.

---

For further enhancements, please refer to the architecture comments in the respective Python/compose files.

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

> Tip (macOS): Prophet and Torch can be heavy to install. See notes below if you hit build issues.

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

You can run in a limited, no-keys environment by setting:

```bash
export DEMO_MODE=true
```
This allows the UI to load with mocked/limited integrations if some keys are missing.

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

## 🧰 macOS install notes

- Torch CPU wheels (if default install fails):
  ```bash
  pip install --force-reinstall --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
  ```
- Prophet may require Xcode Command Line Tools and compiler toolchain:
  ```bash
  xcode-select --install
  ```
  If Prophet remains problematic and is optional for you, consider deferring it by commenting it out in `requirements.txt`, or using `statsmodels` alternatives.

## 🌐 Environment variables

Key variables in `.env`:
- `ETHERSCAN_API_KEY`, `INFURA_PROJECT_ID`, etc.
- `DEMO_MODE` (true/false): allow UI to run with missing keys (limited/mocked integrations).
- `TALLY_API_KEY` (optional): Bearer token for Tally API.
- `WEBSOCKET_CORS_ORIGINS`: comma-separated origins for WebSocket CORS (e.g., `http://localhost,http://localhost:8501`).

For Docker, you can also set:
- `WEBSOCKET_PORT` (default 8000)
- `HEALTH_PORT` (default 8001)
- `DATABASE_URL`, `REDIS_URL`
