"""
Database service with PostgreSQL integration for historical data storage.
"""
import asyncio
import asyncpg
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import os
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class PriceData:
    token: str
    price: float
    timestamp: datetime
    volume_24h: float = 0.0
    market_cap: float = 0.0

@dataclass
class SentimentData:
    source: str
    content: str
    sentiment_score: float
    timestamp: datetime
    metadata: Dict[str, Any] = None

@dataclass
class RiskEvent:
    event_type: str
    protocol: str
    risk_score: float
    description: str
    timestamp: datetime
    metadata: Dict[str, Any] = None

class DatabaseService:
    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv(
            'DATABASE_URL', 
            'postgresql://user:password@localhost:5432/blockchain_monitor'
        )
        self.pool = None
    
    async def connect(self):
        """Initialize database connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            logger.info("Database connection pool established")
            await self.create_tables()
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    async def create_tables(self):
        """Create database tables if they don't exist"""
        tables = [
            """
            CREATE TABLE IF NOT EXISTS price_data (
                id SERIAL PRIMARY KEY,
                token VARCHAR(50) NOT NULL,
                price DECIMAL(20, 8) NOT NULL,
                volume_24h DECIMAL(20, 8) DEFAULT 0,
                market_cap DECIMAL(20, 8) DEFAULT 0,
                timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS sentiment_data (
                id SERIAL PRIMARY KEY,
                source VARCHAR(50) NOT NULL,
                content TEXT NOT NULL,
                sentiment_score DECIMAL(5, 4) NOT NULL,
                timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                metadata JSONB DEFAULT '{}',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS risk_events (
                id SERIAL PRIMARY KEY,
                event_type VARCHAR(50) NOT NULL,
                protocol VARCHAR(100) NOT NULL,
                risk_score DECIMAL(5, 2) NOT NULL,
                description TEXT NOT NULL,
                timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                metadata JSONB DEFAULT '{}',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS protocol_upgrades (
                id SERIAL PRIMARY KEY,
                protocol VARCHAR(100) NOT NULL,
                upgrade_name VARCHAR(200) NOT NULL,
                status VARCHAR(50) NOT NULL,
                scheduled_date TIMESTAMP WITH TIME ZONE,
                completion_date TIMESTAMP WITH TIME ZONE,
                description TEXT,
                risk_assessment JSONB DEFAULT '{}',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS tvl_data (
                id SERIAL PRIMARY KEY,
                protocol VARCHAR(100) NOT NULL,
                tvl DECIMAL(20, 2) NOT NULL,
                chain VARCHAR(50) NOT NULL,
                timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
            """
        ]
        
        # Create indexes
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_price_data_token_timestamp ON price_data(token, timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_sentiment_data_timestamp ON sentiment_data(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_risk_events_timestamp ON risk_events(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_protocol_upgrades_protocol ON protocol_upgrades(protocol)",
            "CREATE INDEX IF NOT EXISTS idx_tvl_data_protocol_timestamp ON tvl_data(protocol, timestamp)"
        ]
        
        async with self.pool.acquire() as conn:
            for table in tables:
                await conn.execute(table)
            
            for index in indexes:
                await conn.execute(index)
        
        logger.info("Database tables created successfully")
    
    async def insert_price_data(self, data: PriceData):
        """Insert price data into database"""
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO price_data (token, price, volume_24h, market_cap, timestamp)
                VALUES ($1, $2, $3, $4, $5)
                """,
                data.token, data.price, data.volume_24h, data.market_cap, data.timestamp
            )
    
    async def insert_sentiment_data(self, data: SentimentData):
        """Insert sentiment data into database"""
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO sentiment_data (source, content, sentiment_score, timestamp, metadata)
                VALUES ($1, $2, $3, $4, $5)
                """,
                data.source, data.content, data.sentiment_score, data.timestamp, 
                json.dumps(data.metadata or {})
            )
    
    async def insert_risk_event(self, event: RiskEvent):
        """Insert risk event into database"""
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO risk_events (event_type, protocol, risk_score, description, timestamp, metadata)
                VALUES ($1, $2, $3, $4, $5, $6)
                """,
                event.event_type, event.protocol, event.risk_score, event.description,
                event.timestamp, json.dumps(event.metadata or {})
            )
    
    async def get_price_history(self, token: str, days: int = 30) -> List[Dict]:
        """Get price history for a token"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT token, price, volume_24h, market_cap, timestamp
                FROM price_data
                WHERE token = $1 AND timestamp > NOW() - INTERVAL '%s days'
                ORDER BY timestamp ASC
                """,
                token, days
            )
            return [dict(row) for row in rows]
    
    async def get_sentiment_trend(self, hours: int = 24) -> List[Dict]:
        """Get sentiment trend for the last N hours"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT 
                    DATE_TRUNC('hour', timestamp) as hour,
                    AVG(sentiment_score) as avg_sentiment,
                    COUNT(*) as count
                FROM sentiment_data
                WHERE timestamp > NOW() - INTERVAL '%s hours'
                GROUP BY hour
                ORDER BY hour ASC
                """,
                hours
            )
            return [dict(row) for row in rows]
    
    async def get_risk_events(self, protocol: str = None, days: int = 7) -> List[Dict]:
        """Get recent risk events"""
        async with self.pool.acquire() as conn:
            if protocol:
                rows = await conn.fetch(
                    """
                    SELECT event_type, protocol, risk_score, description, timestamp, metadata
                    FROM risk_events
                    WHERE protocol = $1 AND timestamp > NOW() - INTERVAL '%s days'
                    ORDER BY timestamp DESC
                    """,
                    protocol, days
                )
            else:
                rows = await conn.fetch(
                    """
                    SELECT event_type, protocol, risk_score, description, timestamp, metadata
                    FROM risk_events
                    WHERE timestamp > NOW() - INTERVAL '%s days'
                    ORDER BY timestamp DESC
                    """,
                    days
                )
            return [dict(row) for row in rows]
    
    async def get_protocol_stats(self) -> Dict[str, Any]:
        """Get aggregated protocol statistics"""
        async with self.pool.acquire() as conn:
            # Get total events by protocol
            protocol_events = await conn.fetch(
                """
                SELECT protocol, COUNT(*) as event_count, AVG(risk_score) as avg_risk
                FROM risk_events
                WHERE timestamp > NOW() - INTERVAL '30 days'
                GROUP BY protocol
                ORDER BY event_count DESC
                """
            )
            
            # Get recent sentiment trend
            sentiment_trend = await conn.fetch(
                """
                SELECT 
                    DATE_TRUNC('day', timestamp) as day,
                    AVG(sentiment_score) as avg_sentiment
                FROM sentiment_data
                WHERE timestamp > NOW() - INTERVAL '7 days'
                GROUP BY day
                ORDER BY day ASC
                """
            )
            
            return {
                'protocol_events': [dict(row) for row in protocol_events],
                'sentiment_trend': [dict(row) for row in sentiment_trend],
                'last_updated': datetime.now().isoformat()
            }
    
    async def cleanup_old_data(self, retention_days: int = 90):
        """Clean up old data based on retention policy"""
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        async with self.pool.acquire() as conn:
            # Clean up old price data
            await conn.execute(
                "DELETE FROM price_data WHERE timestamp < $1",
                cutoff_date
            )
            
            # Clean up old sentiment data
            await conn.execute(
                "DELETE FROM sentiment_data WHERE timestamp < $1",
                cutoff_date
            )
            
            # Keep risk events longer (1 year)
            risk_cutoff = datetime.now() - timedelta(days=365)
            await conn.execute(
                "DELETE FROM risk_events WHERE timestamp < $1",
                risk_cutoff
            )
        
        logger.info(f"Cleaned up data older than {retention_days} days")
    
    async def close(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")

# Global database instance
db_service = DatabaseService()

async def init_database():
    """Initialize database connection"""
    await db_service.connect()

async def cleanup_database():
    """Cleanup database connection"""
    await db_service.close()
