#!/usr/bin/env python3
"""
Test script for the sentiment analysis model.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.models.sentiment_model import (
    analyze_sentiment, 
    analyze_sentiment_detailed, 
    get_sentiment_for_protocol,
    categorize_sentiment,
    get_sentiment_color,
    test_sentiment_analysis
)

def test_basic_sentiment():
    """Test basic sentiment analysis functionality."""
    print("Testing Basic Sentiment Analysis...")
    print("=" * 50)
    
    # Test positive sentiment
    positive_texts = [
        "This upgrade is amazing! Great work by the team.",
        "Bullish on this protocol after the new proposal.",
        "Love the new features, this will boost adoption."
    ]
    
    positive_score = analyze_sentiment(positive_texts)
    print(f"Positive texts score: {positive_score}")
    print(f"Category: {categorize_sentiment(positive_score)}")
    print(f"Color: {get_sentiment_color(positive_score)}")
    
    # Test negative sentiment
    negative_texts = [
        "This upgrade is terrible. Going to crash the price.",
        "Hate this proposal. It's going to ruin everything.",
        "This is a disaster waiting to happen."
    ]
    
    negative_score = analyze_sentiment(negative_texts)
    print(f"\nNegative texts score: {negative_score}")
    print(f"Category: {categorize_sentiment(negative_score)}")
    print(f"Color: {get_sentiment_color(negative_score)}")
    
    # Test mixed sentiment
    mixed_texts = [
        "This proposal has some good points but also risks.",
        "Not sure about this upgrade, could go either way.",
        "Interesting idea but needs more community discussion."
    ]
    
    mixed_score = analyze_sentiment(mixed_texts)
    print(f"\nMixed texts score: {mixed_score}")
    print(f"Category: {categorize_sentiment(mixed_score)}")
    print(f"Color: {get_sentiment_color(mixed_score)}")

def test_detailed_sentiment():
    """Test detailed sentiment analysis."""
    print("\n\nTesting Detailed Sentiment Analysis...")
    print("=" * 50)
    
    sample_texts = [
        "This proposal looks promising and could push prices up.",
        "Not sure if this upgrade is safe. Could lead to vulnerabilities.",
        "Amazing vote turnout! Community is really backing it.",
        "Disaster incoming. Everyone's dumping their tokens!"
    ]
    
    detailed_result = analyze_sentiment_detailed(sample_texts)
    
    print(f"Average sentiment: {detailed_result['average_sentiment']}")
    print(f"Positive count: {detailed_result['positive_count']}")
    print(f"Negative count: {detailed_result['negative_count']}")
    print(f"Total texts: {detailed_result['total_texts']}")
    
    print("\nIndividual scores:")
    for i, score_info in enumerate(detailed_result['individual_scores']):
        print(f"{i+1}. {score_info['text']}")
        print(f"   Label: {score_info['label']} | Score: {score_info['score']:.3f} | Normalized: {score_info['normalized_score']:.3f}")

def test_protocol_sentiment():
    """Test protocol-specific sentiment analysis."""
    print("\n\nTesting Protocol-Specific Sentiment...")
    print("=" * 50)
    
    protocols = ['uniswap', 'aave', 'compound', 'ethereum']
    
    for protocol in protocols:
        print(f"\n{protocol.upper()} Sentiment Analysis:")
        sentiment_data = get_sentiment_for_protocol(protocol)
        
        print(f"  Average Sentiment: {sentiment_data['average_sentiment']}")
        print(f"  Category: {categorize_sentiment(sentiment_data['average_sentiment'])}")
        print(f"  Color: {get_sentiment_color(sentiment_data['average_sentiment'])}")
        print(f"  Positive: {sentiment_data['positive_count']}")
        print(f"  Negative: {sentiment_data['negative_count']}")
        print(f"  Total Texts: {sentiment_data['total_texts']}")

if __name__ == "__main__":
    print("🧪 Sentiment Analysis Testing Suite")
    print("=" * 60)
    
    # Run all tests
    test_basic_sentiment()
    test_detailed_sentiment()
    test_protocol_sentiment()
    
    print("\n\n🎯 Running built-in test function...")
    print("=" * 60)
    test_sentiment_analysis()
    
    print("\n✅ All tests completed!")
