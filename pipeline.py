"""
pipeline.py
Complete monitoring pipeline: runs sentiment, volatility, liquidity,
and triggers alerts if thresholds are breached.

Refactored for testability and configuration-driven thresholding.
"""
from __future__ import annotations

import asyncio
import datetime
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from alerts import alert_user
from src.models.liquidity_model import forecast_tvl, get_tvl_history
from src.models.sentiment_model import analyze_sentiment, get_mock_tweets
from src.models.volatility_model import get_protocol_volatility

# Provide isolated module logger
logger = logging.getLogger(__name__)


@dataclass
class PipelineConfig:
    """Configuration for the monitoring pipeline."""
    sentiment_negative_threshold: float = 0.70
    volatility_threshold_pct: float = 60.0
    liquidity_drop_pct: float = 0.05
    protocol_slug: str = "curve-dex"
    search_term: str = "ethereum upgrade"


def check_sentiment(config: PipelineConfig) -> Tuple[float, List[Any], List[Dict[str, Any]]]:
    """Fetch tweets and calculate the negative sentiment ratio."""
    try:
        # In src.models, get_mock_tweets returns a list of string.
        tweets = get_mock_tweets(config.protocol_slug)
        sentiments = analyze_sentiment(tweets)
        
        # Analyze_tweet_sentiment in src.models returns a single average score from -1 to 1.
        # So we adapt: if it's deeply negative (-1.0 to 0.0), it represents a high ratio of negativity
        # We can map the -1 to 1 scale to a 0 to 1 negative ratio scale where 1 means 100% negative.
        # Wait, the pipeline config expects a ratio.
        # Let's map it: score of -1 => 1.0 (100% negative), score of 1 => 0.0 (0% negative).
        negative_ratio = (1 - sentiments) / 2
        
        logger.info("Sentiment analysis: %.1f%% negative (Score: %s)", negative_ratio * 100, sentiments)
        return negative_ratio, tweets, [{"score": sentiments}]  # Dummy structure to fulfill type
    except Exception as e:
        logger.error("Failed to check sentiment: %s", e)
        return 0.0, [], []


def check_volatility(config: PipelineConfig) -> float:
    """Fetch prices and calculate annualized GARCH volatility."""
    try:
        # get_protocol_volatility in src.models is async and returns a dict
        vol_data = asyncio.run(get_protocol_volatility(config.protocol_slug, days=180))
        vol = float(vol_data.get("volatility", 0.0))
        if "error" in vol_data:
            logger.warning("Volatility model returned error: %s", vol_data["error"])
        
        logger.info("Volatility forecast: %.2f%% annualized", vol)
        return vol
    except Exception as e:
        logger.error("Failed to check volatility: %s", e)
        return 0.0


def check_liquidity(config: PipelineConfig) -> Tuple[float, float, float]:
    """Fetch TVL and forecast the percentage drop over 7 days."""
    try:
        # get_tvl_history in src.models is async and returns a DataFrame
        df = asyncio.run(get_tvl_history(config.protocol_slug, days=90))
        if df.empty:
            return 0.0, 0.0, 0.0
            
        last_tvl = float(df["y"].iloc[-1])
        # forecast_tvl in src.models returns a single float (the yhat value)
        predicted_tvl = forecast_tvl(df, future_days=7)

        drop = (last_tvl - predicted_tvl) / last_tvl if last_tvl > 0 else 0.0
        logger.info(
            "Liquidity forecast: Current TVL=%.0f, 7d forecast=%.0f, drop=%.2f%%",
            last_tvl, predicted_tvl, drop * 100
        )
        return drop, last_tvl, predicted_tvl
    except Exception as e:
        logger.error("Failed to check liquidity: %s", e)
        return 0.0, 0.0, 0.0


def run_monitoring_cycle(config: PipelineConfig) -> List[str]:
    """
    Run one complete cycle of the monitoring pipeline.
    Returns a list of alert messages triggered during the cycle.
    """
    logger.info("Starting monitoring cycle for %s", config.protocol_slug)
    alert_msgs: List[str] = []

    negative_ratio, _, _ = check_sentiment(config)
    if negative_ratio > config.sentiment_negative_threshold:
        msg = f"ALERT: Sentiment risk. Negative sentiment at {negative_ratio*100:.1f}%."
        logger.warning(msg)
        alert_msgs.append(msg)

    vol = check_volatility(config)
    if vol > config.volatility_threshold_pct:
        msg = f"ALERT: Volatility risk. Annualized volatility is {vol:.2f}%."
        logger.warning(msg)
        alert_msgs.append(msg)

    drop, _, _ = check_liquidity(config)
    if drop > config.liquidity_drop_pct:
        msg = f"ALERT: Liquidity risk. TVL forecast drop of {drop*100:.2f}%."
        logger.warning(msg)
        alert_msgs.append(msg)

    return alert_msgs


def main():
    """Main execution point for cron/scheduler."""
    # Optional .env loading
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.FileHandler("pipeline.log"), logging.StreamHandler()]
    )

    config = PipelineConfig()
    alerts = run_monitoring_cycle(config)

    if alerts:
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        metadata = {"timestamp": timestamp}
        for msg in alerts:
            alert_user(title="Blockchain Risk Alert!", message=msg, channel="slack", metadata=metadata)
            alert_user(title="Blockchain Risk Alert!", message=msg, channel="email", metadata=metadata)
        logger.info("Alerts dispatched successfully.")
    else:
        logger.info("No thresholds breached; no alerts dispatched.")


if __name__ == "__main__":
    main()
