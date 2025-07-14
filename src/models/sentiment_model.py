"""
BERT-based Sentiment Analysis Module

This module uses a pretrained transformer model from HuggingFace
to score a batch of tweets/comments related to protocol upgrades.
"""

from transformers import pipeline
from typing import List, Dict, Optional
import numpy as np
import logging
import asyncio
import aiohttp
import json
from datetime import datetime

logger = logging.getLogger(__name__)

# Initialize once globally
try:
    sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
    logger.info("✅ Sentiment model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load sentiment model: {e}")
    sentiment_pipeline = None

def analyze_sentiment(texts: List[str]) -> float:
    """Returns an average sentiment score between -1 and +1"""
    if not sentiment_pipeline or not texts:
        return 0.0
    
    try:
        results = sentiment_pipeline(texts)
        scores = []
        for res in results:
            label = res['label']
            score = res['score']
            if label == 'POSITIVE':
                scores.append(score)           # +ve
            else:
                scores.append(-1 * score)      # -ve
        return round(float(np.mean(scores)), 3)
    except Exception as e:
        logger.error(f"Sentiment analysis failed: {e}")
        return 0.0

def analyze_sentiment_detailed(texts: List[str]) -> Dict:
    """Returns detailed sentiment analysis with individual scores"""
    if not sentiment_pipeline or not texts:
        return {
            'average_sentiment': 0.0,
            'positive_count': 0,
            'negative_count': 0,
            'neutral_count': 0,
            'total_texts': 0,
            'individual_scores': []
        }
    
    try:
        results = sentiment_pipeline(texts)
        scores = []
        positive_count = 0
        negative_count = 0
        individual_scores = []
        
        for i, res in enumerate(results):
            label = res['label']
            score = res['score']
            
            if label == 'POSITIVE':
                normalized_score = score
                positive_count += 1
            else:
                normalized_score = -1 * score
                negative_count += 1
                
            scores.append(normalized_score)
            individual_scores.append({
                'text': texts[i][:100] + '...' if len(texts[i]) > 100 else texts[i],
                'label': label,
                'score': score,
                'normalized_score': normalized_score
            })
        
        return {
            'average_sentiment': round(float(np.mean(scores)), 3),
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': 0,  # DistilBERT doesn't have neutral class
            'total_texts': len(texts),
            'individual_scores': individual_scores
        }
        
    except Exception as e:
        logger.error(f"Detailed sentiment analysis failed: {e}")
        return {
            'average_sentiment': 0.0,
            'positive_count': 0,
            'negative_count': 0,
            'neutral_count': 0,
            'total_texts': 0,
            'individual_scores': []
        }

def get_mock_tweets(protocol_name: str, upgrade_type: str = "general") -> List[str]:
    """Generate mock tweets for testing sentiment analysis"""
    
    base_tweets = [
        "I don't trust this upgrade. Feels rushed.",
        "Big win for the protocol. Gov vote passed!",
        "Risky move. Could cause a price dump.",
        "This proposal looks promising and could push prices up.",
        "Not sure if this upgrade is safe. Could lead to vulnerabilities.",
        "Amazing vote turnout! Community is really backing it.",
        "Disaster incoming. Everyone's dumping their tokens!"
    ]
    
    # Add protocol-specific tweets
    protocol_tweets = {
        'uniswap': [
            f"New {protocol_name} upgrade will improve liquidity!",
            f"Concerned about {protocol_name} governance centralization",
            f"{protocol_name} fees are getting too high with this change",
            f"Bullish on {protocol_name} after this upgrade announcement"
        ],
        'aave': [
            f"AAVE lending rates will be much better after upgrade",
            f"This {protocol_name} proposal could hurt borrowers",
            f"Great to see {protocol_name} innovating in DeFi space",
            f"Worried about {protocol_name} liquidation risks"
        ],
        'compound': [
            f"Compound governance is getting stronger",
            f"Not sure about {protocol_name} new interest rate model",
            f"COMP holders should vote YES on this",
            f"This {protocol_name} upgrade might cause market volatility"
        ]
    }
    
    # Combine base tweets with protocol-specific ones
    all_tweets = base_tweets.copy()
    if protocol_name.lower() in protocol_tweets:
        all_tweets.extend(protocol_tweets[protocol_name.lower()])
    
    # Add upgrade-type specific tweets
    if upgrade_type == "governance":
        all_tweets.extend([
            "Governance proposals are getting too complex",
            "Love seeing community participation in voting",
            "These governance changes will centralize power"
        ])
    elif upgrade_type == "technical":
        all_tweets.extend([
            "Technical upgrades always make me nervous",
            "Smart contract audit looks solid",
            "This code change could introduce bugs"
        ])
    
    return all_tweets

