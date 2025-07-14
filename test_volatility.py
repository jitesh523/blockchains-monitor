#!/usr/bin/env python3
"""
Test script for the volatility model.
"""

import asyncio
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.models.volatility_model import get_protocol_volatility, get_prices, forecast_volatility

async def test_volatility_model():
    """Test the volatility model with some sample protocols."""
    print("Testing Volatility Model...")
    print("=" * 50)
    
    # Test protocols
    protocols = ['ethereum', 'uniswap', 'aave']
    
    for protocol in protocols:
        print(f"\nTesting {protocol}...")
        
        try:
            # Get volatility data
            vol_data = await get_protocol_volatility(protocol, days=90, horizon=3)
            
            if 'error' in vol_data:
                print(f"❌ Error for {protocol}: {vol_data['error']}")
            else:
                print(f"✅ {protocol.upper()} Results:")
                print(f"   Volatility: {vol_data['volatility']:.2f}%")
                print(f"   Token ID: {vol_data['token_id']}")
                print(f"   Data Points: {vol_data['data_points']}")
                print(f"   Latest Price: ${vol_data['latest_price']:.4f}")
                print(f"   24h Change: {vol_data['price_change_24h']:.2f}%")
                
        except Exception as e:
            print(f"❌ Exception for {protocol}: {e}")

if __name__ == "__main__":
    asyncio.run(test_volatility_model())
