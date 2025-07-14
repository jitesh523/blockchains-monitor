#!/usr/bin/env python3
"""
Test script for integrated volatility, sentiment, and liquidity models.
"""

import asyncio
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.models.volatility_model import get_protocol_volatility
from src.models.sentiment_model import analyze_sentiment, get_sentiment_for_protocol
from src.models.liquidity_model import get_tvl_history, forecast_tvl
from src.models.risk_model import get_risk_assessment

async def test_integrated_models():
    """Test all models working together."""
    print("🔬 Testing Integrated Models")
    print("=" * 60)
    
    # Test protocols
    protocols = ['uniswap', 'aave', 'ethereum']
    
    for protocol in protocols:
        print(f"\n📊 Testing {protocol.upper()}:")
        print("-" * 40)
        
        # Test volatility
        try:
            vol_data = await get_protocol_volatility(protocol)
            print(f"  Volatility: {vol_data.get('volatility', 'N/A')}%")
        except Exception as e:
            print(f"  Volatility Error: {e}")
        
        # Test sentiment
        try:
            sentiment_data = get_sentiment_for_protocol(protocol)
            print(f"  Sentiment: {sentiment_data.get('average_sentiment', 'N/A')}")
        except Exception as e:
            print(f"  Sentiment Error: {e}")
        
        # Test liquidity (TVL)
        try:
            # Map protocol names to DeFiLlama slugs
            protocol_mapping = {
                'uniswap': 'uniswap',
                'aave': 'aave',
                'ethereum': 'ethereum'
            }
            
            slug = protocol_mapping.get(protocol, protocol)
            tvl_data = await get_tvl_history(slug)
            
            if not tvl_data.empty:
                current_tvl = tvl_data['y'].iloc[-1]
                forecasted_tvl = forecast_tvl(tvl_data)
                delta = forecasted_tvl - current_tvl
                
                print(f"  Current TVL: ${current_tvl:,.2f}")
                print(f"  Forecasted TVL: ${forecasted_tvl:,.2f}")
                print(f"  Delta: ${delta:+,.2f}")
            else:
                print(f"  TVL: No data available")
                
        except Exception as e:
            print(f"  TVL Error: {e}")
        
        # Test risk assessment
        try:
            risk_data = await get_risk_assessment(protocol)
            print(f"  Risk Score: {risk_data.get('overall_risk_score', 'N/A')}")
            print(f"  Risk Category: {risk_data.get('risk_category', 'N/A')}")
        except Exception as e:
            print(f"  Risk Assessment Error: {e}")

async def test_mock_sentiment():
    """Test mock sentiment analysis."""
    print("\n🎭 Testing Mock Sentiment Analysis")
    print("=" * 60)
    
    mock_tweets = {
        "Uniswap": [
            "This proposal looks solid!",
            "Gov vote might shift liquidity.",
            "Could be risky in the short term."
        ],
        "Aave": [
            "No major changes, good stability.",
            "I'm bullish on this proposal.",
            "This vote is a game changer!"
        ]
    }
    
    for protocol, tweets in mock_tweets.items():
        print(f"\n{protocol} tweets:")
        for tweet in tweets:
            print(f"  - {tweet}")
        
        sentiment_score = analyze_sentiment(tweets)
        print(f"  Sentiment Score: {sentiment_score}")
        
        if sentiment_score > 0.3:
            sentiment_label = "😊 Positive"
        elif sentiment_score < -0.3:
            sentiment_label = "😠 Negative"
        else:
            sentiment_label = "😐 Neutral"
        
        print(f"  Sentiment Label: {sentiment_label}")

if __name__ == "__main__":
    print("🚀 Starting Integrated Model Tests")
    print("=" * 60)
    
    # Run sentiment test first (doesn't require async)
    asyncio.run(test_mock_sentiment())
    
    # Run integrated model tests
    asyncio.run(test_integrated_models())
    
    print("\n✅ All integrated model tests completed!")
