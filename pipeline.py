"""
pipeline.py
Complete monitoring pipeline: runs sentiment, volatility, liquidity, and triggers alerts if thresholds are breached.
Requires: requests, pandas, arch, prophet, transformers, torch, smtplib, python-dotenv (for .env, optional)
"""
import os
import logging
import datetime
from sentiment_analyzer import get_tweets, analyze_tweet_sentiment
from volatility_model import fetch_eth_prices, compute_garch_volatility
from liquidity_model import fetch_tvl, forecast_tvl
from alerts import alert_user

# Optionally load .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s', handlers=[logging.FileHandler("pipeline.log"), logging.StreamHandler()])

# Thresholds (customize for your protocol/system)
SENTIMENT_NEGATIVE_THRESHOLD = 0.7  # if > 70% tweets are negative
VOLATILITY_THRESHOLD = 0.6          # if annualized vol > 60%
LIQUIDITY_DROP_PCT = 0.05           # if forecast TVL drops >5% next week


def check_sentiment():
    tweets = get_tweets("ethereum upgrade", max_results=5)
    sentiments = analyze_tweet_sentiment(tweets)
    negatives = sum(1 for s in sentiments if s['label'] == 'NEGATIVE')
    negative_ratio = negatives / len(sentiments)
    logging.info(f"Sentiment analysis: {negative_ratio*100:.1f}% negative")
    return negative_ratio, tweets, sentiments


def check_volatility():
    prices = fetch_eth_prices(days=180)
    vol = compute_garch_volatility(prices)
    logging.info(f"Volatility forecast: {vol:.2f}% annualized")
    return vol


def check_liquidity(protocol_slug='curve-dex'):
    df = fetch_tvl(protocol_slug)
    forecast = forecast_tvl(df, days=7)
    last = df['y'].iloc[-1]
    predicted = forecast['yhat'].iloc[-1]
    drop = (last - predicted) / last if last > 0 else 0
    logging.info(f"Liquidity forecast: Current TVL={last:,.0f}, 7d forecast={predicted:,.0f}, drop={drop*100:.2f}%")
    return drop, last, predicted


def main():
    negative_ratio, tweets, sentiments = check_sentiment()
    vol = check_volatility()
    drop, last_tvl, pred_tvl = check_liquidity()
    alert_msgs = []

    if negative_ratio > SENTIMENT_NEGATIVE_THRESHOLD:
        msg = f"ALERT: Sentiment risk. Negative sentiment at {negative_ratio*100:.1f}%."
        logging.warning(msg)
        alert_msgs.append(msg)

    if vol > VOLATILITY_THRESHOLD * 100:
        msg = f"ALERT: Volatility risk. Annualized volatility is {vol:.2f}%."
        logging.warning(msg)
        alert_msgs.append(msg)

    if drop > LIQUIDITY_DROP_PCT:
        msg = f"ALERT: Liquidity risk. TVL forecast drop of {drop*100:.2f}%."
        logging.warning(msg)
        alert_msgs.append(msg)

    if alert_msgs:
        for msg in alert_msgs:
            alert_user(
                title="Blockchain Risk Alert!",
                message=msg,
                channel="slack",
                metadata={"timestamp": datetime.datetime.utcnow().isoformat()}
            )
            alert_user(
                title="Blockchain Risk Alert!",
                message=msg,
                channel="email",
                metadata={"timestamp": datetime.datetime.utcnow().isoformat()}
            )
        logging.info("Alerts triggered.")
    else:
        logging.info("No thresholds breached; no alerts.")

if __name__ == "__main__":
    main()

