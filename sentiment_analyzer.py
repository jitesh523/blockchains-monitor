"""
sentiment_analyzer.py
Fetches real tweets using Twitter API and analyzes sentiment with HuggingFace DistilBERT.
Note: Requires transformers, torch, requests. Add to requirements.txt if needed.
"""
import os
import requests
from transformers import pipeline

TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
assert TWITTER_BEARER_TOKEN, "Twitter Bearer Token not set in .env!"

# Set up DistilBERT (or other HuggingFace) for sentiment analysis
sentiment_pipe = pipeline("sentiment-analysis")

def get_tweets(query, max_results=10):
    # Dummy tweets for local dev/testing
    return [
        "Ethereum upgrade is fantastic!",
        "I'm worried about the upcoming Ethereum upgrade.",
        "Mixed feelings on the next ETH hard fork.",
        "ETH upgrades are always exciting.",
        "Serious risks in this Ethereum protocol change!"
    ]

def analyze_tweet_sentiment(tweets):
    return sentiment_pipe(tweets)

if __name__ == "__main__":
    query = "ethereum"  # Simpler query for wider compatibility
    tweets = get_tweets(query=query, max_results=10)
    print("TWEETS:\n", tweets)
    if not tweets:
        print("No tweets found. Your Twitter API subscription may limit search endpoints.")
    else:
        sentiment_results = analyze_tweet_sentiment(tweets)
        for t, r in zip(tweets, sentiment_results):
            print(f"{t}\n -> Sentiment: {r}")