async def fetch_real_tweets(protocol_name: str, keyword: str = "upgrade") -> List[str]:
    """
    Placeholder for real tweet fetching functionality.
    In production, this would use Twitter API v2 or SNScrape.
    """
    # This is a mock implementation
    # In production, you would implement actual Twitter API calls
    logger.info(f"Fetching real tweets for {protocol_name} with keyword '{keyword}'")
    
    # For now, return mock data
    return get_mock_tweets(protocol_name, "general")

def get_sentiment_for_protocol(protocol_name: str, upgrade_type: str = "general") -> Dict:
    """Get sentiment analysis for a specific protocol upgrade"""
    
    # In production, this would fetch real tweets
    # For now, we'll use mock data
    tweets = get_mock_tweets(protocol_name, upgrade_type)
    
    # Analyze sentiment
    sentiment_data = analyze_sentiment_detailed(tweets)
    
    # Add protocol context
    sentiment_data['protocol'] = protocol_name
    sentiment_data['upgrade_type'] = upgrade_type
    sentiment_data['timestamp'] = datetime.now().isoformat()
    
    return sentiment_data

def categorize_sentiment(score: float) -> str:
    """Categorize sentiment score into readable categories"""
    if score >= 0.3:
        return "Very Positive"
    elif score >= 0.1:
        return "Positive"
    elif score >= -0.1:
        return "Neutral"
    elif score >= -0.3:
        return "Negative"
    else:
        return "Very Negative"

def get_sentiment_color(score: float) -> str:
    """Get color code for sentiment visualization"""
    if score >= 0.3:
        return "🟢"  # Green
    elif score >= 0.1:
        return "🟡"  # Yellow-green
    elif score >= -0.1:
        return "🟡"  # Yellow
    elif score >= -0.3:
        return "🟠"  # Orange
    else:
        return "🔴"  # Red

# Test function
def test_sentiment_analysis():
    """Test the sentiment analysis with sample data"""
    print("Testing Sentiment Analysis...")
    print("=" * 50)
    
    sample_tweets = [
        "This proposal looks promising and could push prices up.",
        "Not sure if this upgrade is safe. Could lead to vulnerabilities.",
        "Amazing vote turnout! Community is really backing it.",
        "Disaster incoming. Everyone's dumping their tokens!"
    ]
    
    # Test basic sentiment
    avg_sentiment = analyze_sentiment(sample_tweets)
    print(f"Average sentiment: {avg_sentiment}")
    print(f"Sentiment category: {categorize_sentiment(avg_sentiment)}")
    
    # Test detailed sentiment
    detailed = analyze_sentiment_detailed(sample_tweets)
    print(f"\nDetailed analysis:")
    print(f"- Average: {detailed['average_sentiment']}")
    print(f"- Positive: {detailed['positive_count']}")
    print(f"- Negative: {detailed['negative_count']}")
    print(f"- Total: {detailed['total_texts']}")
    
    # Test protocol-specific sentiment
    protocols = ['uniswap', 'aave', 'compound']
    for protocol in protocols:
        print(f"\n{protocol.upper()} Sentiment:")
        sentiment_data = get_sentiment_for_protocol(protocol)
        print(f"- Score: {sentiment_data['average_sentiment']}")
        print(f"- Category: {categorize_sentiment(sentiment_data['average_sentiment'])}")
        print(f"- Tweets analyzed: {sentiment_data['total_texts']}")

if __name__ == "__main__":
    test_sentiment_analysis()
