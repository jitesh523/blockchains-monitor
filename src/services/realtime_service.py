"""
Real-time data broadcaster service that sends updates via WebSocket.
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any
from src.services.database_service import db_service, PriceData, SentimentData, RiskEvent
from src.services.websocket_server import broadcast_to_clients
from src.services.cache_service import cached, exponential_backoff, with_circuit_breaker
import requests

logger = logging.getLogger(__name__)

class RealtimeService:
    def __init__(self):
        self.is_running = False
        self.update_interval = 30  # seconds
        
    async def start(self):
        """Start the real-time data collection and broadcasting service"""
        self.is_running = True
        logger.info("Real-time service started")
        
        # Start background tasks
        await asyncio.gather(
            self.price_update_loop(),
            self.sentiment_update_loop(),
            self.risk_assessment_loop(),
            self.broadcast_loop()
        )
    
    async def stop(self):
        """Stop the real-time service"""
        self.is_running = False
        logger.info("Real-time service stopped")
    
    @cached(prefix="price_data", ttl=60)
    @exponential_backoff(max_retries=3)
    @with_circuit_breaker("coingecko")
    async def fetch_latest_prices(self) -> Dict[str, Any]:
        """Fetch latest prices from CoinGecko API"""
        tokens = ["ethereum", "bitcoin", "uniswap", "aave", "compound"]
        prices = {}
        
        for token in tokens:
            try:
                response = requests.get(
                    f"https://api.coingecko.com/api/v3/simple/price",
                    params={
                        "ids": token,
                        "vs_currencies": "usd",
                        "include_24hr_vol": "true",
                        "include_market_cap": "true"
                    },
                    timeout=10
                )
                response.raise_for_status()
                data = response.json()
                
                if token in data:
                    prices[token] = {
                        "price": data[token]["usd"],
                        "volume_24h": data[token].get("usd_24h_vol", 0),
                        "market_cap": data[token].get("usd_market_cap", 0),
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    # Store in database
                    price_data = PriceData(
                        token=token,
                        price=data[token]["usd"],
                        volume_24h=data[token].get("usd_24h_vol", 0),
                        market_cap=data[token].get("usd_market_cap", 0),
                        timestamp=datetime.now()
                    )
                    await db_service.insert_price_data(price_data)
                    
            except Exception as e:
                logger.error(f"Error fetching price for {token}: {e}")
                continue
        
        return prices
    
    async def generate_sentiment_data(self) -> Dict[str, Any]:
        """Generate mock sentiment data (replace with real Twitter/Reddit analysis)"""
        import random
        
        sentiment_data = {
            "overall_sentiment": random.uniform(-1, 1),
            "sentiment_sources": [
                {
                    "source": "twitter",
                    "sentiment": random.uniform(-1, 1),
                    "volume": random.randint(100, 1000)
                },
                {
                    "source": "reddit",
                    "sentiment": random.uniform(-1, 1),
                    "volume": random.randint(50, 500)
                }
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        # Store in database
        sentiment_obj = SentimentData(
            source="aggregated",
            content="Real-time sentiment analysis",
            sentiment_score=sentiment_data["overall_sentiment"],
            timestamp=datetime.now(),
            metadata={"sources": sentiment_data["sentiment_sources"]}
        )
        await db_service.insert_sentiment_data(sentiment_obj)
        
        return sentiment_data
    
    async def assess_risk_levels(self) -> Dict[str, Any]:
        """Assess current risk levels across protocols"""
        import random
        
        protocols = ["ethereum", "uniswap", "aave", "compound"]
        risk_data = {}
        
        for protocol in protocols:
            risk_score = random.uniform(0, 100)
            risk_level = "low" if risk_score < 30 else "medium" if risk_score < 70 else "high"
            
            risk_data[protocol] = {
                "risk_score": risk_score,
                "risk_level": risk_level,
                "factors": [
                    {"factor": "volatility", "impact": random.uniform(0, 1)},
                    {"factor": "sentiment", "impact": random.uniform(0, 1)},
                    {"factor": "liquidity", "impact": random.uniform(0, 1)}
                ],
                "timestamp": datetime.now().isoformat()
            }
            
            # Store high-risk events in database
            if risk_score > 70:
                risk_event = RiskEvent(
                    event_type="high_risk_alert",
                    protocol=protocol,
                    risk_score=risk_score,
                    description=f"High risk detected for {protocol}",
                    timestamp=datetime.now(),
                    metadata={"factors": risk_data[protocol]["factors"]}
                )
                await db_service.insert_risk_event(risk_event)
        
        return risk_data
    
    async def price_update_loop(self):
        """Background loop for price updates"""
        while self.is_running:
            try:
                prices = await self.fetch_latest_prices()
                await broadcast_to_clients(json.dumps({
                    "type": "price_update",
                    "data": prices
                }))
                logger.info("Price data broadcasted")
            except Exception as e:
                logger.error(f"Error in price update loop: {e}")
            
            await asyncio.sleep(self.update_interval)
    
    async def sentiment_update_loop(self):
        """Background loop for sentiment updates"""
        while self.is_running:
            try:
                sentiment = await self.generate_sentiment_data()
                await broadcast_to_clients(json.dumps({
                    "type": "sentiment_update",
                    "data": sentiment
                }))
                logger.info("Sentiment data broadcasted")
            except Exception as e:
                logger.error(f"Error in sentiment update loop: {e}")
            
            await asyncio.sleep(self.update_interval * 2)  # Update every 60 seconds
    
    async def risk_assessment_loop(self):
        """Background loop for risk assessment"""
        while self.is_running:
            try:
                risk_data = await self.assess_risk_levels()
                await broadcast_to_clients(json.dumps({
                    "type": "risk_update",
                    "data": risk_data
                }))
                logger.info("Risk assessment data broadcasted")
            except Exception as e:
                logger.error(f"Error in risk assessment loop: {e}")
            
            await asyncio.sleep(self.update_interval * 3)  # Update every 90 seconds
    
    async def broadcast_loop(self):
        """Background loop for periodic status broadcasts"""
        while self.is_running:
            try:
                # Get aggregated stats from database
                stats = await db_service.get_protocol_stats()
                
                await broadcast_to_clients(json.dumps({
                    "type": "system_status",
                    "data": {
                        "status": "operational",
                        "timestamp": datetime.now().isoformat(),
                        "stats": stats
                    }
                }))
                logger.info("System status broadcasted")
            except Exception as e:
                logger.error(f"Error in broadcast loop: {e}")
            
            await asyncio.sleep(self.update_interval * 4)  # Update every 2 minutes

# Global real-time service instance
realtime_service = RealtimeService()

async def start_realtime_service():
    """Start the real-time service"""
    await realtime_service.start()

async def stop_realtime_service():
    """Stop the real-time service"""
    await realtime_service.stop()
